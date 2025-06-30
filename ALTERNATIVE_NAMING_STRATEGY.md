# 🏷️ استراتيجيات بديلة لتسمية مجلدات DDD

## 🎯 **البدائل المتاحة:**

### 1️⃣ **الطريقة الحالية (آمنة):**
```bash
src/application/services/
├── data_cleanup_service.py        # Original
├── cleanup_ddd/                   # DDD version
├── memory_service.py              # Original  
└── memory_ddd/                    # DDD version
```
**فوائد:** ✅ آمن، ✅ واضح، ✅ لا تضارب

---

### 2️⃣ **استخدام مجلد منفصل:**
```bash
src/
├── application/services/          # الملفات الأصلية
│   ├── data_cleanup_service.py
│   ├── memory_service.py
│   └── moderation_service.py
└── domains/                       # DDD domains منفصلة
    ├── cleanup/
    ├── memory/
    └── moderation/
```
**فوائد:** ✅ أسماء طبيعية، ✅ فصل واضح

---

### 3️⃣ **إعادة تسمية الملفات القديمة:**
```bash
src/application/services/
├── legacy/                        # نقل الملفات القديمة
│   ├── data_cleanup_service.py
│   ├── memory_service.py
│   └── moderation_service.py
├── cleanup/                       # أسماء طبيعية للـ DDD
├── memory/
└── moderation/
```
**فوائد:** ✅ أسماء طبيعية، ✅ تنظيم واضح

---

### 4️⃣ **استخدام prefixes:**
```bash
src/application/services/
├── data_cleanup_service.py        # Legacy
├── ddd_cleanup/                   # DDD with prefix
├── memory_service.py              # Legacy
└── ddd_memory/                    # DDD with prefix
```

---

## 🚀 **التوصية:**

**للمشاريع الجديدة:** استخدم البديل رقم 2 (مجلد domains منفصل)
**للمشاريع الموجودة:** استخدم الطريقة الحالية (`_ddd`) لتجنب المشاكل

---

## 🔄 **إذا كنت تريد تغيير التسمية الآن:**

```bash
# يمكننا تغيير:
cleanup_ddd/        → cleanup/
memory_ddd/         → memory/  
emotion_ddd/        → emotion/

# بعد نقل أو حذف الملفات الأصلية
``` 