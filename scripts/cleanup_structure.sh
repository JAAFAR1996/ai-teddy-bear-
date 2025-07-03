#!/bin/bash

# توحيد أسماء الملفات
find . -name "*ملف*" -exec rename 's/ملف/file_' {} \;

# إزالة الملفات غير المستخدمة
rm -rf src/data/ hardware/ logs/tmp/

# تنظيم الملفات
mkdir -p src/legacy/
mv src/presentation/enterprise_dashboard.py src/legacy/
mv src/presentation/enterprise_dashboard_refactored.py src/presentation/dashboard.py 