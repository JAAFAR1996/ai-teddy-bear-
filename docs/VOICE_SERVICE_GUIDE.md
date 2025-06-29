# 🎤 دليل خدمة الصوت - Voice Service Guide

## 📋 نظرة عامة
خدمة الصوت المتطورة لمشروع AI Teddy Bear تدعم تحويل الكلام إلى نص (STT) مع عدة مزودين وتنسيقات صوتية متنوعة، بما في ذلك الصوت المضغوط من أجهزة ESP32.

---

## 🎯 الميزات الرئيسية

### ✅ **مزودي STT المدعومين:**
- **Whisper** (محلي) - الافتراضي والمُستحسن
- **Azure Speech SDK** - للاستخدام السحابي
- **OpenAI Whisper API** - عبر API
- **Mock Provider** - للاختبار والتطوير

### ✅ **تنسيقات الصوت المدعومة:**
- **WAV** - غير مضغوط
- **MP3** - مضغوط (مُستحسن للـ ESP32)
- **OGG** - مضغوط بديل
- **WEBM, M4A, FLAC** - تنسيقات إضافية

### ✅ **ميزات متقدمة:**
- **تحويل تنسيقات تلقائي** (باستخدام pydub أو ffmpeg)
- **دعم ESP32 مخصص** مع metadata إضافية
- **آلية fallback قوية** للتعامل مع الأخطاء
- **مراقبة الأداء** المتقدمة
- **إدارة ذاكرة محسنة**

---

## 🔧 التثبيت والإعداد

### **1. تثبيت المتطلبات الأساسية:**

```bash
# المتطلبات الأساسية
pip install fastapi uvicorn pydantic

# مكتبات الصوت
pip install pydub wave numpy

# Whisper (محلي) - مُستحسن
pip install openai-whisper

# Azure Speech (اختياري)
pip install azure-cognitiveservices-speech

# OpenAI API (اختياري)
pip install openai
```

### **2. تثبيت ffmpeg (للتحويل المتقدم):**

```bash
# Windows (باستخدام chocolatey)
choco install ffmpeg

# macOS (باستخدام homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# أو تحميل من: https://ffmpeg.org/download.html
```

### **3. إعداد متغيرات البيئة:**

```bash
# ملف .env
STT_PROVIDER=whisper              # whisper, azure, openai
WHISPER_MODEL=base                # tiny, base, small, medium, large
MAX_AUDIO_DURATION=30             # ثواني
ENABLE_STT_FALLBACK=true          # تفعيل fallback

# Azure Speech (إذا كنت تستخدمه)
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus
AZURE_SPEECH_LANGUAGE=ar-SA

# OpenAI API (إذا كنت تستخدمه)
OPENAI_API_KEY=your_openai_key
```

---

## 🚀 الاستخدام السريع

### **1. إنشاء Voice Service:**

```python
from src.application.services.voice_service import create_voice_service

# إنشاء الخدمة بالإعدادات الافتراضية
voice_service = create_voice_service()

# أو بإعدادات مخصصة
from src.application.services.voice_service import VoiceService, VoiceServiceConfig, STTProvider

config = VoiceServiceConfig(
    default_provider=STTProvider.WHISPER,
    whisper_model="base",
    max_audio_duration=60,
    enable_fallback=True
)

voice_service = VoiceService(config)
```

### **2. تحويل الصوت إلى نص:**

```python
import asyncio
import base64

async def transcribe_example():
    # قراءة ملف صوتي
    with open("audio.mp3", "rb") as f:
        audio_bytes = f.read()
    
    # تحويل إلى base64 (اختياري)
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # تحويل الصوت إلى نص
    result = await voice_service.transcribe_audio(
        audio_data=audio_base64,  # أو audio_bytes مباشرة
        format=AudioFormat.MP3,
        language="ar",
        provider=STTProvider.WHISPER
    )
    
    print(f"النص: {result.text}")
    print(f"الثقة: {result.confidence:.2f}")
    print(f"المزود: {result.provider}")
    print(f"وقت المعالجة: {result.processing_time_ms}ms")

# تشغيل المثال
asyncio.run(transcribe_example())
```

### **3. معالجة صوت ESP32:**

```python
from src.application.services.voice_service import AudioRequest

async def process_esp32_audio():
    # إنشاء طلب صوت ESP32
    request = AudioRequest(
        audio_data="base64_encoded_mp3_data",
        format=AudioFormat.MP3,
        device_id="ESP32_TEDDY_001",
        session_id="session_123",
        language="ar",
        child_name="أحمد",
        child_age=6
    )
    
    # معالجة الصوت
    result = await voice_service.process_esp32_audio(request)
    
    print(f"جهاز ESP32: {result.metadata['device_id']}")
    print(f"اسم الطفل: {result.metadata['child_name']}")
    print(f"النص المكتشف: {result.text}")

asyncio.run(process_esp32_audio())
```

---

## 🌐 استخدام API Endpoints

### **1. رفع ملف صوتي من ESP32:**

```python
import requests

# إعداد البيانات
files = {
    'file': ('audio.mp3', open('audio.mp3', 'rb'), 'audio/mpeg')
}

data = {
    'device_id': 'ESP32_TEDDY_001',
    'session_id': 'session_123',
    'audio_format': 'mp3',
    'language': 'ar',
    'child_name': 'فاطمة',
    'child_age': 5
}

# إرسال الطلب
response = requests.post(
    'http://localhost:8000/api/voice/esp32/audio',
    files=files,
    data=data
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ نجح التحويل: {result['transcription']['text']}")
    print(f"🤖 رد الذكي: {result['ai_response']['text']}")
else:
    print(f"❌ خطأ: {response.status_code}")
```

### **2. إرسال JSON مباشر:**

```python
import requests
import base64

# تحويل الصوت إلى base64
with open('audio.mp3', 'rb') as f:
    audio_base64 = base64.b64encode(f.read()).decode('utf-8')

# إعداد البيانات
payload = {
    "audio_data": audio_base64,
    "format": "mp3",
    "device_id": "ESP32_TEDDY_002",
    "language": "ar",
    "child_name": "محمد"
}

# إرسال الطلب
response = requests.post(
    'http://localhost:8000/api/voice/esp32/audio-json',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

result = response.json()
print(f"النتيجة: {result}")
```

### **3. مثال ESP32 (Arduino/C++):**

```cpp
// في ملف ESP32
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendAudioToServer(uint8_t* mp3_data, size_t size) {
    HTTPClient http;
    http.begin("http://your-server.com/api/voice/esp32/audio");
    
    // إعداد multipart form data
    String boundary = "----TeddyBearBoundary";
    String body = "";
    
    // إضافة metadata
    body += "--" + boundary + "\r\n";
    body += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    body += "ESP32_TEDDY_001\r\n";
    
    body += "--" + boundary + "\r\n";
    body += "Content-Disposition: form-data; name=\"audio_format\"\r\n\r\n";
    body += "mp3\r\n";
    
    body += "--" + boundary + "\r\n";
    body += "Content-Disposition: form-data; name=\"language\"\r\n\r\n";
    body += "ar\r\n";
    
    // إضافة الملف الصوتي
    body += "--" + boundary + "\r\n";
    body += "Content-Disposition: form-data; name=\"file\"; filename=\"audio.mp3\"\r\n";
    body += "Content-Type: audio/mpeg\r\n\r\n";
    
    // إضافة البيانات الثنائية
    // ... (إضافة mp3_data هنا)
    
    body += "\r\n--" + boundary + "--\r\n";
    
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    
    int response_code = http.POST(body);
    
    if (response_code == 200) {
        String response = http.getString();
        Serial.println("✅ تم إرسال الصوت بنجاح");
        // معالجة الرد...
    }
    
    http.end();
}
```

---

## ⚙️ التكوين المتقدم

### **1. اختيار نموذج Whisper:**

```python
from src.application.services.voice_service import WhisperModel

config = VoiceServiceConfig(
    whisper_model=WhisperModel.SMALL,  # أسرع، دقة جيدة
    # WhisperModel.TINY     -> أسرع جداً، دقة أقل
    # WhisperModel.BASE     -> متوازن (افتراضي)
    # WhisperModel.MEDIUM   -> دقة أعلى، أبطأ
    # WhisperModel.LARGE    -> أعلى دقة، الأبطأ
)
```

### **2. إعداد Azure Speech:**

```python
config = VoiceServiceConfig(
    default_provider=STTProvider.AZURE,
    azure_key="your_subscription_key",
    azure_region="eastus",  # أو منطقتك
    azure_language="ar-SA"  # أو ar-EG, ar-AE, etc.
)
```

### **3. تحسين الأداء:**

```python
config = VoiceServiceConfig(
    max_audio_duration=60,      # ثواني
    supported_formats=[         # تنسيقات مدعومة
        AudioFormat.WAV,
        AudioFormat.MP3,
        AudioFormat.OGG
    ],
    enable_fallback=True,       # تفعيل fallback
    temp_dir="./audio_temp"     # مجلد مؤقت
)
```

---

## 🧪 الاختبار والتطوير

### **1. تشغيل الاختبارات:**

```bash
# اختبارات وحدة
pytest tests/unit/test_voice_service.py -v

# اختبارات تكامل
pytest tests/integration/test_voice_api_integration.py -v

# اختبارات مع Whisper الحقيقي
pytest tests/integration/test_voice_api_integration.py::TestRealServiceIntegration -v -m integration

# جميع الاختبارات
pytest tests/ -v
```

### **2. اختبار سريع:**

```python
# اختبار سريع للخدمة
async def quick_test():
    voice_service = create_voice_service()
    
    # فحص الصحة
    health = await voice_service.health_check()
    print(f"حالة الخدمة: {health}")
    
    # اختبار مع صوت وهمي
    result = await voice_service.transcribe_audio(
        audio_data=b"test_audio_data",
        format=AudioFormat.WAV
    )
    
    print(f"نتيجة الاختبار: {result.text}")

import asyncio
asyncio.run(quick_test())
```

### **3. اختبار الأداء:**

```python
import time

async def performance_test():
    voice_service = create_voice_service()
    
    # تحميل ملف صوتي
    with open("test_audio.mp3", "rb") as f:
        audio_data = f.read()
    
    # قياس الأداء
    start_time = time.time()
    
    result = await voice_service.transcribe_audio(
        audio_data=audio_data,
        format=AudioFormat.MP3
    )
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    print(f"⏱️ إجمالي الوقت: {total_time:.1f}ms")
    print(f"🎵 مدة الصوت: {result.audio_duration_ms}ms")
    print(f"📊 عامل الوقت الفعلي: {total_time / result.audio_duration_ms:.2f}x")

asyncio.run(performance_test())
```

---

## 🔧 استكشاف الأخطاء

### **مشاكل شائعة وحلولها:**

#### **1. خطأ "Whisper model not available":**
```bash
# الحل: تثبيت Whisper
pip install openai-whisper

# أو استخدام مزود آخر
export STT_PROVIDER=azure
```

#### **2. خطأ "ffmpeg not found":**
```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# أو تحميل من الموقع الرسمي
```

#### **3. خطأ "Audio conversion failed":**
```python
# تحقق من تنسيق الصوت
print(f"تنسيق الملف: {file_format}")

# جرب تحويل يدوي
from pydub import AudioSegment
audio = AudioSegment.from_file("audio.mp3")
audio.export("converted.wav", format="wav")
```

#### **4. مشكلة في الأداء:**
```python
# استخدم نموذج أصغر
config.whisper_model = WhisperModel.TINY

# أو قلل جودة الصوت
# تحويل إلى 16kHz قبل الإرسال
```

#### **5. خطأ "Azure Speech not configured":**
```bash
# تعيين متغيرات البيئة
export AZURE_SPEECH_KEY=your_key
export AZURE_SPEECH_REGION=eastus

# أو في الكود
config.azure_key = "your_key"
config.azure_region = "eastus"
```

---

## 📊 مراقبة الأداء

### **1. مؤشرات الأداء الرئيسية:**

```python
async def monitor_performance():
    result = await voice_service.transcribe_audio(...)
    
    # مؤشرات مهمة
    print(f"🎯 الثقة: {result.confidence:.2%}")
    print(f"⏱️ وقت المعالجة: {result.processing_time_ms}ms")
    print(f"🎵 مدة الصوت: {result.audio_duration_ms}ms")
    print(f"📏 نسبة الوقت الفعلي: {result.processing_time_ms / result.audio_duration_ms:.1f}x")
    
    # metadata إضافية
    if "compression_ratio" in result.metadata:
        print(f"📦 نسبة الضغط: {result.metadata['compression_ratio']:.1f}x")
```

### **2. رصد صحة النظام:**

```python
async def system_health_check():
    health = await voice_service.health_check()
    
    print("🏥 فحص صحة النظام:")
    print(f"   الخدمة: {health['service']}")
    print(f"   Whisper: {health['dependencies']['whisper']}")
    print(f"   Azure: {health['dependencies']['azure_speech']}")
    print(f"   pydub: {health['dependencies']['pydub']}")
    
    for provider, status in health['providers'].items():
        print(f"   {provider}: {status}")
```

---

## 🚀 نصائح للإنتاج

### **1. تحسين الأداء:**
- **استخدم Whisper Base أو Small** للتوازن بين السرعة والدقة
- **فعل ffmpeg** لتحويل أسرع للتنسيقات
- **استخدم الضغط MP3** من ESP32 لتوفير bandwidth
- **راقب استهلاك الذاكرة** خاصة مع النماذج الكبيرة

### **2. تحسين الجودة:**
- **استخدم sample rate 16kHz** للكلام
- **تحسين جودة الميكروفون** على ESP32
- **فلترة الضوضاء** قبل الإرسال
- **استخدم Azure** للتحليل المتقدم إذا كان متاحاً

### **3. إدارة الأخطاء:**
- **فعل نظام fallback** دائماً
- **راقب معدل النجاح** والثقة
- **سجل الأخطاء** للتحليل
- **استخدم retry logic** للطلبات المهمة

### **4. الأمان:**
- **شفر الصوت** أثناء النقل
- **احم مفاتيح API** (Azure, OpenAI)
- **حدد حجم الملفات** المقبولة
- **راقب استهلاك الموارد** لمنع DoS

---

## 📱 تكامل مع أجزاء المشروع

### **العلاقة مع النظام الكامل:**

```
ESP32 Device
    ↓ (MP3 Audio)
FastAPI Endpoint (/api/voice/esp32/audio)
    ↓
Voice Service (STT)
    ↓ (Transcribed Text)
AI Service (Response Generation)
    ↓ (AI Response)
Response to ESP32
    ↓
Child Interaction
```

### **تكامل مع قاعدة البيانات:**
```python
# حفظ نتائج التحويل
async def save_transcription(result, device_id):
    transcription_data = {
        "device_id": device_id,
        "text": result.text,
        "confidence": result.confidence,
        "provider": result.provider,
        "timestamp": datetime.now(),
        "processing_time_ms": result.processing_time_ms
    }
    
    # حفظ في قاعدة البيانات
    await database.save_transcription(transcription_data)
```

---

## 🎯 خارطة الطريق المستقبلية

### **ميزات قادمة:**
- 🎯 **دعم لغات متعددة** (إنجليزية، فرنسية، إسبانية)
- 🔊 **تحسين جودة الصوت** التلقائي
- 📱 **دعم WebRTC** للصوت المباشر
- 🤖 **تكامل مع نماذج LLM محلية**
- 📊 **analytics متقدمة** لتحسين الدقة
- 🔒 **تشفير end-to-end** للخصوصية

### **تحسينات تقنية:**
- ⚡ **تحسين السرعة** باستخدام GPU
- 💾 **تحسين استهلاك الذاكرة**
- 🌐 **دعم clustering** للتوسع
- 📈 **مراقبة متقدمة** مع Prometheus
- 🐳 **containerization** محسن

---

**🎉 خدمة الصوت جاهزة للاستخدام!**

مع هذا الدليل، يمكنك الآن تفعيل تحويل الكلام إلى نص بكفاءة عالية في مشروع AI Teddy Bear، مع دعم كامل للصوت المضغوط من ESP32 وتكامل سلس مع باقي مكونات النظام. 