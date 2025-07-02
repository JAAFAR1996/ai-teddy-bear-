# 🧸 محاكي الدب الذكي - AI Teddy Bear Simulator

## نظرة عامة

محاكي Python متقدم يحاكي جهاز ESP32 للدب الذكي، يوفر:
- **تسجيل صوتي** من الميكروفون مباشرة
- **إرسال مباشر** للسيرفر عبر HTTP أو WebSocket
- **استقبال وتشغيل** الرد الصوتي على السبيكر
- **واجهة GUI** سهلة الاستخدام
- **نظام مراقبة وتسجيل** متقدم

## 🚀 التشغيل السريع (Windows)

### الطريقة الأولى: تشغيل تلقائي (موصى بها)
```cmd
# 1. تثبيت المتطلبات (مرة واحدة فقط)
scripts\INSTALL_REQUIREMENTS.bat

# 2. تشغيل المحاكي
scripts\START_TEDDY_SIMULATOR.bat
```

### الطريقة الثانية: تشغيل يدوي
```cmd
# 1. تثبيت المتطلبات
pip install -r requirements_simulator.txt

# 2. تشغيل المحاكي
python scripts/teddy_bear_simulator.py
```

## 📋 المتطلبات الأساسية

### متطلبات النظام
- **Python 3.8+** (موصى بـ 3.11+)
- **Windows 10/11** (64-bit)
- **ميكروفون** وسبيكر متصلان بالجهاز
- **اتصال إنترنت** للتواصل مع السيرفر
- **Microsoft Visual C++ Redistributable** (للـ pyaudio)

### المكتبات المطلوبة
```
pyaudio==0.2.13        # تسجيل الصوت
pygame==2.5.2          # تشغيل الصوت
requests==2.31.0       # HTTP requests
aiohttp==3.9.1         # Async HTTP
websockets==12.0       # WebSocket communication
tkinter                # GUI (مدمجة مع Python)
```

## 🎯 كيفية الاستخدام

### 1. تشغيل المحاكي
- شغل الملف `START_TEDDY_SIMULATOR.bat`
- ستظهر واجهة المحاكي

### 2. الاتصال بالسيرفر
- اضغط زر **"اتصال"**
- تأكد من أن السيرفر يعمل على `localhost:5000`
- يجب أن تظهر رسالة "متصل" باللون الأخضر

### 3. تسجيل الصوت
- اضغط **"🎤 بدء التسجيل"**
- تحدث في الميكروفون (الحد الأقصى 10 ثوان)
- اضغط **"⏹️ إيقاف التسجيل"** عند الانتهاء

### 4. إرسال للسيرفر
- اختر بروتوكول الاتصال (HTTP أو WebSocket)
- اضغط **"📤 إرسال للسيرفر"**
- انتظر استلام الرد

### 5. تشغيل الرد
- اضغط **"🔊 تشغيل الرد"**
- سيتم تشغيل الرد الصوتي من السبيكر

## ⚙️ الإعدادات المتقدمة

### تغيير إعدادات الصوت
```python
class TeddyConfig:
    # Audio Configuration
    SAMPLE_RATE = 22050      # معدل العينات
    CHANNELS = 1             # قناة واحدة (مونو)
    CHUNK_SIZE = 1024        # حجم القطعة
    RECORD_SECONDS = 10      # الحد الأقصى للتسجيل
```

### تغيير إعدادات السيرفر
```python
class TeddyConfig:
    # Server Configuration
    SERVER_HOST = "localhost"    # عنوان السيرفر
    SERVER_PORT = 5000          # منفذ HTTP
    WEBSOCKET_PORT = 8765       # منفذ WebSocket
```

### تخصيص معلومات الطفل
```python
class TeddyConfig:
    # Device Configuration
    CHILD_NAME = "طفل تجريبي"   # اسم الطفل
    CHILD_AGE = 7               # عمر الطفل
```

## 🔧 استكشاف الأخطاء

### مشكلة عدم عمل الميكروفون على ويندوز
```cmd
# فحص الأجهزة الصوتية المتاحة
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)) for i in range(p.get_device_count())]"

# فحص صلاحيات الميكروفون
# اذهب إلى: Settings > Privacy & Security > Microphone
# تأكد من السماح للتطبيقات بالوصول للميكروفون
```

### إعدادات ويندوز للصوت
1. **تفعيل الميكروفون**:
   - كليك يمين على أيقونة الصوت
   - اختر "Open Sound settings"
   - تحت "Input" اختر الميكروفون الصحيح

2. **إعطاء الصلاحيات**:
   - Settings > Privacy & Security > Microphone
   - تأكد من تفعيل "Let apps access your microphone"

### مشكلة عدم تثبيت pyaudio على ويندوز
```cmd
# الطريقة الأولى: استخدام pipwin
pip install pipwin
pipwin install pyaudio

# الطريقة الثانية: تحميل wheel file
# اذهب إلى https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# حمل الملف المناسب لإصدار Python الخاص بك
# مثال: PyAudio-0.2.11-cp311-cp311-win_amd64.whl
pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl

# الطريقة الثالثة: تثبيت Visual Studio Build Tools
# حمل من: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# ثم جرب: pip install pyaudio
```

### مشكلة عدم الاتصال بالسيرفر
1. تأكد من تشغيل السيرفر على المنفذ المناسب
2. فحص الـ firewall
3. تجربة تغيير عنوان السيرفر في الإعدادات

## 📊 واجهة المحاكي

### أقسام الواجهة

1. **معلومات الجهاز**
   - معرف الجهاز الفريد (UDID)
   - اسم وعمر الطفل

2. **الاتصال بالسيرفر**
   - حالة الاتصال (متصل/غير متصل)
   - زر الاتصال/قطع الاتصال

3. **التحكم في الصوت**
   - زر التسجيل/الإيقاف
   - زر الإرسال للسيرفر
   - زر تشغيل الرد

4. **بروتوكول الاتصال**
   - HTTP API (افتراضي)
   - WebSocket (للاتصال المباشر)

5. **عرض الرد**
   - عرض JSON للرد من السيرفر
   - تفاصيل النص والصوت

6. **سجل الأحداث**
   - مراقبة العمليات في الوقت الفعلي
   - رسائل الأخطاء والتنبيهات

## 🌐 بروتوكولات الاتصال

### HTTP API Mode
- يستخدم REST API endpoints
- مناسب للتطبيقات البسيطة
- يدعم multipart file upload

### WebSocket Mode
- اتصال مباشر ومستمر
- أسرع في الاستجابة
- يدعم الرسائل المباشرة

## 📁 هيكل الملفات

```
scripts/
├── teddy_bear_simulator.py      # المحاكي الرئيسي
├── START_TEDDY_SIMULATOR.bat    # ملف التشغيل
├── INSTALL_REQUIREMENTS.bat     # ملف تثبيت المتطلبات
└── README_SIMULATOR.md          # هذا الملف

logs/
└── teddy_simulator.log          # ملف السجل

%TEMP%/
├── teddy_recording.wav          # التسجيل المؤقت
└── teddy_response.wav           # الرد المؤقت
```

## 🔐 الأمان والخصوصية

- **تشفير البيانات**: جميع البيانات المرسلة مشفرة
- **معرف فريد**: كل جهاز له UDID فريد
- **ملفات مؤقتة**: يتم حذف الملفات المؤقتة تلقائياً
- **عدم تخزين**: لا يتم تخزين التسجيلات محلياً

## 🚨 الأخطاء الشائعة

### `ModuleNotFoundError: No module named 'pyaudio'`
```bash
pip install pyaudio
# أو للنوافذ:
pip install pipwin
pipwin install pyaudio
```

### `Permission denied` لـ microphone
- تأكد من إعطاء صلاحيات الميكروفون للتطبيق
- على Windows: Settings > Privacy > Microphone

### `Connection refused`
- تأكد من تشغيل السيرفر
- فحص المنافذ والـ firewall

## 📞 الدعم

للحصول على المساعدة:
1. راجع سجل الأحداث في الواجهة
2. فحص ملف `logs/teddy_simulator.log`
3. تأكد من تشغيل السيرفر
4. فحص إعدادات الصوت في النظام

## 🔄 التحديثات المستقبلية

- [ ] دعم TTS محلي
- [ ] تسجيل متعدد القنوات
- [ ] واجهة ويب
- [ ] دعم المزيد من صيغ الصوت
- [ ] إعدادات متقدمة للضوضاء

---

**🧸 محاكي الدب الذكي - تجربة تفاعلية متقدمة للأطفال** 