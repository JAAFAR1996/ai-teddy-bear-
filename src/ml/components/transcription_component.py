# ===================================================================
# 🎤 AI Teddy Bear - Speech Transcription Component
# Child-Optimized Speech Recognition
# AI Team Lead: Senior AI Engineer
# Date: January 2025
# ===================================================================

from kubeflow.dsl import component, Input, Output, Dataset, Artifact
import logging
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@component(
    base_image="python:3.11-slim",
    packages_to_install=[
        "openai-whisper==20231117",
        "torch==2.1.0",
        "torchaudio==2.1.0",
        "transformers==4.36.0",
        "numpy==1.24.3",
        "librosa==0.10.1",
        "webrtcvad==2.0.10"
    ]
)
def transcribe_audio_op(
    audio: Input[Dataset],
    transcription: Output[Dataset],
    confidence_metrics: Output[Artifact],
    language_model: str = "whisper-large-v3",
    child_optimized: bool = True,
    target_language: str = "auto"
) -> Dict[str, any]:
    """
    تحويل الكلام إلى نص محسن للأطفال
    """
    import whisper
    import torch
    import torchaudio
    import numpy as np
    from transformers import pipeline
    
    logger.info(f"Starting transcription with model: {language_model}")
    
    try:
        # تحميل نموذج Whisper محسن للأطفال
        model = whisper.load_model("large-v3")
        
        # تحميل الصوت
        audio_data, sample_rate = torchaudio.load(audio.path)
        
        # معالجة أولية للصوت
        if child_optimized:
            audio_data = optimize_for_child_speech(audio_data, sample_rate)
        
        # كشف النشاط الصوتي
        voice_segments = detect_voice_activity(audio_data, sample_rate)
        
        # تحويل إلى numpy للمعالجة مع Whisper
        audio_np = audio_data.squeeze().numpy()
        
        # إعداد خيارات التحويل
        transcribe_options = {
            "language": None if target_language == "auto" else target_language,
            "task": "transcribe",
            "temperature": 0.0,  # للحصول على نتائج محددة
            "best_of": 3,        # جرب عدة مرات واختر الأفضل
            "beam_size": 5,      # بحث أوسع
            "patience": 1.0,
            "suppress_tokens": [-1],  # لا تقمع أي رموز
            "initial_prompt": "This is a child speaking clearly and naturally.",
        }
        
        # تنفيذ التحويل
        result = model.transcribe(
            audio_np,
            **transcribe_options
        )
        
        # معالجة النتائج
        processed_result = process_transcription_result(
            result, 
            voice_segments,
            child_optimized
        )
        
        # تحسينات خاصة بالأطفال
        if child_optimized:
            processed_result = apply_child_speech_corrections(processed_result)
        
        # تقييم جودة التحويل
        quality_metrics = assess_transcription_quality(
            result, 
            audio_data, 
            sample_rate
        )
        
        # حفظ النتيجة النهائية
        final_result = {
            'text': processed_result['text'],
            'segments': processed_result['segments'],
            'language': result.get('language', 'unknown'),
            'confidence': quality_metrics['overall_confidence'],
            'processing_metadata': {
                'model_used': language_model,
                'child_optimized': child_optimized,
                'voice_segments_detected': len(voice_segments),
                'processing_timestamp': datetime.now().isoformat(),
                'audio_duration': float(len(audio_np) / sample_rate)
            }
        }
        
        with open(transcription.path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        # حفظ مقاييس الجودة
        with open(confidence_metrics.path, 'w') as f:
            json.dump(quality_metrics, f, indent=2)
        
        logger.info(f"Transcription completed: '{processed_result['text'][:50]}...'")
        return final_result
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        # إنشاء نتيجة طوارئ
        emergency_result = {
            'text': "",
            'confidence': 0.0,
            'error': str(e),
            'processing_timestamp': datetime.now().isoformat()
        }
        
        with open(transcription.path, 'w') as f:
            json.dump(emergency_result, f, indent=2)
        
        raise


def optimize_for_child_speech(audio: torch.Tensor, sample_rate: int) -> torch.Tensor:
    """تحسين الصوت لكلام الأطفال"""
    
    # تطبيق فلتر لتحسين ترددات الكلام للأطفال
    # الأطفال لديهم ترددات أساسية أعلى من البالغين
    
    import torchaudio.transforms as T
    
    # تحسين الترددات المتوسطة العالية (300-3000 Hz)
    highpass = T.HighpassBiquad(sample_rate, cutoff_freq=200.0)
    lowpass = T.LowpassBiquad(sample_rate, cutoff_freq=4000.0)
    
    # تطبيق الفلاتر
    audio = highpass(audio)
    audio = lowpass(audio)
    
    # تطبيع الصوت
    audio = audio / torch.max(torch.abs(audio)) * 0.9
    
    return audio


def detect_voice_activity(audio: torch.Tensor, sample_rate: int) -> List[Tuple[float, float]]:
    """كشف فترات النشاط الصوتي"""
    import webrtcvad
    
    # تحويل إلى تنسيق مناسب لـ WebRTC VAD
    audio_np = audio.squeeze().numpy()
    
    # إعادة عينة إلى 16kHz إذا لزم الأمر
    if sample_rate != 16000:
        import librosa
        audio_np = librosa.resample(audio_np, orig_sr=sample_rate, target_sr=16000)
        sample_rate = 16000
    
    # تحويل إلى 16-bit integers
    audio_int16 = (audio_np * 32767).astype(np.int16)
    
    # إعداد VAD
    vad = webrtcvad.Vad(2)  # مستوى حساسية متوسط
    
    # تحليل الصوت في إطارات 30ms
    frame_duration = 30  # ms
    frame_length = int(sample_rate * frame_duration / 1000)
    
    voice_segments = []
    current_segment_start = None
    
    for i in range(0, len(audio_int16) - frame_length, frame_length):
        frame = audio_int16[i:i + frame_length].tobytes()
        
        if vad.is_speech(frame, sample_rate):
            if current_segment_start is None:
                current_segment_start = i / sample_rate
        else:
            if current_segment_start is not None:
                voice_segments.append((current_segment_start, i / sample_rate))
                current_segment_start = None
    
    # إضافة آخر segment إذا لم ينته
    if current_segment_start is not None:
        voice_segments.append((current_segment_start, len(audio_int16) / sample_rate))
    
    return voice_segments


def process_transcription_result(
    result: Dict, 
    voice_segments: List[Tuple[float, float]], 
    child_optimized: bool
) -> Dict:
    """معالجة نتائج التحويل"""
    
    # استخراج النص الأساسي
    text = result['text'].strip()
    
    # معالجة القطع (segments)
    segments = []
    for segment in result.get('segments', []):
        processed_segment = {
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text'].strip(),
            'confidence': segment.get('avg_logprob', 0.0),
            'words': segment.get('words', [])
        }
        segments.append(processed_segment)
    
    # تطبيق تحسينات خاصة بالأطفال
    if child_optimized:
        text = improve_child_transcription(text)
        segments = [improve_segment_transcription(seg) for seg in segments]
    
    return {
        'text': text,
        'segments': segments,
        'voice_activity_periods': voice_segments
    }


def improve_child_transcription(text: str) -> str:
    """تحسين النص المحول للأطفال"""
    
    # قاموس تصحيحات شائعة لكلام الأطفال
    child_corrections = {
        # أخطاء النطق الشائعة
        'wike': 'like',
        'pwease': 'please',
        'fwend': 'friend',
        'bwother': 'brother',
        'sistew': 'sister',
        'wove': 'love',
        'vewy': 'very',
        'wittle': 'little',
        'hewp': 'help',
        'wat': 'what',
        'wight': 'right',
        'wead': 'read',
        'wun': 'run',
        'wed': 'red',
        
        # كلمات مختصرة شائعة
        'gonna': 'going to',
        'wanna': 'want to',
        'dunno': "don't know",
        'gimme': 'give me',
        'lemme': 'let me',
        
        # تصحيحات نحوية
        'me want': 'I want',
        'me like': 'I like',
        'me go': 'I go',
        'me see': 'I see',
    }
    
    # تطبيق التصحيحات
    corrected_text = text
    for wrong, correct in child_corrections.items():
        corrected_text = corrected_text.replace(wrong, correct)
    
    # تنظيف إضافي
    corrected_text = ' '.join(corrected_text.split())  # إزالة المسافات الزائدة
    
    return corrected_text


def improve_segment_transcription(segment: Dict) -> Dict:
    """تحسين segment واحد"""
    segment['text'] = improve_child_transcription(segment['text'])
    return segment


def apply_child_speech_corrections(result: Dict) -> Dict:
    """تطبيق تصحيحات شاملة لكلام الأطفال"""
    
    # تحسين النص الرئيسي
    result['text'] = improve_child_transcription(result['text'])
    
    # تحسين كل segment
    if 'segments' in result:
        result['segments'] = [
            improve_segment_transcription(seg) 
            for seg in result['segments']
        ]
    
    # إضافة علامات ثقة محسنة للأطفال
    result['child_speech_confidence'] = calculate_child_speech_confidence(result)
    
    return result


def calculate_child_speech_confidence(result: Dict) -> float:
    """حساب مستوى الثقة في التحويل لكلام الأطفال"""
    
    base_confidence = 0.7  # ثقة أساسية
    
    # تحليل عوامل الجودة
    text = result['text']
    
    # طول النص (النصوص القصيرة قد تكون أقل دقة)
    length_factor = min(1.0, len(text.split()) / 5.0)
    
    # وجود كلمات شائعة للأطفال
    child_words = ['mama', 'papa', 'toy', 'play', 'fun', 'happy', 'want', 'like']
    child_word_count = sum(1 for word in child_words if word in text.lower())
    child_factor = min(1.0, child_word_count / 3.0)
    
    # حساب الثقة النهائية
    final_confidence = base_confidence * (0.4 + 0.3 * length_factor + 0.3 * child_factor)
    
    return max(0.1, min(1.0, final_confidence))


def assess_transcription_quality(
    result: Dict, 
    audio: torch.Tensor, 
    sample_rate: int
) -> Dict:
    """تقييم جودة التحويل"""
    
    # حساب مقاييس الجودة
    text = result['text']
    segments = result.get('segments', [])
    
    # مقاييس أساسية
    word_count = len(text.split())
    segment_count = len(segments)
    avg_confidence = np.mean([seg.get('avg_logprob', 0.0) for seg in segments]) if segments else 0.0
    
    # حساب نسبة الصمت إلى الكلام
    audio_duration = len(audio.squeeze()) / sample_rate
    speech_duration = sum(seg['end'] - seg['start'] for seg in segments)
    speech_ratio = speech_duration / audio_duration if audio_duration > 0 else 0.0
    
    # تقييم جودة الصوت
    audio_quality = assess_audio_quality(audio, sample_rate)
    
    # حساب الثقة الإجمالية
    overall_confidence = calculate_overall_confidence(
        avg_confidence, speech_ratio, audio_quality, word_count
    )
    
    return {
        'overall_confidence': overall_confidence,
        'word_count': word_count,
        'segment_count': segment_count,
        'average_segment_confidence': avg_confidence,
        'speech_to_silence_ratio': speech_ratio,
        'audio_quality_score': audio_quality,
        'estimated_accuracy': estimate_transcription_accuracy(overall_confidence),
        'quality_indicators': {
            'sufficient_speech': speech_ratio > 0.3,
            'clear_audio': audio_quality > 0.7,
            'meaningful_length': word_count >= 3,
            'high_confidence': overall_confidence > 0.8
        }
    }


def assess_audio_quality(audio: torch.Tensor, sample_rate: int) -> float:
    """تقييم جودة الصوت"""
    
    # حساب نسبة الإشارة إلى الضوضاء
    signal_power = torch.mean(audio ** 2)
    noise_estimate = torch.std(audio[-int(0.1 * sample_rate):])  # آخر 0.1 ثانية
    
    if noise_estimate > 0:
        snr = 10 * torch.log10(signal_power / (noise_estimate ** 2))
        snr_score = torch.clamp(snr / 30.0, 0.0, 1.0)  # تطبيع إلى 0-1
    else:
        snr_score = 0.5
    
    # تقييم التوزيع الطيفي
    spectral_score = assess_spectral_quality(audio, sample_rate)
    
    # الجودة الإجمالية
    overall_quality = 0.6 * float(snr_score) + 0.4 * spectral_score
    
    return overall_quality


def assess_spectral_quality(audio: torch.Tensor, sample_rate: int) -> float:
    """تقييم جودة التوزيع الطيفي"""
    
    # تحليل FFT بسيط
    fft = torch.fft.fft(audio.squeeze())
    magnitude = torch.abs(fft)
    
    # تحقق من وجود طاقة في نطاق الكلام (300-3400 Hz)
    freqs = torch.fft.fftfreq(len(fft), 1/sample_rate)
    speech_range_mask = (torch.abs(freqs) >= 300) & (torch.abs(freqs) <= 3400)
    
    speech_energy = torch.sum(magnitude[speech_range_mask])
    total_energy = torch.sum(magnitude)
    
    if total_energy > 0:
        speech_ratio = speech_energy / total_energy
        return float(speech_ratio)
    
    return 0.5


def calculate_overall_confidence(
    avg_confidence: float, 
    speech_ratio: float, 
    audio_quality: float, 
    word_count: int
) -> float:
    """حساب الثقة الإجمالية في التحويل"""
    
    # تطبيع avg_confidence (من log probability إلى 0-1)
    normalized_confidence = max(0.0, min(1.0, (avg_confidence + 1.0) / 1.0))
    
    # تطبيع عدد الكلمات
    word_factor = min(1.0, word_count / 10.0)
    
    # حساب الوزن الإجمالي
    overall = (
        0.4 * normalized_confidence +
        0.2 * speech_ratio +
        0.3 * audio_quality +
        0.1 * word_factor
    )
    
    return max(0.1, min(1.0, overall))


def estimate_transcription_accuracy(confidence: float) -> str:
    """تقدير دقة التحويل"""
    
    if confidence >= 0.9:
        return "excellent"
    elif confidence >= 0.8:
        return "very_good"
    elif confidence >= 0.7:
        return "good"
    elif confidence >= 0.6:
        return "fair"
    elif confidence >= 0.4:
        return "poor"
    else:
        return "very_poor" 