"""
Emotion Analysis Domain Service
Specialized service for analyzing emotional patterns and development
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

from ..models.report_models import InteractionAnalysis, EmotionDistribution


class EmotionAnalyzerService:
    """Domain service for emotion analysis"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def count_empathy_indicators(self, interactions: List[InteractionAnalysis]) -> int:
        """Count empathy indicators in interactions"""
        try:
            empathy_keywords = [
                "care", "help", "sorry", "feel", "sad", "happy",
                "يساعد", "يهتم", "آسف", "يشعر", "حزين", "سعيد"
            ]
            
            empathy_count = 0
            for interaction in interactions:
                for indicator in interaction.behavioral_indicators:
                    if any(keyword in indicator.lower() for keyword in empathy_keywords):
                        empathy_count += 1
                
                # Check emotions for empathetic responses
                if interaction.emotions.get("supportive", 0) > 0.3:
                    empathy_count += 1
                if interaction.emotions.get("caring", 0) > 0.3:
                    empathy_count += 1
            
            return empathy_count

        except Exception as e:
            self.logger.error(f"Empathy indicators counting error: {e}")
            return 0

    def analyze_sharing_behavior(self, interactions: List[InteractionAnalysis]) -> int:
        """Analyze sharing behavior patterns"""
        try:
            sharing_keywords = [
                "share", "give", "together", "friend", "play",
                "يشارك", "يعطي", "معاً", "صديق", "يلعب"
            ]
            
            sharing_count = 0
            for interaction in interactions:
                # Check topics for sharing themes
                for topic in interaction.topics_discussed:
                    if any(keyword in topic.lower() for keyword in sharing_keywords):
                        sharing_count += 1
                
                # Check behavioral indicators
                for indicator in interaction.behavioral_indicators:
                    if any(keyword in indicator.lower() for keyword in sharing_keywords):
                        sharing_count += 1
            
            return sharing_count

        except Exception as e:
            self.logger.error(f"Sharing behavior analysis error: {e}")
            return 0

    def calculate_cooperation_level(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate cooperation level (0-1)"""
        try:
            if not interactions:
                return 0.0
            
            cooperation_indicators = []
            
            for interaction in interactions:
                cooperation_score = 0.0
                
                # High quality interactions indicate cooperation
                cooperation_score += interaction.quality_score * 0.4
                
                # Check for cooperative emotions
                cooperative_emotions = ["happy", "calm", "curious", "supportive"]
                for emotion in cooperative_emotions:
                    cooperation_score += interaction.emotions.get(emotion, 0) * 0.15
                
                # Check behavioral indicators for cooperation
                cooperation_keywords = ["listen", "follow", "agree", "يستمع", "يتبع", "يوافق"]
                for indicator in interaction.behavioral_indicators:
                    if any(keyword in indicator.lower() for keyword in cooperation_keywords):
                        cooperation_score += 0.2
                
                cooperation_indicators.append(min(1.0, cooperation_score))
            
            return sum(cooperation_indicators) / len(cooperation_indicators)

        except Exception as e:
            self.logger.error(f"Cooperation level calculation error: {e}")
            return 0.5

    def analyze_sleep_patterns(self, interactions: List[InteractionAnalysis]) -> float:
        """Analyze sleep pattern quality based on interactions"""
        try:
            if not interactions:
                return None
            
            # Look for sleep-related indicators
            bedtime_interactions = []
            for interaction in interactions:
                # Check if interaction happened during bedtime hours (7 PM - 9 PM)
                hour = interaction.timestamp.hour
                if 19 <= hour <= 21:
                    bedtime_interactions.append(interaction)
            
            if not bedtime_interactions:
                return None
            
            # Analyze quality of bedtime interactions
            calm_emotions = ["calm", "sleepy", "peaceful"]
            sleep_quality_scores = []
            
            for interaction in bedtime_interactions:
                quality = 0.0
                
                # Check for calm emotions
                for emotion in calm_emotions:
                    quality += interaction.emotions.get(emotion, 0) * 0.3
                
                # Check for sleep-related topics
                sleep_topics = ["sleep", "dream", "bed", "tired", "نوم", "حلم", "سرير", "تعب"]
                for topic in interaction.topics_discussed:
                    if any(sleep_word in topic.lower() for sleep_word in sleep_topics):
                        quality += 0.3
                
                # Lower excitement indicates better sleep preparation
                excitement_level = interaction.emotions.get("excited", 0)
                quality += max(0, 0.4 - excitement_level)
                
                sleep_quality_scores.append(min(1.0, quality))
            
            return sum(sleep_quality_scores) / len(sleep_quality_scores)

        except Exception as e:
            self.logger.error(f"Sleep pattern analysis error: {e}")
            return None

    def count_bedtime_conversations(self, interactions: List[InteractionAnalysis]) -> int:
        """Count bedtime conversations"""
        try:
            bedtime_count = 0
            
            for interaction in interactions:
                # Check if interaction happened during bedtime hours
                hour = interaction.timestamp.hour
                if 19 <= hour <= 22:  # 7 PM to 10 PM
                    # Check for bedtime-related content
                    bedtime_indicators = [
                        "sleep", "bed", "tired", "goodnight", "dream",
                        "نوم", "سرير", "تعب", "ليلة سعيدة", "حلم"
                    ]
                    
                    has_bedtime_content = False
                    for topic in interaction.topics_discussed:
                        if any(indicator in topic.lower() for indicator in bedtime_indicators):
                            has_bedtime_content = True
                            break
                    
                    if has_bedtime_content:
                        bedtime_count += 1
                    elif hour >= 20:  # After 8 PM, count as bedtime regardless
                        bedtime_count += 1
            
            return bedtime_count

        except Exception as e:
            self.logger.error(f"Bedtime conversation counting error: {e}")
            return 0

    def identify_concerning_patterns(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify concerning emotional patterns"""
        try:
            concerns = []
            
            if not interactions:
                return concerns
            
            # Analyze emotion distribution
            emotion_totals = defaultdict(float)
            for interaction in interactions:
                for emotion, score in interaction.emotions.items():
                    emotion_totals[emotion] += score
            
            total_interactions = len(interactions)
            
            # Check for concerning patterns
            
            # 1. High negative emotions
            negative_emotions = ["sad", "angry", "scared", "frustrated"]
            negative_total = sum(emotion_totals.get(emotion, 0) for emotion in negative_emotions)
            if negative_total > total_interactions * 0.4:
                concerns.append("مستوى عالي من المشاعر السلبية")
            
            # 2. Very low interaction quality
            low_quality_count = sum(
                1 for interaction in interactions
                if interaction.quality_score < 0.3
            )
            if low_quality_count > total_interactions * 0.5:
                concerns.append("جودة تفاعل منخفضة بشكل مستمر")
            
            # 3. Extreme emotional instability
            emotion_changes = 0
            for i in range(1, len(interactions)):
                if interactions[i].primary_emotion != interactions[i-1].primary_emotion:
                    emotion_changes += 1
            
            change_rate = emotion_changes / (len(interactions) - 1) if len(interactions) > 1 else 0
            if change_rate > 0.8:
                concerns.append("عدم استقرار عاطفي شديد")
            
            # 4. Consistent fear or anxiety
            fear_anxiety_total = emotion_totals.get("scared", 0) + emotion_totals.get("anxious", 0)
            if fear_anxiety_total > total_interactions * 0.3:
                concerns.append("مستوى عالي من القلق أو الخوف")
            
            # 5. Social withdrawal indicators
            social_emotions = ["happy", "curious", "playful"]
            social_total = sum(emotion_totals.get(emotion, 0) for emotion in social_emotions)
            if social_total < total_interactions * 0.2:
                concerns.append("انخفاض في المشاعر الاجتماعية الإيجابية")
            
            return concerns

        except Exception as e:
            self.logger.error(f"Concerning patterns identification error: {e}")
            return ["خطأ في تحليل الأنماط العاطفية"]

    def generate_urgent_recommendations(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Generate urgent recommendations based on emotional analysis"""
        try:
            recommendations = []
            concerning_patterns = self.identify_concerning_patterns(interactions)
            
            # Generate specific recommendations based on concerns
            if "مستوى عالي من المشاعر السلبية" in concerning_patterns:
                recommendations.append("التركيز على أنشطة تعزز المشاعر الإيجابية")
                recommendations.append("مراجعة البيئة المحيطة بالطفل للتأكد من الراحة النفسية")
            
            if "جودة تفاعل منخفضة بشكل مستمر" in concerning_patterns:
                recommendations.append("تقليل مدة الجلسات وزيادة تكرارها")
                recommendations.append("استخدام أنشطة أكثر تفاعلية وإثارة للاهتمام")
            
            if "عدم استقرار عاطفي شديد" in concerning_patterns:
                recommendations.append("إنشاء روتين ثابت للتفاعلات")
                recommendations.append("استشارة أخصائي الصحة النفسية للأطفال")
            
            if "مستوى عالي من القلق أو الخوف" in concerning_patterns:
                recommendations.append("التركيز على أنشطة مهدئة ومطمئنة")
                recommendations.append("تجنب المواضيع أو الأنشطة المثيرة للقلق")
                recommendations.append("استشارة أخصائي نفسي فوراً")
            
            if "انخفاض في المشاعر الاجتماعية الإيجابية" in concerning_patterns:
                recommendations.append("زيادة الأنشطة الاجتماعية والتفاعلية")
                recommendations.append("تشجيع اللعب الجماعي مع الأطفال الآخرين")
            
            # General urgent recommendations if multiple concerns
            if len(concerning_patterns) >= 3:
                recommendations.append("مراجعة شاملة مع أخصائي تطوير الطفل")
                recommendations.append("تقييم البيئة المنزلية والمدرسية")
            
            return list(set(recommendations))  # Remove duplicates

        except Exception as e:
            self.logger.error(f"Urgent recommendations generation error: {e}")
            return ["استشارة أخصائي للحصول على تقييم مفصل"] 