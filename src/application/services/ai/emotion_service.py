from src.infrastructure.modern_container import BaseService
from src.audio.hume_emotion_analyzer import ChildVoiceEmotion
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import asdict
import statistics
import sqlite3
import json
import asyncio
import structlog
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

"""
🎭 Emotion Analysis Service for AI Teddy Bear
حفظ وإدارة وتحليل بيانات المشاعر من HUME AI
"""

logger = structlog.get_logger(__name__)


class EmotionService(BaseService):
    """خدمة إدارة المشاعر - حفظ وتحليل وتتبع المشاعر عبر الوقت"""

    def __init__(self, container):
        super().__init__(container)
        self.db_path = Path("data/emotions.db")
        self.db_path.parent.mkdir(exist_ok=True)

        # إنشاء قاعدة البيانات
        asyncio.create_task(self._initialize_database())

        logger.info("🎭 Emotion Service initialized")

    async def _initialize_database(self):
        """إنشاء جداول قاعدة البيانات"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # إنشاء الجداول الأساسية
            self._create_emotion_analyses_table(cursor)
            self._create_parent_feedback_table(cursor)
            self._create_child_stats_table(cursor)
            self._create_database_indexes(cursor)

            conn.commit()
            logger.info("✅ Emotion database initialized")

    def _create_emotion_analyses_table(self, cursor):
        """إنشاء جدول المشاعر الأساسي"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                udid TEXT NOT NULL,
                child_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                dominant_emotion TEXT NOT NULL,
                joy REAL DEFAULT 0.0,
                sadness REAL DEFAULT 0.0,
                anger REAL DEFAULT 0.0,
                fear REAL DEFAULT 0.0,
                excitement REAL DEFAULT 0.0,
                calmness REAL DEFAULT 0.0,
                surprise REAL DEFAULT 0.0,
                curiosity REAL DEFAULT 0.0,
                frustration REAL DEFAULT 0.0,
                shyness REAL DEFAULT 0.0,
                playfulness REAL DEFAULT 0.0,
                tiredness REAL DEFAULT 0.0,
                energy_level REAL DEFAULT 0.0,
                speech_rate REAL DEFAULT 0.0,
                pitch_variation REAL DEFAULT 0.0,
                voice_quality TEXT DEFAULT 'clear',
                confidence REAL DEFAULT 0.0,
                emotional_intensity REAL DEFAULT 0.0,
                attention_level REAL DEFAULT 0.0,
                communication_clarity REAL DEFAULT 0.0,
                developmental_indicators TEXT DEFAULT '[]',
                transcription TEXT DEFAULT '',
                response_text TEXT DEFAULT '',
                session_context TEXT DEFAULT '{}'
            )
        """)

    def _create_parent_feedback_table(self, cursor):
        """إنشاء جدول التغذية الراجعة من الوالدين"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parent_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                udid TEXT NOT NULL,
                interaction_id TEXT NOT NULL,
                feedback TEXT NOT NULL,
                accuracy_rating INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (interaction_id) REFERENCES emotion_analyses (id)
            )
        """)

    def _create_child_stats_table(self, cursor):
        """إنشاء جدول إحصائيات الطفل"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS child_emotion_stats (
                udid TEXT PRIMARY KEY,
                child_name TEXT NOT NULL,
                total_interactions INTEGER DEFAULT 0,
                avg_joy REAL DEFAULT 0.0,
                avg_sadness REAL DEFAULT 0.0,
                avg_curiosity REAL DEFAULT 0.0,
                most_common_emotion TEXT DEFAULT 'curious',
                emotional_stability REAL DEFAULT 1.0,
                last_analysis TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

    def _create_database_indexes(self, cursor):
        """إنشاء indexes للبحث السريع"""
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_udid_timestamp ON emotion_analyses (udid, timestamp)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_dominant_emotion ON emotion_analyses (dominant_emotion)")

    async def save_emotion_analysis(
        self,
        udid: str,
        child_name: str,
        emotion_data: ChildVoiceEmotion,
        transcription: str = "",
        response_text: str = "",
        session_context: Dict[str, Any] = None
    ) -> str:
        """حفظ نتيجة تحليل المشاعر"""

        try:
            session_context = session_context or {}

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # حفظ التحليل
                cursor.execute("""
                    INSERT INTO emotion_analyses (
                        udid, child_name, timestamp, dominant_emotion,
                        joy, sadness, anger, fear, excitement, calmness, surprise,
                        curiosity, frustration, shyness, playfulness, tiredness,
                        energy_level, speech_rate, pitch_variation, voice_quality,
                        confidence, emotional_intensity, attention_level, 
                        communication_clarity, developmental_indicators,
                        transcription, response_text, session_context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                             ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    udid, child_name, emotion_data.timestamp, emotion_data.dominant_emotion,
                    emotion_data.joy, emotion_data.sadness, emotion_data.anger,
                    emotion_data.fear, emotion_data.excitement, emotion_data.calmness,
                    emotion_data.surprise, emotion_data.curiosity, emotion_data.frustration,
                    emotion_data.shyness, emotion_data.playfulness, emotion_data.tiredness,
                    emotion_data.energy_level, emotion_data.speech_rate,
                    emotion_data.pitch_variation, emotion_data.voice_quality,
                    emotion_data.confidence, emotion_data.emotional_intensity,
                    emotion_data.attention_level, emotion_data.communication_clarity,
                    json.dumps(emotion_data.developmental_indicators),
                    transcription, response_text, json.dumps(session_context)
                ))

                interaction_id = str(cursor.lastrowid)
                conn.commit()

                # تحديث إحصائيات الطفل
                await self._update_child_stats(udid, child_name, emotion_data)

                logger.info(
                    f"✅ Emotion analysis saved for {child_name} (ID: {interaction_id})")
                return interaction_id

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            raise

    async def get_emotion_history(
        self,
        udid: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """استرجاع تاريخ المشاعر للطفل"""

        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM emotion_analyses 
                    WHERE udid = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (udid, since_date))

                columns = [description[0]
                           for description in cursor.description]
                results = []

                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))

                    # تحويل JSON strings مرة أخرى إلى objects
                    try:
                        row_dict['developmental_indicators'] = json.loads(
                            row_dict['developmental_indicators'])
                        row_dict['session_context'] = json.loads(
                            row_dict['session_context'])
                    except json.JSONDecodeError as e:
                        logger.error(f"Error in operation: {e}", exc_info=True)
                        row_dict['developmental_indicators'] = []
                        row_dict['session_context'] = {}

                    results.append(row_dict)

                return results

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return []

    async def analyze_emotion_trends(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """تحليل اتجاهات المشاعر"""

        if not history:
            return {"message": "لا توجد بيانات كافية للتحليل"}

        try:
            # حساب متوسط المشاعر
            emotion_fields = ['joy', 'sadness', 'anger', 'fear', 'excitement',
                              'curiosity', 'playfulness', 'tiredness']

            avg_emotions = {}
            for field in emotion_fields:
                values = [item[field]
                          for item in history if item[field] is not None]
                if values:
                    avg_emotions[field] = round(statistics.mean(values), 3)
                else:
                    avg_emotions[field] = 0.0

            # المشاعر المهيمنة
            dominant_emotions = [item['dominant_emotion'] for item in history]
            emotion_counts = {}
            for emotion in dominant_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            most_common_emotion = max(
                emotion_counts.items(), key=lambda x: x[1])

            # تحليل الاستقرار العاطفي
            stability = self._calculate_emotional_stability(history)

            # تحليل الطاقة والنشاط
            energy_levels = [item['energy_level']
                             for item in history if item['energy_level'] is not None]
            avg_energy = statistics.mean(
                energy_levels) if energy_levels else 0.5

            # مؤشرات التطوير الأكثر شيوعاً
            all_indicators = []
            for item in history:
                try:
                    indicators = item['developmental_indicators']
                    if isinstance(indicators, str):
                        indicators = json.loads(indicators)
                    all_indicators.extend(indicators)
                except json.JSONDecodeError as e:
                    logger.error(f"Error in operation: {e}", exc_info=True)
                    continue

            indicator_counts = {}
            for indicator in all_indicators:
                indicator_counts[indicator] = indicator_counts.get(
                    indicator, 0) + 1

            top_indicators = sorted(
                indicator_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # توصيات بناء على التحليل
            recommendations = self._generate_trend_recommendations(
                avg_emotions, most_common_emotion[0], stability, avg_energy
            )

            return {
                "analysis_period": f"{len(history)} تفاعل خلال الفترة المحددة",
                "average_emotions": avg_emotions,
                "most_common_emotion": {
                    "emotion": most_common_emotion[0],
                    "percentage": round(most_common_emotion[1] / len(history) * 100, 1)
                },
                "emotion_distribution": emotion_counts,
                "emotional_stability": round(stability, 3),
                "average_energy_level": round(avg_energy, 3),
                "top_developmental_indicators": [
                    {"indicator": indicator, "frequency": count}
                    for indicator, count in top_indicators
                ],
                "recommendations": recommendations,
                "summary": self._generate_summary(avg_emotions, most_common_emotion[0], stability)
            }

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return {"error": f"خطأ في تحليل الاتجاهات: {str(e)}"}

    def _calculate_emotional_stability(self, history: List[Dict[str, Any]]) -> float:
        """حساب الاستقرار العاطفي"""

        if len(history) < 2:
            return 1.0

        # حساب التباين في المشاعر المهيمنة
        dominant_emotions = [item['dominant_emotion'] for item in history]
        changes = sum(1 for i in range(1, len(dominant_emotions))
                      if dominant_emotions[i] != dominant_emotions[i-1])

        stability = 1.0 - (changes / (len(dominant_emotions) - 1))
        return max(0.0, stability)

    def _generate_trend_recommendations(
        self,
        avg_emotions: Dict[str, float],
        most_common: str,
        stability: float,
        avg_energy: float
    ) -> List[str]:
        """توليد توصيات بناء على اتجاهات المشاعر"""

        recommendations = []

        # توصيات للمشاعر السلبية المرتفعة
        if avg_emotions.get('sadness', 0) > 0.5:
            recommendations.append(
                "مستوى حزن مرتفع - يُنصح بأنشطة ممتعة ومحفزة للمزاج")
            recommendations.append("قد يحتاج الطفل لدعم عاطفي إضافي")

        if avg_emotions.get('fear', 0) > 0.4:
            recommendations.append(
                "مستوى قلق ملحوظ - يُنصح ببيئة آمنة ومطمئنة")
            recommendations.append("تجنب المحتوى المخيف أو المثير للقلق")

        # توصيات للمشاعر الإيجابية
        if avg_emotions.get('curiosity', 0) > 0.6:
            recommendations.append("فضول عالي - وقت ممتاز للأنشطة التعليمية")
            recommendations.append("شجع الاستكشاف والتجارب العلمية البسيطة")

        if avg_emotions.get('playfulness', 0) > 0.6:
            recommendations.append("حب اللعب عالي - أضف ألعاب تفاعلية ونشطة")

        # توصيات للاستقرار العاطفي
        if stability < 0.3:
            recommendations.append(
                "تقلبات عاطفية كثيرة - يُنصح بروتين ثابت ومهدئ")
        elif stability > 0.8:
            recommendations.append(
                "استقرار عاطفي ممتاز - استمر في النهج الحالي")

        # توصيات للطاقة
        if avg_energy > 0.8:
            recommendations.append(
                "طاقة عالية - تأكد من وجود أنشطة حركية كافية")
        elif avg_energy < 0.3:
            recommendations.append("طاقة منخفضة - تحقق من النوم والراحة")

        return recommendations

    def _generate_summary(
        self,
        avg_emotions: Dict[str, float],
        most_common: str,
        stability: float
    ) -> str:
        """توليد ملخص نصي للحالة العاطفية"""

        # ترجمة المشاعر للعربية
        emotion_translations = {
            'joy': 'السعادة',
            'sadness': 'الحزن',
            'curiosity': 'الفضول',
            'playfulness': 'حب اللعب',
            'fear': 'القلق',
            'excitement': 'الإثارة',
            'calmness': 'الهدوء',
            'tiredness': 'التعب',
            'anger': 'الغضب'
        }

        dominant_ar = emotion_translations.get(most_common, most_common)

        if stability > 0.7:
            stability_desc = "مستقر عاطفياً"
        elif stability > 0.4:
            stability_desc = "متقلب قليلاً"
        else:
            stability_desc = "متقلب عاطفياً"

        # تحديد المشاعر البارزة
        high_emotions = []
        for emotion, value in avg_emotions.items():
            if value > 0.6:
                high_emotions.append(
                    emotion_translations.get(emotion, emotion))

        summary = f"الطفل يظهر غالباً مشاعر {dominant_ar} ويبدو {stability_desc}."

        if high_emotions:
            summary += f" المشاعر البارزة: {', '.join(high_emotions)}."

        return summary

    async def save_parent_feedback(
        self,
        udid: str,
        interaction_id: str,
        feedback: str,
        accuracy_rating: int
    ):
        """حفظ تغذية راجعة من الوالدين"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO parent_feedback (
                        udid, interaction_id, feedback, accuracy_rating, timestamp
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    udid, interaction_id, feedback, accuracy_rating,
                    datetime.now().isoformat()
                ))

                conn.commit()
                logger.info(
                    f"✅ Parent feedback saved for interaction {interaction_id}")

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            raise

    async def _update_child_stats(
        self,
        udid: str,
        child_name: str,
        emotion_data: ChildVoiceEmotion
    ):
        """تحديث إحصائيات الطفل"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # التحقق من وجود الطفل في الإحصائيات
                cursor.execute(
                    "SELECT * FROM child_emotion_stats WHERE udid = ?", (udid,))
                existing = cursor.fetchone()

                current_time = datetime.now().isoformat()

                if existing:
                    # تحديث الإحصائيات الموجودة
                    cursor.execute("""
                        UPDATE child_emotion_stats SET
                            total_interactions = total_interactions + 1,
                            last_analysis = ?,
                            updated_at = ?
                        WHERE udid = ?
                    """, (current_time, current_time, udid))

                else:
                    # إنشاء إحصائيات جديدة
                    cursor.execute("""
                        INSERT INTO child_emotion_stats (
                            udid, child_name, total_interactions, 
                            most_common_emotion, last_analysis, 
                            created_at, updated_at
                        ) VALUES (?, ?, 1, ?, ?, ?, ?)
                    """, (
                        udid, child_name, emotion_data.dominant_emotion,
                        current_time, current_time, current_time
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

    async def get_child_stats(self, udid: str) -> Dict[str, Any]:
        """الحصول على إحصائيات الطفل"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT * FROM child_emotion_stats WHERE udid = ?", (udid,))
                result = cursor.fetchone()

                if result:
                    columns = [description[0]
                               for description in cursor.description]
                    return dict(zip(columns, result))
                else:
                    return {"message": "لا توجد إحصائيات لهذا الطفل"}

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return {"error": str(e)}
