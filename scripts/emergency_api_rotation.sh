#!/bin/bash
# emergency_api_rotation.sh - إجراءات الطوارئ الأمنية
# Security Team - إلغاء جميع API Keys المكشوفة

set -euo pipefail

# ألوان للتنبيهات
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 EMERGENCY API ROTATION INITIATED 🚨${NC}"
echo "=========================================="

# قائمة الخدمات للتحديث الفوري
SERVICES=(
    "OpenAI"
    "Anthropic"
    "Azure"
    "ElevenLabs"
    "Google_Gemini"
    "Hume_AI"
    "HuggingFace"
    "Cohere"
    "Perspective"
)

# مفتاح Google Gemini المكشوف - يجب إلغاؤه فوراً!
COMPROMISED_GOOGLE_KEY="AIzaSyCXDVCTFdvbzSiXf6JjHZAsAFxexo3OMbQ"

echo -e "${RED}⚠️  CRITICAL: Found exposed Google Gemini API key!${NC}"
echo -e "${RED}Key: ${COMPROMISED_GOOGLE_KEY}${NC}"
echo -e "${YELLOW}This key MUST be revoked immediately!${NC}"

# وظيفة للتحقق من وجود Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is available${NC}"
}

# وظيفة لإعداد HashiCorp Vault
setup_vault() {
    echo -e "${YELLOW}🔐 Setting up HashiCorp Vault...${NC}"
    
    # إيقاف أي container موجود مسبقاً
    docker stop vault 2>/dev/null || true
    docker rm vault 2>/dev/null || true
    
    # تشغيل Vault في وضع التطوير
    docker run -d --name vault \
        -p 8200:8200 \
        -e 'VAULT_DEV_ROOT_TOKEN_ID=hvs.emergency.$(date +%s)' \
        -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
        -e 'VAULT_API_ADDR=http://0.0.0.0:8200' \
        vault:latest
    
    # انتظار تشغيل Vault
    echo "Waiting for Vault to start..."
    sleep 10
    
    # تصدير متغيرات Vault
    export VAULT_ADDR='http://127.0.0.1:8200'
    export VAULT_TOKEN="hvs.emergency.$(date +%s)"
    
    echo -e "${GREEN}✅ Vault is running on http://localhost:8200${NC}"
    echo -e "${GREEN}🔑 Root token: ${VAULT_TOKEN}${NC}"
}

# وظيفة لتمكين KV secrets engine
enable_kv_secrets() {
    echo -e "${YELLOW}🔧 Enabling KV secrets engine...${NC}"
    
    docker exec vault vault secrets enable -path=teddy-secrets kv-v2
    
    echo -e "${GREEN}✅ KV secrets engine enabled at path: teddy-secrets${NC}"
}

# وظيفة لتخزين الأسرار الجديدة في Vault
store_secrets_in_vault() {
    echo -e "${YELLOW}🔐 Storing new API keys in Vault...${NC}"
    
    # تخزين مفاتيح API الجديدة (مع placeholders آمنة)
    docker exec vault vault kv put teddy-secrets/api-keys \
        openai_api_key="REPLACE_WITH_NEW_OPENAI_KEY" \
        anthropic_api_key="REPLACE_WITH_NEW_ANTHROPIC_KEY" \
        azure_speech_key="REPLACE_WITH_NEW_AZURE_KEY" \
        elevenlabs_api_key="REPLACE_WITH_NEW_ELEVENLABS_KEY" \
        google_gemini_api_key="REPLACE_WITH_NEW_GOOGLE_KEY" \
        hume_api_key="REPLACE_WITH_NEW_HUME_KEY" \
        huggingface_api_key="REPLACE_WITH_NEW_HUGGINGFACE_KEY" \
        cohere_api_key="REPLACE_WITH_NEW_COHERE_KEY" \
        perspective_api_key="REPLACE_WITH_NEW_PERSPECTIVE_KEY"
    
    # تخزين مفاتيح الأمان
    docker exec vault vault kv put teddy-secrets/security \
        encryption_key="$(openssl rand -base64 32)" \
        jwt_secret="$(openssl rand -base64 64)" \
        session_secret="$(openssl rand -base64 32)"
    
    echo -e "${GREEN}✅ Secrets stored in Vault${NC}"
}

# وظيفة لإنشاء سياسات Vault
create_vault_policies() {
    echo -e "${YELLOW}📋 Creating Vault policies...${NC}"
    
    # سياسة للقراءة فقط
    docker exec vault vault policy write teddy-read-only - <<EOF
path "teddy-secrets/data/api-keys" {
  capabilities = ["read"]
}
path "teddy-secrets/data/security" {
  capabilities = ["read"]
}
EOF
    
    # سياسة للكتابة والقراءة
    docker exec vault vault policy write teddy-admin - <<EOF
path "teddy-secrets/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF
    
    echo -e "${GREEN}✅ Vault policies created${NC}"
}

# وظيفة لإنشاء tokens مع صلاحيات محددة
create_vault_tokens() {
    echo -e "${YELLOW}🎫 Creating Vault tokens...${NC}"
    
    # token للتطبيق (قراءة فقط)
    APP_TOKEN=$(docker exec vault vault token create -policy=teddy-read-only -format=json | jq -r .auth.client_token)
    
    # token للإدارة
    ADMIN_TOKEN=$(docker exec vault vault token create -policy=teddy-admin -format=json | jq -r .auth.client_token)
    
    echo -e "${GREEN}✅ Application token: ${APP_TOKEN}${NC}"
    echo -e "${GREEN}✅ Admin token: ${ADMIN_TOKEN}${NC}"
    
    # حفظ tokens في ملف آمن
    cat > .vault_tokens << EOF
# Vault Tokens - KEEP SECURE!
VAULT_ADDR=http://localhost:8200
VAULT_APP_TOKEN=${APP_TOKEN}
VAULT_ADMIN_TOKEN=${ADMIN_TOKEN}
EOF
    
    chmod 600 .vault_tokens
    echo -e "${GREEN}✅ Tokens saved to .vault_tokens${NC}"
}

# وظيفة لتنظيف الملفات المكشوفة
cleanup_exposed_keys() {
    echo -e "${YELLOW}🧹 Cleaning up exposed keys...${NC}"
    
    # إنشاء نسخة احتياطية قبل التنظيف
    cp config/config.json config/config.json.backup.$(date +%s)
    cp config/config/config.json config/config/config.json.backup.$(date +%s)
    
    # استبدال المفاتيح المكشوفة بمتغيرات بيئة
    sed -i 's/AIzaSyCXDVCTFdvbzSiXf6JjHZAsAFxexo3OMbQ/${GOOGLE_GEMINI_API_KEY}/g' config/config.json
    sed -i 's/AIzaSyCXDVCTFdvbzSiXf6JjHZAsAFxexo3OMbQ/${GOOGLE_GEMINI_API_KEY}/g' config/config/config.json
    
    echo -e "${GREEN}✅ Exposed keys replaced with environment variables${NC}"
}

# وظيفة لإنشاء ملف .env آمن
create_secure_env_file() {
    echo -e "${YELLOW}📝 Creating secure .env template...${NC}"
    
    cat > .env.template << EOF
# Teddy Bear AI - Secure Environment Variables
# DO NOT commit this file with real values!

# Vault Configuration
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=your_vault_token_here

# API Keys - Replace with actual keys after rotation
OPENAI_API_KEY=your_new_openai_key_here
ANTHROPIC_API_KEY=your_new_anthropic_key_here
AZURE_SPEECH_KEY=your_new_azure_key_here
ELEVENLABS_API_KEY=your_new_elevenlabs_key_here
GOOGLE_GEMINI_API_KEY=your_new_google_key_here
HUME_API_KEY=your_new_hume_key_here
HUGGINGFACE_API_KEY=your_new_huggingface_key_here
COHERE_API_KEY=your_new_cohere_key_here
PERSPECTIVE_API_KEY=your_new_perspective_key_here

# Security Keys
ENCRYPTION_KEY=your_encryption_key_here
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here

# Database
DATABASE_URL=sqlite:///./core/data/teddy.db

# Application Settings
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
EOF
    
    # إضافة .env إلى .gitignore إذا لم يكن موجوداً
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo ".env" >> .gitignore
        echo ".vault_tokens" >> .gitignore
        echo "*.backup.*" >> .gitignore
    fi
    
    echo -e "${GREEN}✅ Secure .env template created${NC}"
}

# وظيفة لإنشاء script للتحقق من الأمان
create_security_checker() {
    echo -e "${YELLOW}🔍 Creating security checker script...${NC}"
    
    cat > scripts/security_checker.py << 'EOF'
#!/usr/bin/env python3
"""
Security Checker - فحص الكود للتأكد من عدم وجود مفاتيح مكشوفة
"""

import re
import os
import sys
import json
from pathlib import Path

# أنماط مفاتيح API الشائعة
API_KEY_PATTERNS = [
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI
    r'sk-ant-[a-zA-Z0-9]{95}',  # Anthropic
    r'AIza[0-9A-Za-z\-_]{35}',  # Google
    r'xoxb-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}',  # Slack
    r'rk-[a-zA-Z0-9]{32}',  # Replicate
    r'[a-zA-Z0-9]{32}',  # Generic 32-char keys
]

# مسارات للتجاهل
IGNORE_PATHS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.pytest_cache',
    'venv',
    'env',
    '.env.template',
    'scripts/security_checker.py'
]

def is_ignored_path(path):
    """التحقق من تجاهل المسار"""
    for ignore in IGNORE_PATHS:
        if ignore in str(path):
            return True
    return False

def scan_file(file_path):
    """فحص ملف واحد للبحث عن مفاتيح مكشوفة"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        findings = []
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in API_KEY_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # تجاهل التعليقات والأمثلة
                    if any(keyword in line.lower() for keyword in ['example', 'template', 'placeholder', 'your_', 'test_']):
                        continue
                    
                    findings.append({
                        'file': str(file_path),
                        'line': i,
                        'pattern': pattern,
                        'match': match.group(),
                        'context': line.strip()
                    })
        
        return findings
    except Exception as e:
        print(f"خطأ في فحص الملف {file_path}: {e}")
        return []

def scan_directory(directory):
    """فحص مجلد كامل"""
    findings = []
    
    for root, dirs, files in os.walk(directory):
        # إزالة المجلدات المتجاهلة
        dirs[:] = [d for d in dirs if not is_ignored_path(os.path.join(root, d))]
        
        for file in files:
            file_path = Path(root) / file
            
            if is_ignored_path(file_path):
                continue
                
            # فحص الملفات النصية فقط
            if file_path.suffix in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.txt', '.md']:
                file_findings = scan_file(file_path)
                findings.extend(file_findings)
    
    return findings

def main():
    """الوظيفة الرئيسية"""
    print("🔍 Security Checker - فحص الكود للمفاتيح المكشوفة")
    print("=" * 50)
    
    # فحص المجلد الحالي
    findings = scan_directory('.')
    
    if not findings:
        print("✅ لم يتم العثور على مفاتيح مكشوفة!")
        return 0
    
    print(f"🚨 تم العثور على {len(findings)} مفتاح مكشوف محتمل:")
    print()
    
    for finding in findings:
        print(f"📁 الملف: {finding['file']}")
        print(f"📍 السطر: {finding['line']}")
        print(f"🔑 المفتاح: {finding['match']}")
        print(f"📝 السياق: {finding['context']}")
        print("-" * 40)
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    chmod +x scripts/security_checker.py
    echo -e "${GREEN}✅ Security checker script created${NC}"
}

# الوظيفة الرئيسية
main() {
    echo -e "${YELLOW}Starting Emergency API Rotation Protocol...${NC}"
    
    # التحقق من متطلبات النظام
    check_docker
    
    # إعداد Vault
    setup_vault
    enable_kv_secrets
    store_secrets_in_vault
    create_vault_policies
    create_vault_tokens
    
    # تنظيف المفاتيح المكشوفة
    cleanup_exposed_keys
    
    # إنشاء ملفات الأمان
    create_secure_env_file
    create_security_checker
    
    echo -e "${GREEN}✅ Emergency API rotation completed!${NC}"
    echo -e "${YELLOW}📋 Next steps:${NC}"
    echo "1. Revoke the compromised Google Gemini API key in Google Cloud Console"
    echo "2. Generate new API keys for all services"
    echo "3. Update the keys in Vault using the admin token"
    echo "4. Run the security checker regularly: python scripts/security_checker.py"
    echo "5. Review and update the .env.template file"
    
    echo -e "${RED}⚠️  IMPORTANT: The exposed Google Gemini key must be revoked immediately!${NC}"
    echo -e "${RED}Key: ${COMPROMISED_GOOGLE_KEY}${NC}"
}

# تنفيذ البرنامج
main "$@" 