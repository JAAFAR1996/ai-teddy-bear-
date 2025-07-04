from typing import Any, Dict, List
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import re
import os
import json
import hashlib
import ast
import logging

logger = logging.getLogger(__name__)

"""
🔍 Comprehensive Project File Analyzer
Analyzes every Python file in the project and generates detailed reports
"""


class ComprehensiveProjectAnalyzer:
    """محلل شامل للمشروع مع قدرات متقدمة"""

    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "total_lines": 0,
            "file_types": defaultdict(int),
            "duplicate_candidates": [],
            "large_files": [],
            "empty_files": [],
            "test_files": [],
            "config_files": [],
            "security_issues": [],
            "code_quality_issues": [],
            "dependency_analysis": defaultdict(list),
            "detailed_analysis": [],
            "suggested_moves": [],
            "health_score": 0
        }

        # تحديد الأنماط للتصنيف
        self.critical_patterns = [
            'main.py', 'app.py', 'wsgi.py', '__main__.py',
            'security/', 'auth/', 'child_safety/',
            'models/', 'entities/', 'api/endpoints/', 'core/domain/'
        ]

        self.trash_patterns = [
            r'.*_old\.py$', r'.*_backup\.py$', r'.*_temp\.py$',
            r'.*_copy\.py$', r'.*\.pyc$', r'.*~$'
        ]

    def analyze_project(self) -> Dict[str, Any]:
        """تحليل شامل لكل ملف في المشروع"""
        print("🔍 بدء التحليل الشامل للمشروع...")

        # جمع كل ملفات Python
        python_files = list(self.project_root.rglob("*.py"))
        self.analysis_results["total_files"] = len(python_files)

        # تحليل كل ملف
        for idx, file_path in enumerate(python_files, 1):
            if idx % 50 == 0:
                print(f"📊 تم تحليل {idx}/{len(python_files)} ملف...")

            # تجاهل المجلدات غير المهمة
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'backup_']):
                continue

            self.analyze_python_file(file_path)

        # حساب الصحة العامة للمشروع
        self.calculate_project_health()

        # إنشاء اقتراحات النقل
        self.generate_move_suggestions()

        # البحث عن المكررات
        self.find_duplicates()

        return self.analysis_results

    def analyze_python_file(self, file_path: Path) -> None:
        """تحليل ملف Python واحد بعمق"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()

            # إحصائيات أساسية
            self.analysis_results["total_lines"] += len(lines)

            # حساب hash للملف
            file_hash = hashlib.sha256(content.encode()).hexdigest()

            # تحليل AST إذا أمكن
            ast_analysis = self.analyze_ast(content)

            # تحديد نوع وأهمية الملف
            file_type = self.determine_file_type(file_path, content)
            importance = self.determine_importance(
                file_path, content, ast_analysis)

            # البحث عن المشاكل
            issues = self.find_issues(content, file_path)

            # تحليل التبعيات
            dependencies = self.analyze_dependencies(content, ast_analysis)

            # إنشاء تقرير الملف
            file_report = {
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(self.project_root)),
                "type": file_type,
                "importance": importance,
                "size": len(content),
                "lines": len(lines),
                "hash": file_hash,
                "ast_analysis": ast_analysis,
                "dependencies": dependencies,
                "issues": issues,
                "suggested_location": self.suggest_location(file_path, file_type),
                "can_be_deleted": importance == 'trash',
                "needs_refactoring": len(issues) > 3
            }

            # تحديث الإحصائيات
            self.analysis_results["file_types"][file_type] += 1
            self.analysis_results["detailed_analysis"].append(file_report)

            # تصنيف الملفات الخاصة
            if len(lines) == 0:
                self.analysis_results["empty_files"].append(str(file_path))
            elif len(lines) > 500:
                self.analysis_results["large_files"].append({
                    "path": str(file_path),
                    "lines": len(lines)
                })

            if 'test_' in str(file_path) or '_test.py' in str(file_path):
                self.analysis_results["test_files"].append(str(file_path))

            if 'config' in str(file_path).lower():
                self.analysis_results["config_files"].append(str(file_path))

            # تحديث قوائم المشاكل
            if any(issue.startswith("Security:") for issue in issues):
                self.analysis_results["security_issues"].append({
                    "file": str(file_path),
                    "issues": [i for i in issues if i.startswith("Security:")]
                })

            if any(issue.startswith("Quality:") for issue in issues):
                self.analysis_results["code_quality_issues"].append({
                    "file": str(file_path),
                    "issues": [i for i in issues if i.startswith("Quality:")]
                })

        except Exception as e:
            print(f"⚠️ خطأ في تحليل {file_path}: {e}")

    def analyze_ast(self, content: str) -> Dict[str, Any]:
        """تحليل AST للملف"""
        try:
            tree = ast.parse(content)

            # جمع المعلومات
            imports = []
            import_froms = []
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_froms.append(node.module)
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    })
                elif isinstance(node, ast.FunctionDef):
                    # تجاهل الميثودز داخل الكلاسات
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if node in getattr(parent, 'body', [])):
                        functions.append({
                            "name": node.name,
                            "args": len(node.args.args),
                            "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0,
                            "has_docstring": ast.get_docstring(node) is not None
                        })

            return {
                "imports": imports,
                "import_froms": import_froms,
                "classes": classes,
                "functions": functions,
                "total_imports": len(imports) + len(import_froms),
                "total_classes": len(classes),
                "total_functions": len(functions)
            }

        except:
            return {
                "imports": [],
                "import_froms": [],
                "classes": [],
                "functions": [],
                "total_imports": 0,
                "total_classes": 0,
                "total_functions": 0
            }

    def determine_file_type(self, file_path: Path, content: str) -> str:
        """تحديد نوع الملف بدقة"""
        path_str = str(file_path).lower()

        # الاختبارات
        if 'test' in path_str or 'spec' in path_str:
            return 'test'

        # التكوينات
        elif any(x in path_str for x in ['config', 'settings', 'env']):
            return 'config'

        # النماذج والكيانات
        elif any(x in path_str for x in ['model', 'entity', 'schema']):
            return 'model'

        # الخدمات
        elif 'service' in path_str or 'manager' in path_str:
            return 'service'

        # المستودعات
        elif 'repository' in path_str or 'repo' in path_str:
            return 'repository'

        # التحكم والواجهات
        elif any(x in path_str for x in ['controller', 'endpoint', 'route', 'api', 'view']):
            return 'controller'

        # الأدوات المساعدة
        elif any(x in path_str for x in ['util', 'helper', 'tool']):
            return 'utility'

        # البنية التحتية
        elif 'infrastructure' in path_str or 'infra' in path_str:
            return 'infrastructure'

        # المجال الأساسي
        elif 'domain' in path_str or 'core' in path_str:
            return 'domain'

        # السكريبتات
        elif 'script' in path_str:
            return 'script'

        # التهيئة
        elif '__init__.py' in str(file_path):
            return 'init'

        else:
            return 'other'

    def determine_importance(self, file_path: Path, content: str, ast_analysis: Dict) -> str:
        """تحديد أهمية الملف بناءً على معايير متعددة"""
        path_str = str(file_path)

        # ملفات القمامة - احذف فوراً
        if any(re.match(pattern, path_str) for pattern in self.trash_patterns):
            return 'trash'

        # ملفات فارغة
        if len(content.strip()) == 0:
            return 'trash'

        # ملفات مهمة جداً
        if any(pattern in path_str for pattern in self.critical_patterns):
            return 'critical'

        # ملفات الأمان والمصادقة
        if any(x in path_str.lower() for x in ['security', 'auth', 'permission', 'child_safety']):
            return 'critical'

        # ملفات بها منطق معقد
        if ast_analysis['total_classes'] > 2 or ast_analysis['total_functions'] > 5:
            return 'high'

        # خدمات ومستودعات
        if any(x in path_str for x in ['service', 'repository', 'manager']):
            return 'high'

        # ملفات بدون منطق حقيقي
        if ast_analysis['total_classes'] == 0 and ast_analysis['total_functions'] == 0:
            if '__init__.py' not in path_str:  # إلا إذا كان ملف تهيئة
                return 'low'

        # ملفات مؤقتة أو تجريبية
        if any(x in path_str.lower() for x in ['test_', 'example', 'demo', 'sample']):
            if len(content) < 100:  # وصغيرة
                return 'low'

        return 'medium'

    def find_issues(self, content: str, file_path: Path) -> List[str]:
        """إيجاد جميع المشاكل في الملف"""
        issues = []

        # مشاكل أمنية
        if 'eval(' in content or 'exec(' in content:
            issues.append("Security: يستخدم eval/exec (خطر أمني)")

        if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            issues.append("Security: يحتوي على كلمات سر مضمنة")

        if 'pickle.loads' in content:
            issues.append("Security: يستخدم pickle.loads (خطر أمني)")

        # مشاكل جودة الكود
        if 'except:' in content or '# FIXME: replace with specific exception
except Exception as exc:' in content:
            issues.append("Quality: معالجة استثناءات عامة")
        
        if re.search(r'print\s*\(', content) and 'test' not in str(file_path):
            issues.append("Quality: يحتوي على print في كود الإنتاج")
        
        if 'TODO' in content or 'FIXME' in content or 'XXX' in content:
            issues.append("Quality: يحتوي على TODO/FIXME")
        
        if len(content.splitlines()) > 500:
            issues.append("Quality: ملف كبير جداً (>500 سطر)")
        
        if len(content.strip()) == 0:
            issues.append("Quality: ملف فارغ")
        
        # مشاكل الاستيراد
        if 'from ..' in content and content.count('from ..') > 5:
            issues.append("Quality: الكثير من الاستيرادات النسبية")
        
        if 'import *' in content:
            issues.append("Quality: يستخدم import * (غير مستحسن)")
        
        # مشاكل الأداء
        if re.search(r'for .+ in .+:\s*for .+ in .+:', content):
            if re.search(r'for .+ in .+:\s*for .+ in .+:\s*for .+ in .+:', content):
                issues.append("Performance: حلقات متداخلة عميقة (3+ مستويات)")
        
        # مشاكل التوثيق
        if not re.search(r'""".*"""', content, re.DOTALL) and len(content) > 200:
            issues.append("Documentation: لا يحتوي على docstrings")
        
        return issues
    
    def analyze_dependencies(self, content: str, ast_analysis: Dict) -> Dict[str, List[str]]:
        """تحليل التبعيات للملف"""
        dependencies = {
            "internal": [],
            "external": [],
            "circular_risk": []
        }
        
        # التبعيات الداخلية
        for imp in ast_analysis['import_froms']:
            if imp and (imp.startswith('.') or imp.startswith('src') or imp.startswith('app')):
                dependencies["internal"].append(imp)
        
        # التبعيات الخارجية
        for imp in ast_analysis['imports']:
            if imp and not imp.startswith('.'):
                dependencies["external"].append(imp)
        
        # خطر التبعيات الدائرية
        if len(dependencies["internal"]) > 10:
            dependencies["circular_risk"].append("الكثير من التبعيات الداخلية")
        
        return dependencies
    
    def suggest_location(self, file_path: Path, file_type: str) -> str:
        """اقتراح موقع أفضل للملف"""
        current_path = str(file_path.relative_to(self.project_root))
        
        # خريطة النقل المقترحة
        type_to_location = {
            'model': 'src/core/domain/entities/',
            'service': 'src/core/services/',
            'repository': 'src/infrastructure/persistence/repositories/',
            'controller': 'src/api/endpoints/',
            'test': 'tests/unit/' if 'unit' in current_path else 'tests/',
            'config': 'configs/',
            'utility': 'src/shared/utils/',
            'domain': 'src/core/domain/',
            'infrastructure': 'src/infrastructure/',
            'script': 'scripts/',
            'init': None  # لا تنقل ملفات __init__.py
        }
        
        suggested = type_to_location.get(file_type)
        
        if not suggested or current_path.startswith(suggested):
            return None  # الملف في المكان الصحيح
        
        # إنشاء اسم الملف الجديد
        filename = file_path.name
        return suggested + filename
    
    def find_duplicates(self) -> None:
        """البحث عن الملفات المكررة أو المتشابهة"""
        # تجميع الملفات حسب الـ hash
        hash_to_files = defaultdict(list)
        
        for file_info in self.analysis_results["detailed_analysis"]:
            hash_to_files[file_info['hash']].append(file_info['path'])
        
        # إيجاد المكررات الدقيقة
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.analysis_results["duplicate_candidates"].append({
                    "type": "exact",
                    "hash": file_hash,
                    "files": files
                })
        
        # البحث عن التشابه الوظيفي
        function_signatures = defaultdict(list)
        
        for file_info in self.analysis_results["detailed_analysis"]:
            if file_info['ast_analysis']['functions']:
                for func in file_info['ast_analysis']['functions']:
                    signature = f"{func['name']}({func['args']})"
                    function_signatures[signature].append(file_info['path'])
        
        # إيجاد الدوال المكررة
        for signature, files in function_signatures.items():
            if len(files) > 1:
                self.analysis_results["duplicate_candidates"].append({
                    "type": "functional",
                    "signature": signature,
                    "files": files
                })
    
    def calculate_project_health(self) -> None:
        """حساب صحة المشروع العامة"""
        total_files = len(self.analysis_results["detailed_analysis"])
        if total_files == 0:
            self.analysis_results["health_score"] = 0
            return
        
        # حساب النقاط
        score = 100
        
        # خصم نقاط للملفات الفارغة
        empty_ratio = len(self.analysis_results["empty_files"]) / total_files
        score -= empty_ratio * 20
        
        # خصم نقاط للملفات الكبيرة
        large_ratio = len(self.analysis_results["large_files"]) / total_files
        score -= large_ratio * 15
        
        # خصم نقاط للمشاكل الأمنية
        security_ratio = len(self.analysis_results["security_issues"]) / total_files
        score -= security_ratio * 30
        
        # خصم نقاط لمشاكل الجودة
        quality_issues = sum(1 for f in self.analysis_results["detailed_analysis"] if f['needs_refactoring'])
        quality_ratio = quality_issues / total_files
        score -= quality_ratio * 20
        
        # خصم نقاط للملفات في الأماكن الخاطئة
        misplaced = sum(1 for f in self.analysis_results["detailed_analysis"] if f['suggested_location'])
        misplaced_ratio = misplaced / total_files
        score -= misplaced_ratio * 15
        
        self.analysis_results["health_score"] = max(0, min(100, score))
    
    def generate_move_suggestions(self) -> None:
        """إنشاء قائمة باقتراحات النقل"""
        for file_info in self.analysis_results["detailed_analysis"]:
            if file_info['suggested_location'] and file_info['importance'] != 'trash':
                self.analysis_results["suggested_moves"].append({
                    "from": file_info['path'],
                    "to": file_info['suggested_location'],
                    "reason": f"نقل {file_info['type']} للمكان المناسب",
                    "priority": "high" if file_info['importance'] == 'critical' else "medium"
                })
    
    def generate_report(self, output_file: str = "project_analysis_report.json") -> None:
        """إنشاء تقرير JSON مفصل"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ التقرير في: {output_file}")
        
        # طباعة ملخص
        print("\n📊 ملخص التحليل:")
        print(f"  - إجمالي الملفات: {self.analysis_results['total_files']}")
        print(f"  - إجمالي الأسطر: {self.analysis_results['total_lines']:,}")
        print(f"  - صحة المشروع: {self.analysis_results['health_score']:.1f}%")
        print(f"  - ملفات فارغة: {len(self.analysis_results['empty_files'])}")
        print(f"  - ملفات كبيرة: {len(self.analysis_results['large_files'])}")
        print(f"  - مشاكل أمنية: {len(self.analysis_results['security_issues'])}")
        print(f"  - ملفات تحتاج نقل: {len(self.analysis_results['suggested_moves'])}")


def main():
    """تشغيل التحليل الشامل"""
    analyzer = ComprehensiveProjectAnalyzer()
    results = analyzer.analyze_project()
    analyzer.generate_report()
    
    # إنشاء تقرير markdown أيضاً
    create_markdown_report(results)


def create_markdown_report(results: Dict[str, Any]) -> None:
    """إنشاء تقرير Markdown سهل القراءة"""
    with open("project_analysis_report.md", "w", encoding="utf-8") as f:
        f.write("# 📊 تقرير التحليل الشامل لمشروع AI Teddy Bear\n\n")
        f.write(f"**التاريخ**: {results['timestamp']}\n\n")
        
        f.write("## 📈 الإحصائيات العامة\n\n")
        f.write(f"- **إجمالي الملفات**: {results['total_files']}\n")
        f.write(f"- **إجمالي الأسطر**: {results['total_lines']:,}\n")
        f.write(f"- **صحة المشروع**: {results['health_score']:.1f}%\n\n")
        
        f.write("## 📁 توزيع أنواع الملفات\n\n")
        for file_type, count in sorted(results['file_types'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{file_type}**: {count} ملف\n")
        
        f.write("\n## 🚨 المشاكل المكتشفة\n\n")
        f.write(f"### مشاكل أمنية ({len(results['security_issues'])})\n")
        for issue in results['security_issues'][:5]:  # أول 5 فقط
            f.write(f"- `{issue['file']}`: {', '.join(issue['issues'])}\n")
        
        f.write(f"\n### ملفات فارغة ({len(results['empty_files'])})\n")
        for file in results['empty_files'][:10]:  # أول 10 فقط
            f.write(f"- `{file}`\n")
        
        f.write(f"\n### ملفات كبيرة ({len(results['large_files'])})\n")
        for file in sorted(results['large_files'], key=lambda x: x['lines'], reverse=True)[:5]:
            f.write(f"- `{file['path']}`: {file['lines']} سطر\n")
        
        f.write(f"\n## 📦 الملفات المكررة ({len(results['duplicate_candidates'])})\n")
        exact_dups = [d for d in results['duplicate_candidates'] if d['type'] == 'exact']
        if exact_dups:
            f.write(f"### تكرار كامل ({len(exact_dups)})\n")
            for dup in exact_dups[:5]:
                f.write(f"- الملفات: {', '.join(f'`{f}`' for f in dup['files'])}\n")
        
        f.write(f"\n## 🚚 اقتراحات النقل ({len(results['suggested_moves'])})\n")
        high_priority = [m for m in results['suggested_moves'] if m['priority'] == 'high']
        if high_priority:
            f.write("### أولوية عالية\n")
            for move in high_priority[:10]:
                f.write(f"- نقل `{move['from']}` ← `{move['to']}`\n")
    
    print("✅ تم إنشاء تقرير Markdown: project_analysis_report.md")


if __name__ == "__main__":
    main()
