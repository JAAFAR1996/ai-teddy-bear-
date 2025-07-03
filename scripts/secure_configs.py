import os
import json
from cryptography.fernet import Fernet

def secure_configs():
    # إنشاء مفتاح تشفير
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)
    
    cipher = Fernet(key)
    
    # تشفير ملفات التكوين
    config_files = [
        'config/api_keys.json',
        'config/production_config.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            encrypted = cipher.encrypt(json.dumps(data).encode())
            with open(config_file + '.enc', 'wb') as f:
                f.write(encrypted)
            
            os.remove(config_file)

if __name__ == "__main__":
    secure_configs() 