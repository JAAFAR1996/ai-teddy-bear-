from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)

import sys
import asyncio
import base64
import json
import requests
import wave
import pyaudio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from qasync import QEventLoop, asyncSlot
import websockets

SERVER_URL = "http://127.0.0.1:8000"
DEVICE_ID = "ESP32_SIM_001"
WS_URL = f"ws://127.0.0.1:8000/ws/{DEVICE_ID}"
WAKE_WORD = "يا دبدوب"  # للتجربة استخدم أي كلمة

class TeddySimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧸 ESP32 Teddy Simulator")
        self.setGeometry(200, 200, 400, 250)
        self.is_on = False
        self.status = QLabel("🔴 الدبدوب مطفأ", self)
        self.status.setAlignment(Qt.AlignCenter)
        self.toggle_btn = QPushButton("تشغيل الدبدوب", self)
        self.toggle_btn.clicked.connect(self.toggle_power)
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.toggle_btn)
        self.setLayout(layout)
        self.ws_task = None

    @asyncSlot()
    async def listen_for_wake_word(self):
        self.status.setText("🟢 الدبدوب يستمع... قل: يا دبدوب")
        while self.is_on:
            # محاكاة wake word: أي إدخال من المستخدم في الطرفية
            await asyncio.sleep(0.5)
            logger.info("اكتب 'يا دبدوب' في الطرفية لتفعيل الدبدوب:")
            try:
                loop = asyncio.get_event_loop()
                word = await loop.run_in_executor(None, sys.stdin.readline)
                if WAKE_WORD in word:
                    self.status.setText("🎤 تم تفعيل الدبدوب! جاري التسجيل...")
                    await self.record_and_send()
                    self.status.setText("🟢 الدبدوب يستمع... قل: يا دبدوب")
            except Exception as e:
                self.status.setText(f"⚠️ خطأ: {e}")

    async def record_and_send(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        frames = []
        seconds = 4
        for _ in range(0, int(16000 / 1024 * seconds)):
            data = stream.read(1024)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        pa.terminate()
        wf = wave.open("temp.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(frames))
        wf.close()
        with open("temp.wav", "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        payload = {"audio": audio_b64, "device_id": DEVICE_ID}
        try:
            r = requests.post(f"{SERVER_URL}/esp32/audio", json=payload)
            if r.ok:
                self.status.setText("✅ تم إرسال الصوت للسيرفر!")
            else:
                self.status.setText("❌ فشل الإرسال: " + r.text)
        except Exception as e:
            self.status.setText(f"❌ خطأ في الاتصال: {e}")

    async def listen_for_commands(self):
        try:
            async with websockets.connect(WS_URL) as ws:
                self.status.setText("🔗 متصل بالسيرفر، في انتظار الأوامر...")
                while self.is_on:
                    msg = await ws.recv()
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "set_volume":
                            volume = data["volume"]
                            self.status.setText(f"🔊 تم تغيير مستوى الصوت إلى: {volume}")
                        elif data.get("type") == "set_wifi":
                            ssid = data["ssid"]
                            password = data["password"]
                            self.status.setText(f"📶 تم تحديث إعدادات WiFi: {ssid} / {password}")
                    except Exception as e:
                        self.status.setText(f"⚠️ خطأ في استقبال الأمر: {e}")
        except Exception as e:
            self.status.setText(f"⚠️ خطأ في الاتصال بالسيرفر: {e}")

    def toggle_power(self) -> Any:
        self.is_on = not self.is_on
        if self.is_on:
            self.status.setText("🟢 الدبدوب يعمل... يستمع للنداء")
            self.toggle_btn.setText("إطفاء الدبدوب")
            asyncio.create_task(self.listen_for_wake_word())
            self.ws_task = asyncio.create_task(self.listen_for_commands())
        else:
            self.status.setText("🔴 الدبدوب مطفأ")
            self.toggle_btn.setText("تشغيل الدبدوب")
            if self.ws_task:
                self.ws_task.cancel()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    teddy = TeddySimulator()
    teddy.show()
    with loop:
        loop.run_forever() 