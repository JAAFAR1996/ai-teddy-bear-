# 🚀 **دليل البدء مع البنية الجديدة - AI Teddy Bear v5**

## 🎯 **نقطة الدخول الجديدة**

```bash
# تشغيل التطبيق
python src/main.py

# إضافة src إلى Python path إذا لزم الأمر
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## 📦 **تثبيت التبعيات**

```bash
# تثبيت جميع التبعيات من الملف الموحد
pip install -r requirements.txt
```

## 🏗️ **استخدام الكيانات الجديدة**

```python
# استيراد الكيانات من المواقع الجديدة
import sys
sys.path.append('src')

from src.core.domain.entities.child import Child
from src.core.domain.entities.child_events import ChildRegistered

# إنشاء طفل جديد
child = Child(name="أحمد", age=7, device_id="device_123")
print(f"Child {child.name} created with ID: {child.id}")

# التحقق من إمكانية التفاعل
if child.can_interact():
    response = child.start_conversation("مرحبا!")
    print(response)
```

## 📁 **البنية الجديدة**

```
src/
├── main.py                    # 🚀 نقطة الدخول الموحدة
├── core/domain/entities/      # 🧠 الكيانات الأساسية
├── application/use_cases/     # 💼 حالات الاستخدام
├── infrastructure/           # 🔧 البنية التحتية
└── presentation/api/         # 🌐 واجهات API
```

## 🔧 **إعدادات البيئة**

```json
// config/environments/default.json
// config/environments/production.json
```

## 📦 **الملفات المؤرشفة**

جميع الملفات القديمة محفوظة في:
```
_archive/duplicates/
├── main_files/        # ملفات main.py القديمة
├── child_entities/    # كيانات Child المكررة
├── requirements/      # ملفات requirements القديمة
└── config/           # ملفات config المكررة
```

## ✅ **اختبار سريع**

```bash
# اختبار import
python -c "import sys; sys.path.append('src'); from src.core.domain.entities.child import Child; print('✅ OK')"

# اختبار إنشاء كيان
python -c "import sys; sys.path.append('src'); from src.core.domain.entities.child import Child; c=Child('Test', 5, 'dev'); print('✅ Child created:', c.name)"
```

## 🚀 **البدء في التطوير**

1. **استخدم البنية الجديدة** - جميع التطوير الجديد في `src/`
2. **اتبع Clean Architecture** - فصل الطبقات وفقاً للبنية
3. **راجع الأرشيف** - قبل إنشاء ملفات جديدة، تحقق من `_archive/`
4. **استخدم نقطة دخول واحدة** - `src/main.py` فقط

---

**🎉 مبروك! مشروع AI Teddy Bear v5 أصبح منظماً وجاهزاً للتطوير** 🧸✨ 