
# 📝 دليل تحديث الاستيرادات بعد إعادة التوزيع

**التاريخ**: 2025-06-30 05:32:13

## 🎯 الملفات المنقولة والاستيرادات الجديدة


### llm_service
**من**: `deprecated.services.ai_services.llm_service`  
**إلى**: `src.application.services.ai.llm_servicepy`

```python
# بدلاً من:
# from deprecated.services.ai_services.llm_service import LlmService

# استخدم:
from src.application.services.ai.llm_servicepy import LlmService
```

### main_service
**من**: `deprecated.services.ai_services.main_service`  
**إلى**: `src.application.services.ai.main_servicepy`

```python
# بدلاً من:
# from deprecated.services.ai_services.main_service import MainService

# استخدم:
from src.application.services.ai.main_servicepy import MainService
```

### llm_service_factory
**من**: `deprecated.services.ai_services.llm_service_factory`  
**إلى**: `src.application.services.ai.llm_service_factorypy`

```python
# بدلاً من:
# from deprecated.services.ai_services.llm_service_factory import LlmServiceFactory

# استخدم:
from src.application.services.ai.llm_service_factorypy import LlmServiceFactory
```

### transcription_service
**من**: `deprecated.services.audio_services.transcription_service`  
**إلى**: `src.application.services.audio.transcription_servicepy`

```python
# بدلاً من:
# from deprecated.services.audio_services.transcription_service import TranscriptionService

# استخدم:
from src.application.services.audio.transcription_servicepy import TranscriptionService
```

### voice_interaction_service
**من**: `deprecated.services.audio_services.voice_interaction_service`  
**إلى**: `src.application.services.audio.voice_interaction_servicepy`

```python
# بدلاً من:
# from deprecated.services.audio_services.voice_interaction_service import VoiceInteractionService

# استخدم:
from src.application.services.audio.voice_interaction_servicepy import VoiceInteractionService
```

### synthesis_service
**من**: `deprecated.services.audio_services.synthesis_service`  
**إلى**: `src.application.services.audio.synthesis_servicepy`

```python
# بدلاً من:
# from deprecated.services.audio_services.synthesis_service import SynthesisService

# استخدم:
from src.application.services.audio.synthesis_servicepy import SynthesisService
```

### simple_cache_service
**من**: `deprecated.services.cache_services.simple_cache_service`  
**إلى**: `src.infrastructure.services.data.simple_cache_servicepy`

```python
# بدلاً من:
# from deprecated.services.cache_services.simple_cache_service import SimpleCacheService

# استخدم:
from src.infrastructure.services.data.simple_cache_servicepy import SimpleCacheService
```

### issue_tracker_service
**من**: `deprecated.services.monitoring_services.issue_tracker_service`  
**إلى**: `src.infrastructure.services.monitoring.issue_tracker_servicepy`

```python
# بدلاً من:
# from deprecated.services.monitoring_services.issue_tracker_service import IssueTrackerService

# استخدم:
from src.infrastructure.services.monitoring.issue_tracker_servicepy import IssueTrackerService
```

### simple_health_service
**من**: `deprecated.services.monitoring_services.simple_health_service`  
**إلى**: `src.infrastructure.services.monitoring.simple_health_servicepy`

```python
# بدلاً من:
# from deprecated.services.monitoring_services.simple_health_service import SimpleHealthService

# استخدم:
from src.infrastructure.services.monitoring.simple_health_servicepy import SimpleHealthService
```


## 🔍 البحث والاستبدال السريع

يمكنك استخدام هذه الأوامر للبحث والاستبدال:

```bash
# البحث عن الاستيرادات القديمة
grep -r "from deprecated.services" src/
grep -r "import.*deprecated.services" src/

# استبدال سريع (مثال)
find src/ -name "*.py" -exec sed -i 's/from deprecated.services/from src.application.services/g' {} +
```

## 📋 الخطوات التالية:
1. **فحص جميع ملفات Python** للاستيرادات القديمة
2. **تحديث الاستيرادات** حسب الجدول أعلاه  
3. **اختبار المشروع** للتأكد من عمل كل شيء
4. **حذف مجلد deprecated/services** بعد التأكد

---
**تم إنشاؤه بواسطة**: CleanArchitectureRelocator v1.0
