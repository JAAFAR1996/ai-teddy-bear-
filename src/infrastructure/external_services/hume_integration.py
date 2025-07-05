from dotenv import load_dotenv
from database import db_manager
from pathlib import Path
import os
import json
import asyncio
import structlog
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
🎤 HUME AI Integration Script
نموذجين للتكامل مع HUME AI: Batch و Stream
"""

logger = structlog.get_logger(__name__)


# تحميل متغيرات البيئة
load_dotenv()

# استيراد مكتبات HUME AI
try:
    from hume import AsyncHumeClient, HumeClient

    HUME_AVAILABLE = True
    logger.info("✅ HUME AI SDK loaded successfully")
except ImportError:
    HUME_AVAILABLE = False
    logger.error("❌ HUME AI SDK not available. Install with: pip install hume")


class HumeIntegration:
    """
    🎭 HUME AI Integration Class
    يدعم نموذجي Batch و Stream للتحليل
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUME_API_KEY")

        if not self.api_key:
            raise ValueError(
                "❌ HUME API Key not found! Set HUME_API_KEY environment variable"
            )

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

    def _validate_file_paths(self, file_paths: List[str]) -> List[str]:
        """Validates a list of file paths, returning only the existing ones."""
        valid_files = []
        for file_path in file_paths:
            if Path(file_path).exists():
                valid_files.append(file_path)
                self.logger.info(f"  ✅ {file_path}")
            else:
                self.logger.error(f"  ❌ File not found: {file_path}")
        return valid_files

    def _submit_and_wait_for_job(self, valid_files: List[str]) -> Dict:
        """Submits a job to the Hume API and waits for it to complete."""
        self.logger.info("📤 Submitting batch job to HUME...")
        job = self.client.expression_measurement.batch.submit_job(
            urls=valid_files, configs=[{"prosody": {}}, {"face": {}}]
        )
        self.logger.info(f"📋 Job ID: {job.job_id}")
        self.logger.info("⏳ Waiting for analysis to complete...")

        job = self.client.expression_measurement.batch.get_job_details(
            job.job_id)
        while job.state not in ["COMPLETED", "FAILED"]:
            self.logger.info("⏳ Still processing...")
            import time

            time.sleep(5)
            job = self.client.expression_measurement.batch.get_job_details(
                job.job_id)

        return job

    def _process_job_results(self, job: Any, session_record: Any) -> Dict:
        """Processes the results of a completed Hume job."""
        if job.state == "FAILED":
            return {
                "status": "error",
                "mode": "batch",
                "error": "HUME job failed"}

        self.logger.info("📥 Downloading predictions...")
        predictions = self.client.expression_measurement.batch.get_job_predictions(
            job.job_id)

        emotions_data = self._extract_emotions_from_predictions(predictions)
        if emotions_data and session_record:
            self.logger.info("💾 Saving emotions to database...")
            db_manager.save_emotions(session_record.id, emotions_data)
            db_manager.update_session_status(session_record.id, "success")

        output_file = "batch_predictions.json"
        with open(output_file, "w") as f:
            json.dump(predictions, f, indent=2)

        return {
            "status": "success",
            "mode": "batch",
            "session_id": session_record.id if session_record else None,
            "output_file": output_file,
            "job_id": job.job_id,
            "emotions_saved": len(emotions_data) if emotions_data else 0,
            "results": predictions,
        }

    # ==================== BATCH MODE ====================

    def analyze_batch(
        self,
        file_paths: List[str],
        udid: str = "TEST_ESP32",
        child_name: str = "طفل اختبار",
        child_age: int = 6,
    ) -> Dict[str, Any]:
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

        session_record = None

        try:
            logger.info(
                f"🔄 Starting Batch Analysis... Analyzing {len(file_paths)} files."
            )

            valid_files = self._validate_file_paths(file_paths)
            if not valid_files:
                return {"error": "No valid files found"}

            session_record = db_manager.save_session(
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                mode="batch",
                audio_file=valid_files[0],
            )

            job = self._submit_and_wait_for_job(valid_files)
            final_result = self._process_job_results(job, session_record)

            logger.info("✅ Batch analysis completed successfully!")
            return {**final_result, "files_analyzed": len(valid_files)}

        except Exception as e:
            logger.error(f"❌ Batch analysis failed: {e}")

            # تحديث حالة الجلسة في قاعدة البيانات
            if session_record:
                db_manager.update_session_status(
                    session_record.id, "error", str(e))

            return {
                "status": "error",
                "mode": "batch",
                "session_id": session_record.id if session_record else None,
                "error": str(e),
            }

    # ==================== STREAM MODE ====================

    def _validate_stream_file(self, audio_path: str) -> bool:
        """Validates the existence of the audio file for stream analysis."""
        if not Path(audio_path).exists():
            self.logger.error(f"File not found: {audio_path}")
            return False
        return True

    async def _process_stream_results(
        self, result: Dict, session_record: Any
    ) -> Dict[str, Any]:
        """Processes the results of a stream analysis job."""
        emotions_data = self._extract_emotions_from_predictions(result)
        if emotions_data and session_record:
            self.logger.info("💾 Saving emotions to database...")
            db_manager.save_emotions(session_record.id, emotions_data)
            db_manager.update_session_status(session_record.id, "success")

        return {
            "status": "success",
            "mode": "stream",
            "session_id": session_record.id if session_record else None,
            "emotions_saved": len(emotions_data) if emotions_data else 0,
            "results": result,
        }

    async def analyze_stream(
        self,
        audio_path: str,
        udid: str = "TEST_ESP32",
        child_name: str = "طفل اختبار",
        child_age: int = 6,
    ) -> Dict[str, Any]:
        """
        ⚡ نمط Stream - تحليل فوري لملف واحد (HUME v0.9.0) مع حفظ في قاعدة البيانات
        """
        if not HUME_AVAILABLE or not self.async_client:
            return {"error": "HUME SDK not available"}

        session_record = None
        try:
            self.logger.info(
                f"⚡ Starting Stream Analysis... Audio file: {audio_path}")

            if not self._validate_stream_file(audio_path):
                return {
                    "status": "error",
                    "mode": "stream",
                    "error": f"File not found: {audio_path}",
                }

            session_record = db_manager.save_session(
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                mode="stream",
                audio_file=audio_path,
            )

            self.logger.info("🔗 Connecting to HUME Stream...")
            socket = await self.async_client.expression_measurement.stream.connect(
                config={"prosody": {}}
            )

            self.logger.info("📤 Sending audio file...")
            with open(audio_path, "rb") as audio_file_obj:
                audio_data = audio_file_obj.read()
                result = await socket.send_bytes(audio_data)

            await socket.close()

            final_result = await self._process_stream_results(result, session_record)

            self.logger.info("✅ Stream analysis completed!")
            return {**final_result, "file": audio_path}

        except Exception as e:
            self.logger.error(f"❌ Stream analysis failed: {e}")
            if session_record:
                db_manager.update_session_status(
                    session_record.id, "error", str(e))
            return {
                "status": "error",
                "mode": "stream",
                "session_id": session_record.id if session_record else None,
                "error": str(e),
            }

    # ==================== HELPER METHODS ====================

    def _extract_from_batch(self, predictions: List) -> List[Dict[str, Any]]:
        """Extracts emotions from a batch prediction."""
        emotions_data = []
        if predictions:
            first_file = predictions[0]
            if "models" in first_file and "prosody" in first_file["models"]:
                prosody = first_file["models"]["prosody"]
                if "grouped_predictions" in prosody and prosody["grouped_predictions"]:
                    grouped = prosody["grouped_predictions"][0]
                    if "predictions" in grouped:
                        for prediction in grouped["predictions"]:
                            emotions_data.append(
                                {
                                    "name": prediction.get("name", "unknown"),
                                    "score": float(prediction.get("score", 0.0)),
                                    "confidence": (
                                        float(prediction.get("confidence", 0.0))
                                        if prediction.get("confidence")
                                        else None
                                    ),
                                }
                            )
        return emotions_data

    def _extract_from_stream(self, predictions: Dict) -> List[Dict[str, Any]]:
        """Extracts emotions from a stream prediction."""
        emotions_data = []
        if "prosody" in predictions:
            prosody_data = predictions["prosody"]
            if "predictions" in prosody_data:
                for prediction in prosody_data["predictions"]:
                    emotions_data.append(
                        {
                            "name": prediction.get("name", "unknown"),
                            "score": float(prediction.get("score", 0.0)),
                            "confidence": (
                                float(prediction.get("confidence", 0.0))
                                if prediction.get("confidence")
                                else None
                            ),
                        }
                    )
        return emotions_data

    def _extract_emotions_from_predictions(
        self, predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        🎭 استخراج المشاعر من نتائج HUME لحفظها في قاعدة البيانات
        """
        emotions_data = []
        try:
            if isinstance(predictions, list):
                emotions_data = self._extract_from_batch(predictions)
            elif isinstance(predictions, dict):
                emotions_data = self._extract_from_stream(predictions)

            self.logger.info(
                f"🎭 Extracted {len(emotions_data)} emotions from predictions"
            )

        except Exception as e:
            self.logger.error(f"❌ Error extracting emotions: {e}")

        return emotions_data

    def _get_summary_from_stream(self, stream_results: Dict) -> Dict:
        """Extracts an emotion summary from a stream result."""
        if "prosody" in stream_results:
            prosody_data = stream_results["prosody"]
            emotions = {
                p.get("name", "unknown"): p.get("score", 0.0)
                for p in prosody_data.get("predictions", [])
            }
            if emotions:
                sorted_emotions = sorted(
                    emotions.items(), key=lambda x: x[1], reverse=True
                )
                return {
                    "dominant_emotion": sorted_emotions[0],
                    "all_emotions": emotions,
                    "top_3_emotions": sorted_emotions[:3],
                }
        return {}

    def _get_summary_from_batch(self, batch_results: List) -> Dict:
        """Extracts an emotion summary from a batch result."""
        summary = {"files_count": len(batch_results), "analysis_types": []}
        if batch_results:
            first_file = batch_results[0]
            if "models" in first_file:
                models = first_file["models"]
                summary["analysis_types"] = list(models.keys())
                if "prosody" in models:
                    prosody = models["prosody"]
                    if (
                        "grouped_predictions" in prosody
                        and prosody["grouped_predictions"]
                    ):
                        predictions = prosody["grouped_predictions"][0].get(
                            "predictions", []
                        )
                        emotions = {p["name"]: p["score"] for p in predictions}
                        if emotions:
                            sorted_emotions = sorted(
                                emotions.items(), key=lambda x: x[1], reverse=True)
                            summary.update(
                                {
                                    "dominant_emotion": sorted_emotions[0],
                                    "all_emotions": emotions,
                                    "top_3_emotions": sorted_emotions[:3],
                                }
                            )
        return summary

    def extract_emotions_summary(
            self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 استخراج ملخص المشاعر من النتائج
        """
        try:
            mode = results.get("mode")
            if mode == "stream":
                return self._get_summary_from_stream(
                    results.get("results", {}))
            elif mode == "batch":
                return self._get_summary_from_batch(results.get("results", []))

            return {"error": "Could not extract emotion summary"}

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
                ("sample_happy.wav", 440),  # نغمة سعيدة
                ("sample_sad.wav", 220),  # نغمة حزينة
                ("sample_excited.wav", 660),  # نغمة متحمسة
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
            logger.error(f"❌ Failed to create sample files: {e}")
            return []


# ==================== TESTING FUNCTIONS ====================


async def test_stream_mode():
    """
    🧪 اختبار نمط Stream
    """
    logger.info("\n" + "=" * 50)
    logger.info("🧪 TESTING STREAM MODE")
    logger.info("=" * 50)

    try:
        hume = HumeIntegration()

        # إنشاء ملف تجريبي
        sample_files = hume.create_sample_files()

        if sample_files:
            audio_file = sample_files[0]  # أخذ أول ملف

            # تحليل Stream
            result = await hume.analyze_stream(audio_file)

            logger.info(f"\n📊 Stream Results:")
            logger.info(f"Status: {result.get('status')}")

            if result.get("status") == "success":
                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                logger.info(f"\n🎭 Emotions Summary:")
                logger.info(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                logger.error(f"Error: {result.get('error')}")

            return result
        else:
            logger.error("❌ No sample files available for testing")

    except Exception as e:
        logger.error(f"❌ Stream test failed: {e}")


def test_batch_mode() -> Any:
    """
    🧪 اختبار نمط Batch
    """
    logger.info("\n" + "=" * 50)
    logger.info("🧪 TESTING BATCH MODE")
    logger.info("=" * 50)

    try:
        hume = HumeIntegration()

        # إنشاء ملفات تجريبية
        sample_files = hume.create_sample_files()

        if sample_files:
            # تحليل Batch
            result = hume.analyze_batch(sample_files)

            logger.info(f"\n📊 Batch Results:")
            logger.info(f"Status: {result.get('status')}")
            logger.info(f"Files analyzed: {result.get('files_analyzed')}")

            if result.get("status") == "success":
                logger.info(f"Output file: {result.get('output_file')}")

                # استخراج ملخص المشاعر
                summary = hume.extract_emotions_summary(result)
                logger.info(f"\n🎭 Emotions Summary:")
                logger.info(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                logger.error(f"Error: {result.get('error')}")

            return result
        else:
            logger.error("❌ No sample files available for testing")

    except Exception as e:
        logger.error(f"❌ Batch test failed: {e}")


async def run_all_tests():
    """
    🧪 تشغيل جميع الاختبارات
    """
    logger.info("🎤 HUME AI Integration Testing")
    logger.info("=" * 60)

    # التحقق من API Key
    api_key = os.getenv("HUME_API_KEY")
    if not api_key:
        logger.error("❌ HUME_API_KEY not set!")
        logger.info(
            "💡 Set it with: export HUME_API_KEY='your_hume_api_key_here'")
        return

    logger.info(f"🔑 API Key: {api_key[:8]}...")

    # اختبار Stream Mode
    await test_stream_mode()

    # اختبار Batch Mode
    test_batch_mode()

    logger.info("\n" + "=" * 60)
    logger.info("✅ All tests completed!")
    logger.info("📁 Check 'batch_predictions.json' for detailed results")


if __name__ == "__main__":
    # تعيين API Key إذا لم يكن موجوداً
    if not os.getenv("HUME_API_KEY"):
        logger.warning(
            "⚠️ HUME_API_KEY not set - using default for testing only")
        os.environ["HUME_API_KEY"] = "test_key_only_for_development"

    # تشغيل الاختبارات
    asyncio.run(run_all_tests())
