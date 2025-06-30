# Configuration Environments

هذا المجلد يحتوي على ملفات التكوين لبيئات مختلفة من مشروع AI-TEDDY-BEAR.

## ملفات التكوين المتاحة

- **`development.json`**: إعدادات بيئة التطوير المحلي
- **`production_config.json`**: إعدادات بيئة الإنتاج
- **`staging_config.json`**: إعدادات بيئة الاختبار

## الاستخدام

```python
# في كود Python
import json
from pathlib import Path

def load_config(environment='development'):
    config_path = Path(f'config/environments/{environment}.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# تحميل تكوين التطوير
dev_config = load_config('development')

# تحميل تكوين الإنتاج  
prod_config = load_config('production_config')
```

## ملاحظات مهمة

- ⚠️ **لا تضع أسرار أو كلمات مرور في هذه الملفات**
- 🔐 استخدم متغيرات البيئة للبيانات الحساسة
- 📝 أضف أي بيئة جديدة في هذا المجلد
- 🔄 تم دمج الملفات من التحليل الشامل للمشروع

---
**تم إنشاؤه**: 2025-06-30  
**بواسطة**: ArchitectureAnalyzer Pro v2.0 