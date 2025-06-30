#!/bin/bash
# سكريبت تنظيف المشروع - تم توليده تلقائياً
# تاريخ: 2025-06-30 22:57:20

echo "🚀 بدء تنظيف المشروع..."

# حذف الملفات الفارغة
echo "🗑️ حذف الملفات الفارغة..."
rm -f ".\src\application\commands\__init__.py"
rm -f ".\src\data\teddy.db"
rm -f ".\src\infrastructure\child\backup_service.py"

# حذف مجلدات __pycache__
echo "🗑️ حذف مجلدات __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# تنسيق الكود
echo "🎨 تنسيق الكود..."
black src/ --line-length 120 2>/dev/null || echo "تحذير: black غير مثبت"
isort src/ 2>/dev/null || echo "تحذير: isort غير مثبت"

echo "✅ اكتمل التنظيف!"
