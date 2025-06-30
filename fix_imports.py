#!/usr/bin/env python3
"""
🔧 Import Fixer for AI Teddy Bear v5
إصلاح سريع لمشاكل imports بعد إعادة التنظيم

المهندس: جعفر أديب (Jaafar Adeeb)
"""

import os
from pathlib import Path

def fix_imports():
    """إصلاح مشاكل imports الأساسية"""
    
    # إنشاء __init__.py مفقود
    init_files = [
        "src/core/domain/value_objects/__init__.py",
        "src/core/domain/services/__init__.py", 
        "src/core/domain/repositories/__init__.py",
        "src/application/commands/__init__.py",
        "src/application/queries/__init__.py",
        "src/application/use_cases/__init__.py"
    ]
    
    for init_file in init_files:
        path = Path(init_file)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("")
            print(f"✅ Created {init_file}")
    
    # إصلاح core/domain/__init__.py
    core_domain_init = Path("src/core/domain/__init__.py")
    if core_domain_init.exists():
        content = '''"""
🧠 Domain Layer - AI Teddy Bear Core
===================================
"""

# Simplified imports to avoid circular dependencies
from .entities.child import Child

__all__ = [
    'Child'
]
'''
        core_domain_init.write_text(content)
        print("✅ Fixed src/core/domain/__init__.py")
    
    print("🎉 Basic import fixes completed!")

if __name__ == "__main__":
    fix_imports() 