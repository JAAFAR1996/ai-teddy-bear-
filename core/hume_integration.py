#!/usr/bin/env python3
"""
🎤 HUME AI Integration Script
نموذجين للتكامل مع HUME AI: Batch و Stream
"""

import os
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from database import db_manager

# تحميل متغيرات البيئة
load_dotenv()

# استيراد مكتبات HUME AI
try:
    from hume import HumeClient, AsyncHumeClient
    HUME_AVAILABLE = True
    print("✅ HUME AI SDK loaded successfully")
except ImportError:
    HUME_AVAILABLE = False
    print("❌ HUME AI SDK not available. Install with: pip install hume")

class HumeIntegration:
    """
    🎭 HUME AI Integration Class
    يدعم نموذجي Batch و Stream للتحليل
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ HUME API Key not found! Set HUME_API_KEY environment variable")
        
        print(f"🔑 HUME API Key loaded: {self.api_key[:8]}...")
        
        # إنشاء العملاء
        if HUME_AVAILABLE:
            self.client = HumeClient(api_key=self.api_key)
            self.async_client = AsyncHumeClient(api_key=self.api_key)
            print("✅ HUME Clients initialized")
        else:
            self.client = None
            self.async_client = None
            print("⚠️ HUME Clients not available")
    
    # ==================== BATCH MODE ====================
    
    def analyze_batch(self, file_paths: List[str], udid: str = "TEST_ESP32", child_name: str = "طفل اختبار", child_age: int = 6) -> Dict[str, Any]:
        """
        🔄 نمط Batch - تحليل ملفات متعددة (HUME v0.9.0) مع حفظ في قاعدة البيانات
        
        Args:
            file_paths: قائمة مسارات الملفات للتحليل
            udid: معرف الجهاز
            child_name: اسم الطفل
            child_age: عمر الطفل
            
        Returns:
            نتائج التحليل المحفوظة في ملف JSON وقاعدة البيانات
        """
        if not HUME_AVAILABLE or not self.client:
            return {"error": "HUME SDK not available"}
        
        # حفظ الجلسة في قاعدة البيانات
        session_record = None
        
        try:
            print("🔄 Starting Batch Analysis...")
            print(f"📁 Files to analyze: {len(file_paths)}")
            
            # التحقق من وجود الملفات
            valid_files = []
            for file_path in file_paths:
                if Path(file_path).exists():
                    valid_files.append(file_path)
                    print(f"  ✅ {file_path}")
                else:
                    print(f"  ❌ File not found: {file_path}")
            
            if not valid_files:
                return {"error": "No valid files found"}
            
            # 💾 حفظ الجلسة في قاعدة البيانات
            session_record = db_manager.save_session(
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                mode="batch",
                audio_file=valid_files[0] if valid_files else None
            )
            
            print("📤 Submitting batch job to HUME...")
            
            # إرسال الملفات للتحليل (واجهة HUME v0.9.0)
            job = self.client.expression_measurement.batch.submit_job(
                urls=valid_files,
                configs=[
                    {"prosody": {}},  # تحليل نبرة الصوت
                    {"face": {}}      # تحليل تعبيرات الوجه
                ]
            )
            
            print(f"📋 Job ID: {job.job_id}")
            print("⏳ Waiting for analysis to complete...")
            
            # انتظار اكتمال التحليل
            job = self.client.expression_measurement.batch.get_job_details(job.job_id)
            
            while job.state not in ["COMPLETED", "FAILED"]:
                print("⏳ Still processing...")
                import time
                time.sleep(5)
                job = self.client.expression_measurement.batch.get_job_details(job.job_id)
            
            if job.state == "FAILED":
                return {
                    "status": "error",
                    "mode": "batch",
                    "error": "HUME job failed"
                }
            
            # تحميل النتائج
            print("📥 Downloading predictions...")
            predictions = self.client.expression_measurement.batch.get_job_predictions(job.job_id)
            
            # استخراج المشاعر وحفظها في قاعدة البيانات
            emotions_data = self._extract_emotions_from_predictions(predictions)
            
            if emotions_data and session_record:
                print("💾 Saving emotions to database...")
                db_manager.save_emotions(session_record.id, emotions_data)
                db_manager.update_session_status(session_record.id, "success")
            
            # حفظ النتائج في ملف
            output_file = "batch_predictions.json"
            with open(output_file, 'w') as f:
                json.dump(predictions, f, indent=2)
            
            print("✅ Batch analysis completed successfully!")
            
            return {
                "status": "success",
                "mode": "batch",
                "session_id": session_record.id if session_record else None,
                "files_analyzed": len(valid_files),
                "output_file": output_file,
                "job_id": job.job_id,
                "emotions_saved": len(emotions_data) if emotions_data else 0,
                "results": predictions
            }
            
        except Exception as e:
            print(f"❌ Batch analysis failed: {e}")
            
            # تحديث حالة الجلسة في قاعدة البيانات
            if session_record:
                db_manager.update_session_status(session_record.id, "error", str(e))
            
            return {
                "status": "error",
                "mode": "batch",
                "session_id": session_record.id if session_record else None,
                "error": str(e)
            }
    
    # ==================== STREAM MODE ====================
    
    async def analyze_stream(self, audio_path: str, udid: str = "TEST_ESP32", child_name: str = "طفل اختبار", child_age: int = 6) -> Dict[str, Any]:
        """
        ⚡ نمط Stream - تحليل فوري لملف واحد (HUME v0.9.0) مع حفظ في قاعدة البيانات
        
        Args:
            audio_path: مسار الملف الصوتي
            udid: معرف الجهاز
            child_name: اسم الطفل
            child_age: عمر الطفل
            
        Returns:
            نتائج التحليل الفوري محفوظة في قاعدة البيانات
        """
        if not HUME_AVAILABLE or not self.async_client:
            return {"error": "HUME SDK not available"}
        
        # حفظ الجلسة في قاعدة البيانات
        session_record = None
        
        try:
            print("⚡ Starting Stream Analysis...")
            print(f"🎵 Audio file: {audio_path}")
            
            # التحقق من وجود الملف
            if not Path(audio_path).exists():
                return {
                    "status": "error",
                    "mode": "stream",
                    "error": f"File not found: {audio_path}"
                }
            
            # 💾 حفظ الجلسة في قاعدة البيانات
            session_record = db_manager.save_session(
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                mode="stream",
                audio_file=audio_path
            )
            
            print("🔗 Connecting to HUME Stream...")
            
            # استخدام واجهة HUME v0.9.0 للـ Stream
            socket = await self.async_client.expression_measurement.stream.connect(
                config={"prosody": {}}  # تحليل نبرة الصوت فقط
            )
            
            print("📤 Sending audio file...")
            
            # قراءة الملف الصوتي وإرساله
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                result = await socket.send_bytes(audio_data)
            
            await socket.close()
            
            # استخراج المشاعر وحفظها في قاعدة البيانات
            emotions_data = self._extract_emotions_from_predictions(result)
            
            if emotions_data and session_record:
                print("💾 Saving emotions to database...")
                db_manager.save_emotions(session_record.id, emotions_data)
                db_manager.update_session_status(session_record.id, "success")
            
            print("✅ Stream analysis completed!")
            
            return {
                "status": "success", 
                "mode": "stream",
                "session_id": session_record.id if session_record else None,
                "file": audio_path,
                "emotions_saved": len(emotions_data) if emotions_data else 0,
                "results": result
            }
                
        except Exception as e:
            print(f"❌ Stream analysis failed: {e}")
            
            # تحديث حالة الجلسة في قاعدة البيانات
            if session_record:
                db_manager.update_session_status(session_record.id, "error", str(e))
            
            return {
                "status": "error",
                "mode": "stream",
                "session_id": session_record.id if session_record else None,
                "error": str(e)
            }
    
    # ==================== HELPER METHODS ====================
    
    def _extract_emotions_from_predictions(self, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🎭 استخراج المشاعر من نتائج HUME لحفظها في قاعدة البيانات
        
        Args:
            predictions: نتائج HUME AI
            
        Returns:
            قائمة المشاعر بصيغة [{"name": "Joy", "score": 0.85, "confidence": 0.92}, ...]
        """
        emotions_data = []
        
        try:
            # التعامل مع نتائج Batch
            if isinstance(predictions, list) and predictions:
                # أخذ أول ملف كمثال
                first_file = predictions[0]
                
                if "models" in first_file and "prosody" in first_file["models"]:
                    prosody = first_file["models"]["prosody"]
                    
                    if "grouped_predictions" in prosody and prosody["grouped_predictions"]:
                        grouped = prosody["grouped_predictions"][0]
                        
                        if "predictions" in grouped:
                            for prediction in grouped["predictions"]:
                                emotion_data = {
                                    "name": prediction.get("name", "unknown"),
                                    "score": float(prediction.get("score", 0.0)),
                                    "confidence": float(prediction.get("confidence", 0.0)) if prediction.get("confidence") else None
                                }
                                emotions_data.append(emotion_data)
                                
            # التعامل مع نتائج Stream 
            elif isinstance(predictions, dict):
                if "prosody" in predictions:
                    prosody_data = predictions["prosody"]
                    
                    if "predictions" in prosody_data:
                        for prediction in prosody_data["predictions"]:
                            emotion_data = {
                                "name": prediction.get("name", "unknown"),
                                "score": float(prediction.get("score", 0.0)),
                                "confidence": float(prediction.get("confidence", 0.0)) if prediction.get("confidence") else None
                            }
                            emotions_data.append(emotion_data)
            
            print(f"🎭 Extracted {len(emotions_data)} emotions from predictions")
            
        except Exception as e:
            print(f"❌ Error extracting emotions: {e}")
            
        return emotions_data
    
    def extract_emotions_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 استخراج ملخص المشاعر من النتائج
        """
        try:
            if results.get("mode") == "stream":
                # معالجة نتائج Stream
                stream_results = results.get("results", {})
                
                if "prosody" in stream_results:
                    prosody_data = stream_results["prosody"]
                    emotions = {}
                    
                    for prediction in prosody_data.get("predictions", []):
                        emotion_name = prediction.get("name", "unknown")
                        emotion_score = prediction.get("score", 0.0)
                        emotions[emotion_name] = emotion_score
                    
                    # ترتيب المشاعر حسب القوة
                    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                    
                    return {
                        "dominant_emotion": sorted_emotions[0] if sorted_emotions else ("neutral", 0.0),
                        "all_emotions": emotions,
                        "top_3_emotions": sorted_emotions[:3]
                    }
            
            elif results.get("mode") == "batch":
                # معالجة نتائج Batch (أكثر تعقيداً)
                batch_results = results.get("results", [])
                
                if batch_results:
                    # أخذ أول ملف كمثال
                    first_file = batch_results[0]
                    
                    if "models" in first_file:
                        models = first_file["models"]
                        
                        summary = {
                            "files_count": len(batch_results),
                            "analysis_types": list(models.keys())
                        }
                        
                        # استخراج بيانات Prosody إن وجدت
                        if "prosody" in models:
                            prosody = models["prosody"]
                            if "grouped_predictions" in prosody:
                                grouped = prosody["grouped_predictions"]
                                if grouped:
                                    predictions = grouped[0].get("predictions", [])
                                    emotions = {p["name"]: p["score"] for p in predictions}
                                    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                                    
                                    summary.update({
                                        "dominant_emotion": sorted_emotions[0] if sorted_emotions else ("neutral", 0.0),
                                        "all_emotions": emotions,
                                        "top_3_emotions": sorted_emotions[:3]
                                    })
                        
                        return summary
            
            return {"error": "Could not extract emotion summary"}
            
        except Exception as e:
            return {"error": f"Summary extraction failed: {e}"}
    
    def create_sample_files(self):
        """
        🎵 إنشاء ملفات تجريبية للاختبار
        """
        try:
            import numpy as np
            import soundfile as sf
            
            print("🎵 Creating sample audio files...")
            
            # إنشاء نغمات مختلفة
            sample_rate = 16000
            duration = 3
            
            samples = [
                ("sample_happy.wav", 440),    # نغمة سعيدة
                ("sample_sad.wav", 220),      # نغمة حزينة
                ("sample_excited.wav", 660)   # نغمة متحمسة
            ]
            
            created_files = []
            
            for filename, frequency in samples:
                t = np.linspace(0, duration, sample_rate * duration)
                # إنشاء نغمة مع تعديل للمحاكاة
                audio = 0.3 * np.sin(2 * np.pi * frequency * t)
                
                # إضافة بعض التشويش لجعلها أكثر واقعية
                noise = 0.05 * np.random.random(len(audio))
                audio = audio + noise
                
                sf.write(filename, audio, sample_rate)
                created_files.append(filename)
                print(f"  ✅ Created: {filename}")
            
            return created_files
            
        except Exception as e:
            print(f"❌ Failed to create sample files: {e}")
            return []


# ==================== TESTING FUNCTIONS ====================

async def test_stream_mode():
    """
    🧪 اختبار نمط Stream
    """
    print("\n" + "="*50)
    print("🧪 TESTING STREAM MODE")
    print("="*50)
    
    try:
        hume = HumeIntegration()
        
        # إنشاء ملف تجريبي
        sample_files = hume.create_sample_files()
        
        if sample_files:
            audio_file = sample_files[0]  # أخذ أول ملف
            
            # تحليل Stream
            result = await hume.analyze_stream(audio_file)
            
            print(f"\n📊 Stream Results:")
            print(f"Status: {result.get('status')}")
            
            if result.get('status') == 'success':
                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                print(f"\n🎭 Emotions Summary:")
                print(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                print(f"Error: {result.get('error')}")
            
            return result
        else:
            print("❌ No sample files available for testing")
            
    except Exception as e:
        print(f"❌ Stream test failed: {e}")

def test_batch_mode():
    """
    🧪 اختبار نمط Batch
    """
    print("\n" + "="*50)
    print("🧪 TESTING BATCH MODE")
    print("="*50)
    
    try:
        hume = HumeIntegration()
        
        # إنشاء ملفات تجريبية
        sample_files = hume.create_sample_files()
        
        if sample_files:
            # تحليل Batch
            result = hume.analyze_batch(sample_files)
            
            print(f"\n📊 Batch Results:")
            print(f"Status: {result.get('status')}")
            print(f"Files analyzed: {result.get('files_analyzed')}")
            
            if result.get('status') == 'success':
                print(f"Output file: {result.get('output_file')}")
                
                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                print(f"\n🎭 Emotions Summary:")
                print(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                print(f"Error: {result.get('error')}")
            
            return result
        else:
            print("❌ No sample files available for testing")
            
    except Exception as e:
        print(f"❌ Batch test failed: {e}")

async def run_all_tests():
    """
    🧪 تشغيل جميع الاختبارات
    """
    print("🎤 HUME AI Integration Testing")
    print("="*60)
    
    # التحقق من API Key
    api_key = os.getenv("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not set!")
        print("💡 Set it with: export HUME_API_KEY='xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q'")
        return
    
    print(f"🔑 API Key: {api_key[:8]}...")
    
    # اختبار Stream Mode
    await test_stream_mode()
    
    # اختبار Batch Mode
    test_batch_mode()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("📁 Check 'batch_predictions.json' for detailed results")

if __name__ == "__main__":
    # تعيين API Key إذا لم يكن موجوداً
    if not os.getenv("HUME_API_KEY"):
        os.environ["HUME_API_KEY"] = "xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q"
    
    # تشغيل الاختبارات
    asyncio.run(run_all_tests()) 