import structlog
logger = structlog.get_logger(__name__)

import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play

# ====== كود تسجيل الصوت وحفظه كملف WAV ======

def record_and_save_wav(filename="output.wav", duration=3, fs=16000):
    print("🎤 تسجيل... تحدث الآن")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # انتظر انتهاء التسجيل
    write(filename, fs, recording)
    print(f"✅ تم حفظ التسجيل في {filename}")

# ====== كود تشغيل ملف WAV بشكل آمن ======

def is_valid_wav(file_path):
    """يتحقق إذا كان الملف فعلاً WAV صالح"""
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b'RIFF'
    except Exception as e:
    logger.error(f"Error: {e}")"⚠️ حدث خطأ أثناء قراءة رأس الملف:", e)
        return False

def safe_play(file_path):
    """يشغل ملف صوتي بعد التحقق من صيغته"""
    import os
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
        print(f"❌ الملف {file_path} غير موجود أو فارغ.")
        return

    ext = file_path.lower().split('.')[-1]
    if ext == "wav":
        if not is_valid_wav(file_path):
            print(f"❌ الملف {file_path} ليس ملف WAV صالح (لا يبدأ بـ RIFF)")
            return
        try:
            audio = AudioSegment.from_file(file_path, format="wav")
            play(audio)
        except Exception as e:
    logger.error(f"Error: {e}")"❌ خطأ أثناء تشغيل WAV:", e)
    else:
        print(f"❌ صيغة الملف غير مدعومة: {file_path}")

class TTSPlayback:
    def __init__(self, on_playback_complete):
        self.on_playback_complete = on_playback_complete
        self.stream = None

    def play_audio(self, data, samplerate):
        self.stream = sd.OutputStream(samplerate=samplerate, channels=1, callback=self.callback, finished_callback=self.on_playback_complete)
        self.stream.start()

    def callback(self, outdata, frames, time, status):
        if status:
            print(status)
        # This is a placeholder. In a real implementation, you would feed audio data here.
        # For now, we'll just output silence.
        outdata.fill(0)

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

# ====== مثال كامل على التسجيل والتشغيل ======

if __name__ == "__main__":
    filename = "test_mic.wav"
    record_and_save_wav(filename, duration=4)    # غيّر مدة التسجيل لو تريد
    safe_play(filename)

def cleanup_tts_cache(max_age_hours: int = 24) -> int:
    """Clean up TTS cache files older than max_age_hours"""
    try:
        cache_dir = Path("cache/tts")
        if not cache_dir.exists():
            return 0
        current_time = time.time()
        cleaned_count = 0
        for cache_file in cache_dir.glob("*.wav"):
            file_age = current_time - cache_file.stat().st_mtime
            if file_age > (max_age_hours * 3600):
                cache_file.unlink()
                cleaned_count += 1
        print(f"Cleaned {cleaned_count} TTS cache files")
        return cleaned_count
    except Exception as e:
    logger.error(f"Error: {e}")f"Error cleaning TTS cache: {e}")
        return 0