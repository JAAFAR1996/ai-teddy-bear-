"""
Enhanced Teddy Bear Client - عميل الدبدوب المحسّن
نسخة محسّنة مع ميزات متقدمة للتفاعل الصوتي
"""

import asyncio
import base64
import io
import json
import os
import queue
import sys
import threading
import time
import wave
from datetime import datetime

import numpy as np
import simpleaudio as sa
import sounddevice as sd
import websockets
from pydub import AudioSegment
from pydub.playback import play

# إعدادات الصوت
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"

# إعدادات الاتصال
WS_URL = "ws://127.0.0.1:8000/ws/audio"
RECONNECT_DELAY = 3  # ثواني

# إعدادات التسجيل
RECORD_SECONDS = 4
SILENCE_THRESHOLD = 500  # عتبة الصمت
SILENCE_DURATION = 1.5  # ثواني من الصمت للإيقاف التلقائي

# إعدادات التحقق من الصوت
MIN_AUDIO_VOLUME = 1000  # الحد الأدنى لقوة الصوت
MIN_AUDIO_LENGTH = 2000  # الحد الأدنى لطول التسجيل (عينات)


class EnhancedTeddyClient:
    def __init__(self, ws_url=WS_URL):
        self.ws_url = ws_url
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.websocket = None
        self.connected = False

    def record_audio_continuous(self, duration=RECORD_SECONDS):
        """تسجيل صوتي محسّن مع كشف الصمت"""
        print("🎤 تحدث الآن...")

        audio_data = []
        silence_counter = 0
        max_silence_frames = int(SILENCE_DURATION * SAMPLE_RATE / 1024)
        peak_volume = 0

        def audio_callback(indata, frames, time, status):
            if status:
                print(status)

            # حساب مستوى الصوت
            volume_norm = np.linalg.norm(indata) * 10

            # تحديث أعلى مستوى صوت
            nonlocal peak_volume
            if volume_norm > peak_volume:
                peak_volume = volume_norm

            # إضافة البيانات
            audio_data.extend(indata[:, 0])

            # كشف الصمت
            nonlocal silence_counter
            if volume_norm < SILENCE_THRESHOLD:
                silence_counter += 1
                if silence_counter > max_silence_frames:
                    raise sd.CallbackStop()
            else:
                silence_counter = 0
                # مؤشر بصري للصوت مع مستويات
                bars = int(volume_norm / 100)
                if bars > 10:
                    bars = 10
                indicator = "🔊" + "▬" * bars + " " * (10 - bars)
                print(f"\r{indicator} [{volume_norm:4.0f}]", end="", flush=True)

        # بدء التسجيل
        try:
            with sd.InputStream(
                callback=audio_callback,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype=DTYPE,
            ):
                sd.sleep(int(duration * 1000))
        except sd.CallbackStop:
            print("\n✅ تم اكتشاف نهاية الكلام")

        print(f"\n📝 تم التسجيل - أعلى مستوى: {peak_volume:.0f}")
        return np.array(audio_data, dtype=DTYPE)

    def audio_to_wav_bytes(self, audio_data):
        """تحويل البيانات الصوتية إلى WAV في الذاكرة"""
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data.tobytes())

        buffer.seek(0)
        return buffer.read()

    async def connect_with_retry(self):
        """الاتصال مع إعادة المحاولة"""
        while True:
            try:
                print(f"🔄 محاولة الاتصال بـ {self.ws_url}...")
                self.websocket = await websockets.connect(self.ws_url)
                self.connected = True
                print("✅ تم الاتصال بنجاح!")
                return True
            except Exception as e:
                print(f"❌ فشل الاتصال: {e}")
                print(f"⏳ إعادة المحاولة بعد {RECONNECT_DELAY} ثواني...")
                await asyncio.sleep(RECONNECT_DELAY)

    async def send_audio(self, audio_data):
        """إرسال الصوت للسيرفر"""
        try:
            # تحويل لـ WAV
            wav_bytes = self.audio_to_wav_bytes(audio_data)

            # تشفير Base64
            audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")

            # إنشاء الرسالة
            message = json.dumps(
                {
                    "type": "audio",
                    "audio": audio_b64,
                    "format": "wav",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # إرسال
            await self.websocket.send(message)
            print("📤 تم إرسال الصوت... بانتظار الرد...")

            # استقبال الرد
            response = await self.websocket.recv()
            await self.handle_response(response)

        except websockets.exceptions.ConnectionClosed:
            print("📡 انقطع الاتصال")
            self.connected = False
        except Exception as e:
            print(f"❌ خطأ: {e}")

    async def handle_response(self, response):
        """معالجة الرد من السيرفر"""
        try:
            data = json.loads(response)

            if data.get("type") == "audio":
                # فك تشفير الصوت
                audio_bytes = base64.b64decode(data["audio"])

                if "text" in data and data["text"]:
                    print(f"📝 الدبدوب سمع: {data['text']}")

                # تشغيل الصوت
                self.play_audio(audio_bytes)

                # عرض معلومات إضافية
                if "emotion" in data:
                    self.show_emotion(data["emotion"])

            elif data.get("type") == "error":
                print(f"⚠️ خطأ من السيرفر: {data.get('error')}")
            else:
                print(f"📩 رسالة غير متوقعة: {data}")

        except json.JSONDecodeError:
            print("❌ خطأ في تحليل الرد")
        except Exception as e:
            print(f"❌ خطأ في معالجة الرد: {e}")

    def play_audio(self, audio_bytes):
        """تشغيل الصوت من الذاكرة مباشرة (MP3/WAV مدعوم)"""
        import io

        from pydub import AudioSegment
        from pydub.playback import play

    try:
        try:
            # جرّب WAV أولاً
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        except Exception:
            # إذا فشل، جرّب MP3
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

        print("🔊 يتحدث الدبدوب...")
        play(audio)
        print("✅ انتهى الدبدوب من الكلام")

    except Exception as e:
        print(f"❌ خطأ في تشغيل الصوت: {e}")

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
        print(f"💭 مشاعر الدبدوب: {emotions.get(emotion, emotion)}")

    def validate_audio(self, audio_data):
        """التحقق من صحة وقوة الصوت المسجل"""
        # حساب قوة الصوت (RMS/Norm)
        volume = np.linalg.norm(audio_data)
        length = len(audio_data)

        # حساب RMS (Root Mean Square) للدقة
        rms = np.sqrt(np.mean(audio_data**2))

        # عرض معلومات التحليل
        print(f"\n📊 تحليل الصوت:")
        print(f"   - الطول: {length} عينة ({length/SAMPLE_RATE:.1f} ثانية)")
        print(f"   - القوة: {volume:.0f}")
        print(f"   - RMS: {rms:.2f}")

        # التحقق من الحد الأدنى
        min_volume = 1000
        min_length = 2000  # حوالي 0.125 ثانية

        if volume < min_volume or length < min_length:
            print(f"\n⚠️ الصوت ضعيف جداً أو قصير!")
            print(f"   - المطلوب: قوة > {min_volume} وطول > {min_length}")
            print(f"   💡 نصيحة: تحدث بصوت أعلى وأقرب للميكروفون")
            return False

        return True

    async def run_interactive(self):
        """وضع تفاعلي مستمر"""
        print("\n🧸 مرحباً! أنا دبدوبك الذكي")
        print("📌 اضغط Enter للتحدث، أو اكتب 'خروج' للإنهاء\n")

        # الاتصال بالسيرفر
        await self.connect_with_retry()

        consecutive_failures = 0

        try:
            while True:
                # انتظار إدخال المستخدم
                user_input = input("\n[اضغط Enter للتحدث] ")

                if user_input.lower() in ["خروج", "exit", "quit"]:
                    print("👋 وداعاً! سررت باللعب معك!")
                    break

                # تسجيل الصوت
                audio_data = self.record_audio_continuous()

                # التحقق من صحة الصوت
                if not self.validate_audio(audio_data):
                    consecutive_failures += 1

                    if consecutive_failures >= 3:
                        print("\n🎤 يبدو أن هناك مشكلة في الميكروفون")
                        print("   تأكد من:")
                        print("   1. الميكروفون موصول بشكل صحيح")
                        print("   2. إذن الوصول للميكروفون مفعّل")
                        print("   3. لا يوجد تطبيق آخر يستخدم الميكروفون")

                    continue  # العودة لبداية الحلقة

                # إعادة تعيين عداد الفشل
                consecutive_failures = 0

                # إرسال الصوت
                await self.send_audio(audio_data)

        except KeyboardInterrupt:
            print("\n\n👋 تم الإيقاف. إلى اللقاء!")
        finally:
            if self.websocket:
                await self.websocket.close()

    async def run_once(self):
        """تشغيل مرة واحدة (متوافق مع الكود الأصلي)"""
        # الاتصال
        if not await self.connect_with_retry():
            return

        try:
            # تسجيل
            audio_data = self.record_audio_continuous()

            # التحقق من صحة الصوت
            if not self.validate_audio(audio_data):
                print("\n❌ فشل التسجيل. حاول مرة أخرى.")
                return

            # إرسال واستقبال
            await self.send_audio(audio_data)

        finally:
            if self.websocket:
                await self.websocket.close()


# دوال مساعدة للتوافق مع الكود الأصلي
async def run_once():
    """دالة متوافقة مع الكود الأصلي"""
    client = EnhancedTeddyClient()
    await client.run_once()


async def run_interactive():
    """تشغيل الوضع التفاعلي"""
    client = EnhancedTeddyClient()
    await client.run_interactive()


if __name__ == "__main__":
    # تحديد الوضع من سطر الأوامر
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # وضع تفاعلي
        asyncio.run(run_interactive())
    else:
        # تشغيل مرة واحدة (افتراضي)
        asyncio.run(run_once())
