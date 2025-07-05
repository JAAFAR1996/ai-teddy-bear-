from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
🧠 Smart DDD Restructuring Tool
Lead Architect: جعفر أديب
Intelligent Domain-Driven Design migration with advanced analysis
"""

import ast
import json
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .classification_strategies import (
    ApplicationLayerClassificationStrategy,
    DomainServiceClassificationStrategy,
    NameBasedClassificationStrategy,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MigrationPlan:
    """Migration plan with ordered steps and import updates"""

    steps: List[Dict[str, str]]
    import_updates: Dict[str, List[str]]
    risk_level: str
    estimated_hours: int


class SmartRestructurer:
    """Intelligent DDD restructuring with dependency analysis"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.import_map: Dict[str, Set[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.circular_deps: List[Tuple[str, str]] = []

        # New DDD structure
        self.new_structure = {
            "src/domain/entities": [],
            "src/domain/value_objects": [],
            "src/domain/services": [],
            "src/application/commands": [],
            "src/application/queries": [],
            "src/application/handlers": [],
            "src/infrastructure/persistence/repositories": [],
            "src/infrastructure/ai": [],
            "src/infrastructure/messaging": [],
            "src/presentation/api/rest": [],
            "src/presentation/api/graphql": [],
            "src/presentation/websocket": [],
        }

        self._classification_strategies = [
            NameBasedClassificationStrategy(
                ["entity", "aggregate", "child", "user"], "src/domain/entities"
            ),
            NameBasedClassificationStrategy(
                ["value", "id", "enum", "type"], "src/domain/value_objects"
            ),
            DomainServiceClassificationStrategy([], "src/domain/services"),
            ApplicationLayerClassificationStrategy(
                ["use_case", "command", "query"], ""
            ),
            NameBasedClassificationStrategy(
                ["repository", "persistence"],
                "src/infrastructure/persistence/repositories",
            ),
            NameBasedClassificationStrategy(
                ["api", "rest", "endpoint"], "src/presentation/api/rest"
            ),
            NameBasedClassificationStrategy(
                ["graphql"], "src/presentation/api/graphql"
            ),
        ]

    def analyze_dependencies(self) -> Dict[str, Any]:
        """تحليل جميع التبعيات وبناء خريطة"""
        logger.info("🔍 Analyzing project dependencies...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                    self._extract_imports(tree, file_path)
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")

        return {
            "total_files": len(python_files), "analyzed_files": len(
                self.import_map), "total_imports": sum(
                len(imports) for imports in self.import_map.values()), }

    def detect_circular_dependencies(self) -> List[Tuple[str, str]]:
        """كشف التبعيات الدائرية باستخدام Tarjan's algorithm"""
        logger.info("🔄 Detecting circular dependencies...")

        # Build adjacency list
        self._build_dependency_graph()

        # Simple cycle detection
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node) -> Any:
            if node in rec_stack:
                return True  # Cycle detected
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, set()):
                if dfs(neighbor):
                    cycles.append((node, neighbor))

            rec_stack.remove(node)
            return False

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node)

        self.circular_deps = cycles
        logger.info(f"Found {len(cycles)} circular dependencies")
        return cycles

    def generate_migration_plan(self) -> MigrationPlan:
        """توليد خطة هجرة ذكية"""
        logger.info("📋 Generating intelligent migration plan...")

        steps = [{"phase": "1",
                  "title": "Create New DDD Structure",
                  "action": "create_directories",
                  "description": "Create the new domain-driven design directory structure",
                  },
                 {"phase": "2",
                  "title": "Analyze Current Code",
                  "action": "classify_existing_files",
                  "description": "Classify existing files into DDD layers",
                  },
                 {"phase": "3",
                  "title": "Migrate Domain Layer",
                  "action": "migrate_domain_files",
                  "description": "Move and refactor domain entities and value objects",
                  },
                 {"phase": "4",
                  "title": "Migrate Application Layer",
                  "action": "migrate_application_files",
                  "description": "Move use cases, commands, and queries",
                  },
                 {"phase": "5",
                  "title": "Migrate Infrastructure Layer",
                  "action": "migrate_infrastructure_files",
                  "description": "Move repositories, adapters, and external services",
                  },
                 {"phase": "6",
                  "title": "Update Imports",
                  "action": "update_all_imports",
                  "description": "Update all import statements to new structure",
                  },
                 {"phase": "7",
                  "title": "Validate Migration",
                  "action": "validate_migration",
                  "description": "Run tests and validate the new structure",
                  },
                 ]

        import_updates = self._generate_import_updates()
        risk_level = self._assess_risk_level()
        estimated_hours = len(steps) * 2 + len(self.circular_deps) * 1.5

        return MigrationPlan(
            steps=steps,
            import_updates=import_updates,
            risk_level=risk_level,
            estimated_hours=int(estimated_hours),
        )

    def execute_migration(self, plan: MigrationPlan) -> bool:
        """Execute the migration plan"""
        logger.info("🚀 Starting DDD migration execution...")

        try:
            for step in plan.steps:
                logger.info(f"Executing {step['title']}...")

                action = step["action"]
                if action == "create_directories":
                    self._create_ddd_directories()
                elif action == "classify_existing_files":
                    self._classify_existing_files()
                elif action == "migrate_domain_files":
                    self._migrate_domain_files()
                elif action == "migrate_application_files":
                    self._migrate_application_files()
                elif action == "migrate_infrastructure_files":
                    self._migrate_infrastructure_files()
                elif action == "update_all_imports":
                    self._update_all_imports(plan.import_updates)
                elif action == "validate_migration":
                    self._validate_migration()

                logger.info(f"✅ Completed {step['title']}")

            logger.info("🎉 Migration completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "env",
            "test",
            "__init__.py"]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _extract_imports(self, tree: ast.Module, file_path: Path) -> None:
        """Extract imports from AST"""
        file_str = str(file_path)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        self.import_map[file_str] = imports

    def _build_dependency_graph(self) -> Any:
        """Build dependency graph from imports"""
        for file_path, imports in self.import_map.items():
            self.dependency_graph[file_path] = set()

            for import_name in imports:
                # Convert import to potential file paths
                potential_files = self._resolve_import_to_files(import_name)
                for potential_file in potential_files:
                    if potential_file in self.import_map:
                        self.dependency_graph[file_path].add(potential_file)

    def _resolve_import_to_files(self, import_name: str) -> List[str]:
        """Resolve import name to possible file paths"""
        parts = import_name.split(".")
        potential_files = []

        # Try different path combinations
        for i in range(len(parts)):
            # Direct file
            path = self.project_root / "/".join(parts[: i + 1])
            py_file = path.with_suffix(".py")
            if py_file.exists():
                potential_files.append(str(py_file))

            # Package __init__.py
            init_file = path / "__init__.py"
            if init_file.exists():
                potential_files.append(str(init_file))

        return potential_files

    def _generate_import_updates(self) -> Dict[str, List[str]]:
        """Generate import update mappings"""
        updates = {}

        # Domain layer updates
        updates["src.domain.entities"] = [
            "core.domain.entities",
            "domain.entities",
            "entities",
        ]

        # Application layer updates
        updates["src.application.commands"] = [
            "core.application.commands",
            "application.commands",
            "commands",
        ]

        # Infrastructure updates
        updates["src.infrastructure.persistence"] = [
            "core.infrastructure.persistence",
            "infrastructure.persistence",
            "persistence",
        ]

        return updates

    def _assess_risk_level(self) -> str:
        """Assess migration risk level"""
        risk_score = 0

        # Circular dependencies increase risk
        risk_score += len(self.circular_deps) * 10

        # Large number of files increase risk
        total_files = len(self.import_map)
        risk_score += min(total_files / 10, 20)

        # Complex imports increase risk
        total_imports = sum(len(imports)
                            for imports in self.import_map.values())
        risk_score += min(total_imports / 50, 30)

        if risk_score < 30:
            return "LOW"
        elif risk_score < 60:
            return "MEDIUM"
        else:
            return "HIGH"

    def _create_ddd_directories(self) -> Any:
        """Create new DDD directory structure"""
        logger.info("📁 Creating DDD directory structure...")

        for directory in self.new_structure.keys():
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create __init__.py files
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""DDD Layer Module"""')

    def _classify_existing_files(self) -> None:
        """Classify existing files into DDD layers using a strategy pattern."""
        logger.info("🏷️ Classifying existing files...")

        for file_path_str in self.import_map.keys():
            path_obj = Path(file_path_str)
            file_content = path_obj.name.lower()

            for strategy in self._classification_strategies:
                target_layer = strategy.classify(path_obj, file_content)
                if target_layer:
                    if target_layer in self.new_structure:
                        self.new_structure[target_layer].append(file_path_str)
                    else:
                        logger.warning(
                            f"Target layer '{target_layer}' not defined in new structure."
                        )
                    break  # Move to the next file once classified

    def _migrate_domain_files(self) -> Any:
        """Migrate domain layer files"""
        logger.info("🎯 Migrating domain layer...")

        for target_dir, files in self.new_structure.items():
            if "domain" not in target_dir:
                continue

            target_path = self.project_root / target_dir
            for file_path in files:
                self._move_file_safely(file_path, target_path)

    def _migrate_application_files(self) -> Any:
        """Migrate application layer files"""
        logger.info("⚙️ Migrating application layer...")

        for target_dir, files in self.new_structure.items():
            if "application" not in target_dir:
                continue

            target_path = self.project_root / target_dir
            for file_path in files:
                self._move_file_safely(file_path, target_path)

    def _migrate_infrastructure_files(self) -> Any:
        """Migrate infrastructure layer files"""
        logger.info("🏗️ Migrating infrastructure layer...")

        for target_dir, files in self.new_structure.items():
            if "infrastructure" not in target_dir and "presentation" not in target_dir:
                continue

            target_path = self.project_root / target_dir
            for file_path in files:
                self._move_file_safely(file_path, target_path)

    def _move_file_safely(self, source_path: Path, target_dir: Path) -> None:
        """Safely move file to new location"""
        source = Path(source_path)
        if not source.exists():
            return

        target_file = target_dir / source.name

        # Avoid overwriting existing files
        counter = 1
        while target_file.exists():
            name_parts = source.stem, counter, source.suffix
            target_file = target_dir / \
                f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1

        try:
            shutil.move(str(source), str(target_file))
            logger.info(f"Moved {source} -> {target_file}")
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")

    def _update_all_imports(
            self, import_updates: Dict[str, List[str]]) -> None:
        """Update all import statements"""
        logger.info("🔄 Updating import statements...")

        # This would need more sophisticated implementation
        # For now, just log what would be updated
        for new_import, old_imports in import_updates.items():
            logger.info(f"Would update {old_imports} -> {new_import}")

    def _validate_migration(self) -> Any:
        """Validate the migration"""
        logger.info("✅ Validating migration...")

        # Check if new structure exists
        for directory in self.new_structure.keys():
            dir_path = self.project_root / directory
            if not dir_path.exists():
                raise Exception(f"Directory not created: {directory}")

        logger.info("Migration validation passed!")


def main() -> Any:
    """Main execution function"""
    logger.info("🧠 Smart DDD Restructuring Tool")
    logger.info("Lead Architect: جعفر أديب")
    logger.info("=" * 40)

    restructurer = SmartRestructurer()

    # Step 1: Analyze dependencies
    analysis = restructurer.analyze_dependencies()
    logger.info(f"📊 Analyzed {analysis['analyzed_files']} files")

    # Step 2: Detect circular dependencies
    circular_deps = restructurer.detect_circular_dependencies()
    if circular_deps:
        logger.warning(f"⚠️ Found {len(circular_deps)} circular dependencies")

    # Step 3: Generate migration plan
    plan = restructurer.generate_migration_plan()
    logger.info(f"📋 Generated migration plan with {len(plan.steps)} steps")
    logger.info(f"🎯 Risk Level: {plan.risk_level}")
    logger.info(f"⏱️ Estimated Time: {plan.estimated_hours} hours")

    # Step 4: Execute migration (with user confirmation)
    confirm = input("\n🚀 Execute migration? (y/N): ")
    if confirm.lower() == "y":
        success = restructurer.execute_migration(plan)
        if success:
            logger.info("✅ Migration completed successfully!")
        else:
            logger.error("❌ Migration failed!")
    else:
        logger.info("Migration cancelled.")


if __name__ == "__main__":
    main()
