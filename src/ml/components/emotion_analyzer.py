# ===================================================================
# 😊 AI Teddy Bear - Child Emotion Analysis Component
# Advanced Emotion Recognition for Children
# AI Team Lead: Senior AI Engineer
# Date: January 2025
# ===================================================================

from kubeflow.dsl import component, Input, Output, Dataset, Artifact
import logging
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

@component(
    base_image="python:3.11-slim",
    packages_to_install=[
        "transformers==4.36.0",
        "torch==2.1.0",
        "torchaudio==2.1.0",
        "librosa==0.10.1",
        "numpy==1.24.3",
        "scikit-learn==1.3.2",
        "scipy==1.11.4"
    ]
)
def analyze_child_emotions_op(
    audio: Input[Dataset],
    transcript: str,
    emotion_data: Output[Dataset],
    emotion_report: Output[Artifact],
    child_age: int,
    cultural_context: str = "general"
) -> Dict[str, any]:
    """تحليل متقدم لعواطف الأطفال من الصوت والنص"""
    import torch
    import torchaudio
    import librosa
    from transformers import pipeline
    
    logger.info(f"Starting emotion analysis for child age: {child_age}")
    
    try:
        # تحميل الصوت
        waveform, sample_rate = torchaudio.load(audio.path)
        
        # تحليل الخصائص الصوتية
        audio_features = extract_child_audio_features(waveform, sample_rate, child_age)
        
        # تحليل النص للعواطف
        text_emotions = analyze_text_emotions(transcript, child_age)
        
        # تحليل الخصائص الصوتية للعواطف
        voice_emotions = analyze_voice_emotions(audio_features, child_age)
        
        # دمج النتائج
        combined_emotions = combine_emotion_analyses(
            text_emotions, 
            voice_emotions, 
            child_age,
            cultural_context
        )
        
        # تقييم الحالة العاطفية الإجمالية
        emotional_state = assess_overall_emotional_state(
            combined_emotions,
            child_age,
            transcript
        )
        
        # إنشاء التقرير النهائي
        emotion_result = {
            'primary_emotion': emotional_state['primary_emotion'],
            'secondary_emotions': emotional_state['secondary_emotions'],
            'confidence_scores': emotional_state['confidence_scores'],
            'emotional_intensity': emotional_state['intensity'],
            'emotional_stability': emotional_state['stability'],
            'age_appropriate_response': emotional_state['response_guidance'],
            'risk_indicators': emotional_state['risk_factors'],
            'audio_features': audio_features,
            'text_analysis': text_emotions,
            'voice_analysis': voice_emotions,
            'analysis_timestamp': datetime.now().isoformat(),
            'child_age': child_age,
            'cultural_context': cultural_context
        }
        
        # حفظ البيانات العاطفية
        with open(emotion_data.path, 'w', encoding='utf-8') as f:
            json.dump(emotion_result, f, indent=2, ensure_ascii=False)
        
        # إنشاء تقرير مفصل
        detailed_report = generate_emotion_analysis_report(emotion_result)
        
        with open(emotion_report.path, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Emotion analysis completed: {emotional_state['primary_emotion']}")
        return emotion_result
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {str(e)}")
        emergency_result = create_neutral_emotion_result(child_age)
        
        with open(emotion_data.path, 'w') as f:
            json.dump(emergency_result, f, indent=2)
        
        raise


def extract_child_audio_features(waveform: torch.Tensor, sr: int, age: int) -> Dict:
    """استخراج الخصائص الصوتية المناسبة للأطفال"""
    import librosa
    
    # تحويل إلى numpy
    audio = waveform.squeeze().numpy()
    
    features = {}
    
    # 1. الخصائص الطيفية
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
    features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
    
    # 2. الطاقة والشدة
    rms = librosa.feature.rms(y=audio)[0]
    features['energy_mean'] = float(np.mean(rms))
    features['energy_std'] = float(np.std(rms))
    features['energy_max'] = float(np.max(rms))
    
    # 3. التردد الأساسي (مهم للأطفال)
    f0 = librosa.yin(audio, fmin=50, fmax=800)
    f0_clean = f0[f0 > 0]
    
    if len(f0_clean) > 0:
        features['pitch_mean'] = float(np.mean(f0_clean))
        features['pitch_std'] = float(np.std(f0_clean))
        features['pitch_range'] = float(np.max(f0_clean) - np.min(f0_clean))
    else:
        features['pitch_mean'] = 0.0
        features['pitch_std'] = 0.0
        features['pitch_range'] = 0.0
    
    # 4. معدل تغيير الطيف
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
    features['spectral_centroid_std'] = float(np.std(spectral_centroids))
    
    # 5. معدل العبور الصفري
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    features['zcr_mean'] = float(np.mean(zcr))
    features['zcr_std'] = float(np.std(zcr))
    
    # 6. خصائص خاصة بالأطفال
    features.update(extract_child_specific_features(audio, sr, age))
    
    return features


def extract_child_specific_features(audio: np.ndarray, sr: int, age: int) -> Dict:
    """استخراج خصائص خاصة بكلام الأطفال"""
    features = {}
    
    # 1. سرعة الكلام
    speech_rate = estimate_speech_rate(audio, sr)
    features['speech_rate'] = speech_rate
    
    # 2. التقطع في الكلام
    pause_ratio = calculate_pause_ratio(audio, sr)
    features['pause_ratio'] = pause_ratio
    
    # 3. تغيرات الطبقة الصوتية
    pitch_variability = calculate_pitch_variability(audio, sr)
    features['pitch_variability'] = pitch_variability
    
    # 4. وضوح النطق
    articulation_clarity = estimate_articulation_clarity(audio, sr, age)
    features['articulation_clarity'] = articulation_clarity
    
    return features


def analyze_text_emotions(text: str, age: int) -> Dict:
    """تحليل العواطف من النص مع مراعاة العمر"""
    
    # كلمات عاطفية مناسبة للأطفال
    emotion_keywords = {
        'happy': ['happy', 'fun', 'yay', 'wow', 'cool', 'awesome', 'love', 'like'],
        'sad': ['sad', 'cry', 'unhappy', 'no', 'bad', 'hurt', 'miss'],
        'excited': ['excited', 'wow', 'amazing', 'super', 'best', 'favorite'],
        'angry': ['angry', 'mad', 'hate', 'stop', 'no', 'bad'],
        'scared': ['scared', 'afraid', 'monster', 'dark', 'help'],
        'confused': ['what', 'why', 'how', 'dont know', "don't understand"],
        'curious': ['what', 'why', 'how', 'tell me', 'show me']
    }
    
    text_lower = text.lower()
    emotion_scores = {}
    
    # حساب درجات العواطف
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        emotion_scores[emotion] = score
    
    # تطبيع النتائج
    total_score = sum(emotion_scores.values())
    if total_score > 0:
        emotion_probabilities = {
            emotion: score / total_score 
            for emotion, score in emotion_scores.items()
        }
    else:
        emotion_probabilities = {emotion: 0.0 for emotion in emotion_scores}
    
    # تحديد العاطفة الأساسية
    primary_emotion = max(emotion_probabilities, key=emotion_probabilities.get)
    
    # تحليل إضافي بناءً على العمر
    age_adjustments = apply_age_based_emotion_adjustments(
        emotion_probabilities, 
        text, 
        age
    )
    
    return {
        'emotion_scores': emotion_probabilities,
        'primary_emotion_text': primary_emotion,
        'confidence': emotion_probabilities[primary_emotion],
        'age_adjustments': age_adjustments,
        'text_length': len(text.split()),
        'emotional_words_found': total_score
    }


def analyze_voice_emotions(audio_features: Dict, age: int) -> Dict:
    """تحليل العواطف من الخصائص الصوتية"""
    
    voice_emotions = {
        'happy': 0.0,
        'sad': 0.0,
        'excited': 0.0,
        'angry': 0.0,
        'scared': 0.0,
        'calm': 0.0
    }
    
    # 1. تحليل الطاقة
    energy_mean = audio_features.get('energy_mean', 0.0)
    if energy_mean > 0.15:
        voice_emotions['excited'] += 0.3
        voice_emotions['happy'] += 0.2
    elif energy_mean < 0.05:
        voice_emotions['sad'] += 0.3
        voice_emotions['calm'] += 0.2
    
    # 2. تحليل التردد الأساسي
    pitch_mean = audio_features.get('pitch_mean', 0.0)
    pitch_std = audio_features.get('pitch_std', 0.0)
    
    age_adjusted_pitch = adjust_pitch_for_age(pitch_mean, age)
    
    if age_adjusted_pitch > 0.7:
        voice_emotions['excited'] += 0.25
        voice_emotions['scared'] += 0.15
    elif age_adjusted_pitch < 0.3:
        voice_emotions['sad'] += 0.25
        voice_emotions['calm'] += 0.2
    
    # 3. تحليل تغيرات التردد
    if pitch_std > 50:
        voice_emotions['excited'] += 0.2
        voice_emotions['angry'] += 0.15
    elif pitch_std < 20:
        voice_emotions['calm'] += 0.3
        voice_emotions['sad'] += 0.1
    
    # 4. تحليل سرعة الكلام
    speech_rate = audio_features.get('speech_rate', 0.5)
    if speech_rate > 0.7:
        voice_emotions['excited'] += 0.2
        voice_emotions['angry'] += 0.1
    elif speech_rate < 0.3:
        voice_emotions['sad'] += 0.2
        voice_emotions['calm'] += 0.15
    
    # تطبيع النتائج
    total_score = sum(voice_emotions.values())
    if total_score > 0:
        voice_emotions = {
            emotion: score / total_score 
            for emotion, score in voice_emotions.items()
        }
    
    return {
        'emotion_scores': voice_emotions,
        'primary_emotion_voice': max(voice_emotions, key=voice_emotions.get),
        'confidence': max(voice_emotions.values()),
        'audio_quality_indicators': {
            'energy_level': categorize_energy_level(energy_mean),
            'pitch_level': categorize_pitch_level(age_adjusted_pitch),
            'speech_clarity': audio_features.get('articulation_clarity', 0.5)
        }
    }


def combine_emotion_analyses(
    text_emotions: Dict, 
    voice_emotions: Dict, 
    age: int,
    cultural_context: str
) -> Dict:
    """دمج تحليل العواطف من النص والصوت"""
    
    # أوزان الدمج بناءً على العمر
    if age <= 5:
        text_weight = 0.3
        voice_weight = 0.7
    elif age <= 8:
        text_weight = 0.5
        voice_weight = 0.5
    else:
        text_weight = 0.6
        voice_weight = 0.4
    
    # دمج النتائج
    combined_scores = {}
    all_emotions = set(text_emotions['emotion_scores'].keys()) | set(voice_emotions['emotion_scores'].keys())
    
    for emotion in all_emotions:
        text_score = text_emotions['emotion_scores'].get(emotion, 0.0)
        voice_score = voice_emotions['emotion_scores'].get(emotion, 0.0)
        
        combined_scores[emotion] = (
            text_weight * text_score + voice_weight * voice_score
        )
    
    # تطبيق تعديلات ثقافية
    cultural_adjustments = apply_cultural_adjustments(combined_scores, cultural_context)
    
    return {
        'combined_scores': combined_scores,
        'text_weight_used': text_weight,
        'voice_weight_used': voice_weight,
        'cultural_adjustments': cultural_adjustments,
        'primary_emotion_combined': max(combined_scores, key=combined_scores.get),
        'confidence_combined': max(combined_scores.values())
    }


def assess_overall_emotional_state(
    combined_emotions: Dict,
    age: int,
    transcript: str
) -> Dict:
    """تقييم الحالة العاطفية الإجمالية"""
    
    scores = combined_emotions['combined_scores']
    primary_emotion = combined_emotions['primary_emotion_combined']
    
    # تحديد العواطف الثانوية
    sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    secondary_emotions = [emotion for emotion, score in sorted_emotions[1:3] if score > 0.1]
    
    # تقييم الشدة العاطفية
    intensity = assess_emotional_intensity(scores, transcript, age)
    
    # تقييم الاستقرار العاطفي
    stability = assess_emotional_stability(scores, age)
    
    # تحديد عوامل الخطر
    risk_factors = identify_emotional_risk_factors(scores, transcript, age)
    
    # إرشادات الاستجابة
    response_guidance = generate_response_guidance(primary_emotion, age, intensity)
    
    return {
        'primary_emotion': primary_emotion,
        'secondary_emotions': secondary_emotions,
        'confidence_scores': scores,
        'intensity': intensity,
        'stability': stability,
        'risk_factors': risk_factors,
        'response_guidance': response_guidance,
        'needs_attention': len(risk_factors) > 0 or intensity > 0.8
    }


# Helper Functions
def estimate_speech_rate(audio: np.ndarray, sr: int) -> float:
    """تقدير سرعة الكلام"""
    import librosa
    rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
    transitions = np.sum(np.abs(np.diff(rms > np.mean(rms))))
    duration = len(audio) / sr
    return min(1.0, transitions / (duration * 10))


def calculate_pause_ratio(audio: np.ndarray, sr: int) -> float:
    """حساب نسبة التوقفات في الكلام"""
    import librosa
    rms = librosa.feature.rms(y=audio)[0]
    silence_threshold = np.mean(rms) * 0.1
    silence_frames = np.sum(rms < silence_threshold)
    return silence_frames / len(rms)


def calculate_pitch_variability(audio: np.ndarray, sr: int) -> float:
    """حساب تغيرات الطبقة الصوتية"""
    import librosa
    f0 = librosa.yin(audio, fmin=50, fmax=800)
    f0_clean = f0[f0 > 0]
    if len(f0_clean) > 1:
        return float(np.std(f0_clean) / np.mean(f0_clean))
    return 0.0


def estimate_articulation_clarity(audio: np.ndarray, sr: int, age: int) -> float:
    """تقدير وضوح النطق"""
    import librosa
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    clarity_score = np.mean(spectral_centroid) / (sr / 2)
    
    age_factor = min(1.0, age / 8.0)
    return clarity_score * age_factor


def adjust_pitch_for_age(pitch: float, age: int) -> float:
    """تعديل التردد بناءً على العمر"""
    if age <= 4:
        expected_range = (200, 500)
    elif age <= 8:
        expected_range = (180, 400)
    else:
        expected_range = (150, 350)
    
    normalized = (pitch - expected_range[0]) / (expected_range[1] - expected_range[0])
    return max(0.0, min(1.0, normalized))


def apply_age_based_emotion_adjustments(emotions: Dict, text: str, age: int) -> Dict:
    """تطبيق تعديلات بناءً على العمر"""
    adjustments = {}
    
    if age <= 4:
        adjustments['simplified_emotions'] = True
        adjustments['focus_basic_emotions'] = ['happy', 'sad', 'scared']
    elif age <= 8:
        adjustments['developing_emotional_vocabulary'] = True
    else:
        adjustments['complex_emotions_possible'] = True
    
    return adjustments


def apply_cultural_adjustments(emotions: Dict, cultural_context: str) -> Dict:
    """تطبيق تعديلات ثقافية"""
    return {
        'cultural_context_applied': cultural_context,
        'adjustments_made': []
    }


def categorize_energy_level(energy: float) -> str:
    """تصنيف مستوى الطاقة"""
    if energy > 0.2:
        return "high"
    elif energy > 0.1:
        return "medium"
    else:
        return "low"


def categorize_pitch_level(pitch: float) -> str:
    """تصنيف مستوى التردد"""
    if pitch > 0.7:
        return "high"
    elif pitch > 0.3:
        return "medium"
    else:
        return "low"


def assess_emotional_intensity(scores: Dict, transcript: str, age: int) -> float:
    """تقييم شدة العاطفة"""
    max_score = max(scores.values())
    
    intensity_indicators = ['very', 'really', 'so', 'super', '!']
    intensity_boost = sum(1 for indicator in intensity_indicators 
                         if indicator in transcript.lower()) * 0.1
    
    return min(1.0, max_score + intensity_boost)


def assess_emotional_stability(scores: Dict, age: int) -> float:
    """تقييم الاستقرار العاطفي"""
    values = list(scores.values())
    if len(values) > 1:
        stability = 1.0 - (np.std(values) / np.mean(values) if np.mean(values) > 0 else 0)
    else:
        stability = 1.0
    
    return max(0.0, min(1.0, stability))


def identify_emotional_risk_factors(scores: Dict, transcript: str, age: int) -> List[str]:
    """تحديد عوامل الخطر العاطفي"""
    risk_factors = []
    
    if scores.get('sad', 0) > 0.7:
        risk_factors.append('high_sadness')
    
    if scores.get('angry', 0) > 0.7:
        risk_factors.append('high_anger')
    
    if scores.get('scared', 0) > 0.7:
        risk_factors.append('high_fear')
    
    concerning_words = ['hurt', 'pain', 'scared', 'alone', 'hate', 'angry']
    if any(word in transcript.lower() for word in concerning_words):
        risk_factors.append('concerning_language')
    
    return risk_factors


def generate_response_guidance(emotion: str, age: int, intensity: float) -> Dict:
    """إنشاء إرشادات الاستجابة"""
    
    guidance = {
        'tone': 'neutral',
        'approach': 'standard',
        'focus': 'general'
    }
    
    if emotion == 'happy':
        guidance.update({
            'tone': 'cheerful',
            'approach': 'encouraging',
            'focus': 'celebrate and build on positive mood'
        })
    elif emotion == 'sad':
        guidance.update({
            'tone': 'gentle',
            'approach': 'comforting',
            'focus': 'provide emotional support and reassurance'
        })
    elif emotion == 'scared':
        guidance.update({
            'tone': 'calm',
            'approach': 'reassuring',
            'focus': 'provide safety and comfort'
        })
    elif emotion == 'excited':
        guidance.update({
            'tone': 'enthusiastic',
            'approach': 'engaging',
            'focus': 'channel excitement positively'
        })
    
    if intensity > 0.8:
        guidance['intensity_note'] = 'high_intensity_response_needed'
    
    if age <= 4:
        guidance['age_note'] = 'use_simple_language_and_concepts'
    elif age <= 8:
        guidance['age_note'] = 'balance_simplicity_with_engagement'
    
    return guidance


def generate_emotion_analysis_report(emotion_result: Dict) -> Dict:
    """إنشاء تقرير مفصل لتحليل العواطف"""
    
    return {
        'summary': {
            'primary_emotion': emotion_result['primary_emotion'],
            'confidence': emotion_result['confidence_scores'][emotion_result['primary_emotion']],
            'emotional_state': 'stable' if emotion_result['emotional_stability'] > 0.7 else 'variable',
            'needs_attention': emotion_result.get('needs_attention', False)
        },
        'detailed_analysis': {
            'all_emotion_scores': emotion_result['confidence_scores'],
            'text_vs_voice_analysis': {
                'text_emotions': emotion_result['text_analysis'],
                'voice_emotions': emotion_result['voice_analysis']
            },
            'audio_quality_indicators': emotion_result['voice_analysis']['audio_quality_indicators']
        },
        'recommendations': {
            'response_approach': emotion_result['age_appropriate_response'],
            'risk_factors': emotion_result['risk_indicators'],
            'follow_up_needed': len(emotion_result['risk_indicators']) > 0
        },
        'metadata': {
            'analysis_timestamp': emotion_result['analysis_timestamp'],
            'child_age': emotion_result['child_age'],
            'cultural_context': emotion_result['cultural_context']
        }
    }


def create_neutral_emotion_result(age: int) -> Dict:
    """إنشاء نتيجة عاطفية محايدة للطوارئ"""
    
    return {
        'primary_emotion': 'neutral',
        'secondary_emotions': [],
        'confidence_scores': {'neutral': 0.7},
        'emotional_intensity': 0.5,
        'emotional_stability': 1.0,
        'age_appropriate_response': {
            'tone': 'friendly',
            'approach': 'gentle',
            'focus': 'general_conversation'
        },
        'risk_indicators': [],
        'is_emergency_result': True,
        'analysis_timestamp': datetime.now().isoformat(),
        'child_age': age
    } 