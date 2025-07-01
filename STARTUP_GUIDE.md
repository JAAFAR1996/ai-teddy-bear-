# 🚀 دليل تشغيل مشروع AI Teddy Bear الشامل

## 📋 **المتطلبات الأساسية**

### **1. متطلبات النظام:**
- **Python 3.11+** (مهم جداً!)
- **Node.js 18+** و **npm**
- **Git** لاستنساخ المشروع
- **Docker & Docker Compose** (اختياري للنشر السهل)

### **2. فحص متطلبات النظام:**
```bash
# فحص Python
python --version  # يجب أن يكون 3.11+

# فحص Node.js
node --version    # يجب أن يكون 18+

# فحص Git
git --version

# فحص Docker (اختياري)
docker --version
docker-compose --version
```

---

## 🎯 **الطريقة الأولى: التشغيل السريع (مبتدئ)**

### **الخطوة 1: تحضير البيئة**
```bash
# إنتقل إلى مجلد المشروع
cd "C:\Users\jaafa\Desktop\5555\New folder"

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة (Windows)
venv\Scripts\activate
# أو على Mac/Linux
# source venv/bin/activate
```

### **الخطوة 2: تثبيت المتطلبات**
```bash
# تثبيت متطلبات Python
pip install -r requirements.txt

# الإنتقال لمجلد Frontend وتثبيت متطلبات Node.js
cd frontend
npm install
cd ..
```

### **الخطوة 3: إعداد المشروع التلقائي**
```bash
# تشغيل إعداد المشروع التلقائي
python src/setup.py
```

### **الخطوة 4: إنشاء ملف البيئة**
```bash
# إنشاء ملف .env آمن
python scripts/generate_env.py
```

### **الخطوة 5: التشغيل**
```bash
# تشغيل Backend
python src/main.py

# في terminal جديد، تشغيل Frontend
cd frontend
npm start
```

### **النتائج:**
- **Backend API:** http://localhost:8000
- **Frontend Dashboard:** http://localhost:3000
- **WebSocket:** ws://localhost:8765
- **Health Check:** http://localhost:8000/health

---

## 🔧 **الطريقة الثانية: التشغيل اليدوي المتقدم**

### **1. إعداد قاعدة البيانات:**
```bash
# إنشاء قاعدة البيانات
mkdir -p data
python -c "
from src.infrastructure.persistence.database import Database
db = Database()
print('✅ Database initialized')
"
```

### **2. إعداد Redis (اختياري):**
```bash
# تثبيت وتشغيل Redis (Windows)
# تحميل Redis من: https://github.com/microsoftarchive/redis/releases
# أو باستخدام Docker:
docker run -d --name teddy-redis -p 6379:6379 redis:alpine
```

### **3. تشغيل مكونات منفصلة:**
```bash
# Terminal 1: FastAPI Server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: WebSocket Server
python -c "
import asyncio
from src.infrastructure.websocket.websocket_handler import WebSocketHandler
handler = WebSocketHandler()
asyncio.run(handler.start_server())
"

# Terminal 3: Frontend
cd frontend && npm start

# Terminal 4: Monitoring (اختياري)
python -m prometheus_client.start_http_server 9090
```

---

## 🐳 **الطريقة الثالثة: Docker للمطورين**

### **1. إنشاء ملف .env:**
```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديل المفاتيح المطلوبة
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

### **2. تشغيل بـ Docker Compose:**
```bash
# تشغيل فقط الخدمات الأساسية
docker-compose up -d postgres redis

# تشغيل المشروع كاملاً
docker-compose -f docker-compose.production.yml up -d

# مراقبة اللوجز
docker-compose logs -f backend frontend
```

### **3. الوصول للخدمات:**
- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **Grafana Monitoring:** http://localhost:3000
- **Prometheus:** http://localhost:9090

---

## 🏢 **الطريقة الرابعة: النشر الكامل (Production)**

### **1. إعداد البيئة الإنتاجية:**
```bash
# إنشاء ملف البيئة الإنتاجية
cat > .env.production << EOF
# Database
DATABASE_URL=postgresql://teddy:secure_password@localhost:5432/ai_teddy_bear
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your_real_openai_key
ANTHROPIC_API_KEY=your_real_anthropic_key
GOOGLE_API_KEY=your_real_google_key

# Security
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EOF
```

### **2. تشغيل البنية الكاملة:**
```bash
# تشغيل كل شيء مع المراقبة
docker-compose -f docker-compose.production.yml up -d

# فحص حالة الخدمات
docker-compose ps

# فحص اللوجز
docker-compose logs -f
```

### **3. خدمات المراقبة:**
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Kibana:** http://localhost:5601
- **Traefik Dashboard:** http://localhost:8080

---

## ⚡ **سكريبتات التشغيل السريع**

### **للـ Windows:**
```batch
REM ملف: start_teddy.bat
@echo off
echo 🚀 Starting AI Teddy Bear...

REM تفعيل البيئة الافتراضية
call venv\Scripts\activate

REM تشغيل Backend
start "Teddy Backend" python src/main.py

REM انتظار قليل
timeout /t 5

REM تشغيل Frontend
start "Teddy Frontend" cmd /k "cd frontend && npm start"

echo ✅ Teddy Bear is starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
pause
```

### **للـ Mac/Linux:**
```bash
#!/bin/bash
# ملف: start_teddy.sh
echo "🚀 Starting AI Teddy Bear..."

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تشغيل Backend في الخلفية
python src/main.py &
BACKEND_PID=$!

# انتظار قليل
sleep 5

# تشغيل Frontend
cd frontend && npm start &
FRONTEND_PID=$!

echo "✅ Teddy Bear is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop..."

# انتظار إيقاف
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

---

## 🔐 **إعداد مفاتيح API**

### **1. المفاتيح المطلوبة:**
```env
# ملف .env
OPENAI_API_KEY=sk-...                    # OpenAI GPT-4
ANTHROPIC_API_KEY=ant-api03...           # Claude
GOOGLE_API_KEY=AIza...                   # Gemini
ELEVENLABS_API_KEY=...                   # Text-to-Speech
HUME_API_KEY=...                         # Emotion Analysis
```

### **2. كيفية الحصول على المفاتيح:**

#### **OpenAI:**
1. اذهب إلى: https://platform.openai.com/api-keys
2. أنشئ حساب ومشروع جديد
3. انقر "Create new secret key"
4. انسخ المفتاح وضعه في `.env`

#### **Anthropic Claude:**
1. اذهب إلى: https://console.anthropic.com/
2. أنشئ حساب
3. اذهب لـ "API Keys"
4. أنشئ مفتاح جديد

#### **Google Gemini:**
1. اذهب إلى: https://makersuite.google.com/app/apikey
2. أنشئ مفتاح API جديد
3. فعّل Gemini API

#### **ElevenLabs:**
1. اذهب إلى: https://elevenlabs.io/
2. أنشئ حساب
3. اذهب لـ "Profile" > "API Key"

---

## 🧪 **اختبار التشغيل**

### **1. فحص الخدمات:**
```bash
# فحص صحة Backend
curl http://localhost:8000/health

# فحص WebSocket
curl -H "Upgrade: websocket" http://localhost:8765/ws

# فحص Frontend
curl http://localhost:3000
```

### **2. اختبار التفاعل:**
```bash
# اختبار AI API
curl -X POST http://localhost:8000/api/v1/interact \
  -H "Content-Type: application/json" \
  -d '{"message": "مرحبا", "child_id": "test-child"}'
```

---

## 🐛 **حل المشاكل الشائعة**

### **1. Python Version Error:**
```bash
# إذا كان Python قديم
Error: Python 3.11+ required

# الحل:
# تحميل Python 3.11+ من: https://python.org
# أو باستخدام pyenv:
pyenv install 3.11.7
pyenv global 3.11.7
```

### **2. Port Already in Use:**
```bash
# إذا كان المنفذ مستخدم
Error: Port 8000 already in use

# الحل (Windows):
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# الحل (Mac/Linux):
lsof -i :8000
kill -9 [PID]
```

### **3. Missing Dependencies:**
```bash
# إذا كانت المكاتب مفقودة
ModuleNotFoundError: No module named 'xyz'

# الحل:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **4. Database Errors:**
```bash
# إذا كانت قاعدة البيانات معطلة
Database connection failed

# الحل:
rm -rf data/teddy_bear.db
python src/setup.py
```

### **5. Frontend Build Errors:**
```bash
# إذا كان Frontend لا يعمل
npm ERR! missing dependencies

# الحل:
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📊 **مراقبة الأداء**

### **1. معلومات النظام:**
```bash
# استخدام CPU والذاكرة
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"
```

### **2. لوجز المشروع:**
```bash
# مراقبة لوجز Backend
tail -f logs/app.log

# مراقبة لوجز Frontend (في Development)
# اللوجز ستظهر في terminal
```

### **3. قواعد البيانات:**
```bash
# فحص قاعدة البيانات
python -c "
from src.infrastructure.persistence.database import Database
db = Database()
print('Tables:', db.get_table_names())
"
```

---

## 🚀 **توصيات للبداية**

### **للمطورين الجدد:**
1. **ابدأ بالطريقة الأولى** (التشغيل السريع)
2. **تأكد من المتطلبات** قبل البدء
3. **استخدم scripts التشغيل** السريع

### **للمطورين المتقدمين:**
1. **استخدم Docker** للتطوير
2. **فعّل المراقبة** (Prometheus + Grafana)
3. **اختبر الـ APIs** باستمرار

### **للإنتاج:**
1. **استخدم الطريقة الرابعة** (Production)
2. **فعّل جميع خدمات المراقبة**
3. **استخدم مفاتيح API حقيقية**
4. **فعّل SSL/TLS**

---

## 📞 **الدعم والمساعدة**

### **موارد مفيدة:**
- **التوثيق الكامل:** `docs/`
- **أمثلة الاستخدام:** `tests/integration/`
- **إعدادات المراقبة:** `monitoring/`

### **أوامر سريعة:**
```bash
# فحص حالة النظام
python scripts/health_check.py

# إعادة تشغيل سريع
./restart_teddy.sh

# نسخ احتياطي
python scripts/backup_system.py
```

---

## ✅ **قائمة التحقق قبل التشغيل**

- [ ] Python 3.11+ مثبت
- [ ] Node.js 18+ مثبت  
- [ ] تم تثبيت المتطلبات (`pip install -r requirements.txt`)
- [ ] تم إنشاء ملف `.env`
- [ ] تم إضافة مفاتيح API
- [ ] تم تشغيل `python src/setup.py`
- [ ] Frontend dependencies مثبتة (`npm install`)
- [ ] المنافذ 8000 و 3000 متاحة

**🎉 عند إكمال كل هذه الخطوات، مشروعك جاهز للتشغيل!** 