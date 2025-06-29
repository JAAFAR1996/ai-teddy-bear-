#!/usr/bin/env python3
"""
🔐 Secure Key Generator for AI Teddy Bear
Generates cryptographically secure keys for production use
"""

import secrets
import base64
import os
from cryptography.fernet import Fernet

def generate_encryption_key() -> str:
    """Generate a Fernet-compatible encryption key"""
    return Fernet.generate_key().decode()

def generate_jwt_secret(length: int = 64) -> str:
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(length)

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure application secret key"""
    return secrets.token_hex(length)

def generate_all_keys() -> dict:
    """Generate all required secure keys"""
    keys = {
        'TEDDY_ENCRYPTION_KEY': generate_encryption_key(),
        'TEDDY_JWT_SECRET': generate_jwt_secret(64),
        'TEDDY_SECRET_KEY': generate_secret_key(32),
        'BACKUP_ENCRYPTION_KEY': generate_encryption_key(),
        'TEDDY_DATABASE_ENCRYPTION_KEY': generate_encryption_key(),
    }
    return keys

def save_keys_to_file(keys: dict, filename: str = "generated_keys.env"):
    """Save generated keys to a file"""
    with open(filename, 'w') as f:
        f.write("# GENERATED SECURE KEYS\n")
        f.write("# Copy these to your .env file and DELETE this file\n")
        f.write("# Generated at: " + str(os.popen('date').read().strip()) + "\n\n")
        
        for key, value in keys.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Keys generated and saved to {filename}")
    print("⚠️  IMPORTANT: Copy these keys to your .env file and DELETE this file!")

def main():
    """Main execution"""
    print("🔐 Generating secure keys for AI Teddy Bear...")
    
    keys = generate_all_keys()
    save_keys_to_file(keys)
    
    print("\n📋 Generated Keys:")
    print("-" * 50)
    for key in keys:
        print(f"• {key}")
    
    print("\n🔒 Security Notes:")
    print("• These keys are cryptographically secure")
    print("• Store them in a secure password manager")
    print("• Never commit them to version control")
    print("• Rotate them regularly in production")

if __name__ == "__main__":
    main() 