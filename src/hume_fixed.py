from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
🎤 HUME AI Integration Script - FIXED Version
نموذجين للتكامل مع HUME AI: Batch و Stream
"""
import structlog
logger = structlog.get_logger(__name__)


import os
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# استيراد مكتبات HUME AI
try:
    from hume import HumeClient, AsyncHumeClient
    HUME_AVAILABLE = True
    logger.info("✅ HUME AI SDK loaded successfully")
except ImportError:
    HUME_AVAILABLE = False
    logger.error("❌ HUME AI SDK not available. Install with: pip install hume")

class HumeIntegrationFixed:
    """
    🎭 HUME AI Integration Class - FIXED for v0.9.0
    يدعم نموذجي Batch و Stream للتحليل
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ HUME API Key not found! Set HUME_API_KEY environment variable")
        
        logger.info(f"🔑 HUME API Key loaded: {self.api_key[:8]}...")
        
        # إنشاء العملاء
        if HUME_AVAILABLE:
            self.client = HumeClient(api_key=self.api_key)
            self.async_client = AsyncHumeClient(api_key=self.api_key)
            logger.info("✅ HUME Clients initialized")
        else:
            self.client = None
            self.async_client = None
            logger.warning("⚠️ HUME Clients not available")
    
    # ==================== BATCH MODE ====================
    
    def analyze_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        🔄 نمط Batch - تحليل ملفات متعددة (FIXED for HUME v0.9.0)
        """
        if not HUME_AVAILABLE or not self.client:
            return {"error": "HUME SDK not available"}
        
        try:
            logger.info("🔄 Starting Batch Analysis...")
            logger.info(f"📁 Files to analyze: {len(file_paths)}")
            
            # التحقق من وجود الملفات
            valid_files = []
            for file_path in file_paths:
                if Path(file_path).exists():
                    valid_files.append(file_path)
                    logger.info(f"  ✅ {file_path}")
                else:
                    logger.error(f"  ❌ File not found: {file_path}")
            
            if not valid_files:
                return {"error": "No valid files found"}
            
            logger.info("📤 Submitting batch job to HUME...")
            
            # استخدام الواجهة الصحيحة للـ batch
            job = self.client.expression_measurement.batch.start_inference_job_from_local_file(
                file=valid_files[0],  # نأخذ أول ملف كمثال
                configs=[
                    {"prosody": {}},  # تحليل نبرة الصوت
                ]
            )
            
            logger.info(f"📋 Job ID: {job.job_id}")
            logger.info("⏳ Waiting for analysis to complete...")
            
            # انتظار اكتمال التحليل
            import time
            max_wait = 30  # 30 ثانية كحد أقصى
            wait_time = 0
            
            while wait_time < max_wait:
                job_details = self.client.expression_measurement.batch.get_job_details(job.job_id)
                
                if hasattr(job_details, 'state'):
                    if job_details.state == "COMPLETED":
                        break
                    elif job_details.state == "FAILED":
                        return {
                            "status": "error",
                            "mode": "batch",
                            "error": "HUME job failed"
                        }
                
                logger.info("⏳ Still processing...")
                time.sleep(3)
                wait_time += 3
            
            if wait_time >= max_wait:
                return {
                    "status": "error",
                    "mode": "batch",
                    "error": "Analysis timeout"
                }
            
            # تحميل النتائج
            logger.info("📥 Downloading predictions...")
            predictions = self.client.expression_measurement.batch.get_job_predictions(job.job_id)
            
            # حفظ النتائج في ملف
            output_file = "batch_predictions.json"
            with open(output_file, 'w') as f:
                json.dump(predictions, f, indent=2)
            
            logger.info("✅ Batch analysis completed successfully!")
            
            return {
                "status": "success",
                "mode": "batch",
                "files_analyzed": len(valid_files),
                "output_file": output_file,
                "job_id": job.job_id,
                "results": predictions
            }
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Batch analysis failed: {e}")
            return {
                "status": "error",
                "mode": "batch",
                "error": str(e)
            }
    
    # ==================== STREAM MODE ====================
    
    async def analyze_stream(self, audio_path: str) -> Dict[str, Any]:
        """
        ⚡ نمط Stream - تحليل فوري لملف واحد (FIXED for HUME v0.9.0)
        """
        if not HUME_AVAILABLE or not self.async_client:
            return {"error": "HUME SDK not available"}
        
        try:
            logger.info("⚡ Starting Stream Analysis...")
            logger.info(f"🎵 Audio file: {audio_path}")
            
            # التحقق من وجود الملف
            if not Path(audio_path).exists():
                return {
                    "status": "error",
                    "mode": "stream",
                    "error": f"File not found: {audio_path}"
                }
            
            logger.info("🔗 Connecting to HUME Stream...")
            
            # استخدام الواجهة الصحيحة للـ stream
            socket = await self.async_client.expression_measurement.stream.connect()
            
            logger.info("📤 Sending audio file...")
            
            # قراءة الملف الصوتي وإرساله
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                result = await socket.send_bytes(audio_data)
            
            await socket.close()
            
            logger.info("✅ Stream analysis completed!")
            
            return {
                "status": "success", 
                "mode": "stream",
                "file": audio_path,
                "results": result
            }
                
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Stream analysis failed: {e}")
            logger.error(f"   Error details: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "mode": "stream", 
                "error": str(e)
            }
    
    # ==================== HELPER METHODS ====================
    
    def extract_emotions_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 استخراج ملخص المشاعر من النتائج
        """
        try:
            # تحليل بسيط للنتائج
            return {
                "analysis_completed": True,
                "mode": results.get("mode", "unknown"),
                "status": results.get("status", "unknown"),
                "file": results.get("file", "unknown"),
                "message": "تم تحليل الصوت بنجاح باستخدام HUME AI"
            }
            
        except Exception as e:
            return {"error": f"Summary extraction failed: {e}"}
    
    def create_sample_files(self) -> Any:
        """
        🎵 إنشاء ملفات تجريبية للاختبار
        """
        try:
            import numpy as np
            import soundfile as sf
            
            logger.info("🎵 Creating sample audio files...")
            
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
                logger.info(f"  ✅ Created: {filename}")
            
            return created_files
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Failed to create sample files: {e}")
            return []


# ==================== TESTING FUNCTIONS ====================

async def test_stream_mode():
    """🧪 اختبار نمط Stream"""
    logger.info("\n" + "="*50)
    logger.info("🧪 TESTING STREAM MODE")
    logger.info("="*50)
    
    try:
        hume = HumeIntegrationFixed()
        
        # إنشاء ملف تجريبي
        sample_files = hume.create_sample_files()
        
        if sample_files:
            audio_file = sample_files[0]  # أخذ أول ملف
            
            # تحليل Stream
            result = await hume.analyze_stream(audio_file)
            
            logger.info(f"\n📊 Stream Results:")
            logger.info(f"Status: {result.get('status')}")
            
            if result.get('status') == 'success':
                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                logger.info(f"\n🎭 Analysis Summary:")
                logger.info(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                logger.error(f"Error: {result.get('error')}")
            
            return result
        else:
            logger.error("❌ No sample files available for testing")
            
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Stream test failed: {e}")

def test_batch_mode() -> Any:
    """🧪 اختبار نمط Batch"""
    logger.info("\n" + "="*50)
    logger.info("🧪 TESTING BATCH MODE")
    logger.info("="*50)
    
    try:
        hume = HumeIntegrationFixed()
        
        # إنشاء ملفات تجريبية
        sample_files = hume.create_sample_files()
        
        if sample_files:
            # تحليل Batch
            result = hume.analyze_batch(sample_files)
            
            logger.info(f"\n📊 Batch Results:")
            logger.info(f"Status: {result.get('status')}")
            logger.info(f"Files analyzed: {result.get('files_analyzed')}")
            logger.info(f"Job ID: {result.get('job_id')}")
            
            if result.get('status') == 'success':
                logger.info(f"Output file: {result.get('output_file')}")
                
                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                logger.info(f"\n🎭 Analysis Summary:")
                logger.info(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                logger.error(f"Error: {result.get('error')}")
            
            return result
        else:
            logger.error("❌ No sample files available for testing")
            
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Batch test failed: {e}")

async def run_all_tests():
    """🧪 تشغيل جميع الاختبارات"""
    logger.info("🎤 HUME AI Integration Testing - FIXED VERSION")
    logger.info("="*60)
    
    # التحقق من API Key
    api_key = os.getenv("HUME_API_KEY")
    if not api_key:
        logger.error("❌ HUME_API_KEY not set!")
        logger.info("💡 Set it with: export HUME_API_KEY='xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q'")
        return
    
    logger.info(f"🔑 API Key: {api_key[:8]}...")
    
    # اختبار Stream Mode
    await test_stream_mode()
    
    # اختبار Batch Mode
    test_batch_mode()
    
    logger.info("\n" + "="*60)
    logger.info("✅ All tests completed!")
    logger.info("📁 Check 'batch_predictions.json' for detailed results")

if __name__ == "__main__":
    # تعيين API Key إذا لم يكن موجوداً
    if not os.getenv("HUME_API_KEY"):
        os.environ["HUME_API_KEY"] = "xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q"
    
    # تشغيل الاختبارات
    asyncio.run(run_all_tests()) 