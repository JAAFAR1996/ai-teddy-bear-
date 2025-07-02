# 🧸 دليل مرجعي سريع - تقسيم ملفات الدب الذكي

## 📂 التقسيم السريع

### 🖥️ على السيرفر السحابي (Cloud):
```
✅ DEPLOY TO SERVER:
src/main.py                    # السيرفر الرئيسي
src/domain/                    # منطق العمل
src/application/               # خدمات التطبيق  
src/infrastructure/            # قواعد البيانات والAI
src/presentation/              # APIs

config/config.json             # إعدادات السيرفر
requirements_from_core.txt     # مكتبات Python
docker-compose.*.yml           # ملفات النشر
monitoring/                    # مراقبة الأداء
```

### 🎛️ على جهاز ESP32 (الدب):
```
✅ UPLOAD TO ESP32:
esp32/teddy_main.ino          # الكود الرئيسي (ابدأ هنا)
esp32/audio_processor.h       # معالج الصوت
esp32/secure_config.h         # إعدادات الأمان
esp32/ws_handler.ino          # اتصال WebSocket

🔧 HARDWARE NEEDED:
- ESP32 DevKit
- I2S microphone  
- I2S speaker
- 3 buttons
- WS2812B LEDs
```

### 📱 على متصفح الأهل (Web App):
```
✅ DEPLOY TO WEB:
frontend/build/               # التطبيق المبني (بعد npm run build)
frontend/src/                 # الكود المصدري
frontend/package.json         # مكتبات JavaScript
```

---

## ⚡ البدء السريع

### 1️⃣ شغّل السيرفر:
```bash
cd src/
python main.py
```

### 2️⃣ برمج ESP32:
```cpp
// افتح: esp32/teddy_main.ino
// غيّر:
const char* ssid = "YOUR_WIFI";
const char* server_url = "http://YOUR_SERVER:8000";
// ارفع للـ ESP32
```

### 3️⃣ افتح التطبيق:
```bash
cd frontend/
npm start
# افتح: http://localhost:3000
```

---

## 🔗 كيف يعمل النظام

```
1. طفل يضغط زر → ESP32 يسجل
2. ESP32 يرسل صوت → السيرفر يحلل  
3. السيرفر يرسل رد → ESP32 يشغل
4. الأهل يراقبون → عبر التطبيق
```

---

## 📋 Checklist للنشر

### ☑️ السيرفر جاهز:
- [ ] `src/main.py` يعمل
- [ ] قاعدة البيانات متصلة
- [ ] API keys موضوعة في `config/`
- [ ] Docker يعمل (اختياري)

### ☑️ ESP32 جاهز:
- [ ] Arduino IDE مثبت
- [ ] مكتبات ESP32 مثبتة (WiFi, ArduinoJson, FastLED)
- [ ] `esp32/teddy_main.ino` محدث بإعدادات WiFi
- [ ] الكود مرفوع للجهاز

### ☑️ التطبيق جاهز:
- [ ] Node.js مثبت
- [ ] `npm install` تم تشغيله
- [ ] `frontend/.env` محدث برابط السيرفر
- [ ] `npm run build` للنشر

---

## 🆘 مساعدة سريعة

**ESP32 لا يتصل؟**
- تأكد من WiFi credentials
- تأكد من رابط السيرفر صحيح
- افحص Serial Monitor في Arduino IDE

**السيرفر لا يعمل؟**
- تأكد من Python dependencies: `pip install -r requirements_from_core.txt`
- تأكد من port 8000 فارغ: `netstat -an | grep 8000`

**التطبيق لا يظهر بيانات؟**
- تأكد من CORS enabled في السيرفر
- تأكد من API URL صحيح في `.env`
- افحص Network tab في Browser DevTools

---

## 🎯 النصائح الذهبية

1. **ابدأ بالبساطة**: استخدم `esp32/teddy_main.ino` أولاً
2. **اختبر السيرفر أولاً**: تأكد أنه يعمل قبل ESP32
3. **استخدم Serial Monitor**: لمراقبة ESP32
4. **لا تضع API keys في ESP32**: ضعها في السيرفر فقط
5. **استخدم HTTPS في الإنتاج**: لا HTTP

---

## 📞 لمزيد من المساعدة

- **الدليل المفصل**: `PROJECT_DEPLOYMENT_GUIDE.md`
- **أمثلة عملية**: `PRACTICAL_DEPLOYMENT_EXAMPLES.md`
- **هيكل المشروع**: `COMPLETE_PROJECT_TREE.md` 