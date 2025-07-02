#!/usr/bin/env python3
"""
🧹 تنظيف المحاكيات القديمة
==========================
حذف المحاكيات التجريبية القديمة والاحتفاط بالمحاكي الحقيقي فقط
"""

import os
import glob
from pathlib import Path

def cleanup_old_simulators():
    """حذف المحاكيات القديمة غير المطلوبة"""
    
    print("🧹 بدء تنظيف المحاكيات القديمة...")
    
    # قائمة الملفات القديمة المراد حذفها
    old_files = [
        "محاكي_الدبدوب_الذكي.py",
        "تشغيل_المحاكي.bat", 
        "تعليمات_المحاكي.md",
        "حل_المشاكل.py",
        "قائمة_ملفات_المحاكي.txt",
        "teddy_gui.py",
        "محاكي.py",
        "ESP32_Real_Simulator.py",  # اسم خاطئ
        "scripts/esp32_teddy_gui_simulator.py"
    ]
    
    deleted_count = 0
    
    for file_path in old_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ تم حذف: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ فشل حذف {file_path}: {e}")
        else:
            print(f"⚪ غير موجود: {file_path}")
    
    # حذف ملفات temp
    temp_patterns = [
        "temp_*.wav",
        "temp_*.mp3",
        "*.tmp"
    ]
    
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"✅ تم حذف ملف مؤقت: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ فشل حذف {file_path}: {e}")
    
    print(f"\n🎯 انتهى التنظيف: تم حذف {deleted_count} ملف")
    print("\n📋 الملفات الصحيحة المتبقية:")
    print("✅ Real_ESP32_Simulator.py - المحاكي الحقيقي")
    print("✅ Run_Real_ESP32_Simulator.bat - ملف التشغيل")
    print("✅ Real_ESP32_Instructions.md - دليل الاستخدام")
    print("✅ ESP32_Files_List.txt - قائمة الملفات")
    
    return deleted_count

def check_real_simulator():
    """التحقق من وجود المحاكي الحقيقي"""
    required_files = [
        "Real_ESP32_Simulator.py",
        "Run_Real_ESP32_Simulator.bat",
        "Real_ESP32_Instructions.md"
    ]
    
    print("\n🔍 فحص الملفات المطلوبة:")
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ موجود: {file_path}")
        else:
            print(f"❌ مفقود: {file_path}")
            all_exist = False
    
    if all_exist:
        print("\n🎉 جميع ملفات المحاكي الحقيقي موجودة!")
    else:
        print("\n⚠️ بعض الملفات المطلوبة مفقودة")
    
    return all_exist

if __name__ == "__main__":
    print("🧸 ESP32 Real Simulator - تنظيف المشروع")
    print("=" * 50)
    
    # تنظيف الملفات القديمة
    cleanup_old_simulators()
    
    # فحص الملفات المطلوبة
    check_real_simulator()
    
    print("\n✨ انتهى التنظيف! المشروع جاهز للاستخدام.")
    print("🚀 تشغيل المحاكي: Run_Real_ESP32_Simulator.bat") 