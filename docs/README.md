# AI Teddy Bear - دبدوب الذكي

## نظرة عامة

دبدوب الذكي هو مساعد ذكي تفاعلي للأطفال يستخدم تقنيات الذكاء الاصطناعي المتقدمة لتوفير تجربة تعليمية وترفيهية آمنة.

## الميزات الرئيسية

### 🤖 الذكاء الاصطناعي
- معالجة اللغة الطبيعية باللغة العربية
- فهم المشاعر والسياق
- استجابات تعليمية مخصصة حسب العمر

### 🎵 المعالجة الصوتية
- تحويل الكلام إلى نص (STT)
- تحويل النص إلى كلام (TTS)
- تحليل المشاعر من الصوت

### 🔒 الأمان والخصوصية
- تشفير شامل للبيانات
- مراقبة المحتوى
- ضوابط أبوية متقدمة

### 📱 تجربة المستخدم
- تطبيق ويب تقدمي (PWA)
- واجهة متجاوبة
- دعم العمل بدون إنترنت

## التثبيت والإعداد

### المتطلبات
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (للواجهة الأمامية)

### التثبيت السريع

```bash
# استنساخ المشروع
git clone https://github.com/your-org/ai-teddy-bear.git
cd ai-teddy-bear

# إنشاء البيئة الافتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
alembic upgrade head

# تشغيل الخادم
uvicorn src.main:app --reload
```

### متغيرات البيئة

```env
# قاعدة البيانات
DATABASE_URL=postgresql://user:password@localhost/teddybear

# Redis
REDIS_URL=redis://localhost:6379

# OpenAI
OPENAI_API_KEY=your-openai-key

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AWS (اختياري)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## استخدام API

### المصادقة

```python
import httpx

# تسجيل الدخول
response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "parent@example.com",
    "password": "password"
})

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### بدء محادثة

```python
# بدء محادثة جديدة
response = httpx.post(
    "http://localhost:8000/api/v1/conversations/start",
    json={"child_id": "child-123"},
    headers=headers
)

session_data = response.json()
print(f"Session ID: {session_data['session_id']}")
```

### إرسال رسالة

```python
# إرسال رسالة نصية
response = httpx.post(
    f"http://localhost:8000/api/v1/conversations/{session_id}/messages",
    json={"text": "مرحبا، كيف حالك؟"},
    headers=headers
)

ai_response = response.json()
print(f"AI Response: {ai_response['response_text']}")
```

## البنية المعمارية

```
src/
├── api/                 # طبقة API
│   ├── routes/         # مسارات API
│   ├── middleware/     # Middleware
│   └── docs/          # توثيق API
├── core/               # المنطق الأساسي
│   ├── domain/        # Domain Models
│   ├── application/   # Use Cases
│   └── infrastructure/# البنية التحتية
├── services/          # الخدمات الخارجية
│   ├── ai/           # خدمات AI
│   ├── audio/        # معالجة الصوت
│   └── grpc/         # خدمات gRPC
└── edge/             # Edge Computing
```

## المساهمة

نرحب بمساهماتكم! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) قبل البدء.

### خطوات المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# اختبارات الوحدة
pytest tests/unit/

# اختبارات التكامل
pytest tests/integration/

# اختبارات الأداء
locust -f tests/load/locustfile.py
```

## النشر

### Docker

```bash
# بناء الصورة
docker build -t ai-teddy-bear .

# تشغيل الحاوية
docker run -p 8000:8000 ai-teddy-bear
```

### Kubernetes

```bash
# نشر على Kubernetes
kubectl apply -f k8s/
```

## الدعم

- 📧 البريد الإلكتروني: support@teddybear.ai
- 💬 Discord: [رابط الخادم](https://discord.gg/teddybear)
- 📖 الوثائق: [docs.teddybear.ai](https://docs.teddybear.ai)

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## شكر وتقدير

- فريق OpenAI لتوفير GPT API
- مجتمع FastAPI
- جميع المساهمين في المشروع