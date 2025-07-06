"""
Hume calibration task.
"""

import logging
import statistics
from typing import Dict, List

import numpy as np
import soundfile as sf

from .models import CalibrationConfig

logger = logging.getLogger(__name__)


def calibrate_hume(
    hume_client: "EnhancedHumeIntegration",
    confidence_threshold: float,
    config: CalibrationConfig,
) -> Dict[str, float]:
    """🎯 معايرة دقة تحليل المشاعر"""
    logger.info(
        f"🎯 Calibrating HUME with threshold: {confidence_threshold}")

    # Create test samples
    test_samples = _create_test_samples()

    results = []
    for sample in test_samples:
        # Analyze each sample
        emotion_data = hume_client._analyze_sample(sample)
        confidence = emotion_data.get("confidence", 0.0)

        results.append(
            {
                "sample": sample["name"],
                "confidence": confidence,
                "passes_threshold": confidence >= confidence_threshold,
            }
        )

    # Calculate metrics
    success_rate = sum(
        1 for r in results if r["passes_threshold"]) / len(results)
    avg_confidence = statistics.mean([r["confidence"] for r in results])

    # Update configuration
    config.confidence_threshold = confidence_threshold

    logger.info(f"✅ Calibration complete: {success_rate:.1%} success rate")

    return {
        "success_rate": success_rate,
        "average_confidence": avg_confidence,
        "threshold": confidence_threshold,
        "recommendation": _get_calibration_recommendation(success_rate),
    }


def _create_test_samples() -> List[Dict]:
    """إنشاء عينات اختبار للمعايرة"""
    samples = []

    emotions = ["joy", "sadness", "anger", "calm"]
    frequencies = [440, 220, 300, 260]  # Hz

    for emotion, freq in zip(emotions, frequencies):
        # Create synthetic audio
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * freq * t)

        # Add some noise
        noise = 0.05 * np.random.random(len(audio))
        audio = audio + noise

        filename = f"test_{emotion}.wav"
        sf.write(filename, audio, sample_rate)

        samples.append({"name": emotion, "file": filename,
                        "expected_emotion": emotion})

    return samples


def _get_calibration_recommendation(success_rate: float) -> str:
    """توصيات المعايرة"""
    if success_rate >= 0.9:
        return "Excellent calibration"
    elif success_rate >= 0.7:
        return "Good - minor adjustments may help"
    elif success_rate >= 0.5:
        return "Fair - consider lowering threshold"
    else:
        return "Poor - significant calibration needed"
