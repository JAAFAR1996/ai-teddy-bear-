# 🎤 Audio Processing Guide - معالجة الصوت الاحترافية

## 📋 نظرة عامة

تم تطوير نظام معالجة الصوت الاحترافي في AI Teddy Bear ليوفر:
- **تنظيف الضوضاء** باستخدام NoiseReduce
- **تحسين جودة الصوت البشري** باستخدام SciPy 
- **معالجة متقدمة** باستخدام LibROSA
- **تحسين تلقائي حسب قوة الجهاز**

---

## 🚀 التثبيت السريع

```bash
# تثبيت المكتبات الأساسية
pip install sounddevice PyAudio numpy

# تثبيت مكتبات المعالجة المتقدمة
pip install librosa noisereduce scipy

# تثبيت المكتبات المساعدة
pip install psutil soundfile resampy numba

# أو تثبيت جميع المتطلبات
pip install -r requirements_audio_processing.txt
```

---

## ⚙️ مستويات المعالجة

### 🟢 **Low Level** - أجهزة ضعيفة
- **معالجة**: تطبيع الصوت فقط
- **الوقت**: < 1 ثانية
- **الذاكرة**: أقل من 100 MB
- **مناسب لـ**: أجهزة قديمة، معالجات ضعيفة

### 🟡 **Medium Level** - أجهزة متوسطة
- **معالجة**: تطبيع + تقليل ضوضاء + تحسين صوتي
- **الوقت**: < 3 ثواني
- **الذاكرة**: 200-500 MB
- **مناسب لـ**: أجهزة حديثة عادية

### 🔴 **High Level** - أجهزة قوية
- **معالجة**: جميع المراحل + معالجة متقدمة
- **الوقت**: < 10 ثواني  
- **الذاكرة**: 500 MB - 1 GB
- **مناسب لـ**: أجهزة قوية، خوادم

---

## 🎯 كيفية الاستخدام

### 1. **في الواجهة (UI)**

```python
# تشغيل الواجهة
python src/ui/modern_ui.py

# خطوات الاستخدام:
# 1. اختر جهاز الصوت
# 2. حدد مستوى المعالجة (auto/low/medium/high)
# 3. فعّل "Enhanced Audio Processing"
# 4. اضغط "⚡ Test Processing" لاختبار الأداء
# 5. ابدأ التسجيل
```

### 2. **برمجياً (Programming)**

```python
from src.ui.modern_ui import AudioProcessingEngine
import numpy as np

# إنشاء محرك المعالجة
processor = AudioProcessingEngine(sample_rate=16000)

# معالجة الصوت
audio_data = np.random.randn(16000)  # صوت تجريبي
enhanced_audio, info = processor.clean_audio(audio_data, "medium")

print(f"Steps applied: {info['steps_applied']}")
print(f"Processing time: {info['processing_time']:.2f}s")
```

---

## 🔧 مراحل المعالجة التفصيلية

### **1. التطبيع الأولي (Normalization)**
```python
# تطبيع مستوى الصوت لمنع التشويه
normalized = audio / np.max(np.abs(audio)) * 0.8
```

### **2. تقليل الضوضاء (Noise Reduction)**
```python
# استخدام NoiseReduce المتقدم
reduced = nr.reduce_noise(
    y=audio, 
    sr=sample_rate,
    prop_decrease=0.8,  # تقليل 80% من الضوضاء
    stationary=False    # ضوضاء متغيرة
)
```

### **3. تحسين الصوت البشري (Voice Enhancement)**
```python
# فلترة ترددات الصوت البشري (80-8000 Hz)
from scipy.signal import butter, filtfilt

nyquist = sample_rate / 2
low_cutoff = 80 / nyquist
high_cutoff = 6000 / nyquist
b, a = butter(6, [low_cutoff, high_cutoff], btype='band')
enhanced = filtfilt(b, a, audio)
```

### **4. المعالجة المتقدمة (Advanced Processing)**
```python
# فصل المكونات الهارمونية والإيقاعية
harmonic, percussive = librosa.effects.hpss(audio)

# التركيز على المحتوى الصوتي
processed = harmonic + (percussive * 0.1)

# ضغط المدى الديناميكي
compressed = apply_compression(processed, ratio=4.0)
```

---

## 📊 معايير الجودة

### **قياس التحسن**
```python
def calculate_improvement(original, processed):
    return {
        "rms_improvement": rms(processed) / rms(original),
        "dynamic_range": peak_to_peak(processed) / peak_to_peak(original),
        "noise_reduction": estimate_snr_improvement(original, processed)
    }
```

### **مؤشرات الأداء**
- **Real-time Factor**: نسبة وقت المعالجة إلى مدة الصوت
  - `< 0.5x`: ممتاز للوقت الفعلي
  - `< 1.0x`: جيد
  - `< 2.0x`: مقبول
  - `> 2.0x`: بطيء

---

## 🔍 اختبار الأداء

### **اختبار تلقائي**
```python
# في الواجهة اضغط "⚡ Test Processing"
# سيتم:
# 1. إنشاء صوت تجريبي لمدة 5 ثوان
# 2. اختبار جميع المستويات (low/medium/high)
# 3. قياس الأداء والتوصية بالمستوى الأمثل
```

### **نتائج الاختبار**
```
⚡ Performance Test Results:
Low: 0.2s (1 steps) - Excellent
Medium: 1.1s (3 steps) - Good
High: 4.2s (5 steps) - Acceptable

✅ Recommended: Medium level
```

---

## 🖥️ متطلبات النظام

### **أجهزة منخفضة الأداء**
- **CPU**: معالج مزدوج النواة
- **RAM**: 4 GB
- **التوصية**: مستوى Low أو Medium
- **المكتبات الأساسية فقط**

### **أجهزة متوسطة الأداء**
- **CPU**: معالج رباعي النواة  
- **RAM**: 8 GB
- **التوصية**: مستوى Medium أو High
- **جميع المكتبات**

### **أجهزة عالية الأداء**
- **CPU**: 8 أنوية أو أكثر
- **RAM**: 16 GB أو أكثر
- **التوصية**: مستوى High
- **تسريع GPU اختياري**

---

## 🚨 استكشاف الأخطاء

### **مشاكل شائعة وحلولها**

#### **1. خطأ في المكتبات**
```bash
# إذا فشل تثبيت PyAudio
sudo apt-get install portaudio19-dev  # Linux
brew install portaudio               # macOS

# إذا فشل تثبيت LibROSA  
pip install --upgrade numba llvmlite
```

#### **2. بطء في المعالجة**
```python
# تقليل مستوى المعالجة
processor.processing_level = "low"

# تعطيل المعالجة المتقدمة
processor.enable_processing = False
```

#### **3. ذاكرة غير كافية**
```python
# معالجة أجزاء صغيرة
chunk_size = 1024  # تقليل حجم القطعة
sample_rate = 16000  # استخدام معدل عينة أقل
```

---

## 🎵 أمثلة عملية

### **مثال 1: معالجة سريعة**
```python
processor = AudioProcessingEngine()
enhanced, info = processor.clean_audio(audio_data, "low")
print(f"Enhanced in {info['processing_time']:.1f}s")
```

### **مثال 2: جودة عالية**
```python
processor = AudioProcessingEngine()
enhanced, info = processor.clean_audio(audio_data, "high")
print(f"Applied steps: {info['steps_applied']}")
```

### **مثال 3: تحسين مخصص**
```python
# تحديد إعدادات مخصصة
processor.performance_mode = "medium"
enhanced, info = processor.process_audio(
    audio_data, 
    processing_level="medium"
)
```

---

## 📈 قياس التحسن

### **قبل المعالجة**
- ضوضاء خلفية عالية
- ترددات غير مرغوبة
- مستوى صوت غير متسق

### **بعد المعالجة**
- ✅ تقليل الضوضاء بنسبة 60-80%
- ✅ تحسين وضوح الكلام
- ✅ توحيد مستوى الصوت
- ✅ تحسين جودة الإرسال للخادم

---

## 🔮 الميزات المستقبلية

### **قيد التطوير**
- دعم معالجة GPU باستخدام PyTorch
- خوارزميات AI للتحسين التكيفي
- تحليل المشاعر من جودة الصوت
- ضغط ذكي حسب المحتوى

### **طلب الميزات**
- إرسال اقتراحاتك لتحسين النظام
- تقارير الأداء على أجهزة مختلفة
- اختبارات مع أصوات حقيقية

---

## 📞 الدعم الفني

### **المشاكل الشائعة**
1. **بطء المعالجة**: قلل مستوى المعالجة
2. **جودة ضعيفة**: تأكد من توفر جميع المكتبات
3. **أخطاء الذاكرة**: قلل معدل العينة أو استخدم أجزاء أصغر

### **الحصول على المساعدة**
- راجع ملفات السجل في `logs/`
- استخدم وضع التشخيص المدمج
- اختبر الأداء قبل الإبلاغ عن المشاكل

---

**🎉 استمتع بتجربة صوت عالي الجودة مع AI Teddy Bear!** 