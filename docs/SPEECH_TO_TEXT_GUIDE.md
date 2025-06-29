# دليل تجربة تحويل الصوت إلى نص (Speech-to-Text) من الصفر

## المتطلبات الأساسية

### 1. إعداد البيئة
```bash
# إنشاء مجلد للمشروع
mkdir audio_stt_project
cd audio_stt_project

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate

# استنساخ المشروع
git clone https://github.com/your-repo/intelligent-audio-system.git
cd intelligent-audio-system

# تثبيت التبعيات
pip install -r requirements.txt
```

### 2. التحضير للتسجيل الصوتي
- تأكد من وجود ميكروفون متصل بجهازك
- تأكد من تثبيت مكتبات الصوت

## إعداد المفاتيح (اختياري)
إذا أردت استخدام خدمة Azure للتحويل الصوتي:
```bash
# تعيين مفاتيح Azure (اختياري)
export AZURE_SPEECH_KEY=your_azure_cognitive_services_key
export AZURE_SPEECH_REGION=your_azure_region
```

## كود تجريبي كامل للاختبار

```python
import os
import sounddevice as sd
import soundfile as sf
from src.application.services.speech_to_text_service import SpeechToTextService

def record_audio(filename='test_recording.wav', duration=5, sample_rate=44100):
    """
    تسجيل صوت لمدة محددة
    :param filename: اسم الملف الصوتي
    :param duration: مدة التسجيل بالثواني
    :param sample_rate: معدل أخذ العينات
    """
    print(f"سيبدأ التسجيل لمدة {duration} ثواني...")
    recording = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1)
    sd.wait()  # انتظار اكتمال التسجيل
    sf.write(filename, recording, sample_rate)
    print(f"تم التسجيل بنجاح في {filename}")
    return filename

def transcribe_audio(audio_path):
    """
    تحويل الصوت إلى نص
    :param audio_path: مسار الملف الصوتي
    """
    # إنشاء خدمة تحويل الصوت إلى نص
    stt_service = SpeechToTextService(db_path='data/transcriptions.db')
    
    try:
        # محاولة تحويل الصوت
        transcription = stt_service.transcribe_audio(
            audio_path, 
            language='ar-SA'  # يمكن تغيير اللغة حسب الحاجة
        )
        
        # طباعة النص المحول
        print("النص المحول:")
        print(transcription.text)
        print("\nتفاصيل إضافية:")
        print(f"اللغة: {transcription.language}")
        print(f"الثقة: {transcription.confidence}")
        print(f"النموذج المستخدم: {transcription.model_used}")
        
        return transcription
    except Exception as e:
        print(f"خطأ في التحويل: {e}")
        return None

def main():
    # إنشاء مجلد للتسجيلات إن لم يكن موجودًا
    os.makedirs('recordings', exist_ok=True)
    
    # مسار التسجيل
    recording_path = os.path.join('recordings', 'test_recording.wav')
    
    # تسجيل الصوت
    audio_file = record_audio(recording_path, duration=5)
    
    # تحويل الصوت إلى نص
    transcription = transcribe_audio(audio_file)

if __name__ == "__main__":
    main()
```

## نصائح للاختبار

### اختبار Whisper
- تأكد من تثبيت PyTorch وWhisper
- جرب تسجيلات بلغات مختلفة
- راقب جودة التحويل

### اختبار Azure
- احصل على مفتاح Azure Cognitive Services
- تأكد من تعيين المتغيرات البيئية
- جرب تسجيلات بلغات متعددة

## استكشاف الأخطاء

### مشاكل محتملة
1. عدم وجود ميكروفون
2. مشاكل في تثبيت المكتبات
3. عدم وجود مفاتيح Azure

### التحقق من التثبيت
```bash
# التحقق من تثبيت المكتبات
pip list | grep -E "whisper|torch|azure-cognitiveservices-speech"
```

## ملاحظات مهمة
- جودة التحويل تعتمد على جودة التسجيل
- استخدم ميكروفون عالي الجودة
- تحدث بوضوح وبصوت مسموع

## دعم اللغة العربية
- يدعم Whisper واجهة Azure اللغة العربية
- يمكنك تحديد اللغة باستخدام الكود `language='ar-SA'`

## المساعدة
للمساعدة أو الاستفسارات:
- راجع README.md
- تحقق من issues على GitHub
- تواصل مع فريق التطوير
