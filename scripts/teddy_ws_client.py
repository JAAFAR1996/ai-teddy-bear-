import logging

logger = logging.getLogger(__name__)

"""
Enhanced Teddy Bear Client - عميل الدبدوب المحسّن
نسخة محسّنة مع ميزات متقدمة للتفاعل الصوتي
"""
import asyncio
import base64
import io
import json
import queue
import sys
import wave
from datetime import datetime

import numpy as np
import sounddevice as sd
import websockets
from pydub import AudioSegment
from pydub.playback import play

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
WS_URL = "ws://127.0.0.1:8000/ws/audio"
RECONNECT_DELAY = 3
RECORD_SECONDS = 4
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5
MIN_AUDIO_VOLUME = 1000
MIN_AUDIO_LENGTH = 2000


class EnhancedTeddyClient:

    def __init__(self, ws_url=WS_URL):
        self.ws_url = ws_url
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.websocket = None
        self.connected = False

    def record_audio_continuous(self, duration=RECORD_SECONDS):
        """تسجيل صوتي محسّن مع كشف الصمت"""
        logger.info("🎤 تحدث الآن...")
        audio_data = []
        silence_counter = 0
        max_silence_frames = int(SILENCE_DURATION * SAMPLE_RATE / 1024)
        peak_volume = 0

        def audio_callback(indata, frames, time, status):
            if status:
                logger.info(status)
            volume_norm = np.linalg.norm(indata) * 10
            nonlocal peak_volume
            if volume_norm > peak_volume:
                peak_volume = volume_norm
            audio_data.extend(indata[:, 0])
            nonlocal silence_counter
            if volume_norm < SILENCE_THRESHOLD:
                silence_counter += 1
                if silence_counter > max_silence_frames:
                    raise sd.CallbackStop()
            else:
                silence_counter = 0
                bars = int(volume_norm / 100)
                if bars > 10:
                    bars = 10
                indicator = "🔊" + "▬" * bars + " " * (10 - bars)
                logger.info(f"\r{indicator} [{volume_norm:4.0f}]", end="", flush=True)

        try:
            with sd.InputStream(
                callback=audio_callback,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype=DTYPE,
            ):
                sd.sleep(int(duration * 1000))
        except sd.CallbackStop:
            logger.info("\n✅ تم اكتشاف نهاية الكلام")
        logger.info(f"\n📝 تم التسجيل - أعلى مستوى: {peak_volume:.0f}")
        return np.array(audio_data, dtype=DTYPE)

    def audio_to_wav_bytes(self, audio_data):
        """تحويل البيانات الصوتية إلى WAV في الذاكرة"""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data.tobytes())
        buffer.seek(0)
        return buffer.read()

    async def connect_with_retry(self):
        """الاتصال مع إعادة المحاولة"""
        while True:
            try:
                logger.info(f"🔄 محاولة الاتصال بـ {self.ws_url}...")
                self.websocket = await websockets.connect(self.ws_url)
                self.connected = True
                logger.info("✅ تم الاتصال بنجاح!")
                return True
            except Exception as e:
                logger.info(f"❌ فشل الاتصال: {e}")
                logger.info(f"⏳ إعادة المحاولة بعد {RECONNECT_DELAY} ثواني...")
                await asyncio.sleep(RECONNECT_DELAY)

    async def send_audio(self, audio_data):
        """إرسال الصوت للسيرفر"""
        try:
            wav_bytes = self.audio_to_wav_bytes(audio_data)
            audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")
            message = json.dumps(
                {
                    "type": "audio",
                    "audio": audio_b64,
                    "format": "wav",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            await self.websocket.send(message)
            logger.info("📤 تم إرسال الصوت... بانتظار الرد...")
            response = await self.websocket.recv()
            await self.handle_response(response)
        except websockets.exceptions.ConnectionClosed:
            logger.info("📡 انقطع الاتصال")
            self.connected = False
        except Exception as e:
            logger.info(f"❌ خطأ: {e}")

    async def handle_response(self, response):
        """معالجة الرد من السيرفر"""
        try:
            data = json.loads(response)
            if data.get("type") == "audio":
                audio_bytes = base64.b64decode(data["audio"])
                if "text" in data and data["text"]:
                    logger.info(f"📝 الدبدوب سمع: {data['text']}")
                self.play_audio(audio_bytes)
                if "emotion" in data:
                    self.show_emotion(data["emotion"])
            elif data.get("type") == "error":
                logger.info(f"⚠️ خطأ من السيرفر: {data.get('error')}")
            else:
                logger.info(f"📩 رسالة غير متوقعة: {data}")
        except json.JSONDecodeError:
            logger.info("❌ خطأ في تحليل الرد")
        except Exception as e:
            logger.info(f"❌ خطأ في معالجة الرد: {e}")

    def play_audio(self, audio_bytes):
        """تشغيل الصوت من الذاكرة مباشرة (MP3/WAV مدعوم)"""


    try:
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        except Exception:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        logger.info("🔊 يتحدث الدبدوب...")
        play(audio)
        logger.info("✅ انتهى الدبدوب من الكلام")
    except Exception as e:
        logger.info(f"❌ خطأ في تشغيل الصوت: {e}")

    def show_emotion(self, emotion):
        """عرض المشاعر"""
        emotions = {
            "happy": "😊 سعيد",
            "sad": "😢 حزين",
            "excited": "🤗 متحمس",
            "neutral": "🙂 عادي",
            "thinking": "🤔 يفكر",
            "playful": "😄 مرح",
        }
        logger.info(f"💭 مشاعر الدبدوب: {emotions.get(emotion, emotion)}")

    def validate_audio(self, audio_data):
        """التحقق من صحة وقوة الصوت المسجل"""
        volume = np.linalg.norm(audio_data)
        length = len(audio_data)
        rms = np.sqrt(np.mean(audio_data**2))
        logger.info("\n📊 تحليل الصوت:")
        logger.info(f"   - الطول: {length} عينة ({length / SAMPLE_RATE:.1f} ثانية)")
        logger.info(f"   - القوة: {volume:.0f}")
        logger.info(f"   - RMS: {rms:.2f}")
        min_volume = 1000
        min_length = 2000
        if volume < min_volume or length < min_length:
            logger.info("\n⚠️ الصوت ضعيف جداً أو قصير!")
            logger.info(f"   - المطلوب: قوة > {min_volume} وطول > {min_length}")
            logger.info("   💡 نصيحة: تحدث بصوت أعلى وأقرب للميكروفون")
            return False
        return True

    async def run_interactive(self):
        """وضع تفاعلي مستمر"""
        logger.info("\n🧸 مرحباً! أنا دبدوبك الذكي")
        logger.info("📌 اضغط Enter للتحدث، أو اكتب 'خروج' للإنهاء\n")
        await self.connect_with_retry()
        consecutive_failures = 0
        try:
            while True:
                user_input = input("\n[اضغط Enter للتحدث] ")
                if user_input.lower() in ["خروج", "exit", "quit"]:
                    logger.info("👋 وداعاً! سررت باللعب معك!")
                    break
                audio_data = self.record_audio_continuous()
                if not self.validate_audio(audio_data):
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        logger.info("\n🎤 يبدو أن هناك مشكلة في الميكروفون")
                        logger.info("   تأكد من:")
                        logger.info("   1. الميكروفون موصول بشكل صحيح")
                        logger.info("   2. إذن الوصول للميكروفون مفعّل")
                        logger.info("   3. لا يوجد تطبيق آخر يستخدم الميكروفون")
                    continue
                consecutive_failures = 0
                await self.send_audio(audio_data)
        except KeyboardInterrupt:
            logger.info("\n\n👋 تم الإيقاف. إلى اللقاء!")
        finally:
            if self.websocket:
                await self.websocket.close()

    async def run_once(self):
        """تشغيل مرة واحدة (متوافق مع الكود الأصلي)"""
        if not await self.connect_with_retry():
            return
        try:
            audio_data = self.record_audio_continuous()
            if not self.validate_audio(audio_data):
                logger.info("\n❌ فشل التسجيل. حاول مرة أخرى.")
                return
            await self.send_audio(audio_data)
        finally:
            if self.websocket:
                await self.websocket.close()


async def run_once():
    """دالة متوافقة مع الكود الأصلي"""
    client = EnhancedTeddyClient()
    await client.run_once()


async def run_interactive():
    """تشغيل الوضع التفاعلي"""
    client = EnhancedTeddyClient()
    await client.run_interactive()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(run_interactive())
    else:
        asyncio.run(run_once())
