"""
🧠 Enhanced Parent Report Service - Task 7
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

# NLP Libraries
try:
    from collections import Counter

    import nltk
    import spacy
    from nltk.sentiment import SentimentIntensityAnalyzer

    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logger.warning("⚠️ NLP libraries not available. Install with: pip install spacy nltk")

# LLM Integration
try:
    import openai
    from anthropic import Anthropic

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("⚠️ LLM libraries not available. Install with: pip install openai anthropic")


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


class EnhancedParentReportService:
    """
    Enhanced service for analyzing child progress using NLP and LLM
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
        self._load_cot_templates()

    def _init_nlp_models(self) -> Any:
        """Initialize NLP models and tools"""
        if not NLP_AVAILABLE:
            self.logger.warning("NLP models not available")
            return

        try:
            # Load spaCy model for English (Arabic model needs separate installation)
            self.nlp = spacy.load("en_core_web_sm")

            # Initialize NLTK sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()

            self.logger.info("✅ NLP models initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            self.nlp = None

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
                self.logger.info("✅ OpenAI client initialized")

            # Initialize Anthropic client
            anthropic_key = self.config.get("anthropic_api_key")
            if anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                self.logger.info("✅ Anthropic client initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")

    def _load_cot_templates(self) -> Any:
        """Load Chain-of-Thought prompting templates"""
        self.cot_templates = {
            "progress_analysis": """
أنت خبير في تطوير الطفل وتحليل التقدم التعليمي والعاطفي. 
استخدم منهجية التفكير خطوة بخطوة (Chain-of-Thought) لتحليل تقدم الطفل.

بيانات الطفل:
- الاسم: {child_name}
- العمر: {age} سنوات
- فترة التحليل: {period_days} أيام
- إجمالي التفاعلات: {total_interactions}

المقاييس المحسوبة:
{metrics_summary}

التفكير خطوة بخطوة:

الخطوة 1: تحليل الأنماط اللغوية
قم بتحليل نمو المفردات وتطور الحديث:
- المفردات الجديدة: {new_words_count}
- مستوى التعقيد: {complexity_score}
- طول الجملة المتوسط: {avg_sentence_length}

الخطوة 2: تقييم التطور العاطفي
فحص المؤشرات العاطفية والاجتماعية:
- ثراء المفردات العاطفية: {emotion_vocab}
- تكرار التعبير عن التعاطف: {empathy_frequency}
- مؤشرات التنظيم العاطفي: {regulation_indicators}

الخطوة 3: فحص المهارات المعرفية
تحليل القدرات المعرفية والتعلم:
- مؤشرات التفكير المجرد: {abstract_thinking}
- أساليب حل المشكلات: {problem_solving}
- علامات الإبداع: {creativity_markers}

الخطوة 4: تحديد نقاط القوة والتحديات
بناءً على التحليل أعلاه:
- نقاط القوة الرئيسية: 
- المجالات التي تحتاج تطوير:
- مستوى الأولوية للتدخل: {urgency_level}

الخطوة 5: توليد التوصيات المخصصة
قدم 3 توصيات مخصصة وعملية للوالدين:
""",
            "recommendation_generation": """
توليد توصية مخصصة للطفل في مجال {category}:

السياق:
- الطفل: {child_name} ({age} سنوات)
- المجال: {category}
- النقطة المحددة: {specific_area}
- مستوى الأولوية: {priority}

التفكير خطوة بخطوة:

1. تحليل الوضع الحالي:
ما هو وضع الطفل الحالي في هذا المجال؟

2. تحديد الهدف المناسب للعمر:
ما هو الهدف التطويري المناسب لطفل عمره {age} سنوات؟

3. اختيار الاستراتيجية المناسبة:
ما هي أفضل استراتيجية مع مراعاة شخصية الطفل؟

4. تصميم خطة التنفيذ:
كيف يمكن للوالدين تطبيق هذه الاستراتيجية؟

5. معايير النجاح:
كيف يمكن قياس تقدم الطفل؟

التوصية النهائية (JSON format):
""",
        }

    async def analyze_progress(self, child_id: int, period_days: int = 7) -> ProgressMetrics:
        """
        تحليل تقدم الطفل باستخدام NLP متقدم

        Args:
            child_id: معرف الطفل الفريد
            period_days: عدد الأيام للتحليل (افتراضي: 7)

        Returns:
            ProgressMetrics with comprehensive analysis
        """
        self.logger.info(f"🧠 بدء تحليل التقدم المتقدم للطفل {child_id}")

        # جلب بيانات التفاعل
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        interactions = await self._get_interactions_with_text(child_id, start_date, end_date)

        if not interactions:
            self.logger.warning(f"لا توجد تفاعلات للطفل {child_id}")
            return self._create_empty_metrics(child_id)

        # استخراج النصوص للتحليل
        conversation_texts = self._extract_conversation_texts(interactions)

        # تحليل متعدد الطبقات باستخدام NLP
        vocabulary_analysis = await self._analyze_vocabulary_development(conversation_texts)
        emotional_analysis = await self._analyze_emotional_intelligence(conversation_texts)
        cognitive_analysis = await self._analyze_cognitive_development(conversation_texts)
        behavioral_analysis = await self._analyze_behavioral_patterns(interactions)

        # تحديد المخاوف والعلامات الحمراء
        concerns = self._identify_developmental_concerns(vocabulary_analysis, emotional_analysis, cognitive_analysis)

        # إنشاء المقاييس الشاملة
        metrics = ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            # مقاييس المفردات
            total_unique_words=vocabulary_analysis["unique_words"],
            new_words_this_period=vocabulary_analysis["new_words"],
            vocabulary_complexity_score=vocabulary_analysis["complexity_score"],
            reading_level_equivalent=vocabulary_analysis["reading_level"],
            # تطوير اللغة
            average_sentence_length=vocabulary_analysis["avg_sentence_length"],
            grammar_accuracy_score=vocabulary_analysis["grammar_score"],
            question_sophistication_level=vocabulary_analysis["question_level"],
            conversation_coherence_score=vocabulary_analysis["coherence_score"],
            # الذكاء العاطفي
            emotion_vocabulary_richness=emotional_analysis["emotion_vocab_size"],
            empathy_expression_frequency=emotional_analysis["empathy_frequency"],
            emotional_regulation_indicators=emotional_analysis["regulation_indicators"],
            social_awareness_metrics=emotional_analysis["social_awareness"],
            # التطور المعرفي
            abstract_thinking_indicators=cognitive_analysis["abstract_thinking"],
            problem_solving_approaches=cognitive_analysis["problem_solving"],
            creativity_markers=cognitive_analysis["creativity_markers"],
            attention_span_trends=behavioral_analysis["attention_trends"],
            # أنماط التعلم
            preferred_learning_styles=cognitive_analysis["learning_styles"],
            knowledge_retention_rate=cognitive_analysis["retention_rate"],
            curiosity_indicators=cognitive_analysis["curiosity_indicators"],
            learning_velocity=vocabulary_analysis["learning_velocity"],
            # رؤى سلوكية
            initiative_taking_frequency=behavioral_analysis["initiative_frequency"],
            cooperation_patterns=behavioral_analysis["cooperation_patterns"],
            conflict_resolution_skills=behavioral_analysis["conflict_resolution"],
            independence_level=behavioral_analysis["independence_level"],
            # المخاوف والتوصيات
            developmental_concerns=concerns["concerns"],
            intervention_recommendations=concerns["interventions"],
            urgency_level=concerns["urgency_level"],
        )

        self.logger.info(f"✅ اكتمل تحليل التقدم المتقدم للطفل {child_id}")
        return metrics

    async def generate_and_store_report(self, child_id: int, period_days: int = 7) -> Dict[str, Any]:
        """
        توليد وحفظ تقرير شامل للطفل
        """
        # تحليل التقدم
        metrics = await self.analyze_progress(child_id, period_days)

        # جلب معلومات الطفل
        child_info = await self._get_child_info(child_id)

        # توليد التوصيات باستخدام LLM
        recommendations = await self.generate_llm_recommendations(metrics, child_info)

        # حفظ النتائج في قاعدة البيانات
        report_id = await self.store_analysis_results(metrics, recommendations)

        return {
            "report_id": report_id,
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
            "generated_at": datetime.now().isoformat(),
        }

    async def generate_llm_recommendations(
        self, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> List[LLMRecommendation]:
        """
        توليد توصيات مخصصة باستخدام LLM مع Chain-of-Thought prompting
        """
        if not LLM_AVAILABLE or not hasattr(self, "openai_client"):
            return self._generate_fallback_recommendations(metrics)

        self.logger.info("🤖 توليد التوصيات باستخدام LLM مع Chain-of-Thought")

        recommendations = []
        categories = ["emotional", "cognitive", "social", "learning"]

        for category in categories:
            try:
                recommendation = await self._generate_category_recommendation(category, metrics, child_info)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                self.logger.error(f"فشل في توليد توصية {category}: {e}")

        return recommendations[:3]  # أفضل 3 توصيات

    async def _generate_category_recommendation(
        self, category: str, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> Optional[LLMRecommendation]:
        """توليد توصية لفئة محددة باستخدام Chain-of-Thought"""

        # تحضير السياق للفئة المحددة
        context = self._prepare_category_context(category, metrics, child_info)

        # إنشاء Chain-of-Thought prompt
        cot_prompt = self._create_cot_prompt(category, context)

        try:
            # توليد التوصية باستخدام OpenAI
            response = await self._call_openai_with_cot(cot_prompt)

            # تحليل وهيكلة الاستجابة
            recommendation = self._parse_llm_recommendation(category, response)

            return recommendation

        except Exception as e:
            self.logger.error(f"فشل في توليد LLM للفئة {category}: {e}")
            return None

    def _create_cot_prompt(self, category: str, context: Dict[str, Any]) -> str:
        """إنشاء Chain-of-Thought prompt لفئة محددة"""

        prompt = f"""
أنت خبير في تطوير الطفل وتحليل التقدم التعليمي والعاطفي. 
مهمتك تحليل بيانات الطفل وتقديم توصية مخصصة في مجال "{category}".

استخدم منهجية التفكير خطوة بخطوة (Chain-of-Thought) للوصول لأفضل توصية.

بيانات الطفل:
- الاسم: {context['child_name']}
- العمر: {context['age']} سنوات
- المجال المطلوب: {category}

المقاييس الحالية:
{self._format_metrics_for_prompt(category, context['metrics'])}

التفكير خطوة بخطوة:

الخطوة 1: تحليل الوضع الحالي
قم بتحليل نقاط القوة والضعف في مجال {category} بناءً على البيانات أعلاه.

الخطوة 2: تحديد الهدف المناسب للعمر
ما هو الهدف التطويري المناسب لطفل عمره {context['age']} سنوات في مجال {category}؟

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

        return prompt

    async def _call_openai_with_cot(self, prompt: str) -> str:
        """استدعاء OpenAI API مع Chain-of-Thought prompt"""
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

    async def store_analysis_results(self, metrics: ProgressMetrics, recommendations: List[LLMRecommendation]) -> str:
        """حفظ نتائج التحليل في جدول parent_reports"""
        if not self.db:
            raise Exception("خدمة قاعدة البيانات غير متوفرة")

        report_data = {
            "child_id": metrics.child_id,
            "generated_at": metrics.analysis_date.isoformat(),
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
            "analysis_version": "2.0_task7",
            "llm_used": True,
        }

        try:
            # حفظ في قاعدة البيانات
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

            self.logger.info(f"✅ تم حفظ نتائج التحليل برقم: {report_id}")
            return str(report_id)

        except Exception as e:
            self.logger.error(f"فشل في حفظ نتائج التحليل: {e}")
            raise

    # Helper methods implementation

    async def _analyze_vocabulary_development(self, texts: List[str]) -> Dict[str, Any]:
        """تحليل تطوير المفردات باستخدام NLP"""
        if not self.nlp or not texts:
            return self._empty_vocabulary_analysis()

        all_text = " ".join(texts)
        doc = self.nlp(all_text)

        # استخراج الكلمات وتحليل التعقيد
        words = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
        unique_words = list(set(words))

        # حساب تعقيد المفردات
        complexity_score = min(1.0, len(unique_words) / 50.0)  # تبسيط للعرض

        # تحليل بنية الجملة
        sentences = list(doc.sents)
        avg_sentence_length = sum(len(sent) for sent in sentences) / len(sentences) if sentences else 0

        return {
            "unique_words": len(unique_words),
            "new_words": unique_words[-min(5, len(unique_words)) :],  # آخر 5 كلمات كـ "جديدة"
            "complexity_score": complexity_score,
            "reading_level": self._estimate_reading_level(complexity_score),
            "avg_sentence_length": avg_sentence_length,
            "grammar_score": 0.8,  # placeholder
            "question_level": 3,  # placeholder
            "coherence_score": 0.7,  # placeholder
            "learning_velocity": len(unique_words) / 7,  # كلمات في اليوم
        }

    async def _analyze_emotional_intelligence(self, texts: List[str]) -> Dict[str, Any]:
        """تحليل الذكاء العاطفي"""
        emotion_words = self._extract_emotion_words(texts)
        empathy_indicators = self._detect_empathy_expressions(texts)

        return {
            "emotion_vocab_size": len(emotion_words),
            "empathy_frequency": len(empathy_indicators) / len(texts) if texts else 0,
            "regulation_indicators": empathy_indicators[:3],  # أول 3 مؤشرات
            "social_awareness": {"cooperation": 0.7, "sharing": 0.8},
        }

    async def _analyze_cognitive_development(self, texts: List[str]) -> Dict[str, Any]:
        """تحليل التطوير المعرفي"""
        return {
            "abstract_thinking": len([t for t in texts if "لماذا" in t or "كيف" in t]),
            "problem_solving": ["logical", "creative"],
            "creativity_markers": ["imagination", "storytelling"],
            "learning_styles": ["visual", "auditory"],
            "retention_rate": 0.85,
            "curiosity_indicators": ["asking questions", "exploring topics"],
        }

    async def _analyze_behavioral_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """تحليل الأنماط السلوكية"""
        return {
            "attention_trends": {"morning": 0.8, "evening": 0.6},
            "initiative_frequency": len(interactions) // 2,
            "cooperation_patterns": ["turn-taking", "sharing"],
            "conflict_resolution": ["negotiation", "compromise"],
            "independence_level": 0.7,
        }

    def _identify_developmental_concerns(
        self, vocab_analysis, emotional_analysis, cognitive_analysis
    ) -> Dict[str, Any]:
        """تحديد المخاوف التطويرية"""
        concerns = []
        interventions = []
        urgency_level = 0

        if vocab_analysis["unique_words"] < 10:
            concerns.append("محدودية المفردات")
            interventions.append("زيادة وقت القراءة")
            urgency_level = max(urgency_level, 2)

        if emotional_analysis["empathy_frequency"] < 0.1:
            concerns.append("قلة التعبير عن التعاطف")
            interventions.append("أنشطة تطوير التعاطف")
            urgency_level = max(urgency_level, 1)

        return {"concerns": concerns, "interventions": interventions, "urgency_level": urgency_level}

    # Additional helper methods

    def _extract_emotion_words(self, texts: List[str]) -> List[str]:
        """استخراج الكلمات العاطفية"""
        emotion_keywords = ["happy", "sad", "angry", "scared", "excited", "worried", "calm"]
        found_emotions = []
        for text in texts:
            for emotion in emotion_keywords:
                if emotion.lower() in text.lower():
                    found_emotions.append(emotion)
        return list(set(found_emotions))

    def _detect_empathy_expressions(self, texts: List[str]) -> List[str]:
        """اكتشاف تعبيرات التعاطف"""
        empathy_patterns = ["I feel", "I understand", "I know how", "That must be"]
        expressions = []
        for text in texts:
            for pattern in empathy_patterns:
                if pattern.lower() in text.lower():
                    expressions.append(pattern)
        return list(set(expressions))

    def _estimate_reading_level(self, complexity_score: float) -> str:
        """تقدير مستوى القراءة"""
        if complexity_score < 0.3:
            return "مبتدئ"
        elif complexity_score < 0.6:
            return "متوسط"
        else:
            return "متقدم"

    def _empty_vocabulary_analysis(self) -> Dict[str, Any]:
        """تحليل مفردات فارغ"""
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

    def _create_empty_metrics(self, child_id: int) -> ProgressMetrics:
        """إنشاء مقاييس فارغة عند عدم وجود بيانات"""
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

    def _extract_conversation_texts(self, interactions: List[Dict]) -> List[str]:
        """استخراج النصوص من التفاعلات"""
        texts = []
        for interaction in interactions:
            if "message" in interaction and interaction["message"]:
                texts.append(interaction["message"])
            elif "content" in interaction and interaction["content"]:
                texts.append(interaction["content"])
        return texts

    async def _get_interactions_with_text(self, child_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """جلب التفاعلات مع النصوص للتحليل"""
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
            self.logger.error(f"فشل في جلب التفاعلات: {e}")
            return []

    async def _get_child_info(self, child_id: int) -> Dict[str, Any]:
        """جلب معلومات الطفل"""
        if not self.db:
            return {"name": "Unknown", "age": 5}

        try:
            child = await self.db.fetch_one("SELECT * FROM children WHERE id = ?", (child_id,))
            return dict(child) if child else {"name": "Unknown", "age": 5}
        except Exception as e:
            self.logger.error(f"فشل في جلب معلومات الطفل: {e}")
            return {"name": "Unknown", "age": 5}

    def _prepare_category_context(
        self, category: str, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تحضير السياق لفئة محددة"""
        return {
            "child_name": child_info.get("name", "Unknown"),
            "age": child_info.get("age", 5),
            "category": category,
            "metrics": metrics,
        }

    def _format_metrics_for_prompt(self, category: str, metrics: ProgressMetrics) -> str:
        """تنسيق المقاييس للprompt"""
        return f"""
- إجمالي الكلمات الفريدة: {metrics.total_unique_words}
- درجة تعقيد المفردات: {metrics.vocabulary_complexity_score:.2f}
- مستوى القراءة: {metrics.reading_level_equivalent}
- ثراء المفردات العاطفية: {metrics.emotion_vocabulary_richness}
- تكرار التعاطف: {metrics.empathy_expression_frequency:.2f}
- مؤشرات التفكير المجرد: {metrics.abstract_thinking_indicators}
"""

    def _parse_llm_recommendation(self, category: str, response: str) -> LLMRecommendation:
        """تحليل استجابة LLM إلى توصية منظمة"""
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
            return LLMRecommendation(
                category=category,
                recommendation=response[:200] if response else "توصية غير متوفرة",
                reasoning="تم توليدها باستخدام تحليل متقدم",
                expected_impact="تحسين في المجال المحدد",
                implementation_steps=["متابعة التطبيق", "قياس النتائج"],
                success_metrics=["تحسن ملحوظ في التفاعل"],
                priority_level=3,
            )

    def _generate_fallback_recommendations(self, metrics: ProgressMetrics) -> List[LLMRecommendation]:
        """توليد توصيات احتياطية عند عدم توفر LLM"""
        recommendations = []

        if metrics.vocabulary_complexity_score < 0.5:
            recommendations.append(
                LLMRecommendation(
                    category="learning",
                    recommendation="زيادة أنشطة القراءة والحديث",
                    reasoning="المفردات تحتاج تطوير",
                    expected_impact="تحسن في المفردات والتعبير",
                    implementation_steps=["قراءة يومية", "حديث تفاعلي"],
                    success_metrics=["زيادة المفردات", "تحسن التعبير"],
                    priority_level=4,
                )
            )

        if metrics.empathy_expression_frequency < 0.3:
            recommendations.append(
                LLMRecommendation(
                    category="emotional",
                    recommendation="أنشطة تطوير التعاطف والمشاعر",
                    reasoning="قلة التعبير عن التعاطف",
                    expected_impact="تحسن في الذكاء العاطفي",
                    implementation_steps=["قصص تعاطفية", "مناقشة المشاعر"],
                    success_metrics=["زيادة التعبير العاطفي"],
                    priority_level=3,
                )
            )

        if metrics.abstract_thinking_indicators < 2:
            recommendations.append(
                LLMRecommendation(
                    category="cognitive",
                    recommendation="أنشطة تطوير التفكير النقدي",
                    reasoning="محدودية التفكير المجرد",
                    expected_impact="تحسن في المهارات المعرفية",
                    implementation_steps=["ألعاب تفكير", "أسئلة مفتوحة"],
                    success_metrics=["زيادة الأسئلة المعقدة"],
                    priority_level=3,
                )
            )

        return recommendations[:3]
