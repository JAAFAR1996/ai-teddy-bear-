#!/usr/bin/env python3
"""
🔍 Filtered Project Audit - Real Issues Only
فحص مفلتر للمشاكل الحقيقية في ملفات المشروع فقط

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilteredAuditor:
    """فاحص مفلتر للمشاكل الحقيقية"""
    
    def __init__(self):
        self.project_issues = []
        self.venv_issues = []
        self.test_issues = []
        
    def analyze_current_report(self):
        """تحليل التقرير الحالي وفلترة المشاكل"""
        try:
            with open("current_audit_report.json", "r", encoding="utf-8") as f:
                report = json.load(f)
            
            for issue in report.get("current_issues", []):
                file_path = issue["file_path"]
                
                # تجاهل ملفات venv
                if "venv" in file_path or ".venv" in file_path:
                    self.venv_issues.append(issue)
                    continue
                
                # تجاهل ملفات الاختبار (إلا إذا كانت حرجة)
                if "test_" in file_path or "tests/" in file_path:
                    if issue["severity"] == "critical":
                        self.test_issues.append(issue)
                    continue
                
                # المشاكل الحقيقية في ملفات المشروع
                self.project_issues.append(issue)
            
            self._generate_filtered_report()
            
        except Exception as e:
            logger.error(f"خطأ في قراءة التقرير: {e}")
    
    def _generate_filtered_report(self):
        """توليد تقرير مفلتر"""
        report = {
            "timestamp": "2025-07-03T23:57:00",
            "summary": {
                "project_critical_issues": len([i for i in self.project_issues if i["severity"] == "critical"]),
                "project_high_issues": len([i for i in self.project_issues if i["severity"] == "high"]),
                "project_medium_issues": len([i for i in self.project_issues if i["severity"] == "medium"]),
                "test_critical_issues": len([i for i in self.test_issues if i["severity"] == "critical"]),
                "venv_issues_ignored": len(self.venv_issues)
            },
            "project_critical_issues": [
                {
                    "file": issue["file_path"],
                    "line": issue["line_number"],
                    "description": issue["description"],
                    "recommendation": issue["recommendation"]
                }
                for issue in self.project_issues if issue["severity"] == "critical"
            ],
            "project_high_issues": [
                {
                    "file": issue["file_path"],
                    "line": issue["line_number"],
                    "description": issue["description"],
                    "recommendation": issue["recommendation"]
                }
                for issue in self.project_issues if issue["severity"] == "high"
            ],
            "test_critical_issues": [
                {
                    "file": issue["file_path"],
                    "line": issue["line_number"],
                    "description": issue["description"],
                    "recommendation": issue["recommendation"]
                }
                for issue in self.test_issues if issue["severity"] == "critical"
            ]
        }
        
        # حفظ التقرير المفلتر
        with open("filtered_audit_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # عرض الملخص
        print("\n" + "="*80)
        print("🔍 تقرير المشاكل الحقيقية (مفلتر)")
        print("="*80)
        print(f"🚨 مشاكل حرجة في المشروع: {report['summary']['project_critical_issues']}")
        print(f"⚠️ مشاكل عالية في المشروع: {report['summary']['project_high_issues']}")
        print(f"📝 مشاكل متوسطة في المشروع: {report['summary']['project_medium_issues']}")
        print(f"🧪 مشاكل حرجة في الاختبارات: {report['summary']['test_critical_issues']}")
        print(f"🗂️ مشاكل venv تم تجاهلها: {report['summary']['venv_issues_ignored']}")
        print("="*80)
        
        if report['summary']['project_critical_issues'] > 0:
            print("\n🚨 المشاكل الحرجة في ملفات المشروع:")
            for issue in report['project_critical_issues']:
                print(f"  • {issue['file']}:{issue['line']} - {issue['description']}")
        
        if report['summary']['project_high_issues'] > 0:
            print("\n⚠️ المشاكل العالية في ملفات المشروع:")
            for issue in report['project_high_issues']:
                print(f"  • {issue['file']}:{issue['line']} - {issue['description']}")

def main():
    """الدالة الرئيسية"""
    auditor = FilteredAuditor()
    auditor.analyze_current_report()

if __name__ == "__main__":
    main() 