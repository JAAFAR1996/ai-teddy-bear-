#!/usr/bin/env python3
"""
🧸 AI Teddy Bear - Render Setup Checker
=======================================
Quick validation script to check Render deployment configuration
"""

import os
from pathlib import Path
import sys

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_requirements_format() -> bool:
    """Check requirements.render.txt format"""
    try:
        with open('requirements.render.txt', 'r') as f:
            content = f.read()
        
        # Check for problematic patterns
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # Check for proper package format
                if '==' in line or '>=' in line or '<=' in line:
                    continue
                elif line and not any(op in line for op in ['==', '>=', '<=', '>', '<', '~=']):
                    issues.append(f"Line {i}: '{line}' - Missing version specifier")
        
        if issues:
            print("⚠️  Requirements format issues:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print("✅ requirements.render.txt format is valid")
            return True
            
    except Exception as e:
        print(f"❌ Error checking requirements.render.txt: {e}")
        return False

def check_app_structure() -> bool:
    """Check basic app structure"""
    required_files = [
        ('app.py', 'Main application file'),
        ('src/__init__.py', 'Source package init'),
        ('src/infrastructure/audio/cloud_audio_service.py', 'Cloud audio service')
    ]
    
    all_good = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def validate_render_yaml() -> bool:
    """Validate render.yaml configuration"""
    try:
        import yaml
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        if 'services' not in config:
            print("❌ render.yaml: Missing 'services' section")
            return False
        
        service = config['services'][0]
        required_fields = ['type', 'env', 'buildCommand', 'startCommand']
        
        for field in required_fields:
            if field not in service:
                print(f"❌ render.yaml: Missing '{field}' in service")
                return False
        
        print("✅ render.yaml configuration is valid")
        return True
        
    except ImportError:
        print("⚠️  PyYAML not installed - skipping render.yaml validation")
        return True
    except Exception as e:
        print(f"❌ render.yaml validation error: {e}")
        return False

def print_render_instructions():
    """Print Render deployment instructions"""
    print("\n" + "="*60)
    print("🚀 RENDER DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 Method 1: Fix Current Deployment")
    print("1. Go to your Render Dashboard")
    print("2. Click on your service")
    print("3. Go to Settings")
    print("4. Update Build Command to:")
    print("   pip install --upgrade pip && pip install -r requirements.render.txt")
    print("5. Update Start Command to:")
    print("   uvicorn app:app --host 0.0.0.0 --port $PORT")
    print("6. Add Environment Variables:")
    print("   - PYTHON_VERSION: 3.11")
    print("   - OPENAI_API_KEY: your-key (optional)")
    print("   - ELEVENLABS_API_KEY: your-key (optional)")
    
    print("\n📋 Method 2: Use render.yaml (Recommended)")
    print("1. Commit the render.yaml file to your repository")
    print("2. In Render Dashboard, create a new service")
    print("3. Connect your GitHub repository")
    print("4. Render will automatically use render.yaml configuration")
    
    print("\n🔧 Common Issues:")
    print("❌ Don't use backticks in Build Command: `pip install...`")
    print("✅ Use simple command: pip install -r requirements.render.txt")
    print("❌ Don't include quotes around commands")
    print("✅ Copy commands exactly as shown above")

def main():
    """Main validation function"""
    print("🧸 AI Teddy Bear - Render Setup Checker")
    print("="*50)
    
    checks = [
        ("Basic files", check_app_structure),
        ("Requirements format", check_requirements_format),
        ("Render configuration", validate_render_yaml),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking: {name}")
        result = check_func()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Ready for Render deployment.")
    else:
        print("⚠️  Some issues found. Please fix them before deployment.")
    
    # Always show instructions
    print_render_instructions()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main()) 