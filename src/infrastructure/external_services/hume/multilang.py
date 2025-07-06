"""
Hume multi-language analysis task.
"""

import logging
from typing import Dict

import librosa
import numpy as np

from .models import CalibrationConfig

logger = logging.getLogger(__name__)


async def analyze_emotion_multilang(
    hume_client: "EnhancedHumeIntegration",
    audio_file: str,
    lang: str,
    config: CalibrationConfig,
) -> Dict:
    """🌍 تحليل المشاعر مع دعم اللغات المتعددة"""
    logger.info(f"🌍 Analyzing emotion in language: {lang}")

    try:
        # Detect language if auto
        if lang == "auto":
            detected_lang = await _detect_language(audio_file)
            logger.debug(f"🔍 Language detected: {detected_lang}")
        else:
            detected_lang = lang

        # Get language-specific configuration
        lang_config = _get_language_config(detected_lang)

        # Perform analysis with language context
        result = await hume_client._hume_analysis_with_language(audio_file, lang_config)

        # Apply language-specific calibration
        calibrated_result = _apply_language_calibration(
            result, detected_lang, config
        )

        return {
            "detected_language": detected_lang,
            "emotions": calibrated_result["emotions"],
            "dominant_emotion": calibrated_result["dominant_emotion"],
            "confidence": calibrated_result["confidence"],
            "language_confidence": config.language_weights.get(
                detected_lang, 0.8
            ),
        }

    except Exception as e:
        logger.error(f"❌ Multi-language analysis failed: {e}")
        return {"error": str(e)}


async def _detect_language(audio_file: str) -> str:
    """كشف اللغة من الملف الصوتي"""
    try:
        y, sr = librosa.load(audio_file, sr=16000)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        avg_centroid = np.mean(spectral_centroid)
        if avg_centroid > 2000:
            return "en"
        else:
            return "ar"
    except Exception as e:
        logger.error(f"Error detecting language: {e}", exc_info=True)
        return "ar"


def _get_language_config(language: str) -> Dict:
    """إعدادات خاصة بكل لغة"""
    if language == "ar":
        return {
            "prosody": {
                "granularity": "word",
                "language_context": "arabic"}}
    elif language == "en":
        return {
            "prosody": {
                "granularity": "utterance",
                "language_context": "english"}}
    else:
        return {"prosody": {}}


def _apply_language_calibration(
    result: Dict, language: str, config: CalibrationConfig
) -> Dict:
    """تطبيق معايرة خاصة باللغة"""
    language_weight = config.language_weights.get(language, 1.0)

    # Adjust confidence based on language
    adjusted_confidence = result["confidence"] * language_weight

    # Adjust emotion scores
    adjusted_emotions = {}
    for emotion, score in result["emotions"].items():
        adjusted_score = score * language_weight

        # Apply confidence threshold
        if adjusted_score >= config.confidence_threshold:
            adjusted_emotions[emotion] = min(adjusted_score, 1.0)
        else:
            adjusted_emotions[emotion] = adjusted_score * 0.8

    return {
        "emotions": adjusted_emotions,
        "dominant_emotion": max(
            adjusted_emotions,
            key=adjusted_emotions.get),
        "confidence": adjusted_confidence,
    }
