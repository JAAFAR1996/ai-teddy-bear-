"""
🏗️ DDD Architecture Analyzer & Migration Planner
Lead Architect: جعفر أديب
Advanced Domain-Driven Design restructuring with intelligent analysis
"""

import ast
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Analysis result for a single Python file"""

    path: Path
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    dependencies: Set[str]
    domain_layer: Optional[str] = None
    complexity_score: int = 0
    lines_of_code: int = 0
    is_test_file: bool = False


@dataclass
class DomainEntity:
    """Represents a domain entity in the current codebase"""

    name: str
    file_path: Path
    methods: List[str]
    properties: List[str]
    relationships: List[str]
    is_aggregate_root: bool = False


@dataclass
class LayerMapping:
    """Maps current files to DDD layers"""

    domain_entities: List[Path]
    domain_services: List[Path]
    value_objects: List[Path]
    application_services: List[Path]
    use_cases: List[Path]
    infrastructure: List[Path]
    presentation: List[Path]
    unclassified: List[Path]


@dataclass
class MigrationPlan:
    """Complete migration plan for DDD restructuring"""

    steps: List[Dict[str, Any]]
    file_mappings: Dict[str, str]
    import_updates: Dict[str, List[str]]
    circular_dependencies: List[Tuple[str, str]]
    estimated_effort_hours: int
    risk_assessment: str


class DDDArchitectureAnalyzer:
    """Advanced analyzer for DDD architecture migration"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.files_analysis: Dict[str, FileAnalysis] = {}
        self.dependency_graph = nx.DiGraph()
        self.domain_entities: List[DomainEntity] = []
        self.layer_mapping = LayerMapping([], [], [], [], [], [], [], [])
        self.domain_patterns = {
            "entity": [
                "entity",
                "aggregate",
                "child",
                "user",
                "conversation",
                "session",
            ],
            "value_object": ["id", "value", "type", "enum", "status", "score"],
            "service": ["service", "manager", "handler", "processor"],
            "repository": ["repository", "storage", "persistence", "dao"],
            "use_case": ["use_case", "usecase", "command", "query"],
            "event": ["event", "message", "notification"],
            "adapter": ["adapter", "client", "gateway", "api"],
        }

    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis"""
        logger.info("🔍 Starting DDD Architecture Analysis...")
        self._scan_project_files()
        self._build_dependency_graph()
        circular_deps = self._detect_circular_dependencies()
        self._classify_ddd_layers()
        self._identify_domain_entities()
        complexity_metrics = self._calculate_complexity_metrics()
        migration_plan = self._generate_migration_plan()
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_stats": self._get_project_stats(),
            "layer_classification": self._serialize_layer_mapping(),
            "domain_entities": [
                self._serialize_entity(e) for e in self.domain_entities
            ],
            "circular_dependencies": circular_deps,
            "complexity_metrics": complexity_metrics,
            "migration_plan": self._serialize_migration_plan(migration_plan),
            "recommendations": self._generate_recommendations(),
        }

    def _scan_project_files(self):
        """Scan all Python files in the project"""
        logger.info("📁 Scanning project files...")
        python_files = list(self.project_root.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            try:
                analysis = self._analyze_file(file_path)
                self.files_analysis[str(file_path)] = analysis
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "env",
            ".pytest_cache",
            "migrations",
            "alembic",
            "tests",
            "__init__.py",
        ]
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            analysis = FileAnalysis(
                path=file_path,
                imports=[],
                exports=[],
                classes=[],
                functions=[],
                dependencies=set(),
                lines_of_code=len(content.split("\n")),
                is_test_file="test" in file_path.name.lower(),
            )
            visitor = FileVisitor(analysis)
            visitor.visit(tree)
            analysis.domain_layer = self._classify_domain_layer(
                file_path, analysis)
            analysis.complexity_score = self._calculate_file_complexity(
                analysis)
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return FileAnalysis(
                path=file_path,
                imports=[],
                exports=[],
                classes=[],
                functions=[],
                dependencies=set(),
                lines_of_code=0,
            )

    def _classify_by_path(self, path_parts: tuple, file_content: str) -> str:
        """Classify file based on path structure."""
        if "domain" in path_parts:
            return self._classify_domain_content(file_content)
        elif "application" in path_parts or "use_case" in path_parts:
            return "application"
        elif "infrastructure" in path_parts or "adapter" in path_parts:
            return "infrastructure"
        elif "api" in path_parts or "web" in path_parts or "rest" in path_parts:
            return "presentation"
        return None

    def _classify_domain_content(self, file_content: str) -> str:
        """Classify domain files based on content patterns."""
        if any(pattern in file_content for pattern in self.domain_patterns["entity"]):
            return "domain_entity"
        elif any(pattern in file_content for pattern in self.domain_patterns["value_object"]):
            return "value_object"
        elif any(pattern in file_content for pattern in self.domain_patterns["service"]):
            return "domain_service"
        else:
            return "domain"

    def _classify_by_names(self, analysis: FileAnalysis) -> str:
        """Classify file based on class and function names."""
        class_names = [name.lower() for name in analysis.classes]
        function_names = [name.lower() for name in analysis.functions]
        all_names = class_names + function_names

        name_classifications = [
            ("domain_entity", self.domain_patterns["entity"]),
            ("infrastructure", self.domain_patterns["repository"]),
            ("application", self.domain_patterns["use_case"]),
            ("infrastructure", self.domain_patterns["adapter"]),
        ]

        for classification, patterns in name_classifications:
            if any(pattern in name for name in all_names for pattern in patterns):
                return classification

        return None

    def _classify_domain_layer(self, file_path: Path, analysis: FileAnalysis) -> str:
        """Classify file into DDD layer"""
        path_parts = file_path.parts
        file_content = file_path.name.lower()

        # Try path-based classification first
        path_result = self._classify_by_path(path_parts, file_content)
        if path_result:
            return path_result

        # Try name-based classification
        name_result = self._classify_by_names(analysis)
        if name_result:
            return name_result

        return "unclassified"

    def _build_dependency_graph(self):
        """Build dependency graph between files"""
        logger.info("🔗 Building dependency graph...")
        for file_path, analysis in self.files_analysis.items():
            self.dependency_graph.add_node(file_path)
            for import_path in analysis.imports:
                potential_file = self._resolve_import_to_file(import_path)
                if potential_file and potential_file in self.files_analysis:
                    self.dependency_graph.add_edge(file_path, potential_file)

    def _resolve_import_to_file(self, import_path: str) -> Optional[str]:
        """Resolve import statement to actual file path"""
        if import_path.startswith("."):
            return None
        parts = import_path.split(".")
        for i in range(len(parts)):
            potential_path = self.project_root / "/".join(parts[: i + 1])
            py_file = potential_path.with_suffix(".py")
            if py_file.exists():
                return str(py_file)
            init_file = potential_path / "__init__.py"
            if init_file.exists():
                return str(init_file)
        return None

    def _detect_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Detect circular dependencies using cycle detection"""
        logger.info("🔄 Detecting circular dependencies...")
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            circular_deps = []
            for cycle in cycles:
                if len(cycle) == 2:
                    circular_deps.append((cycle[0], cycle[1]))
                elif len(cycle) > 2:
                    circular_deps.append((cycle[0], cycle[-1]))
            logger.info(f"Found {len(circular_deps)} circular dependencies")
            return circular_deps
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return []

    def _classify_ddd_layers(self):
        """Classify all files into DDD layers"""
        logger.info("📊 Classifying files into DDD layers...")
        for file_path, analysis in self.files_analysis.items():
            path_obj = Path(file_path)
            if analysis.domain_layer == "domain_entity":
                self.layer_mapping.domain_entities.append(path_obj)
            elif analysis.domain_layer == "domain_service":
                self.layer_mapping.domain_services.append(path_obj)
            elif analysis.domain_layer == "value_object":
                self.layer_mapping.value_objects.append(path_obj)
            elif analysis.domain_layer == "application":
                self.layer_mapping.application_services.append(path_obj)
            elif analysis.domain_layer == "infrastructure":
                self.layer_mapping.infrastructure.append(path_obj)
            elif analysis.domain_layer == "presentation":
                self.layer_mapping.presentation.append(path_obj)
            else:
                self.layer_mapping.unclassified.append(path_obj)

    def _identify_domain_entities(self):
        """Identify and analyze domain entities"""
        logger.info("🎯 Identifying domain entities...")
        for file_path in self.layer_mapping.domain_entities:
            analysis = self.files_analysis.get(str(file_path))
            if not analysis:
                continue
            for class_name in analysis.classes:
                entity = DomainEntity(
                    name=class_name,
                    file_path=file_path,
                    methods=[],
                    properties=[],
                    relationships=[],
                    is_aggregate_root=self._is_aggregate_root(
                        class_name, file_path),
                )
                self.domain_entities.append(entity)

    def _is_aggregate_root(self, class_name: str, file_path: Path) -> bool:
        """Determine if a class is an aggregate root"""
        aggregate_indicators = [
            "child",
            "user",
            "conversation",
            "session",
            "order",
            "account",
        ]
        class_lower = class_name.lower()
        return any(indicator in class_lower for indicator in aggregate_indicators)

    def _calculate_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate various complexity metrics"""
        total_files = len(self.files_analysis)
        total_lines = sum(
            a.lines_of_code for a in self.files_analysis.values())
        total_classes = sum(len(a.classes)
                            for a in self.files_analysis.values())
        total_functions = sum(len(a.functions)
                              for a in self.files_analysis.values())
        return {
            "total_files": total_files,
            "total_lines_of_code": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "average_file_size": total_lines / total_files if total_files > 0 else 0,
            "dependency_density": self.dependency_graph.number_of_edges()
            / max(1, self.dependency_graph.number_of_nodes()),
            "domain_coverage": {
                "entities": len(self.layer_mapping.domain_entities),
                "services": len(self.layer_mapping.domain_services),
                "value_objects": len(self.layer_mapping.value_objects),
                "application_services": len(self.layer_mapping.application_services),
                "unclassified": len(self.layer_mapping.unclassified),
            },
        }

    def _calculate_file_complexity(self, analysis: FileAnalysis) -> int:
        """Calculate complexity score for a file"""
        complexity = 0
        complexity += len(analysis.classes) * 3
        complexity += len(analysis.functions) * 2
        complexity += len(analysis.imports) * 1
        complexity += len(analysis.dependencies) * 2
        complexity += analysis.lines_of_code // 10
        return complexity

    def _create_setup_step(self) -> Dict[str, Any]:
        """Create initial setup step for migration."""
        return {
            "phase": 1,
            "title": "Create New DDD Directory Structure",
            "description": "Create the new domain-driven design directory structure",
            "actions": ["create_directories", "setup_base_classes"],
            "estimated_hours": 2,
        }

    def _create_layer_migration_steps(self) -> List[Dict[str, Any]]:
        """Create migration steps for each DDD layer."""
        steps = []
        phase = 2

        layer_configs = [
            ("Domain Entities", self.layer_mapping.domain_entities, 1.5),
            ("Value Objects", self.layer_mapping.value_objects, 1.0),
            ("Application Layer", self.layer_mapping.application_services, 2.0),
            ("Infrastructure Layer", self.layer_mapping.infrastructure, 1.5),
        ]

        for title, files, hours_per_file in layer_configs:
            if files:
                steps.append({
                    "phase": phase,
                    "title": f"Migrate {title}",
                    "description": f"Migrate {len(files)} {title.lower()}",
                    "files": [str(f) for f in files],
                    "estimated_hours": len(files) * hours_per_file,
                })
                phase += 1

        return steps

    def _create_final_steps(self, current_phase: int) -> List[Dict[str, Any]]:
        """Create final migration steps."""
        return [
            {
                "phase": current_phase,
                "title": "Update Imports and Dependencies",
                "description": "Update all import statements and fix dependencies",
                "actions": ["update_imports", "fix_circular_dependencies"],
                "estimated_hours": 8,
            },
            {
                "phase": current_phase + 1,
                "title": "Testing and Validation",
                "description": "Run tests and validate migration success",
                "actions": ["run_tests", "validate_architecture"],
                "estimated_hours": 4,
            }
        ]

    def _generate_migration_plan(self) -> MigrationPlan:
        """Generate comprehensive migration plan"""
        logger.info("📋 Generating migration plan...")

        steps = []
        file_mappings = {}
        import_updates = {}

        # Add setup step
        steps.append(self._create_setup_step())

        # Add layer migration steps
        layer_steps = self._create_layer_migration_steps()
        steps.extend(layer_steps)

        # Add final steps
        final_phase = len(steps) + 1
        final_steps = self._create_final_steps(final_phase)
        steps.extend(final_steps)

        # Calculate total effort
        total_hours = sum(step.get("estimated_hours", 0) for step in steps)

        return MigrationPlan(
            steps=steps,
            file_mappings=file_mappings,
            import_updates=import_updates,
            circular_dependencies=self._detect_circular_dependencies(),
            estimated_effort_hours=total_hours,
            risk_assessment=self._assess_migration_risk(),
        )

    def _assess_migration_risk(self) -> str:
        """Assess the risk level of the migration"""
        circular_deps = len(self._detect_circular_dependencies())
        unclassified_files = len(self.layer_mapping.unclassified)
        total_files = len(self.files_analysis)
        risk_score = 0
        risk_score += circular_deps * 10
        risk_score += unclassified_files / total_files * 50
        risk_score += min(total_files / 10, 20)
        if risk_score < 20:
            return "LOW"
        elif risk_score < 50:
            return "MEDIUM"
        else:
            return "HIGH"

    def _generate_recommendations(self) -> List[str]:
        """Generate architectural recommendations"""
        recommendations = []
        circular_deps = len(self._detect_circular_dependencies())
        if circular_deps > 0:
            recommendations.append(
                f"🔄 Fix {circular_deps} circular dependencies before migration"
            )
        unclassified = len(self.layer_mapping.unclassified)
        if unclassified > 0:
            recommendations.append(
                f"📋 Manually classify {unclassified} unclassified files"
            )
        if len(self.domain_entities) == 0:
            recommendations.append(
                "🎯 No clear domain entities found - consider domain modeling workshop"
            )
        if len(self.layer_mapping.domain_entities) < 3:
            recommendations.append(
                "🏗️ Consider identifying more domain entities for better separation"
            )
        large_files = [
            f for f, a in self.files_analysis.items() if a.lines_of_code > 500
        ]
        if large_files:
            recommendations.append(
                f"📏 Consider breaking down {len(large_files)} large files"
            )
        return recommendations

    def _get_project_stats(self) -> Dict[str, Any]:
        """Get overall project statistics"""
        return {
            "total_python_files": len(self.files_analysis),
            "total_lines_of_code": sum(
                a.lines_of_code for a in self.files_analysis.values()
            ),
            "total_classes": sum(len(a.classes) for a in self.files_analysis.values()),
            "total_functions": sum(
                len(a.functions) for a in self.files_analysis.values()
            ),
            "files_by_layer": {
                "domain_entities": len(self.layer_mapping.domain_entities),
                "domain_services": len(self.layer_mapping.domain_services),
                "value_objects": len(self.layer_mapping.value_objects),
                "application_services": len(self.layer_mapping.application_services),
                "infrastructure": len(self.layer_mapping.infrastructure),
                "presentation": len(self.layer_mapping.presentation),
                "unclassified": len(self.layer_mapping.unclassified),
            },
        }

    def _serialize_layer_mapping(self) -> Dict[str, List[str]]:
        """Serialize layer mapping to dict"""
        return {
            "domain_entities": [str(p) for p in self.layer_mapping.domain_entities],
            "domain_services": [str(p) for p in self.layer_mapping.domain_services],
            "value_objects": [str(p) for p in self.layer_mapping.value_objects],
            "application_services": [
                str(p) for p in self.layer_mapping.application_services
            ],
            "infrastructure": [str(p) for p in self.layer_mapping.infrastructure],
            "presentation": [str(p) for p in self.layer_mapping.presentation],
            "unclassified": [str(p) for p in self.layer_mapping.unclassified],
        }

    def _serialize_entity(self, entity: DomainEntity) -> Dict[str, Any]:
        """Serialize domain entity to dict"""
        return {
            "name": entity.name,
            "file_path": str(entity.file_path),
            "methods": entity.methods,
            "properties": entity.properties,
            "relationships": entity.relationships,
            "is_aggregate_root": entity.is_aggregate_root,
        }

    def _serialize_migration_plan(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Serialize migration plan to dict"""
        return {
            "steps": plan.steps,
            "estimated_effort_hours": plan.estimated_effort_hours,
            "risk_assessment": plan.risk_assessment,
            "circular_dependencies_count": len(plan.circular_dependencies),
        }


class FileVisitor(ast.NodeVisitor):
    """AST visitor to extract file information"""

    def __init__(self, analysis: FileAnalysis):
        self.analysis = analysis

    def visit_Import(self, node):
        """Visit import statements"""
        for alias in node.names:
            self.analysis.imports.append(alias.name)
            self.analysis.dependencies.add(alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        """Visit from-import statements"""
        if node.module:
            self.analysis.imports.append(node.module)
            self.analysis.dependencies.add(node.module.split(".")[0])

    def visit_ClassDef(self, node):
        """Visit class definitions"""
        self.analysis.classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        self.analysis.functions.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        self.analysis.functions.append(node.name)
        self.generic_visit(node)


def main():
    """Main execution function"""
    logger.info("🏗️ DDD Architecture Analyzer & Migration Planner")
    logger.info("=" * 50)
    logger.info("Lead Architect: جعفر أديب")
    logger.info("=" * 50)
    analyzer = DDDArchitectureAnalyzer()
    analysis_result = analyzer.analyze_project()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ddd_analysis_report_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    logger.info("\n📊 ANALYSIS SUMMARY")
    logger.info("-" * 30)
    logger.info(
        f"Total Files: {analysis_result['project_stats']['total_python_files']}"
    )
    logger.info(
        f"Lines of Code: {analysis_result['project_stats']['total_lines_of_code']}"
    )
    logger.info(
        f"Domain Entities: {analysis_result['project_stats']['files_by_layer']['domain_entities']}"
    )
    logger.info(
        f"Unclassified Files: {analysis_result['project_stats']['files_by_layer']['unclassified']}"
    )
    logger.info(
        f"Circular Dependencies: {len(analysis_result['circular_dependencies'])}"
    )
    logger.info(
        f"Migration Risk: {analysis_result['migration_plan']['risk_assessment']}"
    )
    logger.info(
        f"Estimated Effort: {analysis_result['migration_plan']['estimated_effort_hours']} hours"
    )
    logger.info("\n📋 RECOMMENDATIONS")
    logger.info("-" * 30)
    for rec in analysis_result["recommendations"]:
        logger.info(f"• {rec}")
    logger.info(f"\n✅ Analysis complete! Report saved to: {output_file}")


if __name__ == "__main__":
    main()
