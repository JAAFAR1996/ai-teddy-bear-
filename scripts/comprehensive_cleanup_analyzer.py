#!/usr/bin/env python3
"""
محلل شامل لتنظيف وترتيب مشروع AI Teddy Bear
يقوم بتحليل 400+ ملف وتصنيفها واكتشاف المشاكل والتوصيات
"""

import os
import sys
import json
import hashlib
import ast
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Set
import shutil

# إضافة المسار للمشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ComprehensiveCleanupAnalyzer:
    """محلل شامل للتنظيف والترتيب"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root).resolve()
        self.results = self._initialize_results()
        
        # معايير التصنيف
        self.critical_patterns = [
            'main.py', 'app.py', 'wsgi.py', '__main__.py',
            'security/', 'auth/', 'child_safety/',
            'models/', 'entities/', 'api/endpoints/', 'core/domain/'
        ]
        
        self.trash_patterns = [
            r'.*_old\.py$', r'.*_backup\.py$', r'.*_temp\.py$',
            r'.*_copy\.py$', r'.*\.pyc$', r'.*~$', r'.*\.swp$'
        ]
        
    def _initialize_results(self) -> Dict[str, Any]:
        """تهيئة هيكل النتائج"""
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "analyzer_version": "1.0"
            },
            "summary": {
                "total_files": 0,
                "total_lines": 0,
                "total_size_mb": 0,
                "files_by_type": defaultdict(int),
                "files_by_importance": defaultdict(int)
            },
            "classification": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "trash": []
            },
            "duplicates": {
                "exact": [],
                "functional": [],
                "similar": []
            },
            "issues": {
                "empty_files": [],
                "large_files": [],
                "security_risks": [],
                "quality_issues": [],
                "misplaced_files": []
            },
            "recommendations": {
                "immediate_deletions": [],
                "suggested_moves": [],
                "refactoring_needed": [],
                "merge_candidates": []
            },
            "detailed_analysis": [],
            "health_score": {
                "overall": 0,
                "organization": 0,
                "quality": 0,
                "security": 0,
                "documentation": 0
            }
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """تحليل شامل للمشروع"""
        print("\n" + "="*60)
        print("🧹 محلل التنظيف الشامل لمشروع AI Teddy Bear")
        print("="*60 + "\n")
        
        # المرحلة 1: جمع الملفات
        print("📂 المرحلة 1: جمع وفحص الملفات...")
        all_files = self._collect_all_files()
        print(f"✅ تم العثور على {len(all_files)} ملف")
        
        # المرحلة 2: تحليل كل ملف
        print("\n📊 المرحلة 2: تحليل الملفات...")
        for idx, file_path in enumerate(all_files, 1):
            if idx % 50 == 0:
                print(f"   ⏳ تم تحليل {idx}/{len(all_files)} ملف...")
            self._analyze_file(file_path)
        
        # المرحلة 3: البحث عن المكررات
        print("\n🔍 المرحلة 3: البحث عن الملفات المكررة...")
        self._find_duplicates()
        
        # المرحلة 4: إنشاء التوصيات
        print("\n💡 المرحلة 4: إنشاء التوصيات...")
        self._generate_recommendations()
        
        # المرحلة 5: حساب الصحة العامة
        print("\n📈 المرحلة 5: حساب مقاييس الصحة...")
        self._calculate_health_scores()
        
        # طباعة ملخص سريع
        self._print_quick_summary()
        
        return self.results
    
    def _collect_all_files(self) -> List[Path]:
        """جمع جميع الملفات في المشروع"""
        files = []
        exclude_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
            'env', '.tox', '.pytest_cache', 'backup_', 'security_backup_'
        }
        
        # جمع ملفات Python
        for file_path in self.project_root.rglob("*.py"):
            if not any(excluded in str(file_path) for excluded in exclude_dirs):
                files.append(file_path)
        
        # جمع ملفات التكوين المهمة
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg"]
        for pattern in config_patterns:
            for file_path in self.project_root.rglob(pattern):
                if not any(excluded in str(file_path) for excluded in exclude_dirs):
                    files.append(file_path)
        
        # جمع ملفات أخرى مهمة
        other_patterns = ["*.md", "*.txt", "*.sh", "*.bat", "Dockerfile*", "*.sql"]
        for pattern in other_patterns:
            for file_path in self.project_root.rglob(pattern):
                if not any(excluded in str(file_path) for excluded in exclude_dirs):
                    files.append(file_path)
        
        return sorted(set(files))
    
    def _analyze_file(self, file_path: Path) -> None:
        """تحليل ملف واحد بعمق"""
        try:
            # معلومات أساسية
            file_info = {
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(self.project_root)),
                "name": file_path.name,
                "extension": file_path.suffix,
                "size_bytes": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # قراءة المحتوى
            content = self._read_file_content(file_path)
            file_info["lines"] = len(content.splitlines()) if content else 0
            file_info["hash"] = hashlib.md5(content.encode()).hexdigest() if content else ""
            
            # تحليل حسب النوع
            if file_path.suffix == '.py':
                python_analysis = self._analyze_python_file(content, file_path)
                file_info.update(python_analysis)
            
            # تحديد النوع والأهمية
            file_info["type"] = self._determine_file_type(file_path, content)
            file_info["importance"] = self._determine_importance(file_path, content, file_info)
            
            # البحث عن المشاكل
            file_info["issues"] = self._find_issues(file_path, content, file_info)
            
            # اقتراح موقع أفضل
            file_info["suggested_location"] = self._suggest_location(file_path, file_info["type"])
            
            # تحديث الإحصائيات
            self._update_statistics(file_info)
            
            # إضافة للنتائج
            self.results["detailed_analysis"].append(file_info)
            
            # تصنيف الملف
            self.results["classification"][file_info["importance"]].append(file_info["relative_path"])
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل {file_path}: {e}")
    
    def _read_file_content(self, file_path: Path) -> str:
        """قراءة محتوى الملف بأمان"""
        try:
            # محاولة قراءة بترميزات مختلفة
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
            return ""
        # FIXME: replace with specific exception
except Exception as exc:return ""
    
    def _analyze_python_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """تحليل ملف Python"""
        analysis = {
            "is_python": True,
            "ast_analysis": {},
            "complexity": 0,
            "dependencies": []
        }
        
        try:
            tree = ast.parse(content)
            
            # تحليل AST
            imports = []
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.FunctionDef):
                    if not self._is_method(node, tree):
                        functions.append({
                            "name": node.name,
                            "args": len(node.args.args),
                            "has_docstring": ast.get_docstring(node) is not None
                        })
            
            analysis["ast_analysis"] = {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "has_main": self._has_main_block(tree)
            }
            
            # حساب التعقيد
            analysis["complexity"] = len(classes) * 2 + len(functions) + len(imports) // 5
            analysis["dependencies"] = list(set(imports))
            
        except SyntaxError:
            analysis["ast_analysis"]["error"] = "Syntax error"
        except Exception as e:
            analysis["ast_analysis"]["error"] = str(e)
        
        return analysis
    
    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """التحقق من أن الدالة هي method داخل class"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def _has_main_block(self, tree: ast.AST) -> bool:
        """التحقق من وجود if __name__ == '__main__'"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                        return True
        return False
    
    def _determine_file_type(self, file_path: Path, content: str) -> str:
        """تحديد نوع الملف بدقة"""
        name_lower = file_path.name.lower()
        path_lower = str(file_path).lower()
        
        # Python files
        if file_path.suffix == '.py':
            if name_lower == '__init__.py':
                return 'init'
            elif name_lower in ['setup.py', 'manage.py']:
                return 'setup'
            elif name_lower in ['main.py', 'app.py', 'wsgi.py']:
                return 'entry_point'
            elif 'test' in path_lower:
                return 'test'
            elif 'migration' in path_lower:
                return 'migration'
            elif any(x in path_lower for x in ['model', 'entity', 'schema']):
                return 'model'
            elif 'service' in path_lower:
                return 'service'
            elif any(x in path_lower for x in ['repository', 'repo']):
                return 'repository'
            elif any(x in path_lower for x in ['controller', 'endpoint', 'handler', 'route', 'api']):
                return 'controller'
            elif any(x in path_lower for x in ['util', 'helper', 'tool']):
                return 'utility'
            elif 'script' in path_lower:
                return 'script'
            elif 'config' in path_lower:
                return 'config'
            else:
                return 'python_other'
        
        # Configuration files
        elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
            return 'config'
        
        # Documentation
        elif file_path.suffix in ['.md', '.rst', '.txt']:
            return 'documentation'
        
        # Scripts
        elif file_path.suffix in ['.sh', '.bat', '.ps1']:
            return 'script'
        
        # Docker
        elif 'dockerfile' in name_lower:
            return 'docker'
        
        # SQL
        elif file_path.suffix == '.sql':
            return 'database'
        
        else:
            return 'other'
    
    def _determine_importance(self, file_path: Path, content: str, file_info: Dict) -> str:
        """تحديد أهمية الملف"""
        path_str = str(file_path).lower()
        
        # قمامة - احذف فوراً
        if len(content.strip()) == 0 and file_path.suffix != '.py':
            self.results["issues"]["empty_files"].append(str(file_path))
            return 'trash'
        
        # ملفات __init__.py فارغة مقبولة
        if file_path.name == '__init__.py' and len(content.strip()) == 0:
            return 'low'
        
        # ملفات مؤقتة أو قديمة
        if any(re.match(pattern, path_str) for pattern in self.trash_patterns):
            return 'trash'
        
        if any(pattern in path_str for pattern in ['_old', '_backup', '_temp', '_copy', '.bak']):
            return 'trash'
        
        # حرجة - لا تحذف أبداً
        if file_path.name in ['main.py', 'app.py', 'wsgi.py', '__main__.py', 'manage.py']:
            return 'critical'
        
        if any(x in path_str for x in ['security', 'auth', 'permission', 'child_safety']):
            return 'critical'
        
        if any(pattern in path_str for pattern in self.critical_patterns):
            return 'critical'
        
        # عالية الأهمية
        if file_info.get("is_python"):
            ast_data = file_info.get("ast_analysis", {})
            if len(ast_data.get("classes", [])) > 2 or len(ast_data.get("functions", [])) > 5:
                return 'high'
        
        if any(x in path_str for x in ['service', 'repository', 'controller', 'api']):
            return 'high'
        
        if file_info.get("type") in ['model', 'service', 'repository', 'controller']:
            return 'high'
        
        # منخفضة الأهمية
        if file_info.get("is_python"):
            ast_data = file_info.get("ast_analysis", {})
            if (len(ast_data.get("classes", [])) == 0 and 
                len(ast_data.get("functions", [])) == 0 and
                file_path.name != '__init__.py'):
                return 'low'
        
        if 'example' in path_str or 'sample' in path_str or 'demo' in path_str:
            return 'low'
        
        # افتراضي
        return 'medium'
    
    def _find_issues(self, file_path: Path, content: str, file_info: Dict) -> List[Dict[str, str]]:
        """البحث عن المشاكل في الملف"""
        issues = []
        
        # ملفات كبيرة
        if file_info["size_bytes"] > 50 * 1024:  # أكبر من 50KB
            issues.append({
                "type": "size",
                "severity": "medium",
                "message": f"ملف كبير جداً ({file_info['size_bytes'] / 1024:.1f} KB)"
            })
            self.results["issues"]["large_files"].append({
                "path": str(file_path),
                "size_kb": file_info["size_bytes"] / 1024
            })
        
        # Python-specific issues
        if file_path.suffix == '.py':
            # مشاكل أمنية
            security_patterns = [
                (r'eval\s*\(', "استخدام eval() - خطر أمني"),
                (r'exec\s*\(', "استخدام exec() - خطر أمني"),
                (r'pickle\.loads', "استخدام pickle.loads - خطر أمني"),
                (r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', "كلمة سر مضمنة"),
                (r'subprocess.*shell\s*=\s*True', "استخدام shell=True - خطر أمني")
            ]
            
            for pattern, message in security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        "type": "security",
                        "severity": "high",
                        "message": message
                    })
                    self.results["issues"]["security_risks"].append({
                        "file": str(file_path),
                        "issue": message
                    })
            
            # مشاكل جودة
            if 'except:' in content or '# FIXME: replace with specific exception
except Exception as exc:' in content:
                issues.append({
                    "type": "quality",
                    "severity": "medium",
                    "message": "معالجة استثناءات عامة"
                })
            
            if re.search(r'print\s*\(', content) and 'test' not in str(file_path):
                issues.append({
                    "type": "quality",
                    "severity": "low",
                    "message": "استخدام print في كود الإنتاج"
                })
            
            # TODOs
            todos = len(re.findall(r'(TODO|FIXME|XXX|HACK)', content))
            if todos > 0:
                issues.append({
                    "type": "quality",
                    "severity": "low",
                    "message": f"يحتوي على {todos} TODO/FIXME"
                })
        
        return issues
    
    def _suggest_location(self, file_path: Path, file_type: str) -> Optional[str]:
        """اقتراح موقع أفضل للملف"""
        current = str(file_path.relative_to(self.project_root))
        
        # الهيكل المثالي
        ideal_structure = {
            'model': 'src/core/domain/entities/',
            'service': 'src/core/services/',
            'repository': 'src/infrastructure/persistence/repositories/',
            'controller': 'src/api/endpoints/',
            'test': 'tests/',
            'config': 'configs/',
            'utility': 'src/shared/utils/',
            'script': 'scripts/',
            'documentation': 'docs/',
            'docker': 'deployments/docker/',
            'migration': 'src/infrastructure/persistence/migrations/'
        }
        
        ideal_location = ideal_structure.get(file_type)
        
        if not ideal_location:
            return None
        
        # تحقق من أن الملف ليس في المكان الصحيح بالفعل
        if current.startswith(ideal_location):
            return None
        
        # إنشاء المسار الجديد
        new_path = ideal_location + file_path.name
        
        # إضافة للملفات المُزاحة
        self.results["issues"]["misplaced_files"].append({
            "current": current,
            "suggested": new_path
        })
        
        return new_path
    
    def _update_statistics(self, file_info: Dict) -> None:
        """تحديث الإحصائيات"""
        summary = self.results["summary"]
        
        summary["total_files"] += 1
        summary["total_lines"] += file_info.get("lines", 0)
        summary["total_size_mb"] += file_info["size_bytes"] / (1024 * 1024)
        summary["files_by_type"][file_info["type"]] += 1
        summary["files_by_importance"][file_info["importance"]] += 1
    
    def _find_duplicates(self) -> None:
        """البحث عن الملفات المكررة"""
        # تجميع الملفات حسب الـ hash
        hash_groups = defaultdict(list)
        
        for file_info in self.results["detailed_analysis"]:
            if file_info.get("hash"):
                hash_groups[file_info["hash"]].append(file_info)
        
        # إيجاد المكررات الدقيقة
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                self.results["duplicates"]["exact"].append({
                    "hash": file_hash,
                    "files": [f["relative_path"] for f in files],
                    "count": len(files),
                    "size_total_kb": sum(f["size_bytes"] for f in files) / 1024
                })
        
        # البحث عن التشابه الوظيفي (Python files only)
        function_signatures = defaultdict(list)
        
        for file_info in self.results["detailed_analysis"]:
            if file_info.get("is_python") and file_info.get("ast_analysis"):
                functions = file_info["ast_analysis"].get("functions", [])
                for func in functions:
                    sig = f"{func['name']}({func['args']})"
                    function_signatures[sig].append(file_info["relative_path"])
        
        # إيجاد الدوال المكررة
        for sig, files in function_signatures.items():
            if len(files) > 1:
                self.results["duplicates"]["functional"].append({
                    "signature": sig,
                    "files": files,
                    "count": len(files)
                })
        
        print(f"✅ تم العثور على {len(self.results['duplicates']['exact'])} مجموعة ملفات مكررة")
        print(f"✅ تم العثور على {len(self.results['duplicates']['functional'])} دالة مكررة")
    
    def _generate_recommendations(self) -> None:
        """إنشاء التوصيات"""
        recs = self.results["recommendations"]
        
        # 1. توصيات الحذف الفوري
        for file_path in self.results["classification"]["trash"]:
            recs["immediate_deletions"].append({
                "file": file_path,
                "reason": "ملف قمامة (فارغ/قديم/مؤقت)",
                "action": "DELETE"
            })
        
        # 2. توصيات النقل
        for file_info in self.results["detailed_analysis"]:
            if file_info.get("suggested_location"):
                recs["suggested_moves"].append({
                    "from": file_info["relative_path"],
                    "to": file_info["suggested_location"],
                    "type": file_info["type"],
                    "reason": "موقع غير مناسب"
                })
        
        # 3. توصيات إعادة الهيكلة
        for file_info in self.results["detailed_analysis"]:
            if file_info.get("lines", 0) > 500:
                recs["refactoring_needed"].append({
                    "file": file_info["relative_path"],
                    "lines": file_info["lines"],
                    "reason": "ملف كبير جداً",
                    "suggestion": "تقسيم إلى ملفات أصغر"
                })
        
        # 4. اقتراحات الدمج
        for dup_group in self.results["duplicates"]["exact"]:
            if dup_group["count"] > 1:
                recs["merge_candidates"].append({
                    "files": dup_group["files"],
                    "action": "MERGE",
                    "reason": "ملفات متطابقة تماماً"
                })
        
        print(f"✅ تم إنشاء {len(recs['immediate_deletions'])} توصية حذف")
        print(f"✅ تم إنشاء {len(recs['suggested_moves'])} توصية نقل")
        print(f"✅ تم إنشاء {len(recs['refactoring_needed'])} توصية إعادة هيكلة")
    
    def _calculate_health_scores(self) -> None:
        """حساب مقاييس صحة المشروع"""
        total_files = self.results["summary"]["total_files"]
        
        if total_files == 0:
            return
        
        # نقاط التنظيم
        misplaced_ratio = len(self.results["issues"]["misplaced_files"]) / total_files
        trash_ratio = len(self.results["classification"]["trash"]) / total_files
        organization_score = max(0, 100 - (misplaced_ratio * 50) - (trash_ratio * 30))
        
        # نقاط الجودة
        quality_issues = sum(1 for f in self.results["detailed_analysis"] 
                           if any(i["type"] == "quality" for i in f.get("issues", [])))
        quality_ratio = quality_issues / total_files
        quality_score = max(0, 100 - (quality_ratio * 60))
        
        # نقاط الأمان
        security_issues = len(self.results["issues"]["security_risks"])
        security_ratio = security_issues / total_files
        security_score = max(0, 100 - (security_ratio * 100))
        
        # نقاط التوثيق
        documented_files = sum(1 for f in self.results["detailed_analysis"]
                             if f.get("is_python") and 
                             any(c.get("has_docstring") for c in f.get("ast_analysis", {}).get("classes", [])))
        doc_ratio = documented_files / max(1, len([f for f in self.results["detailed_analysis"] if f.get("is_python")]))
        documentation_score = doc_ratio * 100
        
        # النقاط الإجمالية
        overall_score = (organization_score * 0.3 + 
                        quality_score * 0.3 + 
                        security_score * 0.3 + 
                        documentation_score * 0.1)
        
        self.results["health_score"] = {
            "overall": round(overall_score, 1),
            "organization": round(organization_score, 1),
            "quality": round(quality_score, 1),
            "security": round(security_score, 1),
            "documentation": round(documentation_score, 1)
        }
    
    def _print_quick_summary(self) -> None:
        """طباعة ملخص سريع"""
        print("\n" + "="*60)
        print("📊 ملخص التحليل السريع")
        print("="*60)
        
        summary = self.results["summary"]
        health = self.results["health_score"]
        
        print(f"\n📈 الإحصائيات العامة:")
        print(f"   • إجمالي الملفات: {summary['total_files']}")
        print(f"   • إجمالي الأسطر: {summary['total_lines']:,}")
        print(f"   • الحجم الإجمالي: {summary['total_size_mb']:.2f} MB")
        
        print(f"\n🏥 صحة المشروع:")
        print(f"   • النقاط الإجمالية: {health['overall']}%")
        print(f"   • التنظيم: {health['organization']}%")
        print(f"   • الجودة: {health['quality']}%")
        print(f"   • الأمان: {health['security']}%")
        print(f"   • التوثيق: {health['documentation']}%")
        
        print(f"\n📁 تصنيف الملفات:")
        for importance, count in self.results["summary"]["files_by_importance"].items():
            print(f"   • {importance}: {count} ملف")
        
        print(f"\n🚨 المشاكل المكتشفة:")
        print(f"   • ملفات فارغة: {len(self.results['issues']['empty_files'])}")
        print(f"   • ملفات كبيرة: {len(self.results['issues']['large_files'])}")
        print(f"   • مشاكل أمنية: {len(self.results['issues']['security_risks'])}")
        print(f"   • ملفات في مكان خاطئ: {len(self.results['issues']['misplaced_files'])}")
        
        print(f"\n💡 التوصيات:")
        recs = self.results["recommendations"]
        print(f"   • ملفات للحذف: {len(recs['immediate_deletions'])}")
        print(f"   • ملفات للنقل: {len(recs['suggested_moves'])}")
        print(f"   • ملفات تحتاج إعادة هيكلة: {len(recs['refactoring_needed'])}")
        print(f"   • مجموعات للدمج: {len(recs['merge_candidates'])}")
    
    def save_reports(self, output_dir: str = "cleanup_reports") -> None:
        """حفظ التقارير بتنسيقات مختلفة"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # حفظ JSON مفصل
        json_file = output_path / f"comprehensive_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ تم حفظ التقرير JSON: {json_file}")
        
        # حفظ تقرير Markdown
        md_file = output_path / f"cleanup_report_{timestamp}.md"
        self._save_markdown_report(md_file)
        print(f"✅ تم حفظ التقرير Markdown: {md_file}")
        
        # حفظ قائمة الإجراءات
        actions_file = output_path / f"cleanup_actions_{timestamp}.txt"
        self._save_action_list(actions_file)
        print(f"✅ تم حفظ قائمة الإجراءات: {actions_file}")
    
    def _save_markdown_report(self, file_path: Path) -> None:
        """حفظ تقرير Markdown شامل"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# 🧹 تقرير التنظيف الشامل لمشروع AI Teddy Bear\n\n")
            f.write(f"**التاريخ**: {self.results['metadata']['timestamp']}\n")
            f.write(f"**المحلل**: Comprehensive Cleanup Analyzer v{self.results['metadata']['analyzer_version']}\n\n")
            
            # ملخص تنفيذي
            f.write("## 📊 ملخص تنفيذي\n\n")
            
            health = self.results["health_score"]
            f.write(f"**صحة المشروع الإجمالية**: {health['overall']}% ")
            
            if health['overall'] >= 80:
                f.write("✅ ممتاز\n\n")
            elif health['overall'] >= 60:
                f.write("⚠️ يحتاج تحسين\n\n")
            else:
                f.write("❌ يحتاج عناية فورية\n\n")
            
            # مقاييس الصحة
            f.write("### 🏥 مقاييس الصحة\n\n")
            f.write("| المقياس | النقاط | التقييم |\n")
            f.write("|---------|--------|----------|\n")
            
            metrics = [
                ("التنظيم", health['organization']),
                ("الجودة", health['quality']),
                ("الأمان", health['security']),
                ("التوثيق", health['documentation'])
            ]
            
            for metric, score in metrics:
                if score >= 80:
                    status = "✅"
                elif score >= 60:
                    status = "⚠️"
                else:
                    status = "❌"
                f.write(f"| {metric} | {score}% | {status} |\n")
            
            # الإحصائيات
            f.write("\n## 📈 الإحصائيات العامة\n\n")
            summary = self.results["summary"]
            f.write(f"- **إجمالي الملفات**: {summary['total_files']}\n")
            f.write(f"- **إجمالي الأسطر**: {summary['total_lines']:,}\n")
            f.write(f"- **الحجم الإجمالي**: {summary['total_size_mb']:.2f} MB\n\n")
            
            # توزيع الملفات
            f.write("### 📁 توزيع الملفات حسب النوع\n\n")
            f.write("| النوع | العدد | النسبة |\n")
            f.write("|-------|-------|--------|\n")
            
            total = summary['total_files']
            for file_type, count in sorted(summary['files_by_type'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total) * 100 if total > 0 else 0
                f.write(f"| {file_type} | {count} | {percentage:.1f}% |\n")
            
            # تصنيف الأهمية
            f.write("\n### 🎯 تصنيف الملفات حسب الأهمية\n\n")
            importance_map = {
                'critical': '🔴 حرجة',
                'high': '🟠 عالية',
                'medium': '🟡 متوسطة',
                'low': '🟢 منخفضة',
                'trash': '⚫ قمامة'
            }
            
            for importance, label in importance_map.items():
                count = summary['files_by_importance'].get(importance, 0)
                f.write(f"- **{label}**: {count} ملف\n")
            
            # المشاكل المكتشفة
            f.write("\n## 🚨 المشاكل المكتشفة\n\n")
            
            issues = self.results["issues"]
            
            # ملفات فارغة
            if issues["empty_files"]:
                f.write(f"### 📄 ملفات فارغة ({len(issues['empty_files'])})\n\n")
                for file in issues["empty_files"][:10]:
                    f.write(f"- `{file}`\n")
                if len(issues["empty_files"]) > 10:
                    f.write(f"- ... و {len(issues['empty_files']) - 10} ملف آخر\n")
            
            # ملفات كبيرة
            if issues["large_files"]:
                f.write(f"\n### 📦 ملفات كبيرة ({len(issues['large_files'])})\n\n")
                for file in sorted(issues["large_files"], key=lambda x: x['size_kb'], reverse=True)[:10]:
                    f.write(f"- `{file['path']}` ({file['size_kb']:.1f} KB)\n")
            
            # مشاكل أمنية
            if issues["security_risks"]:
                f.write(f"\n### 🔐 مشاكل أمنية ({len(issues['security_risks'])})\n\n")
                for risk in issues["security_risks"][:10]:
                    f.write(f"- `{risk['file']}`: {risk['issue']}\n")
            
            # ملفات في مكان خاطئ
            if issues["misplaced_files"]:
                f.write(f"\n### 📍 ملفات في مكان خاطئ ({len(issues['misplaced_files'])})\n\n")
                f.write("| الملف | المكان الحالي | المكان المقترح |\n")
                f.write("|-------|----------------|------------------|\n")
                for misplaced in issues["misplaced_files"][:20]:
                    current = misplaced['current']
                    suggested = misplaced['suggested']
                    f.write(f"| {Path(current).name} | `{Path(current).parent}` | `{Path(suggested).parent}` |\n")
            
            # الملفات المكررة
            f.write("\n## 🔄 الملفات المكررة\n\n")
            
            duplicates = self.results["duplicates"]
            
            if duplicates["exact"]:
                f.write(f"### 📑 ملفات متطابقة تماماً ({len(duplicates['exact'])} مجموعة)\n\n")
                for idx, dup_group in enumerate(duplicates["exact"][:10], 1):
                    f.write(f"**المجموعة {idx}** ({dup_group['count']} ملفات، {dup_group['size_total_kb']:.1f} KB إجمالي):\n")
                    for file in dup_group['files']:
                        f.write(f"- `{file}`\n")
                    f.write("\n")
            
            # التوصيات
            f.write("## 💡 التوصيات والإجراءات\n\n")
            
            recs = self.results["recommendations"]
            
            # حذف فوري
            if recs["immediate_deletions"]:
                f.write(f"### 🗑️ ملفات للحذف الفوري ({len(recs['immediate_deletions'])})\n\n")
                f.write("⚠️ **تحذير**: هذه الملفات يمكن حذفها بأمان\n\n")
                
                for deletion in recs["immediate_deletions"][:20]:
                    f.write(f"- `{deletion['file']}` - {deletion['reason']}\n")
                
                if len(recs["immediate_deletions"]) > 20:
                    f.write(f"\n... و {len(recs['immediate_deletions']) - 20} ملف آخر\n")
                
                # أمر الحذف
                f.write("\n```bash\n# أمر حذف الملفات (تأكد من عمل نسخة احتياطية أولاً)\n")
                for deletion in recs["immediate_deletions"][:5]:
                    f.write(f'rm "{deletion["file"]}"\n')
                f.write("```\n")
            
            # نقل الملفات
            if recs["suggested_moves"]:
                f.write(f"\n### 📦 ملفات للنقل ({len(recs['suggested_moves'])})\n\n")
                
                # تجميع حسب النوع
                moves_by_type = defaultdict(list)
                for move in recs["suggested_moves"]:
                    moves_by_type[move['type']].append(move)
                
                for file_type, moves in moves_by_type.items():
                    f.write(f"\n**{file_type.title()} Files ({len(moves)})**:\n")
                    for move in moves[:5]:
                        f.write(f"- `{move['from']}` → `{move['to']}`\n")
            
            # إعادة هيكلة
            if recs["refactoring_needed"]:
                f.write(f"\n### 🔧 ملفات تحتاج إعادة هيكلة ({len(recs['refactoring_needed'])})\n\n")
                for refactor in recs["refactoring_needed"][:10]:
                    f.write(f"- `{refactor['file']}` ({refactor['lines']} سطر) - {refactor['suggestion']}\n")
            
            # خطة العمل
            f.write("\n## 📋 خطة العمل المقترحة\n\n")
            f.write("### المرحلة 1: التنظيف الفوري (يوم 1)\n")
            f.write(f"1. حذف {len(recs['immediate_deletions'])} ملف قمامة\n")
            f.write(f"2. دمج {len(duplicates['exact'])} مجموعة ملفات مكررة\n")
            f.write("3. عمل نسخة احتياطية قبل أي تغيير\n\n")
            
            f.write("### المرحلة 2: إعادة التنظيم (يوم 2-3)\n")
            f.write(f"1. نقل {len(recs['suggested_moves'])} ملف للأماكن الصحيحة\n")
            f.write("2. تحديث جميع imports المتأثرة\n")
            f.write("3. التأكد من عمل جميع الاختبارات\n\n")
            
            f.write("### المرحلة 3: إعادة الهيكلة (يوم 4-5)\n")
            f.write(f"1. تقسيم {len(recs['refactoring_needed'])} ملف كبير\n")
            f.write(f"2. إصلاح {len(issues['security_risks'])} مشكلة أمنية\n")
            f.write("3. تحسين التوثيق والتعليقات\n\n")
            
            # النتيجة المتوقعة
            f.write("## 🎯 النتيجة المتوقعة بعد التنظيف\n\n")
            
            # حساب التحسينات
            files_after = summary['total_files'] - len(recs['immediate_deletions'])
            size_saved = sum(f['size_bytes'] for f in self.results['detailed_analysis'] 
                           if f['relative_path'] in [d['file'] for d in recs['immediate_deletions']]) / (1024 * 1024)
            
            f.write(f"- **عدد الملفات**: {summary['total_files']} → {files_after} (⬇️ {len(recs['immediate_deletions'])})\n")
            f.write(f"- **الحجم**: {summary['total_size_mb']:.2f} MB → {summary['total_size_mb'] - size_saved:.2f} MB (⬇️ {size_saved:.2f} MB)\n")
            f.write(f"- **صحة المشروع**: {health['overall']}% → ~90% (⬆️ {90 - health['overall']:.0f}%)\n")
            f.write(f"- **هيكل أوضح وأسهل للصيانة**\n")
            f.write(f"- **أمان محسّن وأداء أفضل**\n")
    
    def _save_action_list(self, file_path: Path) -> None:
        """حفظ قائمة إجراءات سريعة"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("قائمة الإجراءات السريعة - مشروع AI Teddy Bear\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("1. ملفات للحذف الفوري:\n")
            f.write("-" * 30 + "\n")
            
            for deletion in self.results["recommendations"]["immediate_deletions"]:
                f.write(f'DEL "{deletion["file"]}"\n')
            
            f.write("\n2. ملفات للنقل:\n")
            f.write("-" * 30 + "\n")
            
            for move in self.results["recommendations"]["suggested_moves"]:
                f.write(f'MOVE "{move["from"]}" -> "{move["to"]}"\n')
            
            f.write("\n3. ملفات للدمج:\n")
            f.write("-" * 30 + "\n")
            
            for merge in self.results["recommendations"]["merge_candidates"]:
                f.write(f'MERGE: {", ".join(merge["files"])}\n')


def main():
    """تشغيل المحلل الشامل"""
    print("\n🚀 بدء تحليل التنظيف الشامل...")
    
    # إنشاء المحلل
    analyzer = ComprehensiveCleanupAnalyzer()
    
    # تشغيل التحليل
    results = analyzer.analyze_project()
    
    # حفظ التقارير
    analyzer.save_reports()
    
    print("\n✅ اكتمل التحليل بنجاح!")
    print("📋 تحقق من مجلد cleanup_reports للتقارير المفصلة")


if __name__ == "__main__":
    main() 