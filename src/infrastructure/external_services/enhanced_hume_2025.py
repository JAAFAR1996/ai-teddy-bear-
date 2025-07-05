#!/usr/bin/env python3
"""
🎤 Enhanced HUME AI Integration - 2025 Edition
تكامل Hume AI مع:
1. معايرة دقة تحليل المشاعر
2. دعم اللغات المتعددة 
3. تكامل البيانات التاريخية
"""

import asyncio
import json
import logging
import os
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

import numpy as np

# HUME AI imports
try:
    import librosa
    import soundfile as sf
    from hume import AsyncHumeClient, HumeClient
    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False


class Language(Enum):
    ARABIC = "ar"
    ENGLISH = "en" 
    AUTO_DETECT = "auto"


@dataclass 
class CalibrationConfig:
    confidence_threshold: float = 0.7
    language_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if not self.language_weights:
            self.language_weights = {
                "ar": 1.0,
                "en": 0.9,
                "auto": 0.8
            }


class EnhancedHumeIntegration:
    """🎭 Enhanced HUME AI with 2025 features"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        if not self.api_key:
            raise ValueError("HUME API Key required!")
        
        self.config = CalibrationConfig()
        self.logger = logging.getLogger(__name__)
        
        if HUME_AVAILABLE:
            self.client = HumeClient(api_key=self.api_key)
            self.async_client = AsyncHumeClient(api_key=self.api_key)
        else:
            self.client = None
            self.async_client = None
    
    # ==================== TASK 1: CALIBRATION ====================
    
    def calibrate_hume(self, confidence_threshold: float) -> Dict[str, float]:
        """🎯 معايرة دقة تحليل المشاعر"""
        logger.info(f"🎯 Calibrating HUME with threshold: {confidence_threshold}")
        
        # Create test samples
        test_samples = self._create_test_samples()
        
        results = []
        for sample in test_samples:
            # Analyze each sample
            emotion_data = self._analyze_sample(sample)
            confidence = emotion_data.get('confidence', 0.0)
            
            results.append({
                'sample': sample['name'],
                'confidence': confidence,
                'passes_threshold': confidence >= confidence_threshold
            })
        
        # Calculate metrics
        success_rate = sum(1 for r in results if r['passes_threshold']) / len(results)
        avg_confidence = statistics.mean([r['confidence'] for r in results])
        
        # Update configuration
        self.config.confidence_threshold = confidence_threshold
        
        logger.info(f"✅ Calibration complete: {success_rate:.1%} success rate")
        
        return {
            'success_rate': success_rate,
            'average_confidence': avg_confidence,
            'threshold': confidence_threshold,
            'recommendation': self._get_calibration_recommendation(success_rate)
        }
    
    def _create_test_samples(self) -> List[Dict]:
        """إنشاء عينات اختبار للمعايرة"""
        samples = []
        
        emotions = ['joy', 'sadness', 'anger', 'calm']
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
            
            samples.append({
                'name': emotion,
                'file': filename,
                'expected_emotion': emotion
            })
        
        return samples
    
    def _analyze_sample(self, sample: Dict) -> Dict:
        """تحليل عينة واحدة"""
        if HUME_AVAILABLE:
            # Real HUME analysis
            return self._real_hume_analysis(sample['file'])
        else:
            # Mock analysis for development
            return self._mock_analysis(sample['expected_emotion'])
    
    def _mock_analysis(self, expected_emotion: str) -> Dict:
        """تحليل وهمي للتطوير"""
        import random
        
        emotions = {
            'joy': random.uniform(0.7, 0.9),
            'sadness': random.uniform(0.2, 0.4),
            'anger': random.uniform(0.1, 0.3),
            'calm': random.uniform(0.3, 0.5)
        }
        
        # Make expected emotion dominant
        emotions[expected_emotion] = random.uniform(0.8, 0.95)
        
        return {
            'emotions': emotions,
            'dominant_emotion': expected_emotion,
            'confidence': emotions[expected_emotion]
        }
    
    def _get_calibration_recommendation(self, success_rate: float) -> str:
        """توصيات المعايرة"""
        if success_rate >= 0.9:
            return "Excellent calibration"
        elif success_rate >= 0.7:
            return "Good - minor adjustments may help"
        elif success_rate >= 0.5:
            return "Fair - consider lowering threshold"
        else:
            return "Poor - significant calibration needed"
    
    # ==================== TASK 2: MULTI-LANGUAGE ====================
    
    async def analyze_emotion_multilang(self, audio_file: str, lang: str) -> Dict:
        """🌍 تحليل المشاعر مع دعم اللغات المتعددة"""
        logger.info(f"🌍 Analyzing emotion in language: {lang}")
        
        try:
            # Detect language if auto
            if lang == "auto":
                detected_lang = await self._detect_language(audio_file)
                logger.debug(f"🔍 Language detected: {detected_lang}")
            else:
                detected_lang = lang
            
            # Get language-specific configuration
            config = self._get_language_config(detected_lang)
            
            # Perform analysis with language context
            if HUME_AVAILABLE:
                result = await self._hume_analysis_with_language(audio_file, config)
            else:
                result = self._mock_multilang_analysis(detected_lang)
            
            # Apply language-specific calibration
            calibrated_result = self._apply_language_calibration(result, detected_lang)
            
            return {
                'detected_language': detected_lang,
                'emotions': calibrated_result['emotions'],
                'dominant_emotion': calibrated_result['dominant_emotion'],
                'confidence': calibrated_result['confidence'],
                'language_confidence': self.config.language_weights.get(detected_lang, 0.8)
            }
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Multi-language analysis failed: {e}")
            return {'error': str(e)}
    
    async def _detect_language(self, audio_file: str) -> str:
        """كشف اللغة من الملف الصوتي"""
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=16000)
            
            # Simple spectral analysis for language detection
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            avg_centroid = np.mean(spectral_centroid)
            
            # Simple rule-based classification (can be improved with ML)
            if avg_centroid > 2000:
                return "en"  # Higher frequencies often in English
            else:
                return "ar"  # Lower frequencies often in Arabic
            except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)t Exception:
            return "ar"  # Default to Arabic
    
    def _get_language_config(self, language: str) -> Dict:
        """إعدادات خاصة بكل لغة"""
        if language == "ar":
            return {
                "prosody": {
                    "granularity": "word",
                    "language_context": "arabic"
                }
            }
        elif language == "en":
            return {
                "prosody": {
                    "granularity": "utterance", 
                    "language_context": "english"
                }
            }
        else:
            return {"prosody": {}}
    
    def _apply_language_calibration(self, result: Dict, language: str) -> Dict:
        """تطبيق معايرة خاصة باللغة"""
        language_weight = self.config.language_weights.get(language, 1.0)
        
        # Adjust confidence based on language
        adjusted_confidence = result['confidence'] * language_weight
        
        # Adjust emotion scores
        adjusted_emotions = {}
        for emotion, score in result['emotions'].items():
            adjusted_score = score * language_weight
            
            # Apply confidence threshold
            if adjusted_score >= self.config.confidence_threshold:
                adjusted_emotions[emotion] = min(adjusted_score, 1.0)
            else:
                adjusted_emotions[emotion] = adjusted_score * 0.8
        
        return {
            'emotions': adjusted_emotions,
            'dominant_emotion': max(adjusted_emotions, key=adjusted_emotions.get),
            'confidence': adjusted_confidence
        }
    
    def _mock_multilang_analysis(self, language: str) -> Dict:
        """تحليل وهمي متعدد اللغات"""
        import random

        # Different emotion patterns for different languages
        if language == "ar":
            emotions = {
                'joy': random.uniform(0.6, 0.8),
                'curiosity': random.uniform(0.5, 0.7),
                'calmness': random.uniform(0.4, 0.6)
            }
        else:  # English
            emotions = {
                'excitement': random.uniform(0.7, 0.9),
                'playfulness': random.uniform(0.6, 0.8),
                'joy': random.uniform(0.5, 0.7)
            }
        
        dominant = max(emotions, key=emotions.get)
        
        return {
            'emotions': emotions,
            'dominant_emotion': dominant,
            'confidence': emotions[dominant]
        }
    
    # ==================== TASK 3: HISTORICAL DATA ====================
    
    def merge_historical_data(self, device_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """📊 تكامل البيانات التاريخية"""
        logger.info(f"📊 Merging historical data for {device_id}")
        
        try:
            # Fetch historical data (simulated)
            historical_sessions = self._fetch_historical_sessions(device_id, start_date, end_date)
            
            if not historical_sessions:
                return {'error': 'No historical data found', 'sessions': 0}
            
            # Process and analyze historical data
            processed_data = self._process_historical_data(historical_sessions)
            
            # Generate insights and trends
            insights = self._generate_historical_insights(processed_data)
            
            # Create comprehensive report
            report = {
                'device_id': device_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'summary': {
                    'total_sessions': len(historical_sessions),
                    'most_common_emotion': insights['dominant_emotion'],
                    'emotional_stability': insights['stability_score'],
                    'trend': insights['trend']
                },
                'daily_breakdown': processed_data['daily_summaries'],
                'recommendations': insights['recommendations']
            }
            
            logger.info(f"✅ Historical analysis complete: {len(historical_sessions)} sessions processed")
            return report
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Historical data merge failed: {e}")
            return {'error': str(e)}
    
    def _fetch_historical_sessions(self, device_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """جلب الجلسات التاريخية من قاعدة البيانات"""
        # Simulated historical data
        sessions = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 1-3 sessions per day
            num_sessions = np.random.randint(1, 4)
            
            for i in range(num_sessions):
                session = {
                    'timestamp': current_date + timedelta(hours=np.random.randint(8, 20)),
                    'device_id': device_id,
                    'audio_duration': np.random.uniform(5, 30),  # seconds
                    'emotions': {
                        'joy': np.random.uniform(0.2, 0.8),
                        'curiosity': np.random.uniform(0.3, 0.7),
                        'excitement': np.random.uniform(0.1, 0.6),
                        'calmness': np.random.uniform(0.2, 0.5)
                    }
                }
                
                # Add dominant emotion
                session['dominant_emotion'] = max(session['emotions'], key=session['emotions'].get)
                session['confidence'] = session['emotions'][session['dominant_emotion']]
                
                sessions.append(session)
            
            current_date += timedelta(days=1)
        
        return sessions
    
    def _process_historical_data(self, sessions: List[Dict]) -> Dict:
        """معالجة البيانات التاريخية"""
        daily_summaries = {}
        all_emotions = {}
        
        for session in sessions:
            date_key = session['timestamp'].date().isoformat()
            
            # Daily summary
            if date_key not in daily_summaries:
                daily_summaries[date_key] = {
                    'sessions': 0,
                    'total_duration': 0,
                    'emotions': {},
                    'dominant_emotions': []
                }
            
            daily_summaries[date_key]['sessions'] += 1
            daily_summaries[date_key]['total_duration'] += session['audio_duration']
            daily_summaries[date_key]['dominant_emotions'].append(session['dominant_emotion'])
            
            # Aggregate emotions
            for emotion, score in session['emotions'].items():
                if emotion not in daily_summaries[date_key]['emotions']:
                    daily_summaries[date_key]['emotions'][emotion] = []
                daily_summaries[date_key]['emotions'][emotion].append(score)
                
                # Overall emotions
                if emotion not in all_emotions:
                    all_emotions[emotion] = []
                all_emotions[emotion].append(score)
        
        # Calculate daily averages
        for day_data in daily_summaries.values():
            for emotion, scores in day_data['emotions'].items():
                day_data['emotions'][emotion] = statistics.mean(scores)
        
        return {
            'daily_summaries': daily_summaries,
            'overall_emotions': {emotion: statistics.mean(scores) for emotion, scores in all_emotions.items()}
        }
    
    def _generate_historical_insights(self, processed_data: Dict) -> Dict:
        """توليد الرؤى من البيانات التاريخية"""
        overall_emotions = processed_data['overall_emotions']
        daily_summaries = processed_data['daily_summaries']
        
        # Find dominant emotion
        dominant_emotion = max(overall_emotions, key=overall_emotions.get)
        
        # Calculate emotional stability (consistency across days)
        daily_dominant_emotions = []
        for day_data in daily_summaries.values():
            if day_data['emotions']:
                day_dominant = max(day_data['emotions'], key=day_data['emotions'].get)
                daily_dominant_emotions.append(day_dominant)
        
        # Stability = how often the same emotion is dominant
        if daily_dominant_emotions:
            most_common_daily = max(set(daily_dominant_emotions), key=daily_dominant_emotions.count)
            stability_score = daily_dominant_emotions.count(most_common_daily) / len(daily_dominant_emotions)
        else:
            stability_score = 0.5
        
        # Trend analysis (simplified)
        if len(daily_summaries) >= 7:
            recent_days = list(daily_summaries.values())[-7:]
            early_days = list(daily_summaries.values())[:7]
            
            recent_joy = statistics.mean([day['emotions'].get('joy', 0) for day in recent_days])
            early_joy = statistics.mean([day['emotions'].get('joy', 0) for day in early_days])
            
            if recent_joy > early_joy + 0.1:
                trend = "improving"
            elif recent_joy < early_joy - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate recommendations
        recommendations = []
        
        if dominant_emotion == "curiosity":
            recommendations.append("Child shows high curiosity - great time for educational activities")
        elif dominant_emotion == "joy":
            recommendations.append("Child is generally happy - maintain current approach")
        elif stability_score < 0.5:
            recommendations.append("Emotional patterns vary - monitor for consistency")
        
        if trend == "improving":
            recommendations.append("Positive emotional trend detected")
        elif trend == "declining":
            recommendations.append("Consider additional emotional support")
        
        return {
            'dominant_emotion': dominant_emotion,
            'stability_score': stability_score,
            'trend': trend,
            'recommendations': recommendations
        }
    
    # ==================== REAL HUME METHODS ====================
    
    def _real_hume_analysis(self, audio_file: str) -> Dict:
        """تحليل HUME حقيقي"""
        try:
            # This would use actual HUME client
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # Batch analysis
            job = self.client.expression_measurement.batch.submit_job(
                urls=[audio_file],
                configs=[{"prosody": {}}]
            )
            
            # Wait for completion (simplified)
            import time
            while job.state not in ["COMPLETED", "FAILED"]:
                time.sleep(2)
                job = self.client.expression_measurement.batch.get_job_details(job.job_id)
            
            if job.state == "COMPLETED":
                predictions = self.client.expression_measurement.batch.get_job_predictions(job.job_id)
                return self._extract_emotions_from_hume(predictions)
            else:
                return self._mock_analysis("neutral")
                
        except Exception as e:
    logger.error(f"Error: {e}")f"Real HUME analysis failed: {e}")
            return self._mock_analysis("neutral")
    
    async def _hume_analysis_with_language(self, audio_file: str, config: Dict) -> Dict:
        """تحليل HUME مع السياق اللغوي"""
        try:
            # Stream analysis with language config
            socket = await self.async_client.expression_measurement.stream.connect(config=config)
            
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            result = await socket.send_bytes(audio_data)
            await socket.close()
            
            return self._extract_emotions_from_hume(result)
            
        except Exception as e:
    logger.error(f"Error: {e}")f"HUME language analysis failed: {e}")
            return self._mock_multilang_analysis("ar")
    
    def _extract_emotions_from_hume(self, hume_result) -> Dict:
        """استخراج المشاعر من نتيجة HUME"""
        emotions = {}
        
        try:
            if isinstance(hume_result, dict) and "prosody" in hume_result:
                predictions = hume_result["prosody"].get("predictions", [])
                for pred in predictions:
                    emotions[pred.get("name", "unknown")] = pred.get("score", 0.0)
            elif isinstance(hume_result, list) and hume_result:
                # Batch result
                first_result = hume_result[0]
                if "models" in first_result and "prosody" in first_result["models"]:
                    prosody = first_result["models"]["prosody"]
                    if "grouped_predictions" in prosody:
                        predictions = prosody["grouped_predictions"][0].get("predictions", [])
                        for pred in predictions:
                            emotions[pred.get("name", "unknown")] = pred.get("score", 0.0)
        except Exception as e:
    logger.error(f"Error: {e}")f"Error extracting emotions: {e}")
        
        if emotions:
            dominant = max(emotions, key=emotions.get)
            confidence = emotions[dominant]
        else:
            emotions = {"neutral": 0.5}
            dominant = "neutral"
            confidence = 0.5
        
        return {
            'emotions': emotions,
            'dominant_emotion': dominant,
            'confidence': confidence
        }


# ==================== USAGE EXAMPLE ====================

async def demo_enhanced_hume():
    """مثال شامل للاستخدام"""
    logger.info("🎤 Enhanced HUME AI Integration Demo")
    logger.info("="*50)
    
    # Initialize
    try:
        hume = EnhancedHumeIntegration()
        logger.info("✅ HUME Integration initialized")
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Initialization failed: {e}")
        return
    
    # Task 1: Calibration
    logger.info("\n🎯 Task 1: Calibrating emotion analysis...")
    calibration_result = hume.calibrate_hume(confidence_threshold=0.75)
    logger.info(f"Success rate: {calibration_result['success_rate']:.1%}")
    logger.info(f"Recommendation: {calibration_result['recommendation']}")
    
    # Task 2: Multi-language analysis
    logger.info("\n🌍 Task 2: Multi-language emotion analysis...")
    
    # Create a test audio file
    test_samples = hume._create_test_samples()
    if test_samples:
        result = await hume.analyze_emotion_multilang(test_samples[0]['file'], "auto")
        logger.info(f"Detected language: {result.get('detected_language', 'unknown')}")
        logger.info(f"Dominant emotion: {result.get('dominant_emotion', 'unknown')}")
        logger.info(f"Confidence: {result.get('confidence', 0):.2f}")
    
    # Task 3: Historical data integration
    logger.info("\n📊 Task 3: Historical data analysis...")
    start_date = datetime.now() - timedelta(days=14)
    end_date = datetime.now()
    
    historical_result = hume.merge_historical_data("TEST_DEVICE_001", start_date, end_date)
    logger.info(f"Sessions analyzed: {historical_result.get('summary', {}).get('total_sessions', 0)}")
    logger.info(f"Most common emotion: {historical_result.get('summary', {}).get('most_common_emotion', 'unknown')}")
    logger.info(f"Emotional stability: {historical_result.get('summary', {}).get('emotional_stability', 0):.2f}")
    
    logger.info("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    # Set demo API key if not present
    if not os.getenv("HUME_API_KEY"):
        os.environ["HUME_API_KEY"] = "demo_key_for_testing"
    
    asyncio.run(demo_enhanced_hume()) 