# 🧪 **HUME Integration Testing Guide**

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install hume python-dotenv numpy soundfile
```

### **2. Set API Key**
```bash
export HUME_API_KEY="xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q"
```

### **3. Run Tests**
```bash
python hume_integration.py
```

## 📊 **What the Script Does**

### **🔄 Batch Mode Testing**
- Creates 3 sample audio files
- Submits them to HUME for batch analysis
- Downloads results to `batch_predictions.json`
- Shows emotion summary

### **⚡ Stream Mode Testing**  
- Takes first sample audio file
- Sends to HUME for real-time analysis
- Returns immediate emotion results
- Shows top emotions detected

## 📁 **Generated Files**

```
sample_happy.wav         # Test audio (440Hz)
sample_sad.wav          # Test audio (220Hz)  
sample_excited.wav      # Test audio (660Hz)
batch_predictions.json  # HUME batch results
```

## 📈 **Expected Output**

```
🎤 HUME AI Integration Testing
============================================================
🔑 API Key: xmkFxYNr...

==================================================
🧪 TESTING STREAM MODE
==================================================
⚡ Starting Stream Analysis...
🎵 Audio file: sample_happy.wav
🔗 Connecting to HUME Stream...
📤 Sending audio file...
✅ Stream analysis completed!

📊 Stream Results:
Status: success

🎭 Emotions Summary:
{
  "dominant_emotion": ["Joy", 0.85],
  "all_emotions": {
    "Joy": 0.85,
    "Excitement": 0.72,
    "Calmness": 0.45
  },
  "top_3_emotions": [
    ["Joy", 0.85],
    ["Excitement", 0.72], 
    ["Calmness", 0.45]
  ]
}

==================================================
🧪 TESTING BATCH MODE
==================================================
🔄 Starting Batch Analysis...
📁 Files to analyze: 3
  ✅ sample_happy.wav
  ✅ sample_sad.wav
  ✅ sample_excited.wav
📤 Submitting job to HUME...
⏳ Waiting for analysis to complete...
📥 Downloading results to batch_predictions.json...
✅ Batch analysis completed successfully!

📊 Batch Results:
Status: success
Files analyzed: 3
Output file: batch_predictions.json
```

## 🔧 **Troubleshooting**

### **❌ "HUME SDK not available"**
```bash
pip install hume
```

### **❌ "HUME API Key not found"**
```bash
export HUME_API_KEY="xmkFxYNrKdHjhY6RiEA0JT46C2xAo4YsdiujXqtg5fd1C99Q"
```

### **❌ "Failed to create sample files"**
```bash
pip install numpy soundfile
```

## 🎯 **Integration with ESP32**

بعد نجاح الاختبار، يمكن دمج نفس الكود مع ESP32:

```python
# في production_teddy_system.py
from hume_integration import HumeIntegration

@app.post("/esp32/hume-analyze")
async def esp32_hume_analysis(audio_file: UploadFile):
    hume = HumeIntegration()
    
    # حفظ مؤقت
    temp_path = f"temp_{audio_file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await audio_file.read())
    
    # تحليل Stream سريع
    result = await hume.analyze_stream(temp_path)
    
    # حذف المؤقت
    os.remove(temp_path)
    
    return result
```

---

## ✅ **Ready to Use!**

الآن لديك نظام HUME AI جاهز للاختبار والاستخدام مع ESP32! 🎤 