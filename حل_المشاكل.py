#!/usr/bin/env python3
"""
🔧 حل المشاكل - محاكي الدبدوب الذكي
=====================================
سكريبت لحل المشاكل الشائعة وفحص النظام
"""

import sys
import subprocess
import platform
import socket
import requests
from datetime import datetime

def فحص_python():
    """فحص إصدار Python"""
    print("🐍 فحص Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - ممتاز!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - يحتاج Python 3.8+")
        return False

def فحص_المكتبات():
    """فحص المكتبات المطلوبة"""
    print("\n📚 فحص المكتبات...")
    
    مكتبات_مطلوبة = [
        "tkinter",
        "httpx", 
        "asyncio",
        "threading"
    ]
    
    مكتبات_ناقصة = []
    
    for مكتبة in مكتبات_مطلوبة:
        try:
            if مكتبة == "tkinter":
                import tkinter
            elif مكتبة == "httpx":
                import httpx
            elif مكتبة == "asyncio":
                import asyncio
            elif مكتبة == "threading":
                import threading
            
            print(f"✅ {مكتبة} - متوفرة")
        except ImportError:
            print(f"❌ {مكتبة} - غير متوفرة")
            مكتبات_ناقصة.append(مكتبة)
    
    return مكتبات_ناقصة

def تثبيت_المكتبات(مكتبات_ناقصة):
    """تثبيت المكتبات الناقصة"""
    if not مكتبات_ناقصة:
        return True
    
    print(f"\n💾 تثبيت المكتبات الناقصة: {', '.join(مكتبات_ناقصة)}")
    
    for مكتبة in مكتبات_ناقصة:
        if مكتبة == "tkinter":
            print("⚠️ tkinter يأتي مع Python عادة. جرب إعادة تثبيت Python")
            continue
        
        try:
            print(f"📦 تثبيت {مكتبة}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", مكتبة])
            print(f"✅ تم تثبيت {مكتبة}")
        except subprocess.CalledProcessError:
            print(f"❌ فشل تثبيت {مكتبة}")
            return False
    
    return True

def فحص_الاتصال():
    """فحص الاتصال بالإنترنت والخادم"""
    print("\n🌐 فحص الاتصال...")
    
    # فحص الإنترنت
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✅ الاتصال بالإنترنت - يعمل")
    except OSError:
        print("❌ الاتصال بالإنترنت - لا يعمل")
        return False
    
    # فحص الخادم
    try:
        response = requests.get("https://ai-teddy-bear.onrender.com/health", timeout=10)
        if response.status_code == 200:
            print("✅ خادم الدبدوب الذكي - يعمل")
            data = response.json()
            print(f"   📊 النسخة: {data.get('version', 'غير معروف')}")
            print(f"   🔗 الحالة: {data.get('status', 'غير معروف')}")
            return True
        else:
            print(f"⚠️ خادم الدبدوب الذكي - مشكلة ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ خادم الدبدوب الذكي - لا يعمل ({e})")
        return False

def فحص_الملفات():
    """فحص وجود الملفات المطلوبة"""
    print("\n📁 فحص الملفات...")
    
    ملفات_مطلوبة = [
        "محاكي_الدبدوب_الذكي.py",
        "تشغيل_المحاكي.bat", 
        "تعليمات_المحاكي.md"
    ]
    
    import os
    جميع_الملفات_موجودة = True
    
    for ملف in ملفات_مطلوبة:
        if os.path.exists(ملف):
            print(f"✅ {ملف} - موجود")
        else:
            print(f"❌ {ملف} - غير موجود")
            جميع_الملفات_موجودة = False
    
    return جميع_الملفات_موجودة

def تشغيل_المحاكي():
    """محاولة تشغيل المحاكي"""
    print("\n🚀 محاولة تشغيل المحاكي...")
    
    try:
        subprocess.Popen([sys.executable, "محاكي_الدبدوب_الذكي.py"])
        print("✅ تم تشغيل المحاكي بنجاح!")
        return True
    except Exception as e:
        print(f"❌ فشل تشغيل المحاكي: {e}")
        return False

def تقرير_النظام():
    """إنشاء تقرير عن حالة النظام"""
    print("\n📋 تقرير النظام:")
    print(f"   🖥️ نظام التشغيل: {platform.system()} {platform.release()}")
    print(f"   🐍 Python: {sys.version}")
    print(f"   ⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """الدالة الرئيسية"""
    print("🔧 حل المشاكل - محاكي الدبدوب الذكي")
    print("=" * 50)
    
    تقرير_النظام()
    
    # فحص Python
    if not فحص_python():
        print("\n❌ يرجى تحديث Python إلى إصدار 3.8 أو أحدث")
        return
    
    # فحص المكتبات
    مكتبات_ناقصة = فحص_المكتبات()
    if مكتبات_ناقصة:
        جواب = input(f"\n❓ هل تريد تثبيت المكتبات الناقصة؟ (y/n): ")
        if جواب.lower() in ['y', 'yes', 'نعم']:
            if not تثبيت_المكتبات(مكتبات_ناقصة):
                print("❌ فشل تثبيت بعض المكتبات")
                return
        else:
            print("⚠️ لن يعمل المحاكي بدون المكتبات المطلوبة")
            return
    
    # فحص الملفات
    if not فحص_الملفات():
        print("❌ بعض الملفات مفقودة. تأكد من وجود جميع الملفات")
        return
    
    # فحص الاتصال
    فحص_الاتصال()
    
    # محاولة تشغيل المحاكي
    print("\n" + "=" * 50)
    جواب = input("❓ هل تريد تشغيل المحاكي الآن؟ (y/n): ")
    if جواب.lower() in ['y', 'yes', 'نعم']:
        تشغيل_المحاكي()
    
    print("\n🎉 انتهى فحص النظام!")
    print("📖 راجع 'تعليمات_المحاكي.md' للمزيد من المساعدة")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف الفحص بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
    
    input("\nاضغط Enter للخروج...") 