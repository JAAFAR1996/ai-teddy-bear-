"""
 AI Teddy Bear Project - Comprehensive Code Quality & Security Analysis
تحليل شامل لجودة الكود ومعايير الأمان - مشروع الدبدوب الذكي
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import ast


class ComprehensiveCodeAnalyzer:
    """محلل شامل لجودة الكود وأمان الأطفال"""
    
    def __init__(self):
        self.total_files = 0
        self.total_lines = 0
        self.issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "child_safety": []
        }
        
        # الأنماط الخطيرة (Critical Security Patterns)
        self.critical_patterns = {
            "sql_injection": [
                r"f\".*SELECT.*WHERE.*{.*}\"",
                r"\".*SELECT.*\" \+ .*",
                r"cursor\.execute\(.*%.*\)",
                r"\.format\(.*SELECT.*\)",
            ],
            "command_injection": [
                r"os\.system\(",
                r"subprocess\.call\(.*shell=True",
                r"subprocess\.run\(.*shell=True",
                r"eval\(",
                r"exec\(",
                r"__import__\(",
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*[\"']\w+[\"']",
                r"api_key\s*=\s*[\"']\w+[\"']",
                r"secret\s*=\s*[\"']\w+[\"']",
                r"token\s*=\s*[\"']\w+[\"']",
                r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
            ],
            "child_safety_violations": [
                r"child_name.*=.*input\(",
                r"age.*<.*3",
                r"location.*share",
                r"photo.*upload.*child",
                r"personal.*info.*collect",
                r"contact.*stranger",
            ]
        }
        
        # أنماط مكافحة الممارسات السيئة (Anti-Patterns)
        self.anti_patterns = {
            "god_class": r"class \w+:.*(?:\n.*){200,}",  # Classes > 200 lines
            "long_method": r"def \w+\(.*:.*(?:\n.*){40,}(?=\n\s*def|\n\s*class|\Z)",
            "deep_nesting": r"(\s{20,})",  # 5+ levels of indentation
            "broad_exceptions": r"except Exception:",
            "print_debugging": r"print\(",
            "synchronous_io": r"requests\.(get|post)",  # In async context
            "mutable_defaults": r"def \w+\([^)]*=\[\]",
            "circular_imports": r"from \. import .*(?=.*from .* import)",
        }
        
        # فحوصات أمان الأطفال (Child Safety Checks)
        self.child_safety_patterns = {
            "coppa_compliance": [
                r"age.*<.*13",
                r"parental.*consent",
                r"data.*collection.*child",
                r"child.*data.*delete",
            ],
            "content_filtering": [
                r"inappropriate.*content",
                r"violence.*detection",
                r"personal.*info.*block",
                r"stranger.*danger",
            ],
            "privacy_protection": [
                r"encryption.*voice",
                r"data.*retention.*90",
                r"access.*control",
                r"audit.*log",
            ]
        }
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """تحليل ملف واحد"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            self.total_files += 1
            self.total_lines += len(lines)
            
            file_issues = {
                "filepath": filepath,
                "lines": len(lines),
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "child_safety": []
            }
            
            # فحص الأنماط الخطيرة
            self._check_critical_patterns(content, filepath, file_issues)
            
            # فحص أنماط مكافحة الممارسات السيئة
            self._check_anti_patterns(content, filepath, file_issues)
            
            # فحص أمان الأطفال
            self._check_child_safety(content, filepath, file_issues)
            
            # فحص بنية الكود
            self._check_code_structure(content, filepath, file_issues)
            
            return file_issues
            
        except Exception as e:
            return {
                "filepath": filepath,
                "error": str(e),
                "lines": 0,
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "child_safety": []
            }
    
    def _check_critical_patterns(self, content: str, filepath: str, file_issues: Dict):
        """فحص الأنماط الخطيرة"""
        for category, patterns in self.critical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issue = {
                        "type": "CRITICAL",
                        "category": category,
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group()[:100],
                        "severity": "CRITICAL"
                    }
                    file_issues["critical"].append(issue)
                    self.issues["critical"].append({**issue, "file": filepath})
    
    def _check_anti_patterns(self, content: str, filepath: str, file_issues: Dict):
        """فحص أنماط مكافحة الممارسات السيئة"""
        for pattern_name, pattern in self.anti_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                severity = "HIGH" if pattern_name in ["god_class", "long_method"] else "MEDIUM"
                
                issue = {
                    "type": "ANTI_PATTERN",
                    "category": pattern_name,
                    "line": line_num,
                    "match": match.group()[:100],
                    "severity": severity
                }
                
                if severity == "HIGH":
                    file_issues["high"].append(issue)
                    self.issues["high"].append({**issue, "file": filepath})
                else:
                    file_issues["medium"].append(issue)
                    self.issues["medium"].append({**issue, "file": filepath})
    
    def _check_child_safety(self, content: str, filepath: str, file_issues: Dict):
        """فحص أمان الأطفال"""
        for category, patterns in self.child_safety_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issue = {
                        "type": "CHILD_SAFETY",
                        "category": category,
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group()[:100],
                        "severity": "HIGH"
                    }
                    file_issues["child_safety"].append(issue)
                    self.issues["child_safety"].append({**issue, "file": filepath})
    
    def _check_code_structure(self, content: str, filepath: str, file_issues: Dict):
        """فحص بنية الكود"""
        lines = content.split('\n')
        
        # فحص طول الملف
        if len(lines) > 300:
            issue = {
                "type": "STRUCTURE",
                "category": "file_too_long",
                "line": len(lines),
                "message": f"File has {len(lines)} lines (limit: 300)",
                "severity": "MEDIUM"
            }
            file_issues["medium"].append(issue)
            self.issues["medium"].append({**issue, "file": filepath})
        
        # فحص الاستيرادات غير المستخدمة
        imports = re.findall(r"^import\s+(\w+)|^from\s+(\w+)", content, re.MULTILINE)
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith(('import ', 'from ')):
                # بحث بسيط عن الاستيرادات غير المستخدمة
                import_name = re.search(r"import\s+(\w+)|from\s+\w+\s+import\s+(\w+)", line)
                if import_name:
                    module = import_name.group(1) or import_name.group(2)
                    if module and content.count(module) == 1:  # يظهر مرة واحدة فقط (في الاستيراد)
                        issue = {
                            "type": "STRUCTURE",
                            "category": "unused_import",
                            "line": line_num,
                            "message": f"Potentially unused import: {module}",
                            "severity": "LOW"
                        }
                        file_issues["low"].append(issue)
                        self.issues["low"].append({**issue, "file": filepath})
    
    def analyze_project(self, root_path: str = ".") -> Dict[str, Any]:
        """تحليل المشروع بالكامل"""
        print(" بدء التحليل الشامل لمشروع AI Teddy Bear...")
        print("=" * 60)
        
        file_results = []
        
        # مسح جميع ملفات Python
        for root, dirs, files in os.walk(root_path):
            # تجاهل المجلدات غير المهمة
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, root_path)
                    
                    print(f" تحليل: {relative_path}")
                    result = self.analyze_file(filepath)
                    file_results.append(result)
        
        return self._generate_report(file_results)
    
    def _generate_report(self, file_results: List[Dict]) -> Dict[str, Any]:
        """إنتاج التقرير النهائي"""
        # تجميع الإحصائيات
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        # تحليل أخطاء أمان الأطفال
        child_safety_score = max(0, 100 - len(self.issues["child_safety"]) * 10)
        
        # نتيجة الأمان العامة
        security_score = max(0, 100 - len(self.issues["critical"]) * 25 - len(self.issues["high"]) * 10)
        
        # نتيجة جودة الكود
        code_quality_score = max(0, 100 - len(self.issues["medium"]) * 5 - len(self.issues["low"]) * 2)
        
        # النتيجة الإجمالية
        overall_score = int((child_safety_score + security_score + code_quality_score) / 3)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "AI Teddy Bear",
            "statistics": {
                "total_files": self.total_files,
                "total_lines": self.total_lines,
                "total_issues": total_issues,
                "critical_issues": len(self.issues["critical"]),
                "high_issues": len(self.issues["high"]),
                "medium_issues": len(self.issues["medium"]),
                "low_issues": len(self.issues["low"]),
                "child_safety_issues": len(self.issues["child_safety"])
            },
            "scores": {
                "overall": overall_score,
                "child_safety": child_safety_score,
                "security": security_score,
                "code_quality": code_quality_score
            },
            "issues": self.issues,
            "file_results": file_results
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """طباعة ملخص التقرير"""
        stats = report["statistics"]
        scores = report["scores"]
        
        print("\n" + "="*60)
        print(" AI TEDDY BEAR - تقرير جودة الكود وأمان الأطفال")
        print("="*60)
        
        print(f"\n إحصائيات المشروع:")
        print(f"    إجمالي الملفات: {stats['total_files']:,}")
        print(f"    إجمالي الأسطر: {stats['total_lines']:,}")
        print(f"     إجمالي المشاكل: {stats['total_issues']:,}")
        
        print(f"\n نتائج التقييم:")
        print(f"    النتيجة الإجمالية: {scores['overall']}%")
        print(f"    أمان الأطفال: {scores['child_safety']}%")
        print(f"    الأمان العام: {scores['security']}%")
        print(f"    جودة الكود: {scores['code_quality']}%")
        
        print(f"\n تفصيل المشاكل:")
        print(f"    حرجة (Critical): {stats['critical_issues']}")
        print(f"    عالية (High): {stats['high_issues']}")
        print(f"    متوسطة (Medium): {stats['medium_issues']}")
        print(f"    منخفضة (Low): {stats['low_issues']}")
        print(f"    أمان الأطفال: {stats['child_safety_issues']}")
        
        # أسوأ الملفات
        worst_files = []
        for file_result in report["file_results"]:
            if "error" not in file_result:
                issue_count = (len(file_result["critical"]) * 4 + 
                             len(file_result["high"]) * 3 + 
                             len(file_result["medium"]) * 2 + 
                             len(file_result["low"]) * 1 +
                             len(file_result["child_safety"]) * 3)
                if issue_count > 0:
                    worst_files.append((file_result["filepath"], issue_count, file_result["lines"]))
        
        worst_files.sort(key=lambda x: x[1], reverse=True)
        
        if worst_files:
            print(f"\n  أسوأ 10 ملفات (من ناحية جودة الكود):")
            for i, (filepath, issue_count, lines) in enumerate(worst_files[:10], 1):
                relative_path = os.path.relpath(filepath)
                print(f"   {i:2d}. {relative_path}")
                print(f"        المشاكل: {issue_count} | الأسطر: {lines}")
        
        # توصيات الإصلاح
        print(f"\n توصيات الإصلاح:")
        
        if stats['critical_issues'] > 0:
            print(f"    URGENT: إصلاح {stats['critical_issues']} مشكلة حرجة فورا!")
        
        if stats['child_safety_issues'] > 0:
            print(f"    URGENT: مراجعة {stats['child_safety_issues']} مشكلة أمان الأطفال!")
        
        if stats['high_issues'] > 10:
            print(f"    HIGH: إصلاح {stats['high_issues']} مشكلة عالية الأولوية")
        
        if stats['medium_issues'] > 20:
            print(f"    تحسين {stats['medium_issues']} مشكلة متوسطة")
        
        # أمثلة على المشاكل الحرجة
        if self.issues["critical"]:
            print(f"\n أمثلة على المشاكل الحرجة:")
            for issue in self.issues["critical"][:5]:
                print(f"    {issue['category']}: {issue['file']}:{issue['line']}")
                print(f"     {issue['match'][:80]}...")
        
        # تقييم عام
        print(f"\n تقييم عام:")
        if scores['overall'] >= 90:
            print("    ممتاز! المشروع يلتزم بمعايير الجودة العالية")
        elif scores['overall'] >= 80:
            print("    جيد جدا! بعض التحسينات البسيطة مطلوبة")
        elif scores['overall'] >= 70:
            print("     متوسط! يحتاج إلى تحسينات ملحوظة")
        elif scores['overall'] >= 60:
            print("    ضعيف! يحتاج إلى إعادة هيكلة كبيرة")
        else:
            print("    خطير! المشروع يحتاج إلى إعادة كتابة شاملة")
        
        print("\n" + "="*60)


def main():
    """النقطة الرئيسية للتشغيل"""
    analyzer = ComprehensiveCodeAnalyzer()
    report = analyzer.analyze_project(".")
    analyzer.print_summary(report)
    
    # حفظ التقرير المفصل
    with open("code_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n تم حفظ التقرير المفصل في: code_quality_report.json")


if __name__ == "__main__":
    main()
