#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel File Splitter for Codacy Issues
يقوم هذا البرنامج بتقسيم ملف Excel كبير إلى ملفات أصغر
لتسهيل معالجة مشاكل Codacy
"""

import pandas as pd
import os
from pathlib import Path
import math
from datetime import datetime
import argparse

class ExcelSplitter:
    def __init__(self, input_file, output_dir="split_files"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.df = None
        self.total_rows = 0
        
    def load_file(self):
        """تحميل ملف Excel"""
        print(f"جاري تحميل الملف: {self.input_file}")
        try:
            self.df = pd.read_excel(self.input_file, engine='openpyxl')
            self.total_rows = len(self.df)
            print(f"✓ تم تحميل {self.total_rows} سطر بنجاح")
            print(f"✓ عدد الأعمدة: {len(self.df.columns)}")
            return True
        except Exception as e:
            print(f"✗ خطأ في تحميل الملف: {e}")
            return False
    
    def create_output_directory(self):
        """إنشاء مجلد الإخراج"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ تم إنشاء مجلد الإخراج: {self.output_dir}")
    
    def split_by_rows(self, rows_per_file=10):
        """تقسيم الملف حسب عدد الأسطر"""
        if not self.df is not None:
            print("✗ يجب تحميل الملف أولاً")
            return
        
        num_files = math.ceil(self.total_rows / rows_per_file)
        print(f"\nتقسيم إلى {num_files} ملف ({rows_per_file} سطر لكل ملف)")
        
        self.create_output_directory()
        
        for i in range(num_files):
            start_idx = i * rows_per_file
            end_idx = min((i + 1) * rows_per_file, self.total_rows)
            
            # استخراج البيانات
            chunk_df = self.df.iloc[start_idx:end_idx]
            
            # اسم الملف
            output_file = self.output_dir / f"{self.input_file.stem}_part_{i+1:03d}.xlsx"
            
            # حفظ الملف
            chunk_df.to_excel(output_file, index=False)
            
            print(f"  ✓ الملف {i+1}/{num_files}: {output_file.name} ({len(chunk_df)} سطر)")
        
        print(f"\n✓ تم التقسيم بنجاح إلى {num_files} ملف")
    
    def split_by_priority(self):
        """تقسيم حسب الأولوية (إذا كان هناك عمود priority)"""
        if 'severity' in self.df.columns or 'priority' in self.df.columns:
            priority_col = 'severity' if 'severity' in self.df.columns else 'priority'
            print(f"\nتقسيم حسب الأولوية ({priority_col})")
            
            self.create_output_directory()
            
            priorities = self.df[priority_col].unique()
            
            for priority in priorities:
                priority_df = self.df[self.df[priority_col] == priority]
                output_file = self.output_dir / f"{self.input_file.stem}_{priority}.xlsx"
                priority_df.to_excel(output_file, index=False)
                print(f"  ✓ {priority}: {len(priority_df)} سطر -> {output_file.name}")
    
    def split_by_file_path(self):
        """تقسيم حسب مسار الملف (إذا كان هناك عمود file)"""
        if 'file' in self.df.columns or 'filepath' in self.df.columns:
            file_col = 'file' if 'file' in self.df.columns else 'filepath'
            print(f"\nتقسيم حسب الملفات المتأثرة")
            
            self.create_output_directory()
            
            # استخراج اسم الملف من المسار
            self.df['file_name'] = self.df[file_col].apply(lambda x: Path(x).name if pd.notna(x) else 'unknown')
            
            # تجميع حسب الملف
            file_groups = self.df.groupby('file_name')
            
            for i, (file_name, group) in enumerate(file_groups):
                # تنظيف اسم الملف للاستخدام في اسم ملف Excel
                safe_name = file_name.replace('.', '_').replace('/', '_')
                output_file = self.output_dir / f"{self.input_file.stem}_file_{safe_name}.xlsx"
                
                group.drop('file_name', axis=1).to_excel(output_file, index=False)
                print(f"  ✓ {file_name}: {len(group)} مشكلة -> {output_file.name}")
    
    def smart_split(self, target_rows=100):
        """تقسيم ذكي يوازن بين حجم الملف وسهولة المعالجة"""
        print(f"\nالتقسيم الذكي (الهدف: ~{target_rows} سطر لكل ملف)")
        
        self.create_output_directory()
        
        # إذا كان هناك عمود أولوية، نستخدمه
        if 'severity' in self.df.columns or 'priority' in self.df.columns:
            priority_col = 'severity' if 'severity' in self.df.columns else 'priority'
            
            # ترتيب حسب الأولوية
            priority_order = ['Error', 'Security', 'Warning', 'Code Style', 'Info']
            if priority_col in self.df.columns:
                self.df['priority_rank'] = self.df[priority_col].map(
                    {p: i for i, p in enumerate(priority_order)}
                )
                self.df = self.df.sort_values('priority_rank')
        
        # تقسيم إلى مجموعات
        num_files = max(1, math.ceil(self.total_rows / target_rows))
        
        for i in range(num_files):
            start_idx = i * target_rows
            end_idx = min((i + 1) * target_rows, self.total_rows)
            
            chunk_df = self.df.iloc[start_idx:end_idx]
            
            # إضافة معلومات عن المحتوى
            info = []
            if 'severity' in chunk_df.columns:
                severity_counts = chunk_df['severity'].value_counts()
                info.append("_".join([f"{k}{v}" for k, v in severity_counts.items()]))
            
            info_str = "_".join(info) if info else ""
            output_file = self.output_dir / f"{self.input_file.stem}_batch_{i+1:03d}_{info_str}.xlsx"
            
            chunk_df.to_excel(output_file, index=False)
            print(f"  ✓ الدفعة {i+1}/{num_files}: {output_file.name} ({len(chunk_df)} سطر)")
    
    def generate_summary(self):
        """إنشاء ملف ملخص"""
        if self.df is None:
            return
        
        summary_file = self.output_dir / f"{self.input_file.stem}_SUMMARY.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"ملخص تقسيم ملف: {self.input_file.name}\n")
            f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            
            f.write(f"إجمالي الأسطر: {self.total_rows}\n")
            f.write(f"عدد الأعمدة: {len(self.df.columns)}\n")
            f.write(f"الأعمدة: {', '.join(self.df.columns)}\n\n")
            
            # إحصائيات إضافية
            if 'severity' in self.df.columns:
                f.write("توزيع الخطورة:\n")
                for severity, count in self.df['severity'].value_counts().items():
                    f.write(f"  - {severity}: {count}\n")
            
            if 'file' in self.df.columns:
                f.write(f"\nعدد الملفات المتأثرة: {self.df['file'].nunique()}\n")
        
        print(f"\n✓ تم إنشاء ملف الملخص: {summary_file}")

def get_recommendations(total_rows):
    """اقتراحات للتقسيم حسب عدد الأسطر"""
    print("\n🎯 اقتراحات التقسيم:")
    print(f"   لديك {total_rows} سطر في الملف")
    print("\n   الخيارات المقترحة:")
    
    recommendations = [
        (10, "تقسيم دقيق جداً - مناسب للمراجعة اليدوية التفصيلية"),
        (50, "تقسيم متوسط - جيد للمعالجة شبه الأوتوماتيكية"),
        (100, "تقسيم متوازن - الأفضل للمعالجة بـ AI Agent"),
        (200, "تقسيم كبير - للمعالجة السريعة"),
        (500, "دفعات كبيرة - للمشاكل البسيطة والمتكررة")
    ]
    
    for rows, desc in recommendations:
        files = math.ceil(total_rows / rows)
        print(f"   {rows:>3} سطر/ملف = {files:>3} ملف - {desc}")
    
    print("\n   💡 التوصية: 100 سطر لكل ملف للتوازن بين السرعة والدقة")

def main():
    parser = argparse.ArgumentParser(description='تقسيم ملف Excel لمعالجة مشاكل Codacy')
    parser.add_argument('input_file', help='مسار ملف Excel المدخل')
    parser.add_argument('-r', '--rows', type=int, default=100, help='عدد الأسطر لكل ملف (افتراضي: 100)')
    parser.add_argument('-o', '--output', default='split_files', help='مجلد الإخراج')
    parser.add_argument('-m', '--mode', choices=['rows', 'priority', 'file', 'smart'], 
                       default='smart', help='طريقة التقسيم')
    
    args = parser.parse_args()
    
    # إنشاء المقسم
    splitter = ExcelSplitter(args.input_file, args.output)
    
    # تحميل الملف
    if not splitter.load_file():
        return
    
    # عرض الاقتراحات
    get_recommendations(splitter.total_rows)
    
    # تنفيذ التقسيم
    print(f"\n🔄 بدء التقسيم بطريقة: {args.mode}")
    
    if args.mode == 'rows':
        splitter.split_by_rows(args.rows)
    elif args.mode == 'priority':
        splitter.split_by_priority()
    elif args.mode == 'file':
        splitter.split_by_file_path()
    else:  # smart
        splitter.smart_split(args.rows)
    
    # إنشاء الملخص
    splitter.generate_summary()
    
    print("\n✅ اكتمل التقسيم بنجاح!")

if __name__ == "__main__":
    # مثال للاستخدام المباشر
    if len(os.sys.argv) == 1:
        print("مثال للاستخدام:")
        print("python excel_splitter.py codacy_issues.xlsx -r 100")
        print("\nأو لتقسيم 3100 سطر:")
        
        # محاكاة للملف الخاص بك
        print("\n📊 تحليل ملف 3100 سطر:")
        get_recommendations(3100)
        
        print("\n🚀 أوامر مقترحة:")
        print("   # للتقسيم السريع (10 أسطر):")
        print("   python excel_splitter.py codacy_issues.xlsx -r 10")
        print("\n   # للتقسيم المتوازن (100 سطر):")
        print("   python excel_splitter.py codacy_issues.xlsx -r 100")
        print("\n   # للتقسيم حسب الأولوية:")
        print("   python excel_splitter.py codacy_issues.xlsx -m priority")
    else:
        main()