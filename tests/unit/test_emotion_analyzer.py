import numpy as np

from src.domain.services.emotion_analyzer import EmotionAnalyzer, EmotionResult


class TestEmotionAnalyzer:
    """Test emotion analysis service"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = EmotionAnalyzer()

    def test_analyze_happy_text(self):
        """Test analyzing happy text"""
        result = self.analyzer.analyze_text("I am so happy and joyful today!")

        assert result.primary_emotion == "happy"
        assert result.confidence > 0.5
        assert "happy" in result.all_emotions

    def test_analyze_sad_text(self):
        """Test analyzing sad text"""
        result = self.analyzer.analyze_text("I feel sad and want to cry")

        assert result.primary_emotion == "sad"
        assert result.confidence > 0.5

    def test_analyze_neutral_text(self):
        """Test analyzing neutral text"""
        result = self.analyzer.analyze_text("The weather is nice today")

        assert result.primary_emotion == "calm"
        assert isinstance(result.all_emotions, dict)

    def test_analyze_voice_features(self):
        """Test voice emotion analysis"""
        # Mock audio features
        audio_features = np.array([0.1, 0.2, 0.3, 0.4])

        result = self.analyzer.analyze_voice(audio_features)

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in [
            "happy", "sad", "angry", "excited", "calm"]
        assert 0 <= result.confidence <= 1
