import pytest
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)


sys.path.append(str(Path(__file__).parent.parent))


class TestIntegration:
    """اختبارات التكامل"""

    @pytest.mark.asyncio
    async def test_voice_interaction_flow(self):
        """اختبار تدفق التفاعل الصوتي الكامل"""
        from config.settings import Config

        from src.application.main_service import AITeddyBearService

        config = Config()
        service = AITeddyBearService(config.__dict__)
        session_result = await service.start_session("test_child")
        assert session_result is not None
        assert "message" in session_result
        end_result = await service.end_session()
        assert end_result is not None

    def test_database_integration(self):
        """اختبار تكامل قاعدة البيانات"""
        from src.data.database import Database

        db = Database(":memory:")
        db.create_child("integration_test", "سارة", 8, {"language": "ar"})
        db.save_interaction(
            "integration_test", "السلام عليكم", "وعليكم السلام", "happy"
        )
        db.save_game_result("integration_test", "trivia", 85, 300)
        db.save_emotion_analysis("integration_test", "happy", 0.8)
        child = db.get_child("integration_test")
        assert child["name"] == "سارة"
        interactions = db.get_interactions("integration_test")
        assert len(interactions) == 1
        games = db.get_game_history("integration_test")
        assert len(games) == 1
        assert games[0]["score"] == 85

    def test_security_integration(self):
        """اختبار تكامل الأمان"""
        from src.infrastructure.security import APISecurityManager, SecurityManager

        security = SecurityManager()
        api_security = APISecurityManager()
        test_audio = b"RIFF" + b"0" * 1000
        result = security.validate_audio_file("test.wav", test_audio)
        assert result["valid"]
        assert api_security.check_rate_limit("127.0.0.1")
        dirty_input = "<script>alert('xss')</script>مرحبا"
        clean_input = api_security.sanitize_input(dirty_input)
        assert "<script>" not in clean_input
        assert "مرحبا" in clean_input


class TestEndToEnd:
    """اختبارات شاملة من البداية للنهاية"""

    def test_complete_user_journey(self):
        """اختبار رحلة المستخدم الكاملة"""
        from src.api.parental_dashboard import ParentalDashboardService
        from src.data.database import Database
        from src.domain.analytics import ChildAnalytics

        db = Database(":memory:")
        child_id = "journey_test"
        db.create_child(
            child_id, "محمد", 6, {
                "interests": [
                    "الألعاب", "القصص"]})
        interactions = [
            ("مرحبا", "مرحبا بك محمد", "happy"),
            ("أريد لعبة", "هيا نلعب لعبة ممتعة", "excited"),
            ("احكي لي قصة", "سأحكي لك قصة جميلة", "calm"),
        ]
        for input_text, response_text, emotion in interactions:
            db.save_interaction(child_id, input_text, response_text, emotion)
            db.save_emotion_analysis(child_id, emotion, 0.8)
        analytics = ChildAnalytics(db)
        dominant_emotion = analytics.get_dominant_emotion(child_id)
        assert dominant_emotion in ["happy", "excited", "calm"]
        stability = analytics.calculate_emotion_stability(child_id)
        assert 0 <= stability <= 1
        dashboard = ParentalDashboardService(db)
        summary = dashboard.get_interaction_summary(child_id)
        assert "total_conversations" in summary
        assert "dominant_emotion" in summary
        assert "recommendations" in summary
        assert len(summary["recommendations"]) > 0

    def test_error_handling(self):
        """اختبار معالجة الأخطاء"""
        from src.data.database import Database

        db = Database(":memory:")
        child = db.get_child("non_existent")
        assert child is None
        interactions = db.get_interactions("non_existent")
        assert interactions == []

    def test_data_consistency(self):
        """اختبار اتساق البيانات"""
        from src.data.database import Database

        db = Database(":memory:")
        child_id = "consistency_test"
        db.create_child(child_id, "فاطمة", 9)
        for i in range(10):
            db.save_interaction(child_id, f"سؤال {i}", f"جواب {i}", "neutral")
            db.save_emotion_analysis(child_id, "neutral", 0.5)
        interactions = db.get_interactions(child_id)
        emotions = db.get_emotion_history(child_id)
        assert len(interactions) == 10
        assert len(emotions) == 10
        assert interactions[0]["input_text"] == "سؤال 9"
        assert interactions[-1]["input_text"] == "سؤال 0"


def run_qa_checklist():
    """قائمة فحص الجودة"""
    logger.info("📋 تشغيل قائمة فحص الجودة...")
    checklist = [
        ("تهيئة قاعدة البيانات", lambda: check_database_init()),
        ("استيراد الوحدات الأساسية", lambda: check_module_imports()),
        ("إعدادات الأمان", lambda: check_security_settings()),
        ("ملفات التكوين", lambda: check_config_files()),
        ("مجلدات المشروع", lambda: check_project_structure()),
    ]
    results = []
    for name, check_func in checklist:
        try:
            result = check_func()
            results.append((name, "✅" if result else "❌"))
            logger.info(f"{'✅' if result else '❌'} {name}")
        except Exception as e:
            results.append((name, f"❌ خطأ: {e}"))
            logger.info(f"❌ {name}: {e}")
    logger.info(
        f"\n📊 النتائج: {sum(1 for _, r in results if r == '✅')}/{len(results)} نجح"
    )
    return results


def check_database_init():
    """فحص تهيئة قاعدة البيانات"""
    from src.data.database import Database

    db = Database(":memory:")
    return True


def check_module_imports():
    """فحص استيراد الوحدات"""
    try:
        from src.application.main_service import AITeddyBearService
        from src.audio.speech_disorder_detector import SpeechDisorderDetector
        from src.domain.services.emotion_analyzer import EmotionAnalyzer

        return True
    except ImportError:
        return False


def check_security_settings():
    """فحص إعدادات الأمان"""
    from src.infrastructure.security import SecurityManager

    security = SecurityManager()
    return len(security.allowed_audio_types) > 0


def check_config_files():
    """فحص ملفات التكوين"""
    required_files = ["requirements.txt", "main.py"]
    return all(Path(f).exists() for f in required_files)


def check_project_structure():
    """فحص هيكل المشروع"""
    required_dirs = ["src", "config", "uploads", "outputs"]
    return all(Path(d).exists() for d in required_dirs)


if __name__ == "__main__":
    run_qa_checklist()
