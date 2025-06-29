"""
🧠 Progress Analyzer Service - Task 7 Implementation
تحليل تقدم الطفل باستخدام NLP وLLM مع Chain-of-Thought prompting
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass, asdict
import logging

# Import LLM service
try:
    import openai
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

@dataclass
class ProgressMetrics:
    """مقاييس التقدم المتقدمة"""
    child_id: int
    analysis_date: datetime
    total_unique_words: int
    new_words_this_period: List[str]
    vocabulary_complexity_score: float
    reading_level_equivalent: str
    emotional_intelligence_score: float
    cognitive_development_score: float
    social_skills_score: float
    learning_velocity: float
    developmental_concerns: List[str]
    intervention_recommendations: List[str]
    urgency_level: int

@dataclass 
class LLMRecommendation:
    """توصية مولدة بواسطة LLM"""
    category: str
    recommendation: str
    reasoning: str
    expected_impact: str
    implementation_steps: List[str]
    success_metrics: List[str]
    priority_level: int

class ProgressAnalyzer:
    """خدمة تحليل تقدم الطفل المتقدمة"""
    
    def __init__(self, database_service=None, config=None):
        self.db = database_service
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._init_llm_client()
    
    def _init_llm_client(self):
        """تهيئة عميل LLM"""
        if LLM_AVAILABLE and self.config.get('openai_api_key'):
            self.openai_client = openai.OpenAI(api_key=self.config['openai_api_key'])
            self.logger.info("✅ OpenAI client initialized")
        else:
            self.logger.warning("⚠️ LLM client not available")
    
    async def analyze_progress(self, child_id: int) -> ProgressMetrics:
        """
        تحليل تقدم الطفل باستخدام NLP متقدم
        """
        self.logger.info(f"🧠 بدء تحليل التقدم للطفل {child_id}")
        
        # جلب بيانات التفاعل (آخر 7 أيام)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        interactions = await self._get_interactions(child_id, start_date, end_date)
        
        if not interactions:
            return self._create_empty_metrics(child_id)
        
        # تحليل المفردات والنصوص
        vocabulary_analysis = self._analyze_vocabulary(interactions)
        emotional_analysis = self._analyze_emotions(interactions)
        cognitive_analysis = self._analyze_cognitive_skills(interactions)
        social_analysis = self._analyze_social_skills(interactions)
        
        # تحديد المخاوف والتوصيات
        concerns = self._identify_concerns(vocabulary_analysis, emotional_analysis, cognitive_analysis)
        
        # إنشاء مقاييس التقدم
        metrics = ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            total_unique_words=vocabulary_analysis['unique_words'],
            new_words_this_period=vocabulary_analysis['new_words'],
            vocabulary_complexity_score=vocabulary_analysis['complexity_score'],
            reading_level_equivalent=vocabulary_analysis['reading_level'],
            emotional_intelligence_score=emotional_analysis['ei_score'],
            cognitive_development_score=cognitive_analysis['cognitive_score'],
            social_skills_score=social_analysis['social_score'],
            learning_velocity=vocabulary_analysis['learning_velocity'],
            developmental_concerns=concerns['concerns'],
            intervention_recommendations=concerns['interventions'],
            urgency_level=concerns['urgency_level']
        )
        
        self.logger.info(f"✅ اكتمل تحليل التقدم للطفل {child_id}")
        return metrics
    
    async def generate_llm_recommendations(
        self, 
        child_id: int,
        metrics: ProgressMetrics
    ) -> List[LLMRecommendation]:
        """
        توليد توصيات مخصصة باستخدام LLM مع Chain-of-Thought prompting
        """
        if not LLM_AVAILABLE or not hasattr(self, 'openai_client'):
            return self._generate_fallback_recommendations(metrics)
        
        # جلب معلومات الطفل
        child_info = await self._get_child_info(child_id)
        
        # توليد توصيات لكل فئة
        categories = ["emotional", "cognitive", "social"]
        recommendations = []
        
        for category in categories:
            try:
                recommendation = await self._generate_category_recommendation(
                    category, metrics, child_info
                )
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                self.logger.error(f"فشل في توليد توصية {category}: {e}")
        
        return recommendations[:3]
    
    async def _generate_category_recommendation(
        self,
        category: str,
        metrics: ProgressMetrics,
        child_info: Dict[str, Any]
    ) -> Optional[LLMRecommendation]:
        """توليد توصية لفئة محددة باستخدام Chain-of-Thought"""
        
        # إنشاء Chain-of-Thought prompt
        prompt = self._create_cot_prompt(category, metrics, child_info)
        
        try:
            # استدعاء OpenAI
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت خبير في تطوير الطفل. استخدم التفكير خطوة بخطوة لتقديم توصيات مخصصة."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # تحليل الاستجابة
            return self._parse_llm_response(category, response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"فشل في استدعاء OpenAI للفئة {category}: {e}")
            return None
    
    def _create_cot_prompt(
        self, 
        category: str, 
        metrics: ProgressMetrics, 
        child_info: Dict[str, Any]
    ) -> str:
        """إنشاء Chain-of-Thought prompt"""
        
        child_name = child_info.get('name', 'غير محدد')
        child_age = child_info.get('age', 5)
        
        prompt = f"""
أنت خبير في تطوير الطفل. قم بتحليل بيانات الطفل وتقديم توصية مخصصة.

معلومات الطفل:
- الاسم: {child_name}
- العمر: {child_age} سنوات
- المجال المطلوب: {category}

المقاييس الحالية:
- إجمالي الكلمات الفريدة: {metrics.total_unique_words}
- درجة تعقيد المفردات: {metrics.vocabulary_complexity_score:.2f}
- مستوى القراءة: {metrics.reading_level_equivalent}
- درجة الذكاء العاطفي: {metrics.emotional_intelligence_score:.2f}
- درجة التطور المعرفي: {metrics.cognitive_development_score:.2f}
- درجة المهارات الاجتماعية: {metrics.social_skills_score:.2f}

المخاوف المحددة: {', '.join(metrics.developmental_concerns) if metrics.developmental_concerns else 'لا توجد'}

استخدم التفكير خطوة بخطوة:

الخطوة 1: تحليل الوضع الحالي
ما هي نقاط القوة والضعف في مجال {category} بناءً على البيانات؟

الخطوة 2: تحديد الهدف المناسب
ما هو الهدف التطويري المناسب لطفل عمره {child_age} سنوات؟

الخطوة 3: اختيار الاستراتيجية
ما هي أفضل استراتيجية لتحقيق هذا الهدف؟

الخطوة 4: تصميم الخطة العملية
كيف يمكن للوالدين تطبيق هذه الاستراتيجية؟

الخطوة 5: معايير النجاح
كيف يمكن قياس نجاح هذه التوصية؟

قدم التوصية النهائية بتنسيق JSON:
{{
    "category": "{category}",
    "recommendation": "التوصية الرئيسية",
    "reasoning": "سبب هذه التوصية",
    "expected_impact": "التأثير المتوقع",
    "implementation_steps": ["خطوة 1", "خطوة 2", "خطوة 3"],
    "success_metrics": ["معيار 1", "معيار 2"],
    "priority_level": 3
}}
"""
        return prompt
    
    def _parse_llm_response(self, category: str, response: str) -> LLMRecommendation:
        """تحليل استجابة LLM"""
        try:
            data = json.loads(response)
            return LLMRecommendation(
                category=data.get('category', category),
                recommendation=data.get('recommendation', ''),
                reasoning=data.get('reasoning', ''),
                expected_impact=data.get('expected_impact', ''),
                implementation_steps=data.get('implementation_steps', []),
                success_metrics=data.get('success_metrics', []),
                priority_level=data.get('priority_level', 3)
            )
        except json.JSONDecodeError:
            # Fallback parsing
            return LLMRecommendation(
                category=category,
                recommendation=response[:150] if response else "توصية غير متوفرة",
                reasoning="تم توليدها باستخدام تحليل متقدم",
                expected_impact="تحسين في المجال المحدد",
                implementation_steps=["متابعة التطبيق", "قياس النتائج"],
                success_metrics=["تحسن ملحوظ"],
                priority_level=3
            )
    
    async def generate_and_store_report(self, child_id: int) -> Dict[str, Any]:
        """توليد وحفظ تقرير شامل"""
        # تحليل التقدم
        metrics = await self.analyze_progress(child_id)
        
        # توليد التوصيات
        recommendations = await self.generate_llm_recommendations(child_id, metrics)
        
        # حفظ في قاعدة البيانات
        report_id = await self._store_report(metrics, recommendations)
        
        return {
            'report_id': report_id,
            'metrics': asdict(metrics),
            'recommendations': [asdict(rec) for rec in recommendations],
            'generated_at': datetime.now().isoformat()
        }
    
    async def _store_report(
        self, 
        metrics: ProgressMetrics, 
        recommendations: List[LLMRecommendation]
    ) -> str:
        """حفظ التقرير في قاعدة البيانات"""
        if not self.db:
            raise Exception("قاعدة البيانات غير متوفرة")
        
        try:
            report_id = await self.db.execute(
                """
                INSERT INTO parent_reports 
                (child_id, generated_at, metrics, recommendations, analysis_version)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    metrics.child_id,
                    metrics.analysis_date.isoformat(),
                    json.dumps(asdict(metrics)),
                    json.dumps([asdict(rec) for rec in recommendations]),
                    'Task7_v1.0'
                )
            )
            
            self.logger.info(f"✅ تم حفظ التقرير برقم: {report_id}")
            return str(report_id)
            
        except Exception as e:
            self.logger.error(f"فشل في حفظ التقرير: {e}")
            raise
    
    # Helper methods for analysis
    
    def _analyze_vocabulary(self, interactions: List[Dict]) -> Dict[str, Any]:
        """تحليل المفردات والنصوص"""
        texts = [i.get('message', '') for i in interactions if i.get('message')]
        all_text = ' '.join(texts)
        
        # تحليل بسيط للمفردات
        words = all_text.lower().split()
        unique_words = list(set(words))
        
        # حساب التعقيد
        complexity_score = min(1.0, len(unique_words) / 50.0)
        
        # تقدير مستوى القراءة
        if complexity_score < 0.3:
            reading_level = "مبتدئ"
        elif complexity_score < 0.6:
            reading_level = "متوسط"
        else:
            reading_level = "متقدم"
        
        return {
            'unique_words': len(unique_words),
            'new_words': unique_words[-5:] if len(unique_words) > 5 else unique_words,
            'complexity_score': complexity_score,
            'reading_level': reading_level,
            'learning_velocity': len(unique_words) / 7  # كلمات في اليوم
        }
    
    def _analyze_emotions(self, interactions: List[Dict]) -> Dict[str, Any]:
        """تحليل المشاعر والذكاء العاطفي"""
        emotion_keywords = ['happy', 'sad', 'angry', 'excited', 'worried', 'calm']
        texts = [i.get('message', '') for i in interactions if i.get('message')]
        
        emotion_count = 0
        for text in texts:
            for emotion in emotion_keywords:
                if emotion.lower() in text.lower():
                    emotion_count += 1
        
        # حساب درجة الذكاء العاطفي
        ei_score = min(1.0, emotion_count / max(1, len(texts)))
        
        return {
            'ei_score': ei_score,
            'emotion_expressions': emotion_count
        }
    
    def _analyze_cognitive_skills(self, interactions: List[Dict]) -> Dict[str, Any]:
        """تحليل المهارات المعرفية"""
        texts = [i.get('message', '') for i in interactions if i.get('message')]
        
        # البحث عن مؤشرات التفكير المعرفي
        cognitive_indicators = ['why', 'how', 'what if', 'because', 'لماذا', 'كيف']
        cognitive_count = 0
        
        for text in texts:
            for indicator in cognitive_indicators:
                if indicator.lower() in text.lower():
                    cognitive_count += 1
        
        cognitive_score = min(1.0, cognitive_count / max(1, len(texts)))
        
        return {
            'cognitive_score': cognitive_score,
            'thinking_indicators': cognitive_count
        }
    
    def _analyze_social_skills(self, interactions: List[Dict]) -> Dict[str, Any]:
        """تحليل المهارات الاجتماعية"""
        texts = [i.get('message', '') for i in interactions if i.get('message')]
        
        # البحث عن مؤشرات المهارات الاجتماعية
        social_indicators = ['please', 'thank you', 'sorry', 'share', 'help']
        social_count = 0
        
        for text in texts:
            for indicator in social_indicators:
                if indicator.lower() in text.lower():
                    social_count += 1
        
        social_score = min(1.0, social_count / max(1, len(texts)))
        
        return {
            'social_score': social_score,
            'social_expressions': social_count
        }
    
    def _identify_concerns(self, vocab_analysis, emotional_analysis, cognitive_analysis) -> Dict[str, Any]:
        """تحديد المخاوف والتوصيات"""
        concerns = []
        interventions = []
        urgency_level = 0
        
        # تحليل المفردات
        if vocab_analysis['complexity_score'] < 0.3:
            concerns.append("محدودية في المفردات")
            interventions.append("زيادة أنشطة القراءة والحديث")
            urgency_level = max(urgency_level, 2)
        
        # تحليل المشاعر
        if emotional_analysis['ei_score'] < 0.3:
            concerns.append("قلة التعبير العاطفي")
            interventions.append("أنشطة تطوير المشاعر")
            urgency_level = max(urgency_level, 1)
        
        # تحليل المهارات المعرفية
        if cognitive_analysis['cognitive_score'] < 0.3:
            concerns.append("محدودية التفكير النقدي")
            interventions.append("أنشطة تطوير التفكير")
            urgency_level = max(urgency_level, 1)
        
        return {
            'concerns': concerns,
            'interventions': interventions,
            'urgency_level': urgency_level
        }
    
    def _create_empty_metrics(self, child_id: int) -> ProgressMetrics:
        """إنشاء مقاييس فارغة"""
        return ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            total_unique_words=0,
            new_words_this_period=[],
            vocabulary_complexity_score=0.0,
            reading_level_equivalent="غير محدد",
            emotional_intelligence_score=0.0,
            cognitive_development_score=0.0,
            social_skills_score=0.0,
            learning_velocity=0.0,
            developmental_concerns=["عدم توفر بيانات كافية"],
            intervention_recommendations=["زيادة التفاعل"],
            urgency_level=0
        )
    
    def _generate_fallback_recommendations(self, metrics: ProgressMetrics) -> List[LLMRecommendation]:
        """توصيات احتياطية"""
        recommendations = []
        
        if metrics.vocabulary_complexity_score < 0.5:
            recommendations.append(LLMRecommendation(
                category="learning",
                recommendation="زيادة أنشطة القراءة والمحادثة",
                reasoning="المفردات تحتاج تطوير",
                expected_impact="تحسن في التعبير والفهم",
                implementation_steps=["قراءة يومية", "محادثات تفاعلية"],
                success_metrics=["زيادة المفردات"],
                priority_level=4
            ))
        
        if metrics.emotional_intelligence_score < 0.5:
            recommendations.append(LLMRecommendation(
                category="emotional",
                recommendation="أنشطة تطوير الذكاء العاطفي",
                reasoning="قلة التعبير العاطفي",
                expected_impact="تحسن في التعبير عن المشاعر",
                implementation_steps=["مناقشة المشاعر", "قصص عاطفية"],
                success_metrics=["تعبير أفضل عن المشاعر"],
                priority_level=3
            ))
        
        return recommendations[:3]
    
    async def _get_interactions(self, child_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """جلب التفاعلات من قاعدة البيانات"""
        if not self.db:
            return []
        
        try:
            interactions = await self.db.fetch_all(
                """
                SELECT * FROM conversations 
                WHERE child_id = ? AND created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
                """,
                (child_id, start_date.isoformat(), end_date.isoformat())
            )
            return [dict(row) for row in interactions]
        except Exception as e:
            self.logger.error(f"فشل في جلب التفاعلات: {e}")
            return []
    
    async def _get_child_info(self, child_id: int) -> Dict[str, Any]:
        """جلب معلومات الطفل"""
        if not self.db:
            return {'name': 'غير محدد', 'age': 5}
        
        try:
            child = await self.db.fetch_one(
                "SELECT * FROM children WHERE id = ?", (child_id,)
            )
            return dict(child) if child else {'name': 'غير محدد', 'age': 5}
        except Exception as e:
            self.logger.error(f"فشل في جلب معلومات الطفل: {e}")
            return {'name': 'غير محدد', 'age': 5} 