# 🚀 Enterprise WebSocket Messaging System Guide

## نظام إرسال الرسائل المتقدم - دليل شامل

### نظرة عامة 📋

تم تطوير نظام **Enterprise WebSocket Messaging** متقدم في `src/ui/modern_ui.py` يوفر:

- ✅ **إرسال رسائل موثوق** مع إعادة المحاولة التلقائية
- ✅ **ضغط وتقسيم الرسائل الكبيرة** للأداء الأمثل
- ✅ **معالجة انقطاع الإنترنت** مع استكمال تلقائي
- ✅ **تحديث الواجهة الفوري** مع تتبع التقدم
- ✅ **بيانات وصفية شاملة** لكل رسالة
- ✅ **أمان مؤسسي** مع تشفير وتتبع

---

## 🏗️ المكونات الرئيسية

### 1. EnterpriseMessageSender Class

```python
class EnterpriseMessageSender(QObject):
    """Advanced message sender with retry logic and metadata support"""
    
    # Signals for real-time UI updates
    message_sent = Signal(str)           # message_id
    message_delivered = Signal(str, dict) # message_id, response
    message_failed = Signal(str, str)    # message_id, error
    sending_progress = Signal(str, int)  # message_id, progress
    connection_restored = Signal()       # Auto-retry activation
```

**الميزات الأساسية:**
- 🔄 **إعادة المحاولة التلقائية** (3 محاولات افتراضية)
- 📦 **ضغط الرسائل** الكبيرة تلقائياً (>10KB)
- 🧩 **تقسيم الرسائل** العملاقة (>100KB) إلى أجزاء
- 📊 **تتبع التقدم** الفوري للمستخدم
- 🔐 **معلومات النظام** والجلسة شاملة

---

## 📤 إرسال الرسائل الصوتية

### استخدام المطور:

```python
# في ModernAudioWidget
async def _send_audio_async(self, wav_data: bytes, metadata: dict):
    message_id = await self.message_sender.send_audio_message(wav_data, metadata)
```

### البيانات الوصفية المرسلة:

```json
{
  "session_id": "unique_session_identifier",
  "device_id": "teddy_ui_client_audio",
  "timestamp": "2025-01-15T10:30:45.123456",
  "audio_specs": {
    "sample_rate": 16000,
    "channels": 1,
    "duration_seconds": 5.2,
    "size_bytes": 166400,
    "format": "wav",
    "bit_depth": 16,
    "compression": "none"
  },
  "processing_info": {
    "steps_applied": ["normalization", "noise_reduction", "voice_enhancement"],
    "processing_time": 1.2,
    "quality_improvement": {"rms_ratio": 1.34, "dynamic_range_improvement": 1.15}
  },
  "user_context": {
    "recording_method": "live_recording",
    "processing_enabled": true,
    "processing_level": "medium",
    "ui_version": "2.0.0",
    "device_performance": "medium"
  },
  "delivery_requirements": {
    "priority": "high",
    "acknowledgment_required": true,
    "timeout_seconds": 30,
    "chunking_enabled": true,
    "compression_enabled": true
  },
  "conversation_context": {
    "message_type": "user_voice_input",
    "expected_response": "ai_voice_response",
    "language": "auto_detect",
    "emotion_analysis": true
  }
}
```

---

## 💬 إرسال الرسائل النصية

### استخدام المطور:

```python
# إرسال رسالة نصية من أي مكان
audio_widget.send_text_message("مرحبا بك", {"source": "conversation_widget"})
```

### البيانات الوصفية للنص:

```json
{
  "session_id": "unique_session_identifier",
  "device_id": "teddy_ui_client_text",
  "text_specs": {
    "length": 12,
    "language": "auto",
    "encoding": "utf-8",
    "word_count": 3
  },
  "conversation_context": {
    "message_type": "user_text_input",
    "expected_response": "ai_text_response",
    "language": "auto_detect"
  }
}
```

---

## 🔄 معالجة الأخطاء وإعادة المحاولة

### سيناريوهات الأخطاء المدعومة:

#### 1. انقطاع الشبكة 🌐
```python
def _on_message_failed(self, message_id: str, error: str):
    if any(term in error.lower() for term in ["connection", "network", "timeout"]):
        # تظهر للمستخدم: "🔄 Network issue - will retry automatically"
        # الرسالة تُضاف لقائمة الإعادة التلقائية
```

#### 2. استنفاد المحاولات 🚫
```python
# بعد 3 محاولات فاشلة
self.status_label.setText("❌ All retry attempts failed")
self.conversation_widget.add_message("System", 
    "❌ Unable to send message after multiple attempts.")
```

#### 3. استعادة الاتصال ✅
```python
def _on_connection_restored(self):
    # إعادة إرسال جميع الرسائل المعلقة تلقائياً
    self.status_label.setText("🔄 Connection restored - retrying pending messages...")
```

---

## 📊 تحديثات التقدم الفورية

### مراحل التقدم المرئية:

```python
def _on_sending_progress(self, message_id: str, progress: int):
    if progress < 25:
        status = "📤 Preparing message..."
    elif progress < 50:
        status = "🗜️ Compressing audio..."
    elif progress < 75:
        status = "📡 Uploading to server..."
    elif progress < 100:
        status = "✅ Upload complete..."
    else:
        status = "⏳ Processing on server..."
    
    self.status_label.setText(f"{status} {progress}%")
```

---

## 🤖 معالجة ردود الخادم

### أنواع الردود المدعومة:

#### 1. ردود الذكاء الاصطناعي 🧠
```python
if response_type == "audio_response":
    payload = response.get("payload", {})
    ai_response = payload.get("response", "")
    confidence = payload.get("confidence", 0)
    emotions = payload.get("emotions", [])
    
    # إضافة الرد للمحادثة
    self.conversation_widget.add_message("Teddy AI", ai_response)
    
    # عرض تحليل المشاعر
    if emotions:
        main_window._update_emotion_display(emotions, confidence)
```

#### 2. تحديثات المعالجة 🔄
```python
elif response_type == "processing_update":
    stage = response.get("payload", {}).get("stage", "unknown")
    progress = response.get("payload", {}).get("progress", 0)
    self.status_label.setText(f"🔄 Processing: {stage} ({progress}%)")
```

#### 3. أخطاء الخادم ⚠️
```python
elif response_type == "error_response":
    error_msg = response.get("payload", {}).get("error", "Unknown error")
    error_code = response.get("payload", {}).get("error_code", "UNKNOWN")
    
    self.conversation_widget.add_message("System", 
        f"⚠️ Error: {error_msg} (Code: {error_code})")
```

---

## 🗜️ ضغط وتقسيم الرسائل

### ضغط تلقائي للرسائل الكبيرة:

```python
async def _compress_message(self, message_data: dict) -> dict:
    if "audio_data" in message_data["payload"]:
        audio_data = message_data["payload"]["audio_data"]
        compressed = gzip.compress(audio_data.encode('utf-8'))
        
        # نسبة الضغط
        compression_ratio = len(compressed) / len(audio_data)
        
        message_data["payload"]["compressed"] = True
        message_data["payload"]["compression_ratio"] = compression_ratio
```

### تقسيم الرسائل العملاقة:

```python
async def _send_chunked_message(self, message_id: str, message_data: dict):
    chunk_size = 64 * 1024  # 64KB لكل جزء
    total_chunks = (len(large_data) + chunk_size - 1) // chunk_size
    
    # إرسال رسالة التهيئة
    init_message = {
        "chunked": True,
        "chunk_info": {
            "total_chunks": total_chunks,
            "total_size": len(large_data)
        }
    }
    
    # إرسال الأجزاء تدريجياً
    for i in range(total_chunks):
        chunk_data = large_data[start_idx:end_idx]
        # إرسال الجزء + تحديث التقدم
```

---

## 🔧 التكامل مع الواجهة

### ربط ModernAudioWidget:

```python
def _setup_message_sender_connections(self):
    """ربط جميع إشارات نظام الرسائل"""
    if hasattr(self, 'message_sender'):
        self.message_sender.message_sent.connect(self._on_message_sent)
        self.message_sender.message_delivered.connect(self._on_message_delivered)
        self.message_sender.message_failed.connect(self._on_message_failed)
        self.message_sender.sending_progress.connect(self._on_sending_progress)
        self.message_sender.connection_restored.connect(self._on_connection_restored)
```

### ربط ConversationWidget:

```python
def _send_message_to_server(self, message: str):
    # البحث عن AudioWidget لاستخدام نظام الرسائل المتقدم
    audio_widget = None
    for widget in main_window.findChildren(ModernAudioWidget):
        if hasattr(widget, 'message_sender'):
            audio_widget = widget
            break
    
    if audio_widget:
        # استخدام النظام المتقدم
        audio_widget.send_text_message(message, {"source": "conversation_widget"})
    else:
        # النظام التقليدي كبديل
        main_window.websocket_client.send_message(legacy_message)
```

---

## 📈 مراقبة الأداء

### معلومات حالة النظام:

```python
def get_message_sender_status(self) -> dict:
    return {
        "pending_messages": self.message_sender.get_pending_messages_count(),
        "connection_status": websocket_client.is_connected,
        "last_message_id": self.current_message_id,
        "retry_queue_size": len(self.message_sender.retry_queue),
        "max_retry_attempts": self.message_sender.max_retry_attempts,
        "system_initialized": True
    }
```

---

## 🎯 أمثلة الاستخدام العملي

### 1. إرسال تسجيل صوتي:
```python
# في ModernAudioWidget عند الانتهاء من التسجيل
wav_data = self._create_wav_data(audio_bytes)
self._send_audio_to_server(wav_data, processing_info)
# ← النظام يقوم بالضغط والإرسال والتتبع تلقائياً
```

### 2. إرسال رسالة نصية:
```python
# من أي مكان في الواجهة
audio_widget.send_text_message("مرحبا يا ذكي", {
    "urgency": "high",
    "context": "greeting"
})
```

### 3. مراقبة الحالة:
```python
status = audio_widget.get_message_sender_status()
print(f"Pending: {status['pending_messages']}")
print(f"Connection: {status['connection_status']}")
```

---

## ✨ الميزات المتقدمة

### 🔐 الأمان
- ✅ تشفير TLS للاتصال
- ✅ معرف جلسة فريد (UDID)
- ✅ توقيتات دقيقة ومراجعة

### 🚀 الأداء  
- ✅ ضغط ذكي للرسائل الكبيرة
- ✅ تقسيم للملفات العملاقة
- ✅ إعادة محاولة ذكية حسب نوع الخطأ

### 🎨 تجربة المستخدم
- ✅ تحديثات فورية لحالة الإرسال
- ✅ رسائل خطأ واضحة ومفيدة
- ✅ استكمال تلقائي بعد انقطاع الشبكة

### 📊 التحليلات
- ✅ تتبع شامل لجميع الرسائل
- ✅ إحصائيات الأداء والضغط
- ✅ تحليل أخطاء الشبكة

---

## 🚀 النتيجة النهائية

تم تطوير نظام **Enterprise-Grade WebSocket Messaging** يوفر:

1. **موثوقية عالية** - إعادة محاولة ذكية ومعالجة شاملة للأخطاء
2. **أداء محسن** - ضغط وتقسيم تلقائي للرسائل الكبيرة  
3. **تجربة مستخدم ممتازة** - تحديثات فورية وتتبع التقدم
4. **مراقبة شاملة** - تتبع مفصل لجميع العمليات
5. **أمان مؤسسي** - بيانات وصفية شاملة وتشفير

النظام جاهز للاستخدام الإنتاجي في بيئة مؤسسية! 🎉

---

## 📞 الدعم التقني

للاستفسارات والدعم:
- 📧 راجع ملف `src/ui/modern_ui.py` للتفاصيل التقنية
- 🔍 استخدم `logger.info` لتتبع العمليات
- 🐛 فحص `message_sender.retry_queue` لحل مشاكل الشبكة 