#!/usr/bin/env python3
"""
🎵 اختبار سريع للصوت - Audio Test
للتأكد من عمل الميكروفون والسبيكر قبل تشغيل المحاكي
"""

import pyaudio
import wave
import time
import tempfile
import pygame
import os

def test_microphone():
    """اختبار الميكروفون"""
    print("🎤 اختبار الميكروفون...")
    
    # إعدادات التسجيل
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050
    RECORD_SECONDS = 3
    
    audio = pyaudio.PyAudio()
    
    try:
        # قائمة الأجهزة المتاحة
        print("\n📋 الأجهزة الصوتية المتاحة:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"   {i}: {info['name']} (Input)")
        
        print(f"\n🔴 تسجيل لمدة {RECORD_SECONDS} ثوان...")
        print("   تحدث الآن!")
        
        # بدء التسجيل
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # حفظ التسجيل
        temp_file = tempfile.gettempdir() + "/test_recording.wav"
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print("✅ تم التسجيل بنجاح!")
        return temp_file
        
    except Exception as e:
        print(f"❌ خطأ في التسجيل: {e}")
        return None
    finally:
        audio.terminate()

def test_speaker(audio_file):
    """اختبار السبيكر"""
    if not audio_file or not os.path.exists(audio_file):
        print("❌ لا يوجد ملف صوتي للاختبار")
        return False
    
    print("\n🔊 اختبار السبيكر...")
    print("   تشغيل التسجيل...")
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # انتظار انتهاء التشغيل
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()
        print("✅ تم تشغيل الصوت بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الصوت: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧸 اختبار الصوت - محاكي الدب الذكي")
    print("=" * 40)
    
    # اختبار الميكروفون
    audio_file = test_microphone()
    
    if audio_file:
        # اختبار السبيكر
        input("\n⏸️ اضغط Enter لتشغيل التسجيل...")
        speaker_ok = test_speaker(audio_file)
        
        # تنظيف الملف المؤقت
        try:
            os.remove(audio_file)
        except:
            pass
        
        if speaker_ok:
            print("\n✅ جميع اختبارات الصوت نجحت!")
            print("🚀 يمكنك الآن تشغيل المحاكي بأمان")
        else:
            print("\n⚠️ اختبار السبيكر فشل")
            print("🔧 تحقق من إعدادات الصوت في النظام")
    else:
        print("\n❌ اختبار الميكروفون فشل")
        print("🔧 تحقق من:")
        print("   - صلاحيات الميكروفون في Windows")
        print("   - اتصال الميكروفون")
        print("   - إعدادات الصوت في النظام")
    
    input("\nاضغط Enter للخروج...")

if __name__ == "__main__":
    main() 