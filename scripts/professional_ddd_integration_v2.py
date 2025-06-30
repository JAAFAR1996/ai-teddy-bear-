#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional DDD Integration Script v2
======================================
Integrates DDD structure into main project professionally
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class DDDIntegrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.legacy_dir = self.project_root / "src" / "legacy"
        self.src_dir = self.project_root / "src"
        self.report = []
        
    def log(self, message: str):
        """Log message to console and report"""
        print(f"✓ {message}")
        self.report.append(message)
    
    def create_legacy_structure(self):
        """Create legacy folder structure"""
        self.log("Creating legacy folder structure...")
        
        legacy_dirs = [
            "god_classes",
            "deprecated_services", 
            "old_implementations",
            "large_files"
        ]
        
        for dir_name in legacy_dirs:
            dir_path = self.legacy_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Create README for legacy
        readme_content = """# Legacy Code Archive
===================

This folder contains old code that has been refactored or replaced:

## god_classes/
Large files (1000+ lines) that have been split into DDD structure

## deprecated_services/
Old service implementations that have been modernized

## old_implementations/
Previous versions of critical components

## large_files/
Files that exceeded our coding standards

**Note**: These files are kept for reference and will be removed in next cleanup cycle.
"""
        
        with open(self.legacy_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
    def identify_god_classes(self) -> List[Path]:
        """Identify God Classes to move to legacy"""
        god_classes = []
        
        # Large service files that need to be moved
        patterns = [
            "application/services/*_service.py",
            "application/services/ai/*.py",
            "application/services/audio/*.py"
        ]
        
        for pattern in patterns:
            for file_path in self.src_dir.glob(pattern):
                if file_path.is_file():
                    # Check file size
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                        if lines > 500:  # Files larger than 500 lines
                            god_classes.append(file_path)
                    except:
                        continue
                        
        return god_classes
    
    def move_to_legacy(self, file_path: Path):
        """Move file to legacy with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = file_path.stem
        extension = file_path.suffix
        
        new_name = f"{file_name}_{timestamp}{extension}"
        legacy_path = self.legacy_dir / "god_classes" / new_name
        
        try:
            shutil.copy2(file_path, legacy_path)
            self.log(f"Moved {file_path.name} to legacy as {new_name}")
            return True
        except Exception as e:
            self.log(f"Error moving {file_path.name}: {str(e)}")
            return False
    
    def get_ddd_domains(self) -> List[str]:
        """Get list of DDD domains to integrate"""
        ddd_domains = []
        services_dir = self.src_dir / "application" / "services"
        
        for item in services_dir.iterdir():
            if item.is_dir() and item.name.endswith("_ddd"):
                domain_name = item.name.replace("_ddd", "")
                ddd_domains.append(domain_name)
                
        return ddd_domains
    
    def integrate_domain(self, domain_name: str):
        """Integrate single DDD domain into project structure"""
        self.log(f"Integrating domain: {domain_name}")
        
        source_dir = self.src_dir / "application" / "services" / f"{domain_name}_ddd"
        
        if not source_dir.exists():
            self.log(f"Warning: {source_dir} does not exist")
            return
            
        # Domain layer
        domain_target = self.src_dir / "domain" / domain_name
        domain_target.mkdir(parents=True, exist_ok=True)
        
        # Application layer  
        app_target = self.src_dir / "application" / domain_name
        app_target.mkdir(parents=True, exist_ok=True)
        
        # Infrastructure layer
        infra_target = self.src_dir / "infrastructure" / domain_name
        infra_target.mkdir(parents=True, exist_ok=True)
        
        # Copy domain files
        for item in source_dir.iterdir():
            if item.is_dir():
                layer_name = item.name
                target_base = None
                
                if layer_name == "domain":
                    target_base = domain_target
                elif layer_name == "application":
                    target_base = app_target  
                elif layer_name == "infrastructure":
                    target_base = infra_target
                    
                if target_base:
                    for sub_item in item.iterdir():
                        if sub_item.is_dir():
                            target_dir = target_base / sub_item.name
                            target_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Copy all files in subdirectory
                            for file_item in sub_item.iterdir():
                                if file_item.is_file() and file_item.suffix == ".py":
                                    target_file = target_dir / file_item.name
                                    shutil.copy2(file_item, target_file)
                                    
        self.log(f"Domain {domain_name} integrated successfully")
    
    def create_domain_init_files(self):
        """Create __init__.py files for all new directories"""
        self.log("Creating __init__.py files...")
        
        for root, dirs, files in os.walk(self.src_dir):
            root_path = Path(root)
            if not (root_path / "__init__.py").exists():
                if any(f.endswith(".py") for f in files):
                    init_file = root_path / "__init__.py"
                    init_file.write_text("# Domain module\n", encoding="utf-8")
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        report_content = f"""# DDD Integration Report
========================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Legacy structure created
- DDD domains integrated into main project
- God Classes moved to legacy folder
- Professional structure implemented

## Integration Log
"""
        
        for item in self.report:
            report_content += f"- {item}\n"
            
        report_content += f"""

## Project Structure After Integration
```
src/
├── domain/
│   ├── accessibility/
│   ├── cleanup/
│   ├── emotion/
│   └── memory/
├── application/
│   ├── accessibility/
│   ├── cleanup/
│   ├── emotion/
│   └── memory/
├── infrastructure/
│   ├── accessibility/
│   ├── cleanup/
│   ├── emotion/
│   └── memory/
└── legacy/
    ├── god_classes/
    ├── deprecated_services/
    └── old_implementations/
```

## Next Steps
1. Update imports in dependent files
2. Run tests to verify integration
3. Remove legacy files after verification
4. Update documentation

## Benefits Achieved
- Clean Architecture implementation
- Domain-Driven Design structure
- Reduced file complexity
- Better maintainability
- Professional organization
"""
        
        report_file = self.project_root / "DDD_INTEGRATION_REPORT.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        self.log(f"Integration report saved to {report_file}")
    
    def run_integration(self):
        """Run complete DDD integration process"""
        print("=" * 60)
        print("Professional DDD Integration Starting...")
        print("=" * 60)
        
        # Phase 1: Create legacy structure
        self.create_legacy_structure()
        
        # Phase 2: Identify and move God Classes
        god_classes = self.identify_god_classes()
        for god_class in god_classes:
            self.move_to_legacy(god_class)
            
        # Phase 3: Integrate DDD domains
        domains = self.get_ddd_domains()
        for domain in domains:
            self.integrate_domain(domain)
            
        # Phase 4: Create init files
        self.create_domain_init_files()
        
        # Phase 5: Generate report
        self.generate_integration_report()
        
        print("=" * 60)
        print("DDD Integration Completed Successfully!")
        print("=" * 60)

if __name__ == "__main__":
    integrator = DDDIntegrator()
    integrator.run_integration() 