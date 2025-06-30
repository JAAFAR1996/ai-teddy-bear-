#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cleanup Action Plan Generator
توليد خطة عمل مفصلة لتنظيف المشروع
"""

import json
from datetime import datetime
from pathlib import Path

class CleanupActionPlanGenerator:
    def __init__(self, analysis_file="cleanup_report_20250630_225358.json"):
        """تهيئة مولد خطة العمل"""
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)
        
        self.total_files = self.analysis['total_files']
        self.empty_files = self.analysis['empty_files']
        self.duplicate_files = self.analysis['duplicate_files']
        self.misplaced_files = self.analysis['misplaced_files']
        self.large_files = self.analysis['large_files']
        
    def generate_action_plan(self):
        """توليد خطة العمل الكاملة"""
        plan = f"""# 🎯 خطة عمل تنظيف مشروع AI Teddy Bear

## 📊 ملخص الوضع الحالي
- **إجمالي الملفات**: {self.total_files}
- **ملفات فارغة**: {len(self.empty_files)}
- **ملفات مكررة**: {self._count_duplicate_files()}
- **ملفات في أماكن خاطئة**: {len(self.misplaced_files)}
- **ملفات كبيرة جداً**: {len([f for f in self.large_files if f['lines'] > 1000])}

## 🎯 الهدف النهائي
تحويل المشروع من **{self.total_files}** ملف إلى حوالي **{int(self.total_files * 0.7)}** ملف منظم ونظيف

---

## 📅 خطة العمل التفصيلية (5 أيام)

### 🗓️ اليوم 1: التنظيف السريع (2-3 ساعات)

#### ✅ المهام:
1. **إنشاء نسخة احتياطية كاملة**
   ```bash
   # إنشاء نسخة احتياطية
   mkdir backup_$(date +%Y%m%d_%H%M%S)
   cp -r . backup_*/
   
   # أو استخدم Git
   git add -A
   git commit -m "Backup before major cleanup"
   git branch backup-before-cleanup
   ```

2. **حذف الملفات الفارغة**
   ```bash
   # حذف الملفات الفارغة المحددة
{self._generate_empty_files_commands()}
   ```

3. **حذف مجلدات __pycache__**
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
   ```

4. **تشغيل التنظيف الأساسي**
   ```bash
   python comprehensive_project_cleaner.py --execute
   ```

#### 📊 النتيجة المتوقعة:
- حذف {len(self.empty_files)} ملف فارغ
- تنظيف مجلدات الكاش
- توفير ~5% من حجم المشروع

---

### 🗓️ اليوم 2: دمج الملفات المكررة (3-4 ساعات)

#### ✅ المهام:
1. **تحليل الملفات المكررة**
{self._generate_duplicate_analysis()}

2. **دمج ملفات __init__.py المكررة**
   - معظم ملفات __init__.py فارغة وهذا طبيعي
   - احتفظ بالملفات التي تحتوي على imports

3. **البحث عن ملفات أخرى مكررة**
   ```bash
   # البحث عن ملفات مكررة باستخدام fdupes
   fdupes -r . | grep -v __pycache__
   ```

#### 📊 النتيجة المتوقعة:
- دمج ~50 ملف مكرر
- تبسيط هيكل المشروع

---

### 🗓️ اليوم 3: إعادة تنظيم الهيكل (4-5 ساعات)

#### ✅ المهام:
1. **إنشاء الهيكل الجديد**
   ```bash
   # إنشاء المجلدات الأساسية
   mkdir -p src/core/domain/entities
   mkdir -p src/core/services  
   mkdir -p src/infrastructure/persistence/repositories
   mkdir -p src/api/endpoints
   mkdir -p tests/unit
   mkdir -p tests/integration
   ```

2. **نقل الملفات للأماكن الصحيحة**
{self._generate_reorganization_commands()}

3. **تحديث جميع imports**
   ```python
   # سكريبت لتحديث imports
   python update_imports.py
   ```

#### 📊 النتيجة المتوقعة:
- نقل {len(self.misplaced_files)} ملف لأماكنها الصحيحة
- هيكل واضح ومنظم

---

### 🗓️ اليوم 4: تقسيم الملفات الكبيرة (3-4 ساعات)

#### ✅ المهام:
1. **تحديد الملفات الكبيرة جداً**
{self._generate_large_files_list()}

2. **تقسيم الملفات حسب المسؤوليات**
   - كل ملف > 1000 سطر يجب تقسيمه
   - كل class في ملف منفصل
   - فصل business logic عن infrastructure

3. **إعادة هيكلة الخدمات الكبيرة**
   - تطبيق Single Responsibility Principle
   - استخدام Composition over Inheritance

#### 📊 النتيجة المتوقعة:
- تقسيم ~15 ملف كبير
- تحسين قابلية القراءة والصيانة

---

### 🗓️ اليوم 5: التحسينات النهائية (2-3 ساعات)

#### ✅ المهام:
1. **تنسيق الكود**
   ```bash
   # تنسيق Python
   black src/ tests/ --line-length 120
   isort src/ tests/ --profile black
   
   # فحص الجودة
   flake8 src/ tests/
   mypy src/ --ignore-missing-imports
   ```

2. **إضافة الوثائق المفقودة**
   - docstrings لكل class ودالة عامة
   - تحديث README.md
   - إضافة architecture.md

3. **تشغيل الاختبارات**
   ```bash
   pytest tests/ -v
   python -m pytest --cov=src tests/
   ```

4. **الـ commit النهائي**
   ```bash
   git add -A
   git commit -m "Major project cleanup and reorganization"
   ```

#### 📊 النتيجة المتوقعة:
- كود منسق ونظيف 100%
- تغطية اختبارات > 80%
- وثائق محدثة

---

## 🛠️ أدوات مساعدة

### سكريبتات جاهزة:
1. `project_cleanup_analyzer.py` - لتحليل المشروع
2. `comprehensive_project_cleaner.py` - للتنظيف التلقائي
3. `cleanup_script.sh` - سكريبت bash للتنظيف السريع

### أوامر مفيدة:
```bash
# عد الملفات
find . -name "*.py" | wc -l

# حجم المشروع
du -sh .

# البحث عن imports معطلة
grep -r "import.*" --include="*.py" | grep -E "(No module|cannot import)"

# البحث عن TODO/FIXME
grep -r "TODO\|FIXME" --include="*.py"
```

---

## ⚠️ نقاط مهمة للانتباه

1. **لا تحذف ملفات __init__.py** - مهمة لـ Python packages
2. **احذر من circular imports** عند نقل الملفات
3. **شغل الاختبارات بعد كل خطوة كبيرة**
4. **احتفظ بنسخة احتياطية دائماً**

---

## 📈 النتائج المتوقعة بعد التنظيف

| المعيار | قبل | بعد | التحسن |
|---------|------|-----|--------|
| عدد الملفات | {self.total_files} | ~{int(self.total_files * 0.7)} | ⬇️ 30% |
| ملفات > 500 سطر | {len(self.large_files)} | ~20 | ⬇️ 85% |
| ملفات مكررة | {self._count_duplicate_files()} | 0 | ⬇️ 100% |
| وضوح الهيكل | 40% | 95% | ⬆️ 137% |
| سرعة البناء | - | - | ⬆️ 30% |

---

## 🚀 الخطوات التالية بعد التنظيف

1. **تحسين الأمان**
   - إصلاح المشاكل الأمنية المكتشفة
   - تطبيق best practices

2. **تحسين الأداء**
   - profiling للكود
   - تحسين الـ queries
   - إضافة caching

3. **تحسين الـ CI/CD**
   - automated testing
   - automated deployment
   - monitoring

---

*تم إنشاء هذه الخطة بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return plan
    
    def _count_duplicate_files(self):
        """حساب إجمالي الملفات المكررة"""
        total = 0
        for group in self.duplicate_files:
            total += len(group['files']) - 1  # -1 لأننا نحتفظ بواحد
        return total
    
    def _generate_empty_files_commands(self):
        """توليد أوامر حذف الملفات الفارغة"""
        commands = []
        for file in self.empty_files:
            commands.append(f'   rm -f "{file}"')
        return '\n'.join(commands)
    
    def _generate_duplicate_analysis(self):
        """توليد تحليل للملفات المكررة"""
        analysis = ""
        for i, group in enumerate(self.duplicate_files[:3], 1):
            analysis += f"\n   **المجموعة {i}** ({len(group['files'])} ملف):\n"
            for file in group['files'][:3]:
                analysis += f"   - {file}\n"
        return analysis
    
    def _generate_reorganization_commands(self):
        """توليد أوامر إعادة التنظيم"""
        commands = []
        
        # تجميع حسب النوع
        by_type = {}
        for item in self.misplaced_files:
            file_type = item['type']
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(item)
        
        # توليد الأوامر
        for file_type, files in by_type.items():
            commands.append(f"\n   # نقل ملفات {file_type}")
            for item in files[:3]:  # أول 3 فقط
                current = item['file']
                suggested = item['suggested']
                filename = Path(current).name
                commands.append(f'   mv "{current}" "{suggested}{filename}"')
        
        return '\n'.join(commands)
    
    def _generate_large_files_list(self):
        """توليد قائمة الملفات الكبيرة"""
        very_large = [f for f in self.large_files if f['lines'] > 1000]
        
        result = "\n   **ملفات يجب تقسيمها فوراً:**\n"
        for file in very_large[:5]:
            result += f"   - {file['path']} ({file['lines']} سطر)\n"
        
        if len(very_large) > 5:
            result += f"   - ... و {len(very_large) - 5} ملف آخر\n"
        
        return result
    
    def save_action_plan(self):
        """حفظ خطة العمل"""
        plan = self.generate_action_plan()
        
        filename = f"cleanup_action_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(plan)
        
        print(f"✅ تم حفظ خطة العمل في: {filename}")
        return filename

def main():
    """البرنامج الرئيسي"""
    print("🚀 توليد خطة عمل تنظيف المشروع...")
    
    try:
        generator = CleanupActionPlanGenerator()
        filename = generator.save_action_plan()
        
        print("\n📋 ملخص سريع:")
        print(f"- إجمالي الملفات: {generator.total_files}")
        print(f"- ملفات للحذف: {len(generator.empty_files)}")
        print(f"- ملفات للدمج: {generator._count_duplicate_files()}")
        print(f"- ملفات للنقل: {len(generator.misplaced_files)}")
        print(f"- ملفات للتقسيم: {len([f for f in generator.large_files if f['lines'] > 1000])}")
        
        print(f"\n✅ تمت! افتح {filename} لقراءة الخطة الكاملة")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 