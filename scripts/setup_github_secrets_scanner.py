#!/usr/bin/env python3
"""
🔍 GitHub Secrets Scanner Setup
Senior DevOps Engineer: جعفر أديب
Enterprise-grade secrets scanning for CI/CD pipelines
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class GitHubSecretsScanner:
    """إعداد مسح الأسرار في GitHub وCI/CD"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.github_dir = self.project_root / '.github'
        self.workflows_dir = self.github_dir / 'workflows'
        
    def setup_github_workflows(self):
        """إعداد GitHub Actions workflows للمسح الأمني"""
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Security scanning workflow
        security_workflow = {
            'name': 'Security Scan',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main', 'develop']},
                'schedule': [{'cron': '0 2 * * *'}]  # Daily at 2 AM
            },
            'jobs': {
                'secret-scan': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Install TruffleHog',
                            'run': 'pip install truffleHog3'
                        },
                        {
                            'name': 'Scan for secrets',
                            'run': 'trufflehog3 --format json --output secrets-report.json .'
                        },
                        {
                            'name': 'Install git-secrets',
                            'run': |
                                'sudo apt-get update && '
                                'sudo apt-get install -y git-secrets'
                        },
                        {
                            'name': 'Configure git-secrets',
                            'run': |
                                'git secrets --register-aws && '
                                'git secrets --install && '
                                'git secrets --scan'
                        },
                        {
                            'name': 'Upload security report',
                            'uses': 'actions/upload-artifact@v4',
                            'if': 'always()',
                            'with': {
                                'name': 'security-report',
                                'path': 'secrets-report.json'
                            }
                        }
                    ]
                },
                'dependency-scan': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Run Snyk security scan',
                            'uses': 'snyk/actions/python@master',
                            'env': {'SNYK_TOKEN': '${{ secrets.SNYK_TOKEN }}'}
                        }
                    ]
                }
            }
        }
        
        with open(self.workflows_dir / 'security-scan.yml', 'w') as f:
            yaml.dump(security_workflow, f, default_flow_style=False)
        
        print("✅ تم إنشاء GitHub Actions workflow للمسح الأمني")
    
    def setup_pre_commit_config(self):
        """إعداد pre-commit hooks للمسح المحلي"""
        pre_commit_config = {
            'repos': [
                {
                    'repo': 'https://github.com/pre-commit/pre-commit-hooks',
                    'rev': 'v4.4.0',
                    'hooks': [
                        {'id': 'check-yaml'},
                        {'id': 'end-of-file-fixer'},
                        {'id': 'trailing-whitespace'},
                        {'id': 'check-added-large-files'},
                        {'id': 'check-merge-conflict'}
                    ]
                },
                {
                    'repo': 'https://github.com/Yelp/detect-secrets',
                    'rev': 'v1.4.0',
                    'hooks': [
                        {
                            'id': 'detect-secrets',
                            'args': ['--baseline', '.secrets.baseline']
                        }
                    ]
                },
                {
                    'repo': 'https://github.com/trufflesecurity/trufflehog',
                    'rev': 'v3.63.2',
                    'hooks': [
                        {
                            'id': 'trufflehog',
                            'name': 'TruffleHog',
                            'description': 'Detect secrets in your data.',
                            'entry': 'bash -c "trufflehog git file://. --since-commit HEAD --only-verified --fail"',
                            'language': 'system',
                            'stages': ['commit', 'manual']
                        }
                    ]
                }
            ]
        }
        
        with open(self.project_root / '.pre-commit-config.yaml', 'w') as f:
            yaml.dump(pre_commit_config, f, default_flow_style=False)
        
        print("✅ تم إنشاء تكوين pre-commit hooks")
    
    def setup_secrets_baseline(self):
        """إنشاء baseline للأسرار المعروفة"""
        try:
            # Run detect-secrets to create baseline
            result = subprocess.run([
                'detect-secrets', 'scan', '--baseline', '.secrets.baseline'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ تم إنشاء secrets baseline")
            else:
                print(f"⚠️ تحذير في إنشاء baseline: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️ detect-secrets غير مثبت - تخطي إنشاء baseline")
    
    def create_security_policy(self):
        """إنشاء سياسة الأمان للمشروع"""
        security_policy = """# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by:

1. **DO NOT** create a public GitHub issue
2. Email security@ai-teddy.com with details
3. Include steps to reproduce the vulnerability
4. We will respond within 48 hours

## Security Measures

### Secrets Management
- All secrets are managed through HashiCorp Vault
- No hardcoded secrets in the codebase
- Automated secret rotation implemented
- Regular security audits performed

### CI/CD Security
- Secrets scanning on every commit
- Dependency vulnerability scanning
- Container security scanning
- Infrastructure as Code security scanning

### Access Control
- Principle of least privilege
- Multi-factor authentication required
- Regular access reviews
- Audit logging enabled

## Security Contact

For security-related inquiries:
- Email: security@ai-teddy.com
- PGP Key: [Public Key]
"""
        
        with open(self.project_root / 'SECURITY.md', 'w') as f:
            f.write(security_policy)
        
        print("✅ تم إنشاء سياسة الأمان")
    
    def setup_dependabot(self):
        """إعداد Dependabot لتحديثات الأمان"""
        dependabot_config = {
            'version': 2,
            'updates': [
                {
                    'package-ecosystem': 'pip',
                    'directory': '/',
                    'schedule': {'interval': 'weekly'},
                    'open-pull-requests-limit': 10,
                    'reviewers': ['@ai-teddy/security-team'],
                    'labels': ['dependencies', 'security']
                },
                {
                    'package-ecosystem': 'npm',
                    'directory': '/frontend',
                    'schedule': {'interval': 'weekly'},
                    'open-pull-requests-limit': 10,
                    'reviewers': ['@ai-teddy/security-team'],
                    'labels': ['dependencies', 'security']
                },
                {
                    'package-ecosystem': 'docker',
                    'directory': '/',
                    'schedule': {'interval': 'weekly'},
                    'reviewers': ['@ai-teddy/security-team'],
                    'labels': ['dependencies', 'security']
                }
            ]
        }
        
        with open(self.github_dir / 'dependabot.yml', 'w') as f:
            yaml.dump(dependabot_config, f, default_flow_style=False)
        
        print("✅ تم إعداد Dependabot")
    
    def create_security_scripts(self):
        """إنشاء سكريبتات الأمان المساعدة"""
        scripts_dir = self.project_root / 'scripts' / 'security'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Secret scanning script
        scan_script = """#!/bin/bash
# Security Scanning Script

set -euo pipefail

echo "🔍 بدء المسح الأمني الشامل..."

# TruffleHog scan
echo "📊 تشغيل TruffleHog..."
trufflehog git file://. --since-commit HEAD~10 --only-verified --json > trufflehog-report.json

# Detect-secrets scan
echo "🔍 تشغيل detect-secrets..."
detect-secrets scan --baseline .secrets.baseline

# Git-secrets scan
echo "🔐 تشغيل git-secrets..."
git secrets --scan

# Bandit security scan for Python
echo "🐍 تشغيل Bandit للكود Python..."
bandit -r . -f json -o bandit-report.json || true

# Safety check for Python dependencies
echo "📦 فحص تبعيات Python..."
safety check --json --output safety-report.json || true

echo "✅ انتهى المسح الأمني"
"""
        
        with open(scripts_dir / 'scan.sh', 'w') as f:
            f.write(scan_script)
        
        os.chmod(scripts_dir / 'scan.sh', 0o755)
        
        print("✅ تم إنشاء سكريبتات الأمان")
    
    def setup_codeql_analysis(self):
        """إعداد تحليل CodeQL للكود"""
        codeql_workflow = {
            'name': 'CodeQL',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']},
                'schedule': [{'cron': '0 6 * * 1'}]  # Weekly on Monday
            },
            'jobs': {
                'analyze': {
                    'name': 'Analyze',
                    'runs-on': 'ubuntu-latest',
                    'permissions': {
                        'actions': 'read',
                        'contents': 'read',
                        'security-events': 'write'
                    },
                    'strategy': {
                        'fail-fast': False,
                        'matrix': {
                            'language': ['python', 'javascript']
                        }
                    },
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Initialize CodeQL',
                            'uses': 'github/codeql-action/init@v2',
                            'with': {
                                'languages': '${{ matrix.language }}',
                                'config-file': './.github/codeql-config.yml'
                            }
                        },
                        {
                            'name': 'Autobuild',
                            'uses': 'github/codeql-action/autobuild@v2'
                        },
                        {
                            'name': 'Perform CodeQL Analysis',
                            'uses': 'github/codeql-action/analyze@v2'
                        }
                    ]
                }
            }
        }
        
        with open(self.workflows_dir / 'codeql-analysis.yml', 'w') as f:
            yaml.dump(codeql_workflow, f, default_flow_style=False)
        
        # CodeQL configuration
        codeql_config = {
            'name': 'AI Teddy CodeQL Config',
            'queries': [
                {'uses': 'security-and-quality'},
                {'uses': 'security-extended'}
            ],
            'paths-ignore': [
                'tests/',
                'docs/',
                'scripts/demo_*'
            ]
        }
        
        with open(self.github_dir / 'codeql-config.yml', 'w') as f:
            yaml.dump(codeql_config, f, default_flow_style=False)
        
        print("✅ تم إعداد تحليل CodeQL")
    
    def run_setup(self):
        """تشغيل الإعداد الكامل"""
        print("🚀 بدء إعداد GitHub Secrets Scanner...")
        
        self.setup_github_workflows()
        self.setup_pre_commit_config()
        self.setup_secrets_baseline()
        self.create_security_policy()
        self.setup_dependabot()
        self.create_security_scripts()
        self.setup_codeql_analysis()
        
        print("\n✅ تم إعداد GitHub Secrets Scanner بنجاح!")
        print("\n📋 التحقق من الإعداد:")
        print("1. تثبيت pre-commit: pip install pre-commit")
        print("2. تفعيل pre-commit: pre-commit install")
        print("3. تشغيل المسح الأولي: ./scripts/security/scan.sh")
        print("4. دفع التغييرات إلى GitHub لتفعيل Actions")

def main():
    scanner = GitHubSecretsScanner()
    scanner.run_setup()

if __name__ == "__main__":
    main() 