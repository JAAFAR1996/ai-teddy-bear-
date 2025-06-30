#!/usr/bin/env python3
"""
🏗️ Quick God Class Splitter - DDD Implementation
تقسيم سريع للملفات الكبيرة باستخدام DDD patterns
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class QuickGodClassSplitter:
    """أداة سريعة لتقسيم God Classes"""
    
    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.report = {}
        
    def identify_god_classes(self) -> List[Tuple[Path, int]]:
        """تحديد God Classes (الملفات الكبيرة)"""
        god_classes = []
        services_path = self.src_path / "application" / "services"
        
        if not services_path.exists():
            print(f"⚠️ Services path not found: {services_path}")
            return god_classes
            
        for py_file in services_path.rglob("*.py"):
            if py_file.is_file() and py_file.name != "__init__.py":
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = len(content.splitlines())
                    
                    # God Class = أكثر من 500 سطر
                    if lines > 500:
                        god_classes.append((py_file, lines))
                        print(f"🚨 God Class detected: {py_file.name} ({lines} lines)")
                        
                except Exception as e:
                    print(f"❌ Error reading {py_file}: {e}")
                    
        return god_classes
    
    def split_god_class(self, file_path: Path, lines: int) -> Dict[str, str]:
        """تقسيم God Class إلى ملفات منفصلة"""
        print(f"\n🔧 Splitting {file_path.name}...")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # استخراج المكونات الأساسية
            components = self._extract_components(content)
            
            # تحديد اسم الدومين
            domain_name = self._get_domain_name(file_path.name)
            
            # إنشاء البنية الجديدة
            new_structure = self._create_ddd_structure(components, domain_name, file_path.parent)
            
            # تحديث التقرير
            self.report[file_path.name] = {
                'original_lines': lines,
                'new_files': len(new_structure),
                'domain': domain_name,
                'created_files': list(new_structure.keys())
            }
            
            print(f"✅ Split {file_path.name} into {len(new_structure)} files")
            return new_structure
            
        except Exception as e:
            print(f"❌ Error splitting {file_path.name}: {e}")
            return {}
    
    def _extract_components(self, content: str) -> Dict[str, List[str]]:
        """استخراج المكونات من الكود"""
        components = {
            'imports': [],
            'classes': [],
            'functions': [],
            'dataclasses': [],
            'constants': []
        }
        
        lines = content.splitlines()
        current_block = []
        current_type = None
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # تجاهل الأسطر الفارغة والتعليقات
            if not stripped or stripped.startswith('#'):
                if current_block:
                    current_block.append(line)
                continue
            
            # Imports
            if stripped.startswith(('import ', 'from ')):
                components['imports'].append(line)
                continue
            
            # Constants (متغيرات بحروف كبيرة)
            if re.match(r'^[A-Z_][A-Z0-9_]*\s*=', stripped):
                components['constants'].append(line)
                continue
            
            # Classes
            if stripped.startswith('class '):
                if current_block and current_type:
                    components[current_type].append('\n'.join(current_block))
                current_block = [line]
                current_type = 'dataclasses' if '@dataclass' in content else 'classes'
                indent_level = len(line) - len(line.lstrip())
                continue
            
            # Functions
            if stripped.startswith('def ') and current_type != 'classes':
                if current_block and current_type:
                    components[current_type].append('\n'.join(current_block))
                current_block = [line]
                current_type = 'functions'
                indent_level = len(line) - len(line.lstrip())
                continue
            
            # إضافة السطر للبلوك الحالي
            if current_block:
                current_block.append(line)
                
                # تحديد نهاية البلوك
                line_indent = len(line) - len(line.lstrip())
                if stripped and line_indent <= indent_level and current_type:
                    # انتهى البلوك
                    if len(current_block) > 1:  # تجاهل البلوكات الفارغة
                        current_block.pop()  # إزالة السطر الأخير
                        components[current_type].append('\n'.join(current_block))
                    current_block = [line]
                    current_type = None
        
        # إضافة البلوك الأخير
        if current_block and current_type:
            components[current_type].append('\n'.join(current_block))
        
        return components
    
    def _get_domain_name(self, filename: str) -> str:
        """استخراج اسم الدومين من اسم الملف"""
        name = filename.replace('.py', '').replace('_service', '')
        
        domain_mapping = {
            'data_cleanup_service': 'cleanup',
            'parent_dashboard_service': 'dashboard', 
            'parent_report_service': 'reporting',
            'memory_service': 'memory',
            'moderation_service': 'moderation',
            'enhanced_hume_integration': 'emotion'
        }
        
        return domain_mapping.get(name, name.replace('_', ''))
    
    def _create_ddd_structure(self, components: Dict, domain_name: str, base_path: Path) -> Dict[str, str]:
        """إنشاء بنية DDD"""
        new_files = {}
        
        # إنشاء مجلد الدومين
        domain_path = base_path / f"{domain_name}_ddd"
        
        # إنشاء البنية
        structure = {
            'domain/aggregates': components.get('classes', [])[:2],  # أول 2 كلاسات كـ aggregates
            'domain/entities': components.get('classes', [])[2:4],   # التالية كـ entities
            'domain/value_objects': components.get('dataclasses', []),
            'application/use_cases': [f for f in components.get('functions', []) if 'execute' in f or 'process' in f][:3],
            'application/services': [f for f in components.get('functions', []) if 'validate' in f or 'calculate' in f][:3],
            'infrastructure/persistence': ['# Repository implementations'],
        }
        
        # إنشاء الملفات
        for path_key, items in structure.items():
            if not items:
                continue
                
            # إنشاء المجلد
            full_path = domain_path / path_key
            full_path.mkdir(parents=True, exist_ok=True)
            
            # إنشاء __init__.py
            init_file = full_path / "__init__.py"
            init_file.write_text("# Auto-generated DDD structure\n", encoding='utf-8')
            
            # إنشاء ملف للمكونات
            file_name = f"{path_key.split('/')[-1]}.py"
            file_path = full_path / file_name
            
            file_content = self._create_file_content(items, components.get('imports', []), domain_name)
            file_path.write_text(file_content, encoding='utf-8')
            
            new_files[f"{path_key}/{file_name}"] = file_content
        
        # إنشاء Orchestrator
        orchestrator_content = self._create_orchestrator(domain_name)
        orchestrator_path = domain_path / "application" / "services" / f"{domain_name}_orchestrator.py"
        orchestrator_path.write_text(orchestrator_content, encoding='utf-8')
        new_files[f"application/services/{domain_name}_orchestrator.py"] = orchestrator_content
        
        return new_files
    
    def _create_file_content(self, items: List[str], imports: List[str], domain_name: str) -> str:
        """إنشاء محتوى الملف"""
        content = f"""#!/usr/bin/env python3
\"\"\"
🏗️ {domain_name.title()} Domain - DDD Implementation
Auto-generated from God Class refactoring
\"\"\"

"""
        
        # إضافة imports أساسية
        basic_imports = [
            "from typing import List, Dict, Any, Optional",
            "from dataclasses import dataclass",
            "from datetime import datetime",
            "import uuid"
        ]
        
        content += '\n'.join(basic_imports) + '\n\n'
        
        # إضافة imports من الملف الأصلي (أول 5 فقط)
        if imports:
            content += "# Original imports\n"
            for imp in imports[:5]:
                content += imp + '\n'
            content += '\n'
        
        # إضافة المكونات
        for item in items:
            if isinstance(item, str) and item.strip():
                content += item + '\n\n'
        
        return content
    
    def _create_orchestrator(self, domain_name: str) -> str:
        """إنشاء Orchestrator للدومين"""
        return f'''#!/usr/bin/env python3
"""
🎭 {domain_name.title()} Orchestrator - DDD Implementation
Orchestrator pattern for coordinating {domain_name} operations
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio

class {domain_name.title()}Context:
    """Context للعملية"""
    def __init__(self, operation_id: str, parameters: Dict[str, Any]):
        self.operation_id = operation_id
        self.parameters = parameters
        self.results = {{}}
        self.errors = []
        self.start_time = datetime.utcnow()

class {domain_name.title()}Orchestrator:
    """
    🎭 Orchestrator for {domain_name} domain
    
    Coordinates complex operations across aggregates
    """
    
    def __init__(self):
        self.strategies = {{}}
        
    async def execute_operation(self, operation_type: str, parameters: Dict[str, Any]):
        """تنفيذ عملية معقدة"""
        context = {domain_name.title()}Context(
            operation_id=f"{{operation_type}}_{{datetime.utcnow().timestamp()}}",
            parameters=parameters
        )
        
        print(f"🚀 Starting {{operation_type}} operation")
        
        try:
            # Pre-validation
            await self._validate_conditions(context)
            
            # Execute steps
            results = await self._execute_steps(context, operation_type)
            
            # Finalize
            await self._finalize_operation(context, results)
            
            duration = (datetime.utcnow() - context.start_time).total_seconds()
            print(f"✅ Operation completed in {{duration:.2f}}s")
            
            return {{
                'success': True,
                'operation_id': context.operation_id,
                'results': context.results,
                'duration': duration
            }}
            
        except Exception as e:
            print(f"❌ Operation failed: {{e}}")
            context.errors.append(str(e))
            raise
    
    async def _validate_conditions(self, context: {domain_name.title()}Context):
        """التحقق من شروط العملية"""
        # Add validation logic here
        pass
    
    async def _execute_steps(self, context: {domain_name.title()}Context, operation_type: str):
        """تنفيذ خطوات العملية"""
        steps = [
            self._step_1_prepare,
            self._step_2_process,
            self._step_3_finalize
        ]
        
        results = []
        for step in steps:
            try:
                result = await step(context)
                results.append(result)
                context.results[step.__name__] = result
            except Exception as e:
                print(f"❌ Step {{step.__name__}} failed: {{e}}")
                # Implement rollback logic here
                raise
        
        return results
    
    async def _finalize_operation(self, context: {domain_name.title()}Context, results):
        """إنهاء العملية"""
        # Add finalization logic here
        pass
    
    async def _step_1_prepare(self, context: {domain_name.title()}Context):
        """خطوة التحضير"""
        print(f"🔧 Preparing operation {{context.operation_id}}")
        await asyncio.sleep(0.1)  # Simulate work
        return "prepared"
    
    async def _step_2_process(self, context: {domain_name.title()}Context):
        """خطوة المعالجة"""
        print(f"⚙️ Processing operation {{context.operation_id}}")
        await asyncio.sleep(0.1)  # Simulate work
        return "processed"
    
    async def _step_3_finalize(self, context: {domain_name.title()}Context):
        """خطوة الإنهاء"""
        print(f"🎯 Finalizing operation {{context.operation_id}}")
        await asyncio.sleep(0.1)  # Simulate work
        return "finalized"

# Example usage
async def main():
    orchestrator = {domain_name.title()}Orchestrator()
    
    result = await orchestrator.execute_operation(
        "test_operation",
        {{"param1": "value1", "param2": "value2"}}
    )
    
    print(f"Operation result: {{result}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def run_splitting(self):
        """تشغيل عملية التقسيم الكاملة"""
        print("🚀 Starting God Class splitting...")
        print("=" * 50)
        
        god_classes = self.identify_god_classes()
        
        if not god_classes:
            print("✅ No God Classes found!")
            return
        
        print(f"\n📊 Found {len(god_classes)} God Classes to split:")
        
        total_files_created = 0
        for file_path, lines in god_classes:
            new_structure = self.split_god_class(file_path, lines)
            total_files_created += len(new_structure)
        
        # طباعة التقرير النهائي
        print("\n" + "=" * 50)
        print("📋 SPLITTING REPORT")
        print("=" * 50)
        
        for filename, report in self.report.items():
            print(f"\n📁 {filename}:")
            print(f"  📏 Original: {report['original_lines']} lines")
            print(f"  🏗️ Domain: {report['domain']}")
            print(f"  📦 New files: {report['new_files']}")
            print(f"  📄 Created files:")
            for created_file in report['created_files']:
                print(f"    - {created_file}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"  God Classes split: {len(self.report)}")
        print(f"  Total new files: {total_files_created}")
        print(f"  Average reduction: {(sum(r['original_lines'] for r in self.report.values()) / len(self.report) / (total_files_created / len(self.report)) if self.report else 0):.0f} lines per file")
        
        print("\n✅ God Class splitting completed!")

if __name__ == "__main__":
    splitter = QuickGodClassSplitter()
    splitter.run_splitting() 