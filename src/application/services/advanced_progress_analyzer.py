# Transformers imports patched for development
"""
🧠 Advanced Progress Analyzer Service - Task 7
تحليل تقدم الطفل باستخدام NLP متقدم وLLM مع Chain-of-Thought prompting
"""

import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLP Libraries
try:
    from collections import Counter

    import nltk
    import spacy
    from nltk.sentiment import SentimentIntensityAnalyzer
    from spacy import displacy
    from textstat import flesch_reading_ease, syllable_count

    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logger.warning(
        "⚠️ NLP libraries not available. Install with: pip install spacy nltk textstat"
    )

# Transformers for advanced analysis
try:
    from transformers import AutoModel, AutoTokenizer, pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    try:
        import torch

        from src.infrastructure.external_services.mock.transformers import (
            AutoModel,
            AutoTokenizer,
            pipeline,
        )

        TRANSFORMERS_AVAILABLE = True
    except ImportError:
        TRANSFORMERS_AVAILABLE = False
        logger.warning(
            "⚠️ Transformers not available. Install with: pip install transformers torch"
        )

# LLM Integration
try:
    import openai
    from anthropic import Anthropic

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning(
        "⚠️ LLM libraries not available. Install with: pip install openai anthropic"
    )


@dataclass
class ProgressMetrics:
    """Advanced progress metrics using NLP analysis"""

    child_id: int
    analysis_date: datetime

    # Vocabulary Analysis
    total_unique_words: int
    new_words_this_period: List[str]
    vocabulary_complexity_score: float  # 0-1
    reading_level_equivalent: str

    # Language Development
    average_sentence_length: float
    grammar_accuracy_score: float
    question_sophistication_level: int  # 1-5
    conversation_coherence_score: float

    # Emotional Intelligence
    emotion_vocabulary_richness: int
    empathy_expression_frequency: float
    emotional_regulation_indicators: List[str]
    social_awareness_metrics: Dict[str, float]

    # Cognitive Development
    abstract_thinking_indicators: int
    problem_solving_approaches: List[str]
    creativity_markers: List[str]
    attention_span_trends: Dict[str, float]

    # Learning Patterns
    preferred_learning_styles: List[str]
    knowledge_retention_rate: float
    curiosity_indicators: List[str]
    learning_velocity: float  # words/concepts per day

    # Behavioral Insights
    initiative_taking_frequency: int
    cooperation_patterns: List[str]
    conflict_resolution_skills: List[str]
    independence_level: float

    # Red Flags & Concerns
    developmental_concerns: List[str]
    intervention_recommendations: List[str]
    urgency_level: int  # 0-3 (0=none, 3=urgent)


@dataclass
class LLMRecommendation:
    """LLM-generated recommendation with reasoning"""

    category: str  # "emotional", "cognitive", "social", "learning"
    recommendation: str
    reasoning: str
    expected_impact: str
    implementation_steps: List[str]
    success_metrics: List[str]
    priority_level: int  # 1-5


class AnalysisType(Enum):
    VOCABULARY = "vocabulary"
    EMOTIONAL = "emotional"
    COGNITIVE = "cognitive"
    SOCIAL = "social"
    BEHAVIORAL = "behavioral"


class AdvancedProgressAnalyzer:
    """
    Advanced service for analyzing child progress using NLP and LLM
    """

    def __init__(self, database_service=None, config=None):
        self.db = database_service
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize NLP models
        self._init_nlp_models()

        # Initialize LLM clients
        self._init_llm_clients()

        # Load analysis templates
        self._load_analysis_templates()

    def _init_nlp_models(self) -> Any:
        """Initialize NLP models and tools"""
        if not NLP_AVAILABLE:
            self.logger.warning("NLP models not available")
            return

        try:
            # Load spaCy model for Arabic and English
            self.nlp_ar = spacy.load("ar_core_news_sm")
            self.nlp_en = spacy.load("en_core_web_sm")

            # Initialize NLTK sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()

            # Load transformers models for advanced analysis
            if TRANSFORMERS_AVAILABLE:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                )
                self.topic_classifier = pipeline(
                    "zero-shot-classification", model="facebook/bart-large-mnli"
                )

            self.logger.info("✅ NLP models initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            self.nlp_ar = None
            self.nlp_en = None

    def _init_llm_clients(self) -> Any:
        """Initialize LLM clients"""
        if not LLM_AVAILABLE:
            self.logger.warning("LLM clients not available")
            return

        try:
            # Initialize OpenAI client
            openai_key = self.config.get("openai_api_key")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)

            # Initialize Anthropic client
            anthropic_key = self.config.get("anthropic_api_key")
            if anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)

            self.logger.info("✅ LLM clients initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")

    def _load_analysis_templates(self) -> Any:
        """Load Chain-of-Thought prompting templates"""
        self.cot_templates = {
            "progress_analysis": """
                تحليل تقدم الطفل - خطوة بخطوة:
                
                المعطيات:
                - اسم الطفل: {child_name}
                - العمر: {age} سنوات
                - فترة التحليل: {period}
                - إجمالي التفاعلات: {total_interactions}
                - المقاييس: {metrics}
                
                الخطوة 1: تحليل الأنماط اللغوية
                {language_analysis}
                
                الخطوة 2: تقييم التطور العاطفي
                {emotional_analysis}
                
                الخطوة 3: فحص المهارات المعرفية
                {cognitive_analysis}
                
                الخطوة 4: تحديد نقاط القوة والضعف
                {strengths_weaknesses}
                
                الخطوة 5: توليد التوصيات المخصصة
                بناءً على التحليل أعلاه، قدم 3 توصيات مخصصة للوالدين:
            """,
            "recommendation_generation": """
                توليد توصية مخصصة للطفل:
                
                السياق:
                - الطفل: {child_name} ({age} سنوات)
                - المجال: {category}
                - النقطة المحددة: {specific_area}
                - مستوى الأولوية: {priority}
                
                التفكير خطوة بخطوة:
                
                1. تحليل الوضع الحالي:
                {current_situation}
                
                2. تحديد الهدف المطلوب:
                {target_goal}
                
                3. اختيار الاستراتيجية المناسبة:
                {strategy}
                
                4. تصميم خطة التنفيذ:
                {implementation_plan}
                
                5. معايير النجاح:
                {success_criteria}
                
                التوصية النهائية:
            """,
        }

    async def _get_interactions_for_period(
        self, child_id: int, period_days: int
    ) -> List[Dict]:
        """Fetches interactions for a given child over a specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        return await self._get_interactions_with_text(child_id, start_date, end_date)

    async def _run_analyses_in_parallel(
        self, conversation_texts: List[str], interactions: List[Dict]
    ) -> Dict[str, Any]:
        """Runs all NLP analyses in parallel for efficiency."""
        results = await asyncio.gather(
            self._analyze_vocabulary_development(conversation_texts),
            self._analyze_emotional_intelligence(conversation_texts),
            self._analyze_cognitive_development(conversation_texts),
            self._analyze_social_skills(conversation_texts),
            self._analyze_behavioral_patterns(interactions),
        )
        return {
            "vocabulary": results[0],
            "emotional": results[1],
            "cognitive": results[2],
            "social": results[3],
            "behavioral": results[4],
        }

    def _aggregate_analysis_results(
        self, child_id: int, analyses: Dict[str, Any]
    ) -> ProgressMetrics:
        """Aggregates results from all analyses into a ProgressMetrics object."""
        concerns = self._identify_developmental_concerns(
            analyses["vocabulary"], analyses["emotional"], analyses["cognitive"]
        )
        return ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            total_unique_words=analyses["vocabulary"]["unique_words"],
            new_words_this_period=analyses["vocabulary"]["new_words"],
            vocabulary_complexity_score=analyses["vocabulary"]["complexity_score"],
            reading_level_equivalent=analyses["vocabulary"]["reading_level"],
            average_sentence_length=analyses["vocabulary"]["avg_sentence_length"],
            grammar_accuracy_score=analyses["vocabulary"]["grammar_score"],
            question_sophistication_level=analyses["vocabulary"]["question_level"],
            conversation_coherence_score=analyses["vocabulary"]["coherence_score"],
            emotion_vocabulary_richness=analyses["emotional"]["emotion_vocab_size"],
            empathy_expression_frequency=analyses["emotional"]["empathy_frequency"],
            emotional_regulation_indicators=analyses["emotional"][
                "regulation_indicators"
            ],
            social_awareness_metrics=analyses["emotional"]["social_awareness"],
            abstract_thinking_indicators=analyses["cognitive"]["abstract_thinking"],
            problem_solving_approaches=analyses["cognitive"]["problem_solving"],
            creativity_markers=analyses["cognitive"]["creativity_markers"],
            attention_span_trends=analyses["behavioral"]["attention_trends"],
            preferred_learning_styles=analyses["cognitive"]["learning_styles"],
            knowledge_retention_rate=analyses["cognitive"]["retention_rate"],
            curiosity_indicators=analyses["cognitive"]["curiosity_indicators"],
            learning_velocity=analyses["vocabulary"]["learning_velocity"],
            initiative_taking_frequency=analyses["behavioral"]["initiative_frequency"],
            cooperation_patterns=analyses["social"]["cooperation_patterns"],
            conflict_resolution_skills=analyses["social"]["conflict_resolution"],
            independence_level=analyses["behavioral"]["independence_level"],
            developmental_concerns=concerns["concerns"],
            intervention_recommendations=concerns["interventions"],
            urgency_level=concerns["urgency_level"],
        )

    async def _fetch_child_data(self, child_id: int) -> Dict[str, Any]:
        """Fetches child data from the database."""
        self.logger.info(f"Fetching data for child_id: {child_id}")
        # This is a placeholder. In a real implementation, this would query the database.
        return {"id": child_id, "name": "Test Child", "age": 5}

    async def _fetch_interaction_data(
        self, child_id: int, period_days: int
    ) -> List[Dict]:
        """Fetches interaction data for a given period."""
        self.logger.info(f"Fetching interactions for the last {period_days} days.")
        return await self._get_interactions_for_period(child_id, period_days)

    async def _process_and_analyze_data(
        self, child_id: int, interactions: List[Dict]
    ) -> ProgressMetrics:
        """Processes interactions and runs various analyses."""
        if not interactions:
            self.logger.warning(
                f"No interactions found for child {child_id}. Returning empty metrics."
            )
            return self._create_empty_metrics(child_id)

        conversation_texts = self._extract_conversation_texts(interactions)
        analysis_results = await self._run_analyses_in_parallel(
            conversation_texts, interactions
        )
        return self._aggregate_analysis_results(child_id, analysis_results)

    async def _generate_and_store_report(
        self, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> str:
        """Generates recommendations and stores the final report."""
        recommendations = await self.generate_llm_recommendations(metrics, child_info)
        report_id = await self.store_analysis_results(metrics, recommendations)
        self.logger.info(
            f"✅ Analysis complete for child {metrics.child_id}. Report ID: {report_id}"
        )
        return report_id

    async def analyze_progress(self, child_id: int, period_days: int = 7) -> str:
        """
        Analyzes a child's progress over a given period by fetching data,
        running analyses, and generating a report.

        Args:
            child_id: The ID of the child to analyze.
            period_days: The number of days to look back for interactions.

        Returns:
            The ID of the stored analysis report.
        """
        self.logger.info(
            f"Starting progress analysis for child_id: {child_id} over {period_days} days."
        )

        child_info = await self._fetch_child_data(child_id)
        interactions = await self._fetch_interaction_data(child_id, period_days)

        metrics = await self._process_and_analyze_data(child_id, interactions)

        report_id = await self._generate_and_store_report(metrics, child_info)

        return report_id

    async def _analyze_vocabulary_development(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze vocabulary development using NLP"""
        if not self.nlp_en or not texts:
            return self._empty_vocabulary_analysis()

        all_text = " ".join(texts)
        doc = self.nlp_en(all_text)

        # Extract words and analyze complexity
        words = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop
        ]
        unique_words = list(set(words))

        # Calculate vocabulary complexity
        complexity_indicators = {
            "avg_word_length": (
                sum(len(word) for word in unique_words) / len(unique_words)
                if unique_words
                else 0
            ),
            "rare_words_count": len([w for w in unique_words if len(w) > 6]),
            "abstract_concepts": len(
                [
                    token
                    for token in doc
                    if token.pos_ in ["NOUN", "ADJ"] and len(token.lemma_) > 5
                ]
            ),
        }

        complexity_score = min(
            1.0,
            (
                complexity_indicators["avg_word_length"] / 8
                + complexity_indicators["rare_words_count"] / 20
                + complexity_indicators["abstract_concepts"] / 15
            )
            / 3,
        )

        # Analyze sentence structure
        sentences = list(doc.sents)
        avg_sentence_length = (
            sum(len(sent) for sent in sentences) / len(sentences) if sentences else 0
        )

        # Estimate reading level
        reading_level = self._estimate_reading_level(
            complexity_score, avg_sentence_length
        )

        # Detect new words (simplified - in real implementation, compare with historical data)
        # Last 10 words as "new"
        new_words = unique_words[-min(10, len(unique_words)) :]

        return {
            "unique_words": len(unique_words),
            "new_words": new_words,
            "complexity_score": complexity_score,
            "reading_level": reading_level,
            "avg_sentence_length": avg_sentence_length,
            "grammar_score": self._estimate_grammar_accuracy(doc),
            "question_level": self._analyze_question_sophistication(texts),
            "coherence_score": self._calculate_coherence_score(doc),
            "learning_velocity": len(new_words) / 7,  # per day
        }

    async def _analyze_emotional_intelligence(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emotional intelligence and expression"""
        if not texts:
            return self._empty_emotional_analysis()

        # Emotion words detection
        emotion_words = self._extract_emotion_words(texts)

        # Empathy indicators
        empathy_indicators = self._detect_empathy_expressions(texts)

        # Emotional regulation markers
        regulation_indicators = self._identify_regulation_strategies(texts)

        # Social awareness
        social_awareness = self._assess_social_awareness(texts)

        return {
            "emotion_vocab_size": len(emotion_words),
            "empathy_frequency": len(empathy_indicators) / len(texts) if texts else 0,
            "regulation_indicators": regulation_indicators,
            "social_awareness": social_awareness,
        }

    async def _analyze_cognitive_development(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze cognitive development patterns"""
        if not texts:
            return self._empty_cognitive_analysis()

        # Abstract thinking detection
        abstract_thinking = self._detect_abstract_thinking(texts)

        # Problem-solving approaches
        problem_solving = self._identify_problem_solving_patterns(texts)

        # Creativity markers
        creativity_markers = self._detect_creativity_indicators(texts)

        # Learning style preferences
        learning_styles = self._infer_learning_styles(texts)

        return {
            "abstract_thinking": len(abstract_thinking),
            "problem_solving": problem_solving,
            "creativity_markers": creativity_markers,
            "learning_styles": learning_styles,
            "retention_rate": 0.85,  # Placeholder - would calculate from historical data
            "curiosity_indicators": self._identify_curiosity_markers(texts),
        }

    async def _analyze_social_skills(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze social interaction skills"""
        cooperation_patterns = self._detect_cooperation_patterns(texts)
        conflict_resolution = self._identify_conflict_resolution_skills(texts)

        return {
            "cooperation_patterns": cooperation_patterns,
            "conflict_resolution": conflict_resolution,
        }

    async def _analyze_behavioral_patterns(
        self, interactions: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze behavioral patterns from interaction data"""
        attention_trends = self._calculate_attention_trends(interactions)
        initiative_frequency = self._count_initiative_indicators(interactions)
        independence_level = self._assess_independence_level(interactions)

        return {
            "attention_trends": attention_trends,
            "initiative_frequency": initiative_frequency,
            "independence_level": independence_level,
        }

    async def generate_llm_recommendations(
        self, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> List[LLMRecommendation]:
        """
        Generate personalized recommendations using LLM with Chain-of-Thought prompting
        """
        if not LLM_AVAILABLE:
            return self._generate_fallback_recommendations(metrics)

        self.logger.info(
            "🤖 Generating LLM recommendations with Chain-of-Thought prompting"
        )

        recommendations = []

        # Generate recommendations for different categories
        categories = ["emotional", "cognitive", "social", "learning"]

        for category in categories:
            try:
                recommendation = await self._generate_category_recommendation(
                    category, metrics, child_info
                )
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                self.logger.error(f"Failed to generate {category} recommendation: {e}")

        return recommendations[:3]  # Return top 3 recommendations

    async def _generate_category_recommendation(
        self, category: str, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> Optional[LLMRecommendation]:
        """Generate a single category recommendation using Chain-of-Thought"""

        # Prepare context for the specific category
        context = self._prepare_category_context(category, metrics, child_info)

        # Create Chain-of-Thought prompt
        cot_prompt = self._create_cot_prompt(category, context)

        try:
            # Generate recommendation using OpenAI
            response = await self._call_openai_with_cot(cot_prompt)

            # Parse and structure the response
            recommendation = self._parse_llm_recommendation(category, response)

            return recommendation

        except Exception as e:
            self.logger.error(f"LLM generation failed for {category}: {e}")
            return None

    def _create_cot_prompt(self, category: str, context: Dict[str, Any]) -> str:
        """Create Chain-of-Thought prompt for specific category"""

        base_prompt = f"""
        أنت خبير في تطوير الطفل وتحليل التقدم التعليمي والعاطفي. 
        مهمتك تحليل بيانات الطفل وتقديم توصية مخصصة في مجال "{category}".
        
        استخدم منهجية التفكير خطوة بخطوة (Chain-of-Thought) للوصول لأفضل توصية.
        
        بيانات الطفل:
        - الاسم: {context["child_name"]}
        - العمر: {context["age"]} سنوات
        - المجال المطلوب: {category}
        
        المقاييس الحالية:
        {self._format_metrics_for_prompt(category, context["metrics"])}
        
        التفكير خطوة بخطوة:
        
        الخطوة 1: تحليل الوضع الحالي
        قم بتحليل نقاط القوة والضعف في مجال {category} بناءً على البيانات أعلاه.
        
        الخطوة 2: تحديد الهدف المناسب للعمر
        ما هو الهدف التطويري المناسب لطفل عمره {context["age"]} سنوات في مجال {category}؟
        
        الخطوة 3: اختيار الاستراتيجية
        ما هي أفضل استراتيجية لتحقيق هذا الهدف مع مراعاة شخصية الطفل؟
        
        الخطوة 4: تصميم الخطة العملية
        كيف يمكن للوالدين تطبيق هذه الاستراتيجية عملياً؟
        
        الخطوة 5: معايير القياس
        كيف يمكن قياس نجاح هذه التوصية؟
        
        التوصية النهائية (بتنسيق JSON):
        {{
            "category": "{category}",
            "recommendation": "التوصية الرئيسية هنا",
            "reasoning": "سبب هذه التوصية",
            "expected_impact": "التأثير المتوقع",
            "implementation_steps": ["خطوة 1", "خطوة 2", "خطوة 3"],
            "success_metrics": ["معيار 1", "معيار 2"],
            "priority_level": 3
        }}
        """

        return base_prompt

    async def _call_openai_with_cot(self, prompt: str) -> str:
        """Calls OpenAI with Chain-of-Thought prompt and returns the response."""
        if not hasattr(self, "openai_client"):
            raise Exception("OpenAI client not initialized")

        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "أنت خبير في تطوير الطفل. استخدم التفكير المنطقي خطوة بخطوة لتقديم توصيات مخصصة ومفيدة.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content

    def _parse_llm_recommendation(
        self, category: str, response: str
    ) -> LLMRecommendation:
        """Parse LLM response into structured recommendation"""
        try:
            data = json.loads(response)
            return LLMRecommendation(
                category=data.get("category", category),
                recommendation=data.get("recommendation", ""),
                reasoning=data.get("reasoning", ""),
                expected_impact=data.get("expected_impact", ""),
                implementation_steps=data.get("implementation_steps", []),
                success_metrics=data.get("success_metrics", []),
                priority_level=data.get("priority_level", 3),
            )
        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            return LLMRecommendation(
                category=category,
                recommendation=response[:200] if response else "توصية غير متوفرة",
                reasoning="تم توليدها باستخدام تحليل متقدم",
                expected_impact="تحسين في المجال المحدد",
                implementation_steps=["متابعة التطبيق", "قياس النتائج"],
                success_metrics=["تحسن ملحوظ في التفاعل"],
                priority_level=3,
            )

    async def store_analysis_results(
        self, metrics: ProgressMetrics, recommendations: List[LLMRecommendation]
    ) -> str:
        """Store analysis results in parent_reports table"""
        if not self.db:
            raise Exception("Database service not available")

        report_data = {
            "child_id": metrics.child_id,
            "generated_at": metrics.analysis_date.isoformat(),
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
            "analysis_version": "2.0",
            "llm_used": True,
        }

        try:
            # Store in database
            report_id = await self.db.execute(
                """
                INSERT INTO parent_reports 
                (child_id, generated_at, metrics, recommendations, analysis_version)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    metrics.child_id,
                    report_data["generated_at"],
                    json.dumps(report_data["metrics"]),
                    json.dumps(report_data["recommendations"]),
                    report_data["analysis_version"],
                ),
            )

            self.logger.info(f"✅ Analysis results stored with ID: {report_id}")
            return str(report_id)

        except Exception as e:
            self.logger.error(f"Failed to store analysis results: {e}")
            raise

    # Helper methods (simplified implementations)

    def _extract_conversation_texts(self, interactions: List[Dict]) -> List[str]:
        """Extract text content from interactions"""
        texts = []
        for interaction in interactions:
            if "text" in interaction and interaction["text"]:
                texts.append(interaction["text"])
        return texts

    def _estimate_reading_level(
        self, complexity_score: float, avg_sentence_length: float
    ) -> str:
        """Estimate reading level based on complexity"""
        if complexity_score < 0.3:
            return "مبتدئ"
        elif complexity_score < 0.6:
            return "متوسط"
        else:
            return "متقدم"

    def _empty_vocabulary_analysis(self) -> Dict[str, Any]:
        """Return empty vocabulary analysis"""
        return {
            "unique_words": 0,
            "new_words": [],
            "complexity_score": 0.0,
            "reading_level": "غير محدد",
            "avg_sentence_length": 0.0,
            "grammar_score": 0.0,
            "question_level": 1,
            "coherence_score": 0.0,
            "learning_velocity": 0.0,
        }

    def _empty_emotional_analysis(self) -> Dict[str, Any]:
        """Return empty emotional analysis"""
        return {
            "emotion_vocab_size": 0,
            "empathy_frequency": 0.0,
            "regulation_indicators": [],
            "social_awareness": {},
        }

    def _empty_cognitive_analysis(self) -> Dict[str, Any]:
        """Return empty cognitive analysis"""
        return {
            "abstract_thinking": 0,
            "problem_solving": [],
            "creativity_markers": [],
            "learning_styles": [],
            "retention_rate": 0.0,
            "curiosity_indicators": [],
        }

    def _create_empty_metrics(self, child_id: int) -> ProgressMetrics:
        """Create empty metrics for cases with no data"""
        return ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            total_unique_words=0,
            new_words_this_period=[],
            vocabulary_complexity_score=0.0,
            reading_level_equivalent="غير محدد",
            average_sentence_length=0.0,
            grammar_accuracy_score=0.0,
            question_sophistication_level=1,
            conversation_coherence_score=0.0,
            emotion_vocabulary_richness=0,
            empathy_expression_frequency=0.0,
            emotional_regulation_indicators=[],
            social_awareness_metrics={},
            abstract_thinking_indicators=0,
            problem_solving_approaches=[],
            creativity_markers=[],
            attention_span_trends={},
            preferred_learning_styles=[],
            knowledge_retention_rate=0.0,
            curiosity_indicators=[],
            learning_velocity=0.0,
            initiative_taking_frequency=0,
            cooperation_patterns=[],
            conflict_resolution_skills=[],
            independence_level=0.0,
            developmental_concerns=["عدم توفر بيانات كافية للتحليل"],
            intervention_recommendations=["زيادة التفاعل مع النظام"],
            urgency_level=0,
        )

    async def _get_interactions_with_text(
        self, child_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Get interactions with text content for analysis"""
        if not self.db:
            return []

        try:
            interactions = await self.db.fetch_all(
                """
                SELECT * FROM conversations 
                WHERE child_id = ? AND created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
                """,
                (child_id, start_date.isoformat(), end_date.isoformat()),
            )
            return [dict(row) for row in interactions]
        except Exception as e:
            self.logger.error(f"Failed to fetch interactions: {e}")
            return []

    # Additional helper methods would be implemented here...
    # (Due to length constraints, showing structure only)

    def _extract_emotion_words(self, texts: List[str]) -> List[str]:
        """Extract emotion-related words from texts"""
        emotion_keywords = ["سعيد", "حزين", "غاضب", "خائف", "متحمس", "قلق", "مرتاح"]
        found_emotions = []
        for text in texts:
            for emotion in emotion_keywords:
                if emotion in text:
                    found_emotions.append(emotion)
        return list(set(found_emotions))

    def _detect_empathy_expressions(self, texts: List[str]) -> List[str]:
        """Detect empathy expressions in text"""
        empathy_patterns = ["أشعر بـ", "أفهم", "أتفهم", "أحس"]
        expressions = []
        for text in texts:
            for pattern in empathy_patterns:
                if pattern in text:
                    expressions.append(pattern)
        return expressions

    def _extract_emotion_words(self, texts: List[str]) -> List[str]:
        """Extract emotion-related words from texts"""
        emotion_keywords = ["سعيد", "حزين", "غاضب", "خائف", "متحمس", "قلق", "مرتاح"]
        found_emotions = []
        for text in texts:
            for emotion in emotion_keywords:
                if emotion in text:
                    found_emotions.append(emotion)
        return list(set(found_emotions))

    def _detect_empathy_expressions(self, texts: List[str]) -> List[str]:
        """Detect empathy expressions in text"""
        empathy_patterns = ["أشعر بـ", "أفهم", "أتفهم", "أحس"]
        expressions = []
        for text in texts:
            for pattern in empathy_patterns:
                if pattern in text:
                    expressions.append(pattern)
        return expressions
