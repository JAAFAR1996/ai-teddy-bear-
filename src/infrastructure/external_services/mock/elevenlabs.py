"""Mock ElevenLabs for development"""


class Voice:
    def __init__(self, voice_id: str, name: str = ""):
        self.voice_id = voice_id
        self.name = name


class VoiceSettings:
    def __init__(self, stability: float = 0.5, similarity_boost: float = 0.8):
        self.stability = stability
        self.similarity_boost = similarity_boost


def generate(text: str, voice: Voice, voice_settings: VoiceSettings = None):
    return b"mock_audio_data"


def voices():
    return [Voice("voice1", "Arabic Voice"), Voice("voice2", "English Voice")]
