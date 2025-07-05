import re
from datetime import datetime
from typing import Any, Dict, List

from .models import EmotionAnalysis, EmotionCategory


class TextEmotionAnalyzer:
    def __init__(self, emotion_keywords: Dict, emoji_emotions: Dict, cultural_patterns: Dict):
        self._emotion_keywords = emotion_keywords
        self._emoji_emotions = emoji_emotions
        self._cultural_patterns = cultural_patterns

    def analyze(self, text: str, language: str = "ar") -> EmotionAnalysis:
        try:
            start_time = datetime.now()
            pipeline_data = self._run_text_analysis_pipeline(text, language)
            synthesis_data = self._synthesize_analysis_results(pipeline_data)
            return self._package_emotion_result(text, language, start_time, pipeline_data, synthesis_data)
        except Exception as e:
            return EmotionAnalysis(
                primary_emotion=EmotionCategory.NEUTRAL, confidence=0.5,
                language=language, analysis_method="text_fallback", metadata={"error": str(e)}
            )

    def _run_text_analysis_pipeline(self, text: str, language: str) -> Dict[str, Any]:
        text_clean = text.strip().lower()
        return {
            "text_clean": text_clean,
            "keyword_emotions": self._analyze_keywords(text_clean),
            "emoji_emotions": self._analyze_emojis(text),
            "cultural_emotions": self._analyze_cultural_patterns(text_clean, language),
            "intensity_score": self._analyze_intensity(text),
        }

    def _synthesize_analysis_results(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        all_emotions = self._combine_emotion_scores(
            (analysis_data["keyword_emotions"], 0.4),
            (analysis_data["emoji_emotions"], 0.3),
            (analysis_data["cultural_emotions"], 0.3),
        )
        primary_emotion = self._get_primary_emotion(all_emotions)
        return {
            "all_emotions": all_emotions, "primary_emotion": primary_emotion,
            "confidence": self._calculate_confidence(all_emotions, primary_emotion, analysis_data["intensity_score"]),
            "sentiment_score": self._calculate_sentiment(all_emotions),
            "arousal_level": self._calculate_arousal(primary_emotion, analysis_data["intensity_score"]),
        }

    def _package_emotion_result(self, text: str, language: str, start_time: datetime, pipeline_data: Dict, synthesis_data: Dict) -> EmotionAnalysis:
        processing_time = int(
            (datetime.now() - start_time).total_seconds() * 1000)
        return EmotionAnalysis(
            primary_emotion=synthesis_data["primary_emotion"], confidence=synthesis_data["confidence"],
            secondary_emotions={k: v for k, v in synthesis_data["all_emotions"].items(
            ) if k != synthesis_data["primary_emotion"]},
            sentiment_score=synthesis_data["sentiment_score"], arousal_level=synthesis_data["arousal_level"],
            keywords=self._extract_emotional_keywords(
                pipeline_data["text_clean"]),
            language=language, analysis_method="text", processing_time_ms=processing_time,
            metadata={"text_length": len(
                text), "intensity_score": pipeline_data["intensity_score"]}
        )

    def _analyze_keywords(self, text: str) -> Dict[EmotionCategory, float]:
        scores = {}
        for emotion, keywords in self._emotion_keywords.items():
            score = sum(text.count(kw) for kw in keywords)
            if score > 0:
                scores[emotion] = min(score / (len(text.split()) + 1), 1.0)
        return scores

    def _analyze_emojis(self, text: str) -> Dict[EmotionCategory, float]:
        scores = {}
        for emoji, emotion in self._emoji_emotions.items():
            if (count := text.count(emoji)) > 0:
                scores[emotion] = scores.get(
                    emotion, 0) + min(count * 0.4, 1.0)
        return {k: min(v, 1.0) for k, v in scores.items()}

    def _analyze_cultural_patterns(self, text: str, language: str) -> Dict[EmotionCategory, float]:
        scores: Dict[EmotionCategory, float] = {}
        patterns = self._cultural_patterns.get(language, {})
        for pattern, emotions in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                for emotion, score in emotions.items():
                    scores[emotion] = scores.get(emotion, 0) + score
        return scores

    def _analyze_intensity(self, text: str) -> float:
        intensity_markers = {"very": 0.3, "really": 0.3,
                             "so": 0.2, "extremely": 0.5, "جداً": 0.4}
        intensity = 0.5 + \
            sum(boost for marker, boost in intensity_markers.items()
                if marker in text.lower())
        intensity += min(text.count("!") * 0.1, 0.3)
        return min(intensity, 1.0)

    def _combine_emotion_scores(self, *weighted_scores) -> Dict[EmotionCategory, float]:
        combined = {}
        total_weight = sum(weight for _, weight in weighted_scores)
        for scores, weight in weighted_scores:
            for emotion, score in scores.items():
                combined[emotion] = combined.get(
                    emotion, 0) + (score * (weight / total_weight))
        return combined

    def _get_primary_emotion(self, emotions: Dict[EmotionCategory, float]) -> EmotionCategory:
        if not emotions:
            return EmotionCategory.NEUTRAL
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        return max_emotion[0] if max_emotion[1] >= 0.3 else EmotionCategory.NEUTRAL

    def _calculate_confidence(self, emotions: Dict, primary_emotion: EmotionCategory, intensity: float) -> float:
        if not emotions or primary_emotion not in emotions:
            return 0.5
        primary_score = emotions[primary_emotion]
        other_scores = [score for emotion,
                        score in emotions.items() if emotion != primary_emotion]
        separation = primary_score - \
            max(other_scores) if other_scores else primary_score
        return min(primary_score + (separation * 0.3) + (intensity * 0.2), 1.0)

    def _calculate_sentiment(self, emotions: Dict[EmotionCategory, float]) -> float:
        pos_emotions = {EmotionCategory.HAPPY, EmotionCategory.EXCITED,
                        EmotionCategory.LOVE, EmotionCategory.JOY}
        neg_emotions = {EmotionCategory.SAD,
                        EmotionCategory.ANGRY, EmotionCategory.SCARED}
        pos_score = sum(emotions.get(e, 0) for e in pos_emotions)
        neg_score = sum(emotions.get(e, 0) for e in neg_emotions)
        return (pos_score - neg_score) / (pos_score + neg_score) if (pos_score + neg_score) > 0 else 0.0

    def _calculate_arousal(self, emotion: EmotionCategory, intensity: float) -> float:
        high_arousal = {EmotionCategory.EXCITED, EmotionCategory.ANGRY,
                        EmotionCategory.SCARED, EmotionCategory.SURPRISE}
        low_arousal = {EmotionCategory.TIRED,
                       EmotionCategory.SAD, EmotionCategory.CONFUSED}
        base_arousal = 0.8 if emotion in high_arousal else 0.3 if emotion in low_arousal else 0.5
        return min(base_arousal * (0.5 + intensity * 0.5), 1.0)

    def _extract_emotional_keywords(self, text: str) -> List[str]:
        keywords = {kw for keywords in self._emotion_keywords.values()
                    for kw in keywords if kw in text}
        if "!" in text:
            keywords.add("exclamation")
        if "?" in text:
            keywords.add("question")
        return list(keywords)[:5]
