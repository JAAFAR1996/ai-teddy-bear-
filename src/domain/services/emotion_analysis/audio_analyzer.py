import logging
from datetime import datetime
from typing import Any, Dict

from .models import EmotionAnalysis, EmotionCategory

# Optional imports for Hume AI
try:
    from hume import StreamDataModels
    from hume.client import AsyncHumeClient
    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioEmotionAnalyzer:
    def __init__(self, hume_client: 'AsyncHumeClient' = None):
        self.hume_client = hume_client

    async def analyze(self, audio_file_path: str, language: str = "ar") -> EmotionAnalysis:
        if not HUME_AVAILABLE or not self.hume_client:
            logger.warning("Hume AI not available for audio analysis.")
            return await self._fallback_audio_analysis(audio_file_path, language)

        start_time = datetime.now()
        try:
            results = await self._get_hume_results(audio_file_path)
            processed_data = self._process_hume_results(results)
            return self._package_audio_emotion_result(processed_data, language, start_time)
        except Exception as e:
            logger.error(f"Audio emotion analysis failed: {e}")
            return await self._fallback_audio_analysis(audio_file_path, language, error_message=str(e))

    async def _get_hume_results(self, audio_file_path: str) -> list:
        config = StreamDataModels.voice()
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()

        results = []
        async with self.hume_client.connect_async([config]) as socket:
            response = await socket.send_bytes(audio_bytes)
            results.extend(response.get("voice", {}).get("predictions", []))
        return results

    def _process_hume_results(self, results: list) -> Dict[str, Any]:
        if not results:
            return {"primary": EmotionCategory.NEUTRAL, "confidence": 0.5, "secondary": {}}

        top_emotion = max(results[0]["emotions"], key=lambda x: x["score"])
        primary_emotion = self._map_hume_emotion(top_emotion["name"])
        confidence = min(top_emotion["score"], 1.0)

        secondary_emotions = {
            self._map_hume_emotion(e["name"]): e["score"]
            for e in sorted(results[0]["emotions"], key=lambda x: x["score"], reverse=True)[1:4]
        }
        return {"primary": primary_emotion, "confidence": confidence, "secondary": secondary_emotions}

    def _package_audio_emotion_result(self, data: Dict, language: str, start_time: datetime) -> EmotionAnalysis:
        processing_time = int(
            (datetime.now() - start_time).total_seconds() * 1000)
        return EmotionAnalysis(
            primary_emotion=data["primary"], confidence=data["confidence"],
            secondary_emotions=data["secondary"], language=language,
            analysis_method="audio", processing_time_ms=processing_time, metadata={"source": "HumeAI"}
        )

    def _map_hume_emotion(self, hume_emotion: str) -> EmotionCategory:
        mapping = {
            "joy": EmotionCategory.HAPPY, "sadness": EmotionCategory.SAD,
            "anger": EmotionCategory.ANGRY, "fear": EmotionCategory.SCARED,
            "surprise": EmotionCategory.SURPRISE, "excitement": EmotionCategory.EXCITED,
            "confusion": EmotionCategory.CONFUSED, "neutral": EmotionCategory.NEUTRAL,
            "love": EmotionCategory.LOVE, "curiosity": EmotionCategory.CURIOUS,
        }
        return mapping.get(hume_emotion.lower(), EmotionCategory.NEUTRAL)

    async def _fallback_audio_analysis(self, audio_file_path: str, language: str, error_message: str = "Hume AI not available") -> EmotionAnalysis:
        return EmotionAnalysis(
            primary_emotion=EmotionCategory.NEUTRAL, confidence=0.4, language=language,
            analysis_method="audio_fallback",
            metadata={"error": error_message, "audio_file": audio_file_path}
        )
