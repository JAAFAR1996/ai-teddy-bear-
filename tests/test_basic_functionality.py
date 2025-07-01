import logging

logger = logging.getLogger(__name__)

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent))
from src.application.services.emotion_analyzer import EmotionAnalyzer
from src.core.domain.entities.voice_games_engine import (GameType,
                                                         VoiceGameEngine)
from src.infrastructure.database import Database
from src.infrastructure.external_services.speech_disorder_detector import \
    SpeechDisorderDetector


class TestBasicFunctionality:
    """اختبارات الوظائف الأساسية"""

    def test_emotion_analyzer_initialization(self):
        """اختبار تهيئة محلل المشاعر"""
        analyzer = EmotionAnalyzer("test_key")
        assert analyzer.hume_api_key == "test_key"
        assert analyzer.emotion_history == []

    def test_game_engine_initialization(self):
        """اختبار تهيئة محرك الألعاب"""
        engine = VoiceGameEngine("test_key")
        assert engine.game_state is not None
        assert engine.game_prompts is not None

    def test_speech_detector_initialization(self):
        """اختبار تهيئة كاشف النطق"""
        detector = SpeechDisorderDetector()
        assert detector.disorder_indicators == []
        assert detector.alert_threshold == 0.3

    def test_database_initialization(self):
        """اختبار تهيئة قاعدة البيانات"""
        db = Database(":memory:")
        assert db.db_path == ":memory:"

    def test_game_types_enum(self):
        """اختبار أنواع الألعاب"""
        assert GameType.TRIVIA.value == "trivia"
        assert GameType.RIDDLES.value == "ألغاز"

    def test_database_child_operations(self):
        """اختبار عمليات الأطفال في قاعدة البيانات"""
        db = Database(":memory:")
        result = db.create_child("test_child", "أحمد", 7, {"language": "ar"})
        assert result == True
        child = db.get_child("test_child")
        assert child is not None
        assert child["name"] == "أحمد"
        assert child["age"] == 7

    def test_interaction_saving(self):
        """اختبار حفظ التفاعلات"""
        db = Database(":memory:")
        db.create_child("test_child", "أحمد", 7)
        result = db.save_interaction("test_child", "مرحبا", "مرحبا بك أيضاً", "happy")
        assert result == True
        interactions = db.get_interactions("test_child")
        assert len(interactions) == 1
        assert interactions[0]["input_text"] == "مرحبا"


class TestAPIEndpoints:
    """اختبارات نقاط النهاية"""

    @pytest.fixture
    def client(self):
        """إعداد عميل الاختبار"""
        from fastapi.testclient import TestClient

        from main import app

        return TestClient(app)

    def test_home_endpoint(self, client):
        """اختبار الصفحة الرئيسية"""
        response = client.get("/")
        assert response.status_code == 200

    def test_children_api(self, client):
        """اختبار API الأطفال"""
        response = client.get("/api/children")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSecurityFeatures:
    """اختبارات الأمان"""

    def test_file_validation(self):
        """اختبار التحقق من الملفات"""
        from src.infrastructure.security import SecurityManager

        security = SecurityManager()
        result = security.validate_audio_file("test.wav", b"RIFF" + b"0" * 100)
        assert result["valid"] == True
        large_file = b"0" * (15 * 1024 * 1024)
        result = security.validate_audio_file("test.wav", large_file)
        assert result["valid"] == False
        assert "حجم الملف كبير جداً" in result["errors"]

    def test_filename_sanitization(self):
        """اختبار تنظيف أسماء الملفات"""
        from src.infrastructure.security import SecurityManager

        security = SecurityManager()
        dangerous_name = "test<script>alert('xss')</script>.wav"
        safe_name = security.sanitize_filename(dangerous_name)
        assert "<script>" not in safe_name
        assert "alert" not in safe_name


class TestDataProcessing:
    """اختبارات معالجة البيانات"""

    def test_emotion_stability_calculation(self):
        """اختبار حساب استقرار المشاعر"""
        from src.domain.analytics import ChildAnalytics

        class MockDB:

            def get_emotion_history(self, child_id, start_date, end_date):
                return [
                    {"emotion": "happy"},
                    {"emotion": "happy"},
                    {"emotion": "calm"},
                    {"emotion": "happy"},
                ]

        analytics = ChildAnalytics(MockDB())
        stability = analytics.calculate_emotion_stability("test_child")
        assert 0 <= stability <= 1

    def test_speech_concerns_detection(self):
        """اختبار كشف مخاوف النطق"""
        from src.domain.analytics import ChildAnalytics

        class MockDB:

            def get_speech_analysis(self, child_id):
                return [
                    {"concerns": ["تأتأة", "بطء في الكلام"]},
                    {"concerns": ["تأتأة"]},
                    {"concerns": ["تأتأة", "توقفات متكررة"]},
                    {"concerns": ["تأتأة"]},
                ]

        analytics = ChildAnalytics(MockDB())
        concerns = analytics.get_speech_concerns("test_child")
        assert "تأتأة" in concerns


def run_manual_tests():
    """اختبارات يدوية للتحقق السريع"""
    logger.info("🧪 تشغيل الاختبارات اليدوية...")
    required_dirs = ["uploads", "outputs", "data", "static"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            logger.info(f"✅ مجلد {dir_name} موجود")
        else:
            logger.info(f"❌ مجلد {dir_name} مفقود")
    required_files = ["main.py", "requirements.txt", ".env"]
    for file_name in required_files:
        if Path(file_name).exists():
            logger.info(f"✅ ملف {file_name} موجود")
        else:
            logger.info(f"❌ ملف {file_name} مفقود")
    try:
        from src.application.main_service import AITeddyBearService

        logger.info("✅ يمكن استيراد الخدمة الرئيسية")
    except ImportError as e:
        logger.info(f"❌ فشل استيراد الخدمة الرئيسية: {e}")
    logger.info("✅ انتهت الاختبارات اليدوية")


if __name__ == "__main__":
    run_manual_tests()
