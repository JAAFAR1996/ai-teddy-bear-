#!/usr/bin/env python3
"""
Simple DDD Integration Script
============================
"""

import os
import shutil
from pathlib import Path

def create_legacy_folder():
    """Create legacy folder for old files"""
    legacy_path = Path("src/legacy")
    legacy_path.mkdir(parents=True, exist_ok=True)
    
    # Create subfolders
    (legacy_path / "god_classes").mkdir(exist_ok=True)
    (legacy_path / "deprecated_services").mkdir(exist_ok=True)
    
    print("✓ Legacy folder created")

def move_ddd_domains():
    """Move DDD domains to proper structure"""
    services_dir = Path("src/application/services")
    
    # Find DDD domains
    ddd_domains = []
    for item in services_dir.iterdir():
        if item.is_dir() and item.name.endswith("_ddd"):
            domain_name = item.name.replace("_ddd", "")
            ddd_domains.append(domain_name)
    
    print(f"Found DDD domains: {ddd_domains}")
    
    for domain in ddd_domains:
        source = services_dir / f"{domain}_ddd"
        
        # Create target directories
        domain_dir = Path(f"src/domain/{domain}")
        app_dir = Path(f"src/application/{domain}")
        infra_dir = Path(f"src/infrastructure/{domain}")
        
        domain_dir.mkdir(parents=True, exist_ok=True)
        app_dir.mkdir(parents=True, exist_ok=True)
        infra_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files from DDD structure
        if source.exists():
            for item in source.iterdir():
                if item.is_dir():
                    if item.name == "domain":
                        copy_structure(item, domain_dir)
                    elif item.name == "application":
                        copy_structure(item, app_dir)
                    elif item.name == "infrastructure":
                        copy_structure(item, infra_dir)
        
        print(f"✓ Integrated domain: {domain}")

def copy_structure(source_dir, target_dir):
    """Copy directory structure"""
    for item in source_dir.iterdir():
        if item.is_dir():
            target = target_dir / item.name
            target.mkdir(exist_ok=True)
            copy_structure(item, target)
        elif item.is_file() and item.suffix == ".py":
            target_file = target_dir / item.name
            shutil.copy2(item, target_file)

def create_init_files():
    """Create __init__.py files"""
    for root, dirs, files in os.walk("src"):
        if any(f.endswith(".py") for f in files):
            init_file = Path(root) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Module\n")

def main():
    print("Starting DDD Integration...")
    
    create_legacy_folder()
    move_ddd_domains()
    create_init_files()
    
    print("DDD Integration completed!")

if __name__ == "__main__":
    main() 