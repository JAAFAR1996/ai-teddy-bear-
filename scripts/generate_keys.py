#!/usr/bin/env python3
"""
مولد مفاتيح الأمان لـ AI Teddy Bear
يولد مفاتيح التشفير و JWT بشكل آمن
"""

import base64
import secrets
import string

from cryptography.fernet import Fernet


def generate_encryption_key():
    """توليد مفتاح تشفير آمن"""
    return Fernet.generate_key().decode()


def generate_jwt_secret():
    """توليد مفتاح JWT سري"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(64))


def generate_random_key(length=32):
    """توليد مفتاح عشوائي بطول محدد"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main():
    print("🔐 مولد مفاتيح الأمان - AI Teddy Bear")
    print("=" * 50)

    # توليد المفاتيح
    encryption_key = generate_encryption_key()
    jwt_secret = generate_jwt_secret()

    print(f"\n🔑 مفتاح التشفير:")
    print(f"encryption_key: {encryption_key}")

    print(f"\n🔐 مفتاح JWT:")
    print(f"jwt_secret: {jwt_secret}")

    print(f"\n📋 انسخ هذه المفاتيح إلى ملف config/config.json:")
    print("=" * 50)
    print(f'"encryption_key": "{encryption_key}",')
    print(f'"jwt_secret": "{jwt_secret}",')

    print(f"\n✅ تم توليد المفاتيح بنجاح!")
    print("⚠️  احتفظ بهذه المفاتيح في مكان آمن!")


if __name__ == "__main__":
    main()
