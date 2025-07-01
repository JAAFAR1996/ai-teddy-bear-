#!/usr/bin/env python3
"""
🔐 GitHub Secrets Scanner Setup
إعداد نظام مسح الأسرار والحماية الأمنية لمشروع AI Teddy Bear
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# إعداد logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_github_workflow() -> None:
    """
    إنشاء GitHub Actions workflow للمسح الأمني
    """
    workflow_content = """name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run weekly security scan
    - cron: '0 2 * * 1'

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Run detect-secrets
      uses: reviewdog/action-detect-secrets@master
      with:
        reporter: github-pr-review
        github_token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Run Gitleaks
      uses: zricethezav/gitleaks-action@master
      with:
        config-path: .gitleaks.toml
        
  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Snyk
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
"""
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/security-scan.yml', 'w') as f:
        f.write(workflow_content)
    
    logger.info("✅ تم إنشاء GitHub Actions workflow للمسح الأمني")


def create_precommit_hooks() -> None:
    """
    إنشاء تكوين pre-commit hooks للحماية
    """
    precommit_content = """repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json
        
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.15.0
    hooks:
      - id: gitleaks
      
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'src/', '-f', 'json', '-o', 'bandit-report.json']
        
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3.11
"""
    
    with open('.pre-commit-config.yaml', 'w') as f:
        f.write(precommit_content)
    
    logger.info("✅ تم إنشاء تكوين pre-commit hooks")


def create_secrets_baseline() -> None:
    """
    إنشاء secrets baseline للمقارنة
    """
    try:
        result = subprocess.run([
            'detect-secrets', 'scan', '--baseline', '.secrets.baseline'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ تم إنشاء secrets baseline")
        else:
            logger.warning(f"⚠️ تحذير في إنشاء baseline: {result.stderr}")
            
    except FileNotFoundError:
        logger.warning("⚠️ detect-secrets غير مثبت - تخطي إنشاء baseline")


def create_gitleaks_config() -> None:
    """
    إنشاء تكوين Gitleaks للكشف عن التسريبات
    """
    gitleaks_config = """[extend]
useDefault = true

[[rules]]
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["key", "AWS"]

[[rules]]
description = "AWS Secret Key"
regex = '''[0-9a-zA-Z/+]{40}'''
tags = ["secret", "AWS"]

[[rules]]
description = "API Key"
regex = '''(?i)(api[_-]?key|apikey)[=:\s]+['\"]?([0-9a-zA-Z\-_]+)['\"]?'''
tags = ["api", "key"]

[[rules]]
description = "Database Password"
regex = '''(?i)(db[_-]?pass|database[_-]?password)[=:\s]+['\"]?([^\s'"]{8,})['\"]?'''
tags = ["database", "password"]

[allowlist]
description = "Ignore test files"
files = ['''tests/.*''', '''test_.*\.py''']
paths = ['''.*/tests/.*''', '''.*/test_.*''']

[allowlist]
description = "Ignore example configurations"
files = ['''.*\.example$''', '''.*\.sample$''']
"""
    
    with open('.gitleaks.toml', 'w') as f:
        f.write(gitleaks_config)
    
    logger.info("✅ تم إنشاء تكوين Gitleaks")


def create_security_policy() -> None:
    """
    إنشاء سياسة الأمان للمشروع
    """
    security_policy = """# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2025.x  | :white_check_mark: |
| < 2025  | :x:                |

## Reporting a Vulnerability

إذا اكتشفت ثغرة أمنية، يرجى إبلاغنا فوراً:

1. **لا تنشر** الثغرة علناً
2. أرسل تقريراً مفصلاً إلى: security@aiteddy.com
3. اتبع الممارسات المسؤولة للكشف

### المعلومات المطلوبة:
- وصف الثغرة
- خطوات إعادة الإنتاج
- التأثير المحتمل
- إصدار المنتج المتأثر

## Security Measures

- 🔐 تشفير البيانات الحساسة
- 🔑 إدارة آمنة للمفاتيح
- 🛡️ مسح أمني مستمر
- 📋 مراجعة الكود الأمنية
- 🔄 تحديثات أمنية منتظمة

## Best Practices

- استخدم متغيرات البيئة للأسرار
- فعّل المصادقة الثنائية
- راجع التبعيات بانتظام
- احرص على أحدث إصدارات الأمان
"""
    
    with open('SECURITY.md', 'w') as f:
        f.write(security_policy)
    
    logger.info("✅ تم إنشاء سياسة الأمان")


def create_dependabot_config() -> None:
    """
    إنشاء تكوين Dependabot للتحديثات الأمنية
    """
    dependabot_config = """version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "security-team"
    assignees:
      - "maintainer"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    reviewers:
      - "security-team"
      
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
"""
    
    os.makedirs('.github', exist_ok=True)
    with open('.github/dependabot.yml', 'w') as f:
        f.write(dependabot_config)
    
    logger.info("✅ تم إعداد Dependabot")


def create_security_scripts() -> None:
    """
    إنشاء سكريبتات الأمان المساعدة
    """
    os.makedirs('scripts/security', exist_ok=True)
    
    # سكريبت المسح الأمني
    scan_script = """#!/bin/bash
set -e

echo "🔍 Running comprehensive security scan..."

# Check for secrets
if command -v detect-secrets &> /dev/null; then
    echo "📝 Scanning for secrets..."
    detect-secrets scan --baseline .secrets.baseline
else
    echo "⚠️ detect-secrets not installed"
fi

# Check for vulnerabilities
if command -v bandit &> /dev/null; then
    echo "🛡️ Running Bandit security linter..."
    bandit -r src/ -f json -o bandit-report.json
else
    echo "⚠️ bandit not installed"
fi

# Check dependencies
if command -v safety &> /dev/null; then
    echo "📦 Checking dependencies for vulnerabilities..."
    safety check
else
    echo "⚠️ safety not installed"
fi

echo "✅ Security scan completed"
"""
    
    with open('scripts/security/scan.sh', 'w') as f:
        f.write(scan_script)
    
    os.chmod('scripts/security/scan.sh', 0o755)
    
    # سكريبت التنظيف الأمني
    cleanup_script = """#!/bin/bash
set -e

echo "🧹 Running security cleanup..."

# Remove temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.log" -delete

# Clear sensitive environment files
if [ -f ".env" ]; then
    echo "⚠️ Found .env file - should be in .gitignore"
fi

echo "✅ Security cleanup completed"
"""
    
    with open('scripts/security/cleanup.sh', 'w') as f:
        f.write(cleanup_script)
    
    os.chmod('scripts/security/cleanup.sh', 0o755)
    
    logger.info("✅ تم إنشاء سكريبتات الأمان")


def create_codeql_config() -> None:
    """
    إنشاء تكوين CodeQL للتحليل الأمني
    """
    codeql_workflow = """name: "CodeQL"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * 1'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""
    
    with open('.github/workflows/codeql.yml', 'w') as f:
        f.write(codeql_workflow)
    
    logger.info("✅ تم إنشاء تكوين CodeQL")


def main() -> None:
    """
    الدالة الرئيسية لإعداد GitHub Secrets Scanner
    """
    logger.info("🚀 بدء إعداد GitHub Secrets Scanner...")
    
    try:
        create_github_workflow()
        create_precommit_hooks()
        create_secrets_baseline()
        create_gitleaks_config()
        create_security_policy()
        create_dependabot_config()
        create_security_scripts()
        create_codeql_config()
        
        logger.info("\n✅ تم إعداد GitHub Secrets Scanner بنجاح!")
        logger.info("\n📋 التحقق من الإعداد:")
        logger.info("1. تثبيت pre-commit: pip install pre-commit")
        logger.info("2. تفعيل pre-commit: pre-commit install")
        logger.info("3. تشغيل المسح الأولي: ./scripts/security/scan.sh")
        logger.info("4. دفع التغييرات إلى GitHub لتفعيل Actions")
        
    except Exception as e:
        logger.error(f"❌ خطأ في الإعداد: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 