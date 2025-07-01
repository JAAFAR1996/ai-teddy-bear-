# 🚀 Quick Start - AI Teddy Bear

## الطريقة الأسرع للتشغيل:

### **1. تحقق من المتطلبات:**
```bash
python --version  # يجب أن يكون 3.11+
node --version    # يجب أن يكون 18+
```

### **2. تشغيل سريع (Windows):**
```batch
# انقر مرتين على:
start_teddy.bat
```

### **3. تشغيل سريع (Mac/Linux):**
```bash
./start_teddy.sh
```

### **4. الوصول للتطبيق:**
- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000

---

## إذا كانت المرة الأولى:

### **1. تثبيت Python 3.11+:**
- **Windows:** https://python.org/downloads/
- **Mac:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11`

### **2. تثبيت Node.js 18+:**
- **جميع الأنظمة:** https://nodejs.org/

### **3. إضافة مفاتيح AI:**
بعد تشغيل `start_teddy.bat` أول مرة، ضع مفاتيحك في ملف `.env`:
```env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=ant-api-your-anthropic-key
```

---

## إيقاف التشغيل:
```batch
# Windows
stop_teddy.bat

# Mac/Linux  
./stop_teddy.sh
```

---

## 🎮 **تجربة بدون ESP32:**
```batch
# تشغيل العرض الكامل مع محاكي:
run_complete_demo.bat    # Windows
./run_complete_demo.sh   # Mac/Linux

# أو محاكي فقط:
python src/simulators/esp32_production_simulator.py
```

**🎯 يحاكي ESP32 كاملاً - صوت + AI + dashboard!**

---

## المساعدة:
- **🎮 للمحاكي:** اقرأ `SIMULATOR_DEMO_GUIDE.md`
- **🔧 للـ ESP32:** اقرأ `ESP32_QUICK_SETUP.md`  
- **📖 شامل:** اقرأ `README_COMPLETE_SETUP.md`

**🎉 استمتع بتجربة كاملة بدون شراء أي شيء!** 