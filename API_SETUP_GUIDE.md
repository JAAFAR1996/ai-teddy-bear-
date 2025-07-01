# 🔐 **دليل إعداد API Keys - AI Teddy Bear**

## 📍 **المكان الصحيح: ملف `.env` في جذر المشروع**

```
New folder/          ← هنا مجلد المشروع
├── .env            ← هنا ضع API Keys (الملف الصحيح)
├── config/
├── src/
└── ...
```

---

## 🎯 **الخطوات:**

### **1. تحرير ملف `.env`:**
```bash
# في جذر المشروع:
notepad .env        # Windows
nano .env           # Linux/Mac
```

### **2. إضافة مفاتيحك:**
```env
# الأساسي - مطلوب:
TEDDY_OPENAI_API_KEY=sk-your_real_openai_key_here

# الصوت - مطلوب:
TEDDY_ELEVENLABS_API_KEY=your_real_elevenlabs_key_here

# إضافي - اختياري:
TEDDY_ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

---

## 🔑 **المفاتيح المطلوبة:**

### **🎯 للتشغيل الأساسي:**
| المفتاح | المطلوب | الاستخدام |
|---------|---------|-----------|
| `TEDDY_OPENAI_API_KEY` | ✅ **مطلوب** | للردود الذكية |
| `TEDDY_ELEVENLABS_API_KEY` | ⚠️ مستحسن | للصوت عالي الجودة |

### **🚀 للتشغيل المتقدم:**
| المفتاح | الاستخدام |
|---------|-----------|
| `TEDDY_ANTHROPIC_API_KEY` | Claude AI كبديل |
| `TEDDY_AZURE_SPEECH_KEY` | Azure Speech |
| `TEDDY_GOOGLE_GEMINI_API_KEY` | Google Gemini |
| `TEDDY_HUME_API_KEY` | تحليل المشاعر |

---

## 🏪 **كيفية الحصول على المفاتيح:**

### **🤖 OpenAI (مطلوب):**
1. اذهب إلى: https://platform.openai.com/api-keys
2. سجل حساب جديد أو ادخل
3. اضغط "Create new secret key"
4. انسخ المفتاح: `sk-...`
5. ضعه في `.env`:
   ```env
   TEDDY_OPENAI_API_KEY=sk-your_actual_key_here
   ```

### **🎤 ElevenLabs (للصوت):**
1. اذهب إلى: https://elevenlabs.io
2. سجل حساب
3. اذهب إلى Profile → API Keys
4. انسخ المفتاح
5. ضعه في `.env`:
   ```env
   TEDDY_ELEVENLABS_API_KEY=your_actual_key_here
   ```

### **🔮 Anthropic (اختياري):**
1. اذهب إلى: https://console.anthropic.com
2. احصل على API key
3. ضعه في `.env`:
   ```env
   TEDDY_ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
   ```

---

## ⚡ **تشغيل سريع بمفتاح واحد:**

```env
# للتجربة السريعة - مفتاح واحد فقط:
TEDDY_OPENAI_API_KEY=sk-your_openai_key_here

# باقي الإعدادات تلقائية
```

---

## 🔧 **التحقق من الإعدادات:**

### **بعد وضع المفاتيح:**
```bash
# تشغيل النظام:
start_teddy.bat

# فحص صحة المفاتيح:
python health_check.py
```

### **إذا نجح:**
```
✅ OpenAI API: Connected
✅ ElevenLabs API: Connected  
✅ System Health: OK
```

---

## 🚨 **أخطاء شائعة:**

### **❌ "ملف .env غير موجود":**
```bash
# أنشئ الملف:
echo. > .env    # Windows
touch .env      # Linux/Mac
```

### **❌ "API key invalid":**
- تأكد من نسخ المفتاح كاملاً
- تأكد من عدم وجود مسافات زائدة
- تأكد من صحة اسم المتغير `TEDDY_`

### **❌ "Permission denied":**
- تأكد من الحساب مفعّل
- تأكد من وجود رصيد (للمفاتيح المدفوعة)

---

## 💡 **نصائح مهمة:**

### **🔐 الأمان:**
- **لا تشارك** ملف `.env` مع أحد
- **لا ترفعه** على GitHub
- **احتفظ بنسخة احتياطية** آمنة

### **💰 التكلفة:**
- **OpenAI:** مدفوع بالاستخدام ($0.03/1K tokens)
- **ElevenLabs:** 10K حرف مجاناً شهرياً
- **Anthropic:** $15 رصيد مجاني

### **⚡ للتوفير:**
```env
# استخدم مودل أرخص:
TEDDY_OPENAI_MODEL=gpt-3.5-turbo  # بدلاً من gpt-4

# أو استخدم البدائل المجانية في الكود
```

---

## 📋 **قالب جاهز:**

```env
# انسخ هذا والصق في .env واستبدل المفاتيح:

# 🎯 الأساسي (مطلوب):
TEDDY_OPENAI_API_KEY=sk-your_openai_key_here

# 🎤 الصوت (مستحسن):  
TEDDY_ELEVENLABS_API_KEY=your_elevenlabs_key_here

# 🚀 إضافي (اختياري):
TEDDY_ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
TEDDY_AZURE_SPEECH_KEY=your_azure_key_here
TEDDY_AZURE_SPEECH_REGION=eastus

# 🔐 الأمان (تلقائي):
TEDDY_SECRET_KEY=auto_generated_secure_key
TEDDY_ENCRYPTION_KEY=auto_generated_encryption_key
TEDDY_JWT_SECRET=auto_generated_jwt_secret

# 🌍 البيئة:
TEDDY_ENVIRONMENT=development
TEDDY_DEBUG=true
```

---

## 🎉 **بعد الانتهاء:**

```bash
# تشغيل المشروع:
start_teddy.bat

# تشغيل المحاكي:
python src/simulators/esp32_production_simulator.py

# الاستمتاع بالدمية الذكية! 🧸
```

**🎯 المفتاح الواحد `TEDDY_OPENAI_API_KEY` كافي للبدء!** 