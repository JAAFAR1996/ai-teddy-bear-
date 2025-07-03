#!/usr/bin/env python3
"""
🔍 Comprehensive Project Audit Script
فحص شامل للمشروع واكتشاف جميع المشاكل والثغرات

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
class AuditIssue:
    """مشكلة تم اكتشافها في المشروع"""
    severity: str  # critical, high, medium, low
    category: str  # security, quality, performance, architecture
    file_path: str
    line_number: Optional[int]
    description: str
    code_snippet: Optional[str]
    suggested_fix: Optional[str]
    rule_violated: Optional[str]

@dataclass
class FileAnalysis:
    """تحليل ملف واحد"""
    file_path: Path
    lines_count: int
    complexity_score: int
    issues: List[AuditIssue] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)

@dataclass
class ProjectAudit:
    """نتائج الفحص الشامل للمشروع"""
    total_files: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    file_analyses: Dict[str, FileAnalysis]
    issues_by_category: Dict[str, List[AuditIssue]]
    issues_by_severity: Dict[str, List[AuditIssue]]
    god_classes: List[str]
    circular_dependencies: List[Tuple[str, str]]
    security_risks: List[AuditIssue]
    performance_issues: List[AuditIssue]
    architecture_issues: List[AuditIssue]
    code_quality_issues: List[AuditIssue]

class ComprehensiveProjectAuditor:
    """محلل شامل للمشروع"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.audit_results = ProjectAudit(
            total_files=0,
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            file_analyses={},
            issues_by_category=defaultdict(list),
            issues_by_severity=defaultdict(list),
            god_classes=[],
            circular_dependencies=[],
            security_risks=[],
            performance_issues=[],
            architecture_issues=[],
            code_quality_issues=[]
        )
        
        # أنماط البحث عن المشاكل
        self.patterns = {
            'security': {
                'hardcoded_secrets': [
                    r'(password|secret|key|token|api_key)\s*=\s*["\'][^"\']+["\']',
                    r'os\.getenv\(["\'](password|secret|key|token|api_key)["\']\)',
                ],
                'dangerous_functions': [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'pickle\.loads\s*\(',
                    r'subprocess\.call.*shell\s*=\s*True',
                ],
                'sql_injection': [
                    r'execute\s*\(\s*f["\'][^"\']*\{[^}]*\}',
                    r'execute\s*\(\s*["\'][^"\']*\+',
                ]
            },
            'quality': {
                'broad_exceptions': [
                    r'except\s*:',
                    r'except\s+Exception\s*:',
                ],
                'print_statements': [
                    r'print\s*\(',
                ],
                'todos': [
                    r'#\s*(TODO|FIXME|XXX|HACK)',
                ],
                'wildcard_imports': [
                    r'from\s+[\w.]+\s+import\s+\*',
                ]
            },
            'performance': {
                'large_files': 500,  # أكثر من 500 سطر
                'complex_functions': 10,  # تعقيد دوري أكبر من 10
                'deep_nesting': 5,  # تداخل أعمق من 5 مستويات
            }
        }

    def run_comprehensive_audit(self) -> ProjectAudit:
        """تشغيل الفحص الشامل"""
        logger.info("🔍 بدء الفحص الشامل للمشروع...")
        logger.info(f"📁 المشروع: {self.project_root}")
        
        # العثور على جميع ملفات Python
        python_files = self._find_python_files()
        self.audit_results.total_files = len(python_files)
        logger.info(f"📊 تم العثور على {len(python_files)} ملف Python")
        
        # تحليل كل ملف
        for file_path in python_files:
            try:
                analysis = self._analyze_file(file_path)
                self.audit_results.file_analyses[str(file_path)] = analysis
                
                # تجميع المشاكل
                for issue in analysis.issues:
                    self._categorize_issue(issue)
                    
            except Exception as e:
                logger.error(f"❌ خطأ في تحليل {file_path}: {e}")
        
        # كشف God Classes
        self._detect_god_classes()
        
        # كشف التبعيات الدائرية
        self._detect_circular_dependencies()
        
        # حساب الإحصائيات
        self._calculate_statistics()
        
        # طباعة التقرير
        self._print_audit_report()
        
        return self.audit_results

    def _find_python_files(self) -> List[Path]:
        """العثور على جميع ملفات Python في المشروع"""
        python_files = []
        exclude_patterns = [
            '__pycache__', '.git', 'venv', '.venv', 'env', '.env',
            'node_modules', 'build', 'dist', '.pytest_cache'
        ]
        
        for file_path in self.project_root.rglob('*.py'):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                python_files.append(file_path)
        
        return python_files

    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """تحليل ملف واحد"""
        logger.debug(f"🔍 تحليل {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            logger.warning(f"⚠️ لا يمكن قراءة {file_path}: {e}")
            return FileAnalysis(
                file_path=file_path,
                lines_count=0,
                complexity_score=0
            )
        
        analysis = FileAnalysis(
            file_path=file_path,
            lines_count=len(lines),
            complexity_score=0
        )
        
        # تحليل AST
        try:
            tree = ast.parse(content)
            ast_analyzer = ASTAnalyzer()
            ast_analyzer.visit(tree)
            
            analysis.complexity_score = ast_analyzer.complexity_score
            analysis.classes = ast_analyzer.classes
            analysis.functions = ast_analyzer.functions
            analysis.imports = ast_analyzer.imports
            analysis.dependencies = ast_analyzer.dependencies
            
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تحليل AST لـ {file_path}: {e}")
        
        # فحص المشاكل الأمنية
        analysis.issues.extend(self._check_security_issues(file_path, content, lines))
        
        # فحص مشاكل الجودة
        analysis.issues.extend(self._check_quality_issues(file_path, content, lines))
        
        # فحص مشاكل الأداء
        analysis.issues.extend(self._check_performance_issues(file_path, content, lines, analysis))
        
        # فحص مشاكل الهندسة المعمارية
        analysis.issues.extend(self._check_architecture_issues(file_path, content, lines, analysis))
        
        return analysis

    def _check_security_issues(self, file_path: Path, content: str, lines: List[str]) -> List[AuditIssue]:
        """فحص المشاكل الأمنية"""
        issues = []
        
        for pattern_name, patterns in self.patterns['security'].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_number = content[:match.start()].count('\n') + 1
                    line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                    
                    issue = AuditIssue(
                        severity="critical" if pattern_name == "dangerous_functions" else "high",
                        category="security",
                        file_path=str(file_path),
                        line_number=line_number,
                        description=f"مشكلة أمنية: {pattern_name}",
                        code_snippet=line_content.strip(),
                        suggested_fix=self._get_security_fix(pattern_name, match.group()),
                        rule_violated=f"SECURITY_{pattern_name.upper()}"
                    )
                    issues.append(issue)
        
        return issues

    def _check_quality_issues(self, file_path: Path, content: str, lines: List[str]) -> List[AuditIssue]:
        """فحص مشاكل الجودة"""
        issues = []
        
        for pattern_name, patterns in self.patterns['quality'].items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_number = content[:match.start()].count('\n') + 1
                    line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                    
                    severity = "high" if pattern_name == "broad_exceptions" else "medium"
                    
                    issue = AuditIssue(
                        severity=severity,
                        category="quality",
                        file_path=str(file_path),
                        line_number=line_number,
                        description=f"مشكلة جودة: {pattern_name}",
                        code_snippet=line_content.strip(),
                        suggested_fix=self._get_quality_fix(pattern_name, match.group()),
                        rule_violated=f"QUALITY_{pattern_name.upper()}"
                    )
                    issues.append(issue)
        
        return issues

    def _check_performance_issues(self, file_path: Path, content: str, lines: List[str], analysis: FileAnalysis) -> List[AuditIssue]:
        """فحص مشاكل الأداء"""
        issues = []
        
        # ملف كبير جداً
        if analysis.lines_count > self.patterns['performance']['large_files']:
            issues.append(AuditIssue(
                severity="medium",
                category="performance",
                file_path=str(file_path),
                line_number=None,
                description=f"ملف كبير جداً: {analysis.lines_count} سطر",
                code_snippet=None,
                suggested_fix="قسّم الملف إلى ملفات أصغر أو استخدم EXTRACT CLASS pattern",
                rule_violated="PERFORMANCE_LARGE_FILE"
            ))
        
        # تعقيد دوري عالي
        if analysis.complexity_score > self.patterns['performance']['complex_functions']:
            issues.append(AuditIssue(
                severity="medium",
                category="performance",
                file_path=str(file_path),
                line_number=None,
                description=f"تعقيد دوري عالي: {analysis.complexity_score}",
                code_snippet=None,
                suggested_fix="استخدم EXTRACT FUNCTION pattern لتقليل التعقيد",
                rule_violated="PERFORMANCE_HIGH_COMPLEXITY"
            ))
        
        return issues

    def _check_architecture_issues(self, file_path: Path, content: str, lines: List[str], analysis: FileAnalysis) -> List[AuditIssue]:
        """فحص مشاكل الهندسة المعمارية"""
        issues = []
        
        # God Class detection
        if (analysis.lines_count > 300 and 
            len(analysis.classes) > 3 and 
            analysis.complexity_score > 15):
            issues.append(AuditIssue(
                severity="high",
                category="architecture",
                file_path=str(file_path),
                line_number=None,
                description="God Class محتمل",
                code_snippet=None,
                suggested_fix="قسّم الكلاس إلى كلاسات أصغر باستخدام DDD patterns",
                rule_violated="ARCHITECTURE_GOD_CLASS"
            ))
        
        # الكثير من الاستيرادات
        if len(analysis.imports) > 20:
            issues.append(AuditIssue(
                severity="medium",
                category="architecture",
                file_path=str(file_path),
                line_number=None,
                description=f"كثير من الاستيرادات: {len(analysis.imports)}",
                code_snippet=None,
                suggested_fix="قلّل من الاستيرادات أو استخدم facade pattern",
                rule_violated="ARCHITECTURE_TOO_MANY_IMPORTS"
            ))
        
        return issues

    def _detect_god_classes(self):
        """كشف God Classes"""
        for file_path, analysis in self.audit_results.file_analyses.items():
            if (analysis.lines_count > 500 or 
                (analysis.lines_count > 300 and len(analysis.classes) > 5) or
                analysis.complexity_score > 20):
                self.audit_results.god_classes.append(file_path)

    def _detect_circular_dependencies(self):
        """كشف التبعيات الدائرية"""
        # بناء خريطة التبعيات
        dependency_graph = {}
        for file_path, analysis in self.audit_results.file_analyses.items():
            dependency_graph[file_path] = analysis.dependencies
        
        # كشف الدورات
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if len(cycle) == 2:  # أبسط دورة
                    self.audit_results.circular_dependencies.append((cycle[0], cycle[1]))
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])

    def _categorize_issue(self, issue: AuditIssue):
        """تصنيف المشكلة"""
        self.audit_results.issues_by_category[issue.category].append(issue)
        self.audit_results.issues_by_severity[issue.severity].append(issue)
        
        if issue.category == "security":
            self.audit_results.security_risks.append(issue)
        elif issue.category == "performance":
            self.audit_results.performance_issues.append(issue)
        elif issue.category == "architecture":
            self.audit_results.architecture_issues.append(issue)
        else:
            self.audit_results.code_quality_issues.append(issue)

    def _calculate_statistics(self):
        """حساب الإحصائيات"""
        self.audit_results.critical_issues = len(self.audit_results.issues_by_severity.get("critical", []))
        self.audit_results.high_issues = len(self.audit_results.issues_by_severity.get("high", []))
        self.audit_results.medium_issues = len(self.audit_results.issues_by_severity.get("medium", []))
        self.audit_results.low_issues = len(self.audit_results.issues_by_severity.get("low", []))
        self.audit_results.total_issues = (
            self.audit_results.critical_issues +
            self.audit_results.high_issues +
            self.audit_results.medium_issues +
            self.audit_results.low_issues
        )

    def _get_security_fix(self, pattern_name: str, matched_code: str) -> str:
        """الحصول على إصلاح أمني"""
        fixes = {
            'hardcoded_secrets': "استخدم secrets manager أو environment variables",
            'dangerous_functions': "استخدم safe_expression_parser أو ast.literal_eval",
            'sql_injection': "استخدم parameterized queries"
        }
        return fixes.get(pattern_name, "راجع الكود يدوياً")

    def _get_quality_fix(self, pattern_name: str, matched_code: str) -> str:
        """الحصول على إصلاح جودة"""
        fixes = {
            'broad_exceptions': "استخدم استثناءات محددة",
            'print_statements': "استخدم logging بدلاً من print",
            'todos': "أكمل التنفيذ أو أنشئ ticket",
            'wildcard_imports': "استخدم استيرادات محددة"
        }
        return fixes.get(pattern_name, "راجع الكود يدوياً")

    def _print_audit_report(self):
        """طباعة تقرير الفحص"""
        logger.info("\n" + "="*80)
        logger.info("🔍 تقرير الفحص الشامل للمشروع")
        logger.info("="*80)
        
        logger.info(f"📊 إحصائيات عامة:")
        logger.info(f"   📁 إجمالي الملفات: {self.audit_results.total_files}")
        logger.info(f"   ⚠️ إجمالي المشاكل: {self.audit_results.total_issues}")
        logger.info(f"   🚨 مشاكل حرجة: {self.audit_results.critical_issues}")
        logger.info(f"   🔴 مشاكل عالية: {self.audit_results.high_issues}")
        logger.info(f"   🟡 مشاكل متوسطة: {self.audit_results.medium_issues}")
        logger.info(f"   🟢 مشاكل منخفضة: {self.audit_results.low_issues}")
        
        logger.info(f"\n🏗️ مشاكل الهندسة المعمارية:")
        logger.info(f"   🏛️ God Classes: {len(self.audit_results.god_classes)}")
        logger.info(f"   🔄 تبعيات دائرية: {len(self.audit_results.circular_dependencies)}")
        
        logger.info(f"\n🔐 مشاكل الأمان:")
        logger.info(f"   🚨 مخاطر أمنية: {len(self.audit_results.security_risks)}")
        
        logger.info(f"\n⚡ مشاكل الأداء:")
        logger.info(f"   🐌 مشاكل أداء: {len(self.audit_results.performance_issues)}")
        
        logger.info(f"\n📝 مشاكل جودة الكود:")
        logger.info(f"   ✏️ مشاكل جودة: {len(self.audit_results.code_quality_issues)}")
        
        # طباعة المشاكل الحرجة
        if self.audit_results.critical_issues > 0:
            logger.info(f"\n🚨 المشاكل الحرجة:")
            for issue in self.audit_results.issues_by_severity.get("critical", [])[:5]:
                logger.info(f"   📄 {issue.file_path}:{issue.line_number} - {issue.description}")
        
        # طباعة God Classes
        if self.audit_results.god_classes:
            logger.info(f"\n🏛️ God Classes المكتشفة:")
            for god_class in self.audit_results.god_classes[:5]:
                logger.info(f"   📄 {god_class}")
        
        # طباعة التبعيات الدائرية
        if self.audit_results.circular_dependencies:
            logger.info(f"\n🔄 التبعيات الدائرية:")
            for dep1, dep2 in self.audit_results.circular_dependencies[:5]:
                logger.info(f"   📄 {dep1} ↔ {dep2}")

    def save_audit_report(self, output_file: str = "audit_report.json"):
        """حفظ تقرير الفحص إلى ملف"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "statistics": {
                "total_files": self.audit_results.total_files,
                "total_issues": self.audit_results.total_issues,
                "critical_issues": self.audit_results.critical_issues,
                "high_issues": self.audit_results.high_issues,
                "medium_issues": self.audit_results.medium_issues,
                "low_issues": self.audit_results.low_issues,
            },
            "god_classes": self.audit_results.god_classes,
            "circular_dependencies": [
                {"file1": dep1, "file2": dep2} 
                for dep1, dep2 in self.audit_results.circular_dependencies
            ],
            "issues_by_category": {
                category: [
                    {
                        "severity": issue.severity,
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "description": issue.description,
                        "suggested_fix": issue.suggested_fix,
                        "rule_violated": issue.rule_violated
                    }
                    for issue in issues
                ]
                for category, issues in self.audit_results.issues_by_category.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 تم حفظ التقرير في: {output_file}")


class ASTAnalyzer(ast.NodeVisitor):
    """محلل AST للكشف عن التعقيد والتبعيات"""
    
    def __init__(self):
        self.complexity_score = 0
        self.classes = []
        self.functions = []
        self.imports = set()
        self.dependencies = set()
    
    def visit_ClassDef(self, node):
        self.complexity_score += 2
        self.classes.append(node.name)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.complexity_score += 1
        self.functions.append(node.name)
        
        # حساب تعقيد الدالة
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
            self.dependencies.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
            self.dependencies.add(node.module)
        self.generic_visit(node)


def main():
    """الدالة الرئيسية"""
    logger.info("🔍 بدء الفحص الشامل لمشروع AI Teddy Bear")
    logger.info("Lead Architect: جعفر أديب (Jaafar Adeeb)")
    logger.info("="*60)
    
    auditor = ComprehensiveProjectAuditor()
    audit_results = auditor.run_comprehensive_audit()
    
    # حفظ التقرير
    auditor.save_audit_report()
    
    # تقييم عام
    if audit_results.critical_issues > 0:
        logger.error("❌ المشروع يحتوي على مشاكل حرجة تحتاج معالجة فورية!")
        sys.exit(1)
    elif audit_results.high_issues > 10:
        logger.warning("⚠️ المشروع يحتوي على مشاكل عالية تحتاج معالجة قريبة!")
    else:
        logger.info("✅ المشروع في حالة جيدة!")


if __name__ == "__main__":
    main() 