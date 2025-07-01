#!/usr/bin/env python3
"""
🏗️ God Class Refactoring Tool - Domain-Driven Design Implementation
Advanced code restructuring using DDD patterns for AI Teddy Bear Project

Lead Architect: جعفر أديب (Jaafar Adeeb)
"""

import ast
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import structlog

logger = structlog.get_logger()


@dataclass
class RefactoringTarget:
    """هدف إعادة الهيكلة"""

    file_path: Path
    current_size: int
    complexity_score: int
    responsibility_domains: Set[str] = field(default_factory=set)
    extracted_components: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)


@dataclass
class DDDStructure:
    """هيكل DDD للملف المستهدف"""

    domain_name: str
    aggregates: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    value_objects: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)


class DDDRefactoringEngine:
    """محرك إعادة الهيكلة باستخدام DDD"""

    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.god_classes = []
        self.refactoring_report = {}

    def identify_god_classes(self) -> List[RefactoringTarget]:
        """تحديد God Classes المرشحة للإعادة هيكلة"""
        logger.info("🔍 تحديد God Classes...")

        god_classes = []
        services_path = self.src_path / "application" / "services"

        if not services_path.exists():
            logger.warning(f"Services path not found: {services_path}")
            return god_classes

        for py_file in services_path.rglob("*.py"):
            if py_file.is_file() and py_file.name != "__init__.py":
                target = self._analyze_file(py_file)
                if self._is_god_class(target):
                    god_classes.append(target)

        logger.info(f"📊 تم تحديد {len(god_classes)} God Class للإعادة هيكلة")
        return god_classes

    def _analyze_file(self, file_path: Path) -> RefactoringTarget:
        """تحليل ملف Python لتحديد التعقيد والمسؤوليات"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = len(content.splitlines())

            # تحليل الكود باستخدام AST
            tree = ast.parse(content)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)

            return RefactoringTarget(
                file_path=file_path,
                current_size=lines,
                complexity_score=analyzer.complexity_score,
                responsibility_domains=analyzer.domains,
                dependencies=analyzer.dependencies,
            )

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return RefactoringTarget(
                file_path=file_path, current_size=0, complexity_score=0
            )

    def _is_god_class(self, target: RefactoringTarget) -> bool:
        """تحديد ما إذا كان الملف God Class"""
        return (
            target.current_size > 500  # أكثر من 500 سطر
            or target.complexity_score > 15  # تعقيد عالي
            or len(target.responsibility_domains) > 3  # مسؤوليات متعددة
        )

    async def refactor_to_ddd(self, target: RefactoringTarget) -> DDDStructure:
        """إعادة هيكلة God Class إلى DDD structure"""
        logger.info(f"🏗️ إعادة هيكلة {target.file_path.name}...")

        # تحديد Domain name من اسم الملف
        domain_name = self._extract_domain_name(target.file_path.name)

        # إنشاء DDD structure
        ddd_structure = DDDStructure(domain_name=domain_name)

        # تحليل وتقسيم الكود
        content = target.file_path.read_text(encoding="utf-8")
        components = await self._extract_components(content, domain_name)

        # توزيع المكونات على DDD layers
        await self._distribute_to_ddd_layers(components, ddd_structure)

        # إنشاء الملفات الجديدة
        await self._create_ddd_structure(ddd_structure, target.file_path.parent)

        # إنشاء orchestrator pattern
        await self._create_orchestrator(ddd_structure, target.file_path.parent)

        self.refactoring_report[target.file_path.name] = {
            "original_size": target.current_size,
            "new_structure": ddd_structure,
            "created_files": len(
                ddd_structure.aggregates
                + ddd_structure.entities
                + ddd_structure.value_objects
                + ddd_structure.use_cases
            ),
        }

        return ddd_structure

    def _extract_domain_name(self, filename: str) -> str:
        """استخراج اسم Domain من اسم الملف"""
        name = filename.replace(".py", "").replace("_service", "")

        # تحويل إلى domain names معروفة
        domain_mapping = {
            "data_cleanup": "cleanup",
            "parent_dashboard": "dashboard",
            "parent_report": "reporting",
            "memory_service": "memory",
            "moderation": "moderation",
            "enhanced_hume_integration": "emotion",
        }

        return domain_mapping.get(name, name)

    async def _extract_components(
        self, content: str, domain_name: str
    ) -> Dict[str, List[str]]:
        """استخراج المكونات من الكود الأصلي"""
        components = {
            "classes": [],
            "functions": [],
            "dataclasses": [],
            "enums": [],
            "constants": [],
        }

        try:
            tree = ast.parse(content)
            extractor = ComponentExtractor()
            extractor.visit(tree)

            components["classes"] = extractor.classes
            components["functions"] = extractor.functions
            components["dataclasses"] = extractor.dataclasses
            components["enums"] = extractor.enums
            components["constants"] = extractor.constants

        except Exception as e:
            logger.error(f"Error extracting components: {e}")

        return components

    async def _distribute_to_ddd_layers(
        self, components: Dict, ddd_structure: DDDStructure
    ):
        """توزيع المكونات على طبقات DDD"""

        # Aggregates - الكيانات المعقدة
        for class_name, class_content in components.get("classes", []):
            if self._is_aggregate(class_name, class_content):
                ddd_structure.aggregates.append((class_name, class_content))

        # Entities - الكيانات البسيطة
        for class_name, class_content in components.get("classes", []):
            if self._is_entity(class_name, class_content):
                ddd_structure.entities.append((class_name, class_content))

        # Value Objects - القيم
        for dataclass_name, dataclass_content in components.get("dataclasses", []):
            ddd_structure.value_objects.append((dataclass_name, dataclass_content))

        # Use Cases - حالات الاستخدام
        for func_name, func_content in components.get("functions", []):
            if self._is_use_case(func_name, func_content):
                ddd_structure.use_cases.append((func_name, func_content))

        # Services - الخدمات
        for func_name, func_content in components.get("functions", []):
            if self._is_service_method(func_name, func_content):
                ddd_structure.services.append((func_name, func_content))

    def _is_aggregate(self, class_name: str, class_content: str) -> bool:
        """تحديد ما إذا كان الكلاس aggregate"""
        indicators = ["Policy", "Manager", "Orchestrator", "Controller"]
        return any(indicator in class_name for indicator in indicators)

    def _is_entity(self, class_name: str, class_content: str) -> bool:
        """تحديد ما إذا كان الكلاس entity"""
        indicators = ["Job", "Result", "Report", "Record", "Session"]
        return any(indicator in class_name for indicator in indicators)

    def _is_use_case(self, func_name: str, func_content: str) -> bool:
        """تحديد ما إذا كانت الدالة use case"""
        indicators = ["execute", "process", "handle", "run", "perform"]
        return any(indicator in func_name.lower() for indicator in indicators)

    def _is_service_method(self, func_name: str, func_content: str) -> bool:
        """تحديد ما إذا كانت الدالة service method"""
        indicators = ["validate", "calculate", "transform", "convert", "format"]
        return any(indicator in func_name.lower() for indicator in indicators)

    async def _create_ddd_structure(self, ddd_structure: DDDStructure, base_path: Path):
        """إنشاء هيكل DDD الفعلي"""
        domain_path = base_path / ddd_structure.domain_name

        # إنشاء الديريكتوريز
        paths = {
            "domain": domain_path / "domain",
            "aggregates": domain_path / "domain" / "aggregates",
            "entities": domain_path / "domain" / "entities",
            "value_objects": domain_path / "domain" / "value_objects",
            "repositories": domain_path / "domain" / "repositories",
            "application": domain_path / "application",
            "use_cases": domain_path / "application" / "use_cases",
            "services": domain_path / "application" / "services",
            "dto": domain_path / "application" / "dto",
            "infrastructure": domain_path / "infrastructure",
            "persistence": domain_path / "infrastructure" / "persistence",
        }

        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
            (path / "__init__.py").touch()

        # إنشاء ملفات Aggregates
        for aggregate_name, aggregate_content in ddd_structure.aggregates:
            await self._create_aggregate_file(
                paths["aggregates"],
                aggregate_name,
                aggregate_content,
                ddd_structure.domain_name,
            )

        # إنشاء ملفات Entities
        for entity_name, entity_content in ddd_structure.entities:
            await self._create_entity_file(
                paths["entities"],
                entity_name,
                entity_content,
                ddd_structure.domain_name,
            )

        # إنشاء ملفات Value Objects
        for vo_name, vo_content in ddd_structure.value_objects:
            await self._create_value_object_file(
                paths["value_objects"], vo_name, vo_content, ddd_structure.domain_name
            )

        # إنشاء ملفات Use Cases
        for uc_name, uc_content in ddd_structure.use_cases:
            await self._create_use_case_file(
                paths["use_cases"], uc_name, uc_content, ddd_structure.domain_name
            )

    async def _create_orchestrator(self, ddd_structure: DDDStructure, base_path: Path):
        """إنشاء Orchestrator pattern للتنسيق بين المكونات"""
        orchestrator_path = (
            base_path / ddd_structure.domain_name / "application" / "services"
        )

        orchestrator_content = f'''#!/usr/bin/env python3
"""
🎭 {ddd_structure.domain_name.title()} Orchestrator - DDD Implementation
Orchestrator pattern for coordinating complex {ddd_structure.domain_name} operations
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import structlog
from dependency_injector.wiring import inject, Provide

from ..domain.aggregates import *
from ..domain.entities import *
from ..domain.repositories import {ddd_structure.domain_name.title()}Repository
from ...infrastructure.messaging import EventBus
from ...infrastructure.monitoring import MetricsCollector

logger = structlog.get_logger()

@dataclass
class {ddd_structure.domain_name.title()}Context:
    """Context object للحفاظ على state أثناء العملية"""
    operation_id: str
    start_time: datetime
    parameters: Dict[str, Any]
    results: Dict[str, Any] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = {{}}
        if self.errors is None:
            self.errors = []

class {ddd_structure.domain_name.title()}Orchestrator:
    """
    🎭 Orchestrator pattern for {ddd_structure.domain_name} domain
    
    Responsibilities:
    - Coordinate complex business operations
    - Manage transaction boundaries
    - Handle cross-aggregate operations
    - Implement saga patterns for distributed operations
    """
    
    @inject
    def __init__(
        self,
        repository: {ddd_structure.domain_name.title()}Repository = Provide["{ddd_structure.domain_name}_repository"],
        event_bus: EventBus = Provide["event_bus"],
        metrics: MetricsCollector = Provide["metrics_collector"]
    ):
        self.repository = repository
        self.event_bus = event_bus
        self.metrics = metrics
        self._strategies = {{}}
        self._compensation_actions = []
        
    def register_strategy(self, operation_type: str, strategy: 'OperationStrategy'):
        """تسجيل استراتيجيات العمليات المختلفة"""
        self._strategies[operation_type] = strategy
        logger.info("Strategy registered", operation_type=operation_type)
        
    async def execute_operation(
        self, 
        operation_type: str, 
        parameters: Dict[str, Any]
    ) -> '{ddd_structure.domain_name.title()}Result':
        """
        تنفيذ عملية معقدة مع Saga pattern
        
        Args:
            operation_type: نوع العملية
            parameters: معاملات العملية
            
        Returns:
            نتيجة العملية
        """
        context = {ddd_structure.domain_name.title()}Context(
            operation_id=f"{{operation_type}}_{{datetime.utcnow().timestamp()}}",
            start_time=datetime.utcnow(),
            parameters=parameters
        )
        
        logger.info("Operation started", 
                   operation_id=context.operation_id,
                   operation_type=operation_type)
        
        try:
            # Pre-operation validation
            await self._validate_operation_conditions(context, operation_type)
            
            # Execute operation with compensation tracking
            async with self._create_operation_saga(context) as saga:
                results = await self._execute_operation_steps(context, operation_type, saga)
                
            # Post-operation actions
            await self._finalize_operation(context, results)
            
            duration = (datetime.utcnow() - context.start_time).total_seconds()
            
            logger.info("Operation completed successfully",
                       operation_id=context.operation_id,
                       duration_seconds=duration)
            
            return {ddd_structure.domain_name.title()}Result(
                success=True,
                operation_id=context.operation_id,
                results=context.results,
                duration_seconds=duration
            )
            
        except Exception as e:
            await self._handle_operation_failure(context, e)
            raise {ddd_structure.domain_name.title()}OperationError(
                f"Operation {{operation_type}} failed: {{str(e)}}"
            ) from e
    
    async def _validate_operation_conditions(
        self, 
        context: {ddd_structure.domain_name.title()}Context, 
        operation_type: str
    ):
        """التحقق من شروط العملية قبل التنفيذ"""
        if operation_type not in self._strategies:
            raise ValueError(f"Unknown operation type: {{operation_type}}")
            
        strategy = self._strategies[operation_type]
        await strategy.validate_preconditions(context.parameters)
        
        logger.debug("Operation conditions validated",
                    operation_id=context.operation_id)
    
    async def _execute_operation_steps(
        self,
        context: {ddd_structure.domain_name.title()}Context,
        operation_type: str,
        saga: 'OperationSaga'
    ) -> List['StepResult']:
        """تنفيذ خطوات العملية مع إمكانية الـ rollback"""
        strategy = self._strategies[operation_type]
        steps = await strategy.get_execution_steps(context.parameters)
        
        results = []
        for step in steps:
            try:
                step_result = await step.execute(context)
                saga.add_compensation(step.name, step_result.compensation_action)
                results.append(step_result)
                
                # Update context with step results
                context.results[step.name] = step_result.data
                
                logger.debug("Step completed",
                           operation_id=context.operation_id,
                           step_name=step.name)
                           
            except Exception as e:
                logger.error("Step failed, initiating rollback",
                           operation_id=context.operation_id,
                           step_name=step.name,
                           error=str(e))
                await saga.compensate()  # Rollback all previous steps
                raise OperationStepFailure(f"Step {{step.name}} failed: {{str(e)}}") from e
                
        return results
    
    async def _finalize_operation(
        self,
        context: {ddd_structure.domain_name.title()}Context,
        results: List['StepResult']
    ):
        """إنهاء العملية وتحديث المقاييس"""
        # Update metrics
        self.metrics.increment_counter(
            "operation_completed",
            tags={{"operation_type": context.operation_id.split('_')[0]}}
        )
        
        # Publish domain events
        await self.event_bus.publish(
            {ddd_structure.domain_name.title()}OperationCompleted(
                operation_id=context.operation_id,
                results=context.results
            )
        )
        
        logger.info("Operation finalized",
                   operation_id=context.operation_id)
    
    async def _handle_operation_failure(
        self,
        context: {ddd_structure.domain_name.title()}Context,
        error: Exception
    ):
        """التعامل مع فشل العملية"""
        context.errors.append(str(error))
        
        # Update error metrics
        self.metrics.increment_counter(
            "operation_failed",
            tags={{"operation_type": context.operation_id.split('_')[0]}}
        )
        
        # Publish failure event
        await self.event_bus.publish(
            {ddd_structure.domain_name.title()}OperationFailed(
                operation_id=context.operation_id,
                error=str(error)
            )
        )
        
        logger.error("Operation failed",
                    operation_id=context.operation_id,
                    error=str(error))

# Domain Events
@dataclass
class {ddd_structure.domain_name.title()}OperationCompleted:
    operation_id: str
    results: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class {ddd_structure.domain_name.title()}OperationFailed:
    operation_id: str
    error: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

# Result classes
@dataclass
class {ddd_structure.domain_name.title()}Result:
    success: bool
    operation_id: str
    results: Dict[str, Any]
    duration_seconds: float
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

# Custom exceptions
class {ddd_structure.domain_name.title()}OperationError(Exception):
    """خطأ في عملية {ddd_structure.domain_name}"""
    pass

class OperationStepFailure(Exception):
    """خطأ في خطوة من خطوات العملية"""
    pass
'''

        orchestrator_file = (
            orchestrator_path / f"{ddd_structure.domain_name}_orchestrator.py"
        )
        orchestrator_file.write_text(orchestrator_content, encoding="utf-8")

        logger.info(f"✅ Orchestrator created: {orchestrator_file}")


class CodeAnalyzer(ast.NodeVisitor):
    """محلل الكود لاستخراج المعلومات"""

    def __init__(self):
        self.complexity_score = 0
        self.domains = set()
        self.dependencies = set()

    def visit_ClassDef(self, node):
        self.complexity_score += 2
        if "Service" in node.name:
            self.domains.add("service")
        elif "Repository" in node.name:
            self.domains.add("repository")
        elif "Manager" in node.name:
            self.domains.add("management")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.complexity_score += 1
        if node.name.startswith("_"):
            self.complexity_score += 0.5
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.dependencies.add(alias.name)
        self.generic_visit(node)


class ComponentExtractor(ast.NodeVisitor):
    """مستخرج المكونات من الكود"""

    def __init__(self):
        self.classes = []
        self.functions = []
        self.dataclasses = []
        self.enums = []
        self.constants = []

    def visit_ClassDef(self, node):
        # تحديد نوع الكلاس
        decorators = [d.id if hasattr(d, "id") else str(d) for d in node.decorator_list]

        if "dataclass" in decorators:
            self.dataclasses.append((node.name, ast.unparse(node)))
        elif any(
            base.id == "Enum" if hasattr(base, "id") else False for base in node.bases
        ):
            self.enums.append((node.name, ast.unparse(node)))
        else:
            self.classes.append((node.name, ast.unparse(node)))

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not node.name.startswith("_"):  # Public functions only
            self.functions.append((node.name, ast.unparse(node)))
        self.generic_visit(node)


async def main():
    """تشغيل إعادة الهيكلة"""
    engine = DDDRefactoringEngine()

    # تحديد God Classes
    god_classes = engine.identify_god_classes()

    if not god_classes:
        logger.info("✅ لا توجد God Classes تحتاج إعادة هيكلة")
        return

    logger.info(f"🎯 تم تحديد {len(god_classes)} God Classes للإعادة هيكلة")

    # إعادة هيكلة كل God Class
    for target in god_classes:
        try:
            ddd_structure = await engine.refactor_to_ddd(target)
            logger.info(f"✅ تم إعادة هيكلة {target.file_path.name} بنجاح")

        except Exception as e:
            logger.error(f"❌ فشل في إعادة هيكلة {target.file_path.name}: {e}")

    # طباعة التقرير
    logger.info("📊 تقرير إعادة الهيكلة:")
    for filename, report in engine.refactoring_report.items():
        logger.info(f"  📁 {filename}:")
        logger.info(f"    📏 الحجم الأصلي: {report['original_size']} سطر")
        logger.info(f"    🏗️ الملفات الجديدة: {report['created_files']} ملف")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
