import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ChildSpeechProcessor:
    """Processor for enhancing and post-processing child speech for transcription."""

    def enhance_for_children(self, audio_array: np.ndarray) -> np.ndarray:
        """
        🎪 تحسين البيانات الصوتية للأطفال
        Child-specific audio enhancements
        """
        audio_array = self._boost_high_frequencies(audio_array)
        audio_array = self._reduce_background_noise(audio_array)
        audio_array = self._normalize_for_quiet_children(audio_array)
        return audio_array

    def _boost_high_frequencies(self, audio_array: np.ndarray) -> np.ndarray:
        """تعزيز الترددات العالية لأصوات الأطفال"""
        if len(audio_array) > 2:
            enhanced = np.copy(audio_array)
            enhanced[1:-1] = (0.25 * enhanced[:-2] + 0.5 *
                              enhanced[1:-1] + 0.25 * enhanced[2:])
            return enhanced
        return audio_array

    def _reduce_background_noise(self, audio_array: np.ndarray) -> np.ndarray:
        """تقليل ضوضاء الخلفية الشائعة في بيئة الأطفال"""
        noise_threshold = np.std(audio_array) * 0.1
        audio_array = np.where(
            np.abs(audio_array) < noise_threshold, 0, audio_array)
        return audio_array

    def _normalize_for_quiet_children(
            self, audio_array: np.ndarray) -> np.ndarray:
        """تطبيع الصوت للأطفال ذوي الأصوات المنخفضة"""
        max_val = np.max(np.abs(audio_array))
        if max_val > 0 and max_val < 0.3:
            boost_factor = min(3.0, 0.8 / max_val)
            audio_array = audio_array * boost_factor
        return audio_array

    def post_process_child_speech(
            self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        👶 معالجة لاحقة لتحسين نتائج نسخ كلام الأطفال
        """
        text = result.get("text", "").strip()
        if not text:
            return result

        text = self._fix_common_child_speech_errors(text)
        confidence = result.get("confidence", 0.0)
        if self._is_clear_child_speech(text):
            confidence = min(1.0, confidence + 0.1)

        result["text"] = text
        result["confidence"] = confidence
        result["child_optimized"] = True
        return result

    def _fix_common_child_speech_errors(self, text: str) -> str:
        """إصلاح الأخطاء الشائعة في كلام الأطفال"""
        common_fixes = {
            " wike ": " like ", " wove ": " love ", " pwease ": " please ",
            " fwiend ": " friend ", " bwother ": " brother ", " sistew ": " sister ",
        }
        for wrong, correct in common_fixes.items():
            text = text.replace(wrong, correct)
        return text

    def _is_clear_child_speech(self, text: str) -> bool:
        """تحديد ما إذا كان النص يشير إلى كلام طفل واضح"""
        clear_indicators = [
            len(text.split()) >= 3,
            not any(char in text for char in "[](){}"),
            text.count(" ") >= 2,
            any(word in text.lower()
                for word in ["hello", "hi", "teddy", "play", "story"]),
        ]
        return sum(clear_indicators) >= 2
