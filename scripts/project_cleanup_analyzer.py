#!/usr/bin/env python3
"""
AI Teddy Bear Project Cleanup Analyzer
تحليل شامل لتنظيف المشروع وإزالة الفوضى
"""

import os
import hashlib
import ast
import re
from pathlib import Path
from collections import defaultdict
import json
from typing import List, Dict, Any, Tuple
import shutil
from datetime import datetime

class ProjectCleanupAnalyzer:
    """محلل تنظيف المشروع الذكي"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": defaultdict(int),
            "duplicate_candidates": [],
            "large_files": [],
            "empty_files": [],
            "test_files": [],
            "config_files": [],
            "critical_files": [],
            "trash_files": [],
            "detailed_analysis": [],
            "hash_map": defaultdict(list),
            "import_dependencies": defaultdict(set),
            "suggested_moves": [],
            "security_issues": []
        }
        
        # تعريف الأنماط المهمة
        self.critical_patterns = [
            'main.py', 'app.py', 'wsgi.py', '__main__.py',
            'security/', 'auth/', 'child_safety/',
            'models/', 'entities/', 'domain/',
            'api/endpoints/', 'core/'
        ]
        
        self.trash_patterns = [
            r'.*_old\.py$', r'.*_backup\.py$', r'.*_temp\.py$',
            r'.*_copy\.py$', r'.*\.pyc$', r'__pycache__',
            r'\.pytest_cache', r'.*_test\.py$'  # إذا كان فارغاً
        ]
        
        self.ignore_dirs = {
            '.git', '__pycache__', 'node_modules', 
            '.venv', 'venv', '.pytest_cache', '.mypy_cache'
        }

    def analyze_project(self) -> Dict[str, Any]:
        """تحليل المشروع بالكامل"""
        print("🔍 بدء تحليل المشروع...")
        
        # 1. مسح جميع الملفات
        self._scan_all_files()
        
        # 2. تحليل التكرارات
        self._find_duplicates()
        
        # 3. تحليل التبعيات
        self._analyze_dependencies()
        
        # 4. اقتراح التحسينات
        self._suggest_improvements()
        
        # 5. إنشاء تقرير
        self._generate_report()
        
        return self.analysis_results

    def _scan_all_files(self):
        """مسح جميع الملفات في المشروع"""
        for root, dirs, files in os.walk(self.project_root):
            # تجاهل المجلدات غير المهمة
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            # حساب المجلدات
            self.analysis_results["total_directories"] += len(dirs)
            
            for file in files:
                self.analysis_results["total_files"] += 1
                file_path = Path(root) / file
                
                # تحديد نوع الملف
                file_ext = file_path.suffix.lower()
                self.analysis_results["file_types"][file_ext] += 1
                
                # تحليل ملفات Python
                if file_ext == '.py':
                    self._analyze_python_file(file_path)
                elif file_ext in ['.json', '.yaml', '.yml', '.ini', '.env']:
                    self._analyze_config_file(file_path)

    def _analyze_python_file(self, file_path: Path):
        """تحليل ملف Python واحد"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # حساب hash للملف
            file_hash = hashlib.md5(content.encode()).hexdigest()
            self.analysis_results["hash_map"][file_hash].append(str(file_path))
            
            # معلومات أساسية
            file_size = file_path.stat().st_size
            is_empty = len(content.strip()) == 0
            
            # تحليل AST إذا أمكن
            ast_info = self._analyze_ast(content, file_path)
            
            # تحديد نوع الملف
            file_type = self._determine_file_type(str(file_path), content)
            
            # تحديد الأهمية
            importance = self._determine_importance(
                str(file_path), content, 
                ast_info['classes'], ast_info['functions']
            )
            
            # البحث عن المشاكل
            issues = self._find_issues(content, str(file_path))
            
            # اقتراح موقع جديد
            suggested_location = self._suggest_location(str(file_path), file_type)
            
            # إنشاء تقرير الملف
            file_report = {
                "path": str(file_path),
                "type": file_type,
                "importance": importance,
                "size": file_size,
                "lines": len(lines),
                "is_empty": is_empty,
                "stats": ast_info,
                "hash": file_hash,
                "issues": issues,
                "suggested_location": suggested_location,
                "imports": ast_info.get('imports', [])
            }
            
            # إضافة إلى التصنيفات
            self._categorize_file(file_report)
            
            # إضافة إلى التحليل التفصيلي
            self.analysis_results["detailed_analysis"].append(file_report)
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل {file_path}: {e}")

    def _analyze_ast(self, content: str, file_path: Path) -> Dict[str, Any]:
        """تحليل AST للملف"""
        try:
            tree = ast.parse(content)
            
            imports = []
            import_froms = []
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_froms.append(node.module)
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': len(node.args.args),
                        'lines': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    })
            
            # تحديث import dependencies
            all_imports = imports + import_froms
            for imp in all_imports:
                self.analysis_results["import_dependencies"][str(file_path)].add(imp)
            
            return {
                'imports': all_imports,
                'classes': len(classes),
                'functions': len(functions),
                'class_details': classes,
                'function_details': functions
            }
            
        except:
            return {
                'imports': [],
                'classes': 0,
                'functions': 0,
                'class_details': [],
                'function_details': []
            }

    def _determine_file_type(self, file_path: str, content: str) -> str:
        """تحديد نوع الملف"""
        path_lower = file_path.lower()
        
        if 'test_' in path_lower or '_test.py' in path_lower:
            return 'test'
        elif 'config' in path_lower:
            return 'config'
        elif any(x in path_lower for x in ['model', 'entity', 'entities']):
            return 'model'
        elif 'service' in path_lower:
            return 'service'
        elif any(x in path_lower for x in ['repository', 'repo']):
            return 'repository'
        elif any(x in path_lower for x in ['controller', 'endpoint', 'route', 'api']):
            return 'controller'
        elif any(x in path_lower for x in ['util', 'helper']):
            return 'utility'
        elif '__init__.py' in path_lower:
            return 'init'
        elif 'migration' in path_lower:
            return 'migration'
        elif 'exception' in path_lower:
            return 'exception'
        else:
            return 'other'

    def _determine_importance(self, file_path: str, content: str, 
                            num_classes: int, num_functions: int) -> str:
        """تحديد أهمية الملف"""
        path_lower = file_path.lower()
        
        # Critical files
        if any(pattern in path_lower for pattern in self.critical_patterns):
            return 'critical'
        
        # Check for security-related content
        security_keywords = ['auth', 'security', 'child_safety', 'encryption', 'token']
        if any(keyword in path_lower or keyword in content.lower() 
               for keyword in security_keywords):
            return 'critical'
        
        # Empty or trash files
        if len(content.strip()) == 0:
            return 'trash'
        
        # Old/backup files
        if any(re.match(pattern, file_path) for pattern in self.trash_patterns):
            return 'trash'
        
        # High importance - substantial code
        if num_classes > 2 or num_functions > 5:
            return 'high'
        
        # Service/Repository files
        if any(x in path_lower for x in ['service', 'repository', 'controller']):
            return 'high'
        
        # Low importance - minimal code
        if num_classes == 0 and num_functions <= 1:
            return 'low'
        
        return 'medium'

    def _find_issues(self, content: str, file_path: str) -> List[str]:
        """إيجاد المشاكل في الملف"""
        issues = []
        
        # فحص الأمان
        if 'eval(' in content or 'exec(' in content:
            issues.append("🚨 Security: Uses eval/exec")
            self.analysis_results["security_issues"].append({
                'file': file_path,
                'issue': 'eval/exec usage'
            })
        
        # فحص معالجة الأخطاء
        if re.search(r'except\s*:', content) or re.search(r'except\s+Exception\s*:', content):
            issues.append("⚠️ Generic exception handling")
        
        # فحص print statements
        if 'print(' in content and 'test' not in file_path.lower():
            issues.append("📝 Contains print statements")
        
        # فحص TODOs
        if 'TODO' in content or 'FIXME' in content:
            issues.append("📌 Contains TODO/FIXME")
        
        # فحص حجم الملف
        lines = content.splitlines()
        if len(lines) > 500:
            issues.append(f"📏 File too large ({len(lines)} lines)")
        
        # فحص الملفات الفارغة
        if len(content.strip()) == 0:
            issues.append("📄 Empty file")
        
        # فحص hardcoded values
        if re.search(r'(password|token|secret)\s*=\s*["\']', content, re.IGNORECASE):
            issues.append("🔑 Possible hardcoded secrets")
            self.analysis_results["security_issues"].append({
                'file': file_path,
                'issue': 'hardcoded secrets'
            })
        
        return issues

    def _suggest_location(self, current_path: str, file_type: str) -> str:
        """اقتراح موقع أفضل للملف"""
        type_to_location = {
            'model': 'src/core/domain/entities/',
            'service': 'src/core/services/',
            'repository': 'src/infrastructure/persistence/repositories/',
            'controller': 'src/api/endpoints/',
            'test': 'tests/',
            'config': 'configs/',
            'utility': 'src/shared/utils/',
            'exception': 'src/core/domain/exceptions/',
            'migration': 'src/infrastructure/persistence/migrations/'
        }
        
        suggested = type_to_location.get(file_type, 'src/')
        
        # تحقق من الموقع الحالي
        if suggested in current_path:
            return None  # الملف في المكان الصحيح
            
        # إنشاء اسم ملف جديد
        filename = Path(current_path).name
        return suggested + filename

    def _categorize_file(self, file_report: Dict[str, Any]):
        """تصنيف الملف في الفئات المناسبة"""
        if file_report['is_empty']:
            self.analysis_results["empty_files"].append(file_report['path'])
        
        if file_report['size'] > 100_000:  # 100KB
            self.analysis_results["large_files"].append({
                'path': file_report['path'],
                'size': file_report['size']
            })
        
        if file_report['type'] == 'test':
            self.analysis_results["test_files"].append(file_report['path'])
        
        if file_report['type'] == 'config':
            self.analysis_results["config_files"].append(file_report['path'])
        
        if file_report['importance'] == 'critical':
            self.analysis_results["critical_files"].append(file_report['path'])
        
        if file_report['importance'] == 'trash':
            self.analysis_results["trash_files"].append(file_report['path'])
        
        if file_report['suggested_location']:
            self.analysis_results["suggested_moves"].append({
                'from': file_report['path'],
                'to': file_report['suggested_location'],
                'reason': f"Better organization for {file_report['type']} file"
            })

    def _analyze_config_file(self, file_path: Path):
        """تحليل ملف تكوين"""
        try:
            size = file_path.stat().st_size
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # البحث عن أسرار محتملة
            if re.search(r'(api_key|secret|password|token)', content, re.IGNORECASE):
                self.analysis_results["security_issues"].append({
                    'file': str(file_path),
                    'issue': 'Contains potential secrets in config'
                })
            
            self.analysis_results["config_files"].append(str(file_path))
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل ملف التكوين {file_path}: {e}")

    def _find_duplicates(self):
        """إيجاد الملفات المكررة"""
        print("🔍 البحث عن الملفات المكررة...")
        
        # التكرارات الكاملة (نفس الـ hash)
        for file_hash, files in self.analysis_results["hash_map"].items():
            if len(files) > 1:
                self.analysis_results["duplicate_candidates"].append({
                    'type': 'exact',
                    'hash': file_hash,
                    'files': files,
                    'count': len(files)
                })
        
        # التشابه الوظيفي (تحليل أعمق)
        self._find_functional_duplicates()

    def _find_functional_duplicates(self):
        """إيجاد الملفات المتشابهة وظيفياً"""
        function_signatures = defaultdict(list)
        
        for file_info in self.analysis_results["detailed_analysis"]:
            if file_info['type'] in ['service', 'utility', 'helper']:
                # استخراج توقيعات الدوال
                for func in file_info['stats'].get('function_details', []):
                    sig = f"{func['name']}({func['args']})"
                    function_signatures[sig].append(file_info['path'])
        
        # إيجاد التشابهات
        for sig, files in function_signatures.items():
            if len(files) > 1:
                self.analysis_results["duplicate_candidates"].append({
                    'type': 'functional',
                    'signature': sig,
                    'files': files,
                    'count': len(files)
                })

    def _analyze_dependencies(self):
        """تحليل التبعيات بين الملفات"""
        print("🔗 تحليل التبعيات...")
        
        # هذا يساعد في معرفة أي ملفات يمكن دمجها أو نقلها
        dependency_graph = defaultdict(set)
        
        for file_path, imports in self.analysis_results["import_dependencies"].items():
            for imp in imports:
                # تحويل import إلى مسار ملف محتمل
                if imp.startswith('.'):
                    # relative import
                    continue
                    
                # البحث عن الملف المستورد في المشروع
                possible_files = self._find_imported_file(imp)
                for pf in possible_files:
                    dependency_graph[file_path].add(pf)

    def _find_imported_file(self, import_name: str) -> List[str]:
        """إيجاد الملف المستورد"""
        possible_files = []
        
        # تحويل import إلى مسار
        path_parts = import_name.split('.')
        possible_path = os.path.join(*path_parts) + '.py'
        
        # البحث في المشروع
        for file_info in self.analysis_results["detailed_analysis"]:
            if possible_path in file_info['path']:
                possible_files.append(file_info['path'])
        
        return possible_files

    def _suggest_improvements(self):
        """اقتراح التحسينات"""
        print("💡 اقتراح التحسينات...")
        
        # إضافة اقتراحات إضافية بناءً على التحليل
        improvements = {
            'merge_candidates': [],
            'refactor_candidates': [],
            'security_fixes': []
        }
        
        # اقتراح دمج الملفات الصغيرة المتشابهة
        utility_files = [
            f for f in self.analysis_results["detailed_analysis"]
            if f['type'] == 'utility' and f['lines'] < 50
        ]
        
        if len(utility_files) > 3:
            improvements['merge_candidates'].append({
                'files': [f['path'] for f in utility_files],
                'target': 'src/shared/utils/common_utils.py',
                'reason': 'Small utility files can be merged'
            })
        
        self.analysis_results['improvements'] = improvements

    def _generate_report(self):
        """إنشاء تقرير شامل"""
        print("📊 إنشاء التقرير...")
        
        report = {
            'summary': {
                'total_files': self.analysis_results['total_files'],
                'total_directories': self.analysis_results['total_directories'],
                'critical_files': len(self.analysis_results['critical_files']),
                'trash_files': len(self.analysis_results['trash_files']),
                'duplicate_files': len(self.analysis_results['duplicate_candidates']),
                'files_to_move': len(self.analysis_results['suggested_moves']),
                'security_issues': len(self.analysis_results['security_issues'])
            },
            'file_types': dict(self.analysis_results['file_types']),
            'duplicates': self.analysis_results['duplicate_candidates'],
            'trash_files': self.analysis_results['trash_files'],
            'suggested_moves': self.analysis_results['suggested_moves'][:20],  # أول 20 اقتراح
            'security_issues': self.analysis_results['security_issues']
        }
        
        # حفظ التقرير
        with open('cleanup_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # إنشاء تقرير markdown
        self._create_markdown_report(report)

    def _create_markdown_report(self, report: Dict[str, Any]):
        """إنشاء تقرير Markdown"""
        markdown = f"""# 📊 تقرير تحليل مشروع AI Teddy Bear

## 📅 معلومات التحليل
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **إجمالي الملفات**: {report['summary']['total_files']}
- **إجمالي المجلدات**: {report['summary']['total_directories']}

## 🚨 النتائج المهمة

### 📈 الإحصائيات
- **الملفات الحرجة**: {report['summary']['critical_files']}
- **الملفات القمامة**: {report['summary']['trash_files']}
- **الملفات المكررة**: {report['summary']['duplicate_files']}
- **الملفات للنقل**: {report['summary']['files_to_move']}
- **مشاكل الأمان**: {report['summary']['security_issues']}

### 📊 أنواع الملفات
"""
        for ext, count in sorted(report['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            markdown += f"- `{ext}`: {count} ملف\n"
        
        markdown += "\n### 🗑️ ملفات للحذف الفوري\n"
        for trash_file in report['trash_files'][:20]:
            markdown += f"- `{trash_file}`\n"
        
        markdown += "\n### 🔄 ملفات مكررة\n"
        for dup in report['duplicates'][:10]:
            markdown += f"\n#### {dup['type']} duplicate ({dup['count']} files)\n"
            for file in dup['files'][:5]:
                markdown += f"- `{file}`\n"
        
        markdown += "\n### 📂 اقتراحات النقل\n"
        for move in report['suggested_moves'][:15]:
            markdown += f"- **من**: `{move['from']}`\n"
            markdown += f"  **إلى**: `{move['to']}`\n"
            markdown += f"  **السبب**: {move['reason']}\n\n"
        
        if report['security_issues']:
            markdown += "\n### 🔐 مشاكل الأمان\n"
            for issue in report['security_issues'][:10]:
                markdown += f"- **{issue['issue']}** في `{issue['file']}`\n"
        
        markdown += "\n## 🎯 الخطوات التالية\n"
        markdown += "1. حذف الملفات القمامة\n"
        markdown += "2. دمج الملفات المكررة\n"
        markdown += "3. نقل الملفات للأماكن الصحيحة\n"
        markdown += "4. إصلاح مشاكل الأمان\n"
        markdown += "5. تنظيف وإعادة هيكلة الكود\n"
        
        with open('cleanup_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(markdown)


if __name__ == "__main__":
    analyzer = ProjectCleanupAnalyzer()
    results = analyzer.analyze_project()
    
    print("\n✅ تم الانتهاء من التحليل!")
    print(f"📊 تم إنشاء التقارير:")
    print("   - cleanup_analysis_report.json")
    print("   - cleanup_analysis_report.md")
    print(f"\n🗑️ ملفات للحذف: {len(results['trash_files'])}")
    print(f"🔄 ملفات مكررة: {len(results['duplicate_candidates'])}")
    print(f"📂 ملفات للنقل: {len(results['suggested_moves'])}") 