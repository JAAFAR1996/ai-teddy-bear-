# 🚀 دليل تثبيت Node.js وتشغيل المشروع

## ❌ المشكلة الحالية
```
npm : The term 'npm' is not recognized...
```
هذا يعني أن Node.js غير مثبت على النظام.

## ✅ الحل السريع

### 1. تحميل وتثبيت Node.js

#### الطريقة الأسرع:
1. **زيارة الموقع الرسمي**: https://nodejs.org/
2. **تحميل النسخة LTS** (الموصى بها)
3. **تشغيل المثبت** واتباع التعليمات
4. **إعادة تشغيل PowerShell**

#### أو باستخدام Chocolatey (إذا كان مثبتاً):
```powershell
choco install nodejs
```

#### أو باستخدام winget:
```powershell
winget install OpenJS.NodeJS
```

### 2. التحقق من التثبيت
```bash
node --version
npm --version
```

يجب أن تظهر أرقام الإصدارات.

### 3. تشغيل المشروع
```bash
cd frontend
npm install
npm start
```

## 🎯 بدائل فورية (بدون تثبيت)

### استخدام Node.js محمول:
1. تحميل Node.js Portable من: https://nodejs.org/en/download/
2. استخراج الملفات
3. إضافة المجلد للـ PATH مؤقتاً

### أو استخدام Replit/CodeSandbox:
- رفع الكود على منصة سحابية للاختبار السريع

## 🔧 مشاكل شائعة وحلولها

### المشكلة: PowerShell لا يتعرف على npm بعد التثبيت
**الحل:**
```powershell
# إعادة تحديث PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# أو إعادة تشغيل PowerShell
```

### المشكلة: خطأ في الصلاحيات
**الحل:**
```powershell
# تشغيل PowerShell كمدير
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### المشكلة: خطأ في npm install
**الحل:**
```bash
# مسح cache
npm cache clean --force

# أو استخدام yarn بدلاً من npm
npm install -g yarn
yarn install
yarn start
```

## 📋 معلومات إضافية

### متطلبات النظام:
- **Node.js**: الإصدار 16+ (موصى به 18 أو 20)
- **npm**: يأتي مع Node.js
- **المساحة**: ~500MB للـ node_modules

### إصدارات موصى بها لعام 2025:
- **Node.js 20.x LTS** - الأكثر استقراراً
- **npm 10.x** - أحدث إصدار

---

## 🎉 بعد التثبيت الناجح

ستتمكن من تشغيل:
```bash
START_DASHBOARD_DEMO.bat
```

أو يدوياً:
```bash
cd frontend
npm install
npm start
```

Dashboard سيفتح على: **http://localhost:3000**

**ميزات ستراها:**
- 📊 رسوم بيانية تفاعلية (4 أنواع)
- 📥 تحميل PDF احترافي  
- 🔔 تنبيهات WebSocket حية
- 🎨 واجهة عربية متطورة

---

**في حالة استمرار المشاكل:**
- تأكد من إغلاق أي antivirus مؤقتاً أثناء التثبيت
- جرب تشغيل PowerShell كمدير
- تأكد من وجود اتصال إنترنت مستقر 