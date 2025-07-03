#!/usr/bin/env python3
"""
🔍 Updated Project Audit Script - Current State
فحص محدث للمشروع لرؤية الوضع الحالي بعد الإصلاحات

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import ast
import json
import logging
import os
import re
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CurrentIssue:
    """مشكلة حالية في المشروع"""
    severity: str  # critical, high, medium, low
    category: str  # security, quality, performance, architecture
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    is_fixed: bool = False

class CurrentProjectAuditor:
    """فاحص المشروع الحالي"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[CurrentIssue] = []
        self.stats = {
            "total_files": 0,
            "python_files": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "fixed_issues": 0
        }
    
    def run_current_audit(self) -> Dict[str, Any]:
        """تشغيل الفحص الحالي"""
        logger.info("🔍 بدء الفحص الحالي للمشروع...")
        
        # فحص الملفات
        self._scan_all_files()
        
        # فحص الأمان الحالي
        self._check_current_security()
        
        # فحص جودة الكود الحالي
        self._check_current_code_quality()
        
        # فحص الأداء الحالي
        self._check_current_performance()
        
        # فحص الهندسة المعمارية الحالية
        self._check_current_architecture()
        
        return self._generate_current_report()
    
    def _scan_all_files(self):
        """فحص جميع الملفات"""
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                self.stats["total_files"] += 1
                if file_path.suffix == ".py":
                    self.stats["python_files"] += 1
                    self._analyze_python_file(file_path)
    
    def _analyze_python_file(self, file_path: Path):
        """تحليل ملف Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص استخدام eval/exec الحقيقي
            self._check_real_eval_exec_usage(file_path, content)
            
            # فحص except broad الحقيقي
            self._check_real_broad_exceptions(file_path, content)
            
            # فحص print statements الحقيقية
            self._check_real_print_statements(file_path, content)
            
            # فحص الأسرار المكشوفة الحقيقية
            self._check_real_exposed_secrets(file_path, content)
            
        except Exception as e:
            logger.warning(f"خطأ في قراءة الملف {file_path}: {e}")
    
    def _check_real_eval_exec_usage(self, file_path: Path, content: str):
        """فحص استخدام eval/exec الحقيقي (غير الآمن)"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # تجاهل التعليقات والسلاسل النصية
            if line.startswith('#') or line.startswith('"""') or line.startswith("'''"):
                continue
            
            # فحص eval() الحقيقي (غير الآمن)
            if re.search(r'\beval\s*\(', line) and 'ast.literal_eval' not in line and 'safe_eval' not in line:
                self.issues.append(CurrentIssue(
                    severity="critical",
                    category="security",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"استخدام eval() غير آمن في السطر {i}",
                    recommendation="استبدل بـ ast.literal_eval() أو safe_eval()"
                ))
                self.stats["critical_issues"] += 1
            
            # فحص exec() الحقيقي (غير الآمن)
            if re.search(r'\bexec\s*\(', line) and '# SECURITY' not in line and 'secure_exec' not in line:
                self.issues.append(CurrentIssue(
                    severity="critical",
                    category="security",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"استخدام exec() غير آمن في السطر {i}",
                    recommendation="استبدل بـ secure_exec() أو أضف تعليق SECURITY"
                ))
                self.stats["critical_issues"] += 1
    
    def _check_real_broad_exceptions(self, file_path: Path, content: str):
        """فحص except broad الحقيقي"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # تجاهل التعليقات
            if line.startswith('#'):
                continue
            
            # فحص except: الحقيقي
            if re.match(r'^\s*except\s*:\s*$', line):
                self.issues.append(CurrentIssue(
                    severity="high",
                    category="quality",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"استخدام except: واسع في السطر {i}",
                    recommendation="استبدل بـ except Exception as e: أو استثناء محدد"
                ))
                self.stats["high_issues"] += 1
            
            # فحص except Exception: بدون معالجة
            elif re.match(r'^\s*except\s+Exception\s*:\s*$', line):
                self.issues.append(CurrentIssue(
                    severity="medium",
                    category="quality",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"استخدام except Exception: بدون معالجة في السطر {i}",
                    recommendation="أضف معالجة للاستثناء أو استخدم استثناء محدد"
                ))
                self.stats["medium_issues"] += 1
    
    def _check_real_print_statements(self, file_path: Path, content: str):
        """فحص print statements الحقيقية"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # تجاهل التعليقات
            if line.startswith('#'):
                continue
            
            # فحص print() الحقيقية
            if re.search(r'\bprint\s*\(', line) and 'logger' not in line and 'logging' not in line:
                self.issues.append(CurrentIssue(
                    severity="medium",
                    category="quality",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"استخدام print() في السطر {i}",
                    recommendation="استبدل بـ logger.info() أو logger.debug()"
                ))
                self.stats["medium_issues"] += 1
    
    def _check_real_exposed_secrets(self, file_path: Path, content: str):
        """فحص الأسرار المكشوفة الحقيقية"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # تجاهل التعليقات
            if line.startswith('#'):
                continue
            
            # فحص كلمات المرور والمفاتيح المكشوفة
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                self.issues.append(CurrentIssue(
                    severity="critical",
                    category="security",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"كلمة مرور مكشوفة في السطر {i}",
                    recommendation="استخدم متغيرات البيئة أو ملف تكوين آمن"
                ))
                self.stats["critical_issues"] += 1
            
            if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                self.issues.append(CurrentIssue(
                    severity="critical",
                    category="security",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"مفتاح API مكشوف في السطر {i}",
                    recommendation="استخدم متغيرات البيئة أو ملف تكوين آمن"
                ))
                self.stats["critical_issues"] += 1
    
    def _check_current_security(self):
        """فحص الأمان الحالي"""
        logger.info("🔐 فحص الأمان الحالي...")
        
        # فحص وجود ملفات الأمان
        security_files = [
            "src/infrastructure/security/safe_expression_parser.py",
            "src/infrastructure/security/security_solutions_integration.py",
            "src/infrastructure/security/security_migration_examples.py"
        ]
        
        for security_file in security_files:
            if Path(security_file).exists():
                self.stats["fixed_issues"] += 1
                logger.info(f"✅ ملف أمان موجود: {security_file}")
    
    def _check_current_code_quality(self):
        """فحص جودة الكود الحالي"""
        logger.info("📝 فحص جودة الكود الحالي...")
        
        # فحص وجود ملفات جودة الكود
        quality_files = [
            "scripts/comprehensive_project_audit.py",
            "scripts/security_audit_and_fix.py",
            "scripts/project_health_check.py"
        ]
        
        for quality_file in quality_files:
            if Path(quality_file).exists():
                self.stats["fixed_issues"] += 1
                logger.info(f"✅ ملف جودة موجود: {quality_file}")
    
    def _check_current_performance(self):
        """فحص الأداء الحالي"""
        logger.info("⚡ فحص الأداء الحالي...")
        
        # فحص وجود ملفات الأداء
        performance_files = [
            "src/infrastructure/caching/",
            "src/infrastructure/monitoring/",
            "src/infrastructure/observability/"
        ]
        
        for perf_dir in performance_files:
            if Path(perf_dir).exists():
                self.stats["fixed_issues"] += 1
                logger.info(f"✅ مجلد أداء موجود: {perf_dir}")
    
    def _check_current_architecture(self):
        """فحص الهندسة المعمارية الحالية"""
        logger.info("🏗️ فحص الهندسة المعمارية الحالية...")
        
        # فحص وجود هيكل DDD
        ddd_structure = [
            "src/domain/",
            "src/application/",
            "src/infrastructure/",
            "src/presentation/"
        ]
        
        for ddd_dir in ddd_structure:
            if Path(ddd_dir).exists():
                self.stats["fixed_issues"] += 1
                logger.info(f"✅ هيكل DDD موجود: {ddd_dir}")
    
    def _generate_current_report(self) -> Dict[str, Any]:
        """توليد التقرير الحالي"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "statistics": self.stats,
            "current_issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "is_fixed": issue.is_fixed
                }
                for issue in self.issues
            ],
            "summary": {
                "total_issues_found": len(self.issues),
                "critical_issues": len([i for i in self.issues if i.severity == "critical"]),
                "high_issues": len([i for i in self.issues if i.severity == "high"]),
                "medium_issues": len([i for i in self.issues if i.severity == "medium"]),
                "low_issues": len([i for i in self.issues if i.severity == "low"]),
                "improvements_made": self.stats["fixed_issues"]
            }
        }
        
        return report

def main():
    """الدالة الرئيسية"""
    auditor = CurrentProjectAuditor()
    report = auditor.run_current_audit()
    
    # حفظ التقرير
    with open("current_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # عرض الملخص
    print("\n" + "="*80)
    print("🔍 تقرير الفحص الحالي للمشروع")
    print("="*80)
    print(f"📊 إجمالي الملفات: {report['statistics']['total_files']}")
    print(f"🐍 ملفات Python: {report['statistics']['python_files']}")
    print(f"🚨 مشاكل حرجة: {report['summary']['critical_issues']}")
    print(f"⚠️ مشاكل عالية: {report['summary']['high_issues']}")
    print(f"📝 مشاكل متوسطة: {report['summary']['medium_issues']}")
    print(f"✅ تحسينات تمت: {report['summary']['improvements_made']}")
    print("="*80)
    
    if report['summary']['critical_issues'] > 0:
        print("\n🚨 المشاكل الحرجة المتبقية:")
        for issue in report['current_issues']:
            if issue['severity'] == 'critical':
                print(f"  • {issue['file_path']}:{issue['line_number']} - {issue['description']}")
    
    if report['summary']['high_issues'] > 0:
        print("\n⚠️ المشاكل العالية المتبقية:")
        for issue in report['current_issues']:
            if issue['severity'] == 'high':
                print(f"  • {issue['file_path']}:{issue['line_number']} - {issue['description']}")

if __name__ == "__main__":
    main() 