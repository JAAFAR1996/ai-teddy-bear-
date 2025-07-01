#!/usr/bin/env python3
"""
🏥 AI Teddy Bear - Health Check Script
تحقق من صحة النظام والخدمات
"""
import asyncio
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import aiohttp
    import psutil
    import requests
except ImportError:
    print("⚠️ Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "psutil", "requests"])
    import aiohttp
    import psutil
    import requests


def print_header():
    """طباعة رأس التقرير"""
    print("=" * 60)
    print("🏥 AI Teddy Bear - System Health Check")
    print("=" * 60)
    print()


def check_system_requirements() -> Dict[str, bool]:
    """التحقق من متطلبات النظام"""
    print("🔍 Checking system requirements...")
    results = {}
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version >= (3, 11)
    results['python'] = python_ok
    print(f"  Python {python_version.major}.{python_version.minor}.{python_version.micro}: {'✅' if python_ok else '❌'}")
    
    # Check Node.js
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        node_version = node_result.stdout.strip().replace('v', '')
        node_major = int(node_version.split('.')[0])
        node_ok = node_major >= 18
        results['nodejs'] = node_ok
        print(f"  Node.js {node_version}: {'✅' if node_ok else '❌'}")
    except:
        results['nodejs'] = False
        print("  Node.js: ❌ Not found")
    
    # Check npm
    try:
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        npm_version = npm_result.stdout.strip()
        results['npm'] = True
        print(f"  npm {npm_version}: ✅")
    except:
        results['npm'] = False
        print("  npm: ❌ Not found")
    
    return results


def check_project_structure() -> Dict[str, bool]:
    """التحقق من بنية المشروع"""
    print("\n📁 Checking project structure...")
    results = {}
    
    required_files = [
        "requirements.txt",
        "src/main.py", 
        "frontend/package.json",
        "config/config.json"
    ]
    
    required_dirs = [
        "src",
        "frontend", 
        "config",
        "scripts"
    ]
    
    for file_path in required_files:
        exists = Path(file_path).exists()
        results[file_path] = exists
        print(f"  {file_path}: {'✅' if exists else '❌'}")
    
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        results[dir_path] = exists
        print(f"  {dir_path}/: {'✅' if exists else '❌'}")
    
    return results


def check_dependencies() -> Dict[str, bool]:
    """التحقق من المتطلبات المثبتة"""
    print("\n📦 Checking Python dependencies...")
    results = {}
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "aioredis", "websockets", "openai", "anthropic"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            results[package] = True
            print(f"  {package}: ✅")
        except ImportError:
            results[package] = False
            print(f"  {package}: ❌")
    
    return results


def check_environment() -> Dict[str, bool]:
    """التحقق من ملف البيئة"""
    print("\n🔐 Checking environment configuration...")
    results = {}
    
    env_file = Path(".env")
    results['env_file_exists'] = env_file.exists()
    print(f"  .env file: {'✅' if env_file.exists() else '❌'}")
    
    if env_file.exists():
        with open(env_file) as f:
            env_content = f.read()
        
        required_keys = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", 
            "DATABASE_URL", "SECRET_KEY"
        ]
        
        for key in required_keys:
            has_key = key in env_content and not env_content.split(f"{key}=")[1].split('\n')[0].strip() in ['', 'your_key_here']
            results[f'env_{key.lower()}'] = has_key
            print(f"  {key}: {'✅' if has_key else '❌'}")
    
    return results


def check_ports() -> Dict[str, bool]:
    """التحقق من توفر المنافذ"""
    print("\n🔌 Checking port availability...")
    results = {}
    
    required_ports = [8000, 3000, 8765]
    
    for port in required_ports:
        try:
            # Try to bind to the port
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                results[f'port_{port}'] = True
                print(f"  Port {port}: ✅ Available")
        except OSError:
            results[f'port_{port}'] = False
            print(f"  Port {port}: ❌ In use")
    
    return results


async def check_services() -> Dict[str, bool]:
    """التحقق من الخدمات المتشغلة"""
    print("\n🚀 Checking running services...")
    results = {}
    
    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:3000"),
        ("WebSocket", "ws://localhost:8765")
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for name, url in services:
            try:
                if url.startswith('ws://'):
                    # WebSocket check
                    import websockets
                    async with websockets.connect(url):
                        results[name.lower().replace(' ', '_')] = True
                        print(f"  {name}: ✅ Running")
                else:
                    # HTTP check
                    async with session.get(url) as response:
                        if response.status < 400:
                            results[name.lower().replace(' ', '_')] = True
                            print(f"  {name}: ✅ Running")
                        else:
                            results[name.lower().replace(' ', '_')] = False
                            print(f"  {name}: ❌ Error {response.status}")
            except Exception as e:
                results[name.lower().replace(' ', '_')] = False
                print(f"  {name}: ❌ Not accessible")
    
    return results


def check_system_resources() -> Dict[str, bool]:
    """التحقق من موارد النظام"""
    print("\n💻 Checking system resources...")
    results = {}
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_ok = cpu_percent < 80
    results['cpu'] = cpu_ok
    print(f"  CPU Usage: {cpu_percent:.1f}% {'✅' if cpu_ok else '⚠️'}")
    
    # Memory usage
    memory = psutil.virtual_memory()
    memory_ok = memory.percent < 85
    results['memory'] = memory_ok
    print(f"  Memory Usage: {memory.percent:.1f}% {'✅' if memory_ok else '⚠️'}")
    
    # Disk space
    disk = psutil.disk_usage('.')
    disk_ok = disk.percent < 90
    results['disk'] = disk_ok
    print(f"  Disk Usage: {disk.percent:.1f}% {'✅' if disk_ok else '⚠️'}")
    
    return results


def generate_report(all_results: Dict[str, Dict[str, bool]]):
    """إنشاء تقرير شامل"""
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        category_passed = sum(results.values())
        category_total = len(results)
        total_checks += category_total
        passed_checks += category_passed
        
        status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
        print(f"{status} {category.title()}: {category_passed}/{category_total}")
    
    print(f"\n🎯 Overall Score: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("🎉 Perfect! Your system is ready to run AI Teddy Bear!")
    elif passed_checks >= total_checks * 0.8:
        print("👍 Good! Minor issues detected, but should work fine.")
    elif passed_checks >= total_checks * 0.6:
        print("⚠️ Warning! Several issues detected. Check the details above.")
    else:
        print("❌ Critical! Major issues detected. Please fix before running.")
    
    # Save report to file
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform.platform(),
        "python_version": sys.version,
        "results": all_results,
        "score": f"{passed_checks}/{total_checks}",
        "percentage": round(passed_checks/total_checks*100, 1)
    }
    
    with open("health_check_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: health_check_report.json")


async def main():
    """الدالة الرئيسية"""
    print_header()
    
    all_results = {}
    
    # Run all checks
    all_results["system_requirements"] = check_system_requirements()
    all_results["project_structure"] = check_project_structure()
    all_results["dependencies"] = check_dependencies()
    all_results["environment"] = check_environment()
    all_results["ports"] = check_ports()
    all_results["services"] = await check_services()
    all_results["system_resources"] = check_system_resources()
    
    # Generate final report
    generate_report(all_results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Health check interrupted by user.")
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1) 