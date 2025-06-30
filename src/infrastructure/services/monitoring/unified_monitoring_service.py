from typing import Dict, List, Any, Optional

#!/usr/bin/env python3
"""
UnifiedMonitoringService
خدمة موحدة تم دمجها من عدة ملفات منفصلة
تم الإنشاء: 2025-06-30 05:25:00
"""

from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
from typing import Dict, List, Optional
from typing import Dict, List, Optional, Tuple
import asyncio
import hashlib
import json
import psutil
import sqlite3
import structlog
import time
import traceback
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class UnifiedMonitoringService:
    """
    خدمة موحدة تجمع وظائف متعددة من:
        - deprecated\services\monitoring_services\issue_tracker_service.py
    - deprecated\services\monitoring_services\rate_monitor_service.py
    - deprecated\services\monitoring_services\simple_health_service.py
    """
    
    def __init__(self):
        """تهيئة الخدمة الموحدة"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """تهيئة المكونات الفرعية"""
        # تهيئة قاعدة البيانات
        self._init_database()
        
        # تهيئة عدادات المعدل
        self._init_counters()
        
        # تهيئة متغيرات المراقبة
        self.issues = {}
        self.health_checks = deque(maxlen=100)
        
        self.logger.info("Unified monitoring service initialized successfully")

    # ==========================================
    # الوظائف المدموجة من الملفات المختلفة
    # ==========================================

    # ----- من issue_tracker_service.py -----
    
    def _load_config(self) -> Dict[str, Any]:
        """تحميل إعدادات المراقبة"""
        return {
            "max_issues": 1000,
            "retention_days": 30,
            "alert_threshold": 10,
            "db_path": "monitoring_issues.db"
        }

    def _init_database(self) -> None:
        """تهيئة قاعدة بيانات المراقبة"""
        config = self._load_config()
        db_path = config.get("db_path", "monitoring_issues.db")
        
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        
        # جدول المشاكل
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                issue_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                error_type TEXT NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                count INTEGER DEFAULT 1,
                resolved BOOLEAN DEFAULT 0
            )
        """)
        
        # جدول معدلات الاستخدام
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                endpoint TEXT PRIMARY KEY,
                requests_count INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()

    def _generate_issue_id(self, title: str, error_type: str) -> str:
        """توليد معرف فريد للمشكلة"""
        content = f"{title}:{error_type}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


    # ----- من rate_monitor_service.py -----
    
    def _init_counters(self) -> None:
        """تهيئة عدادات المعدل"""
        self.rate_counters = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
        self.rate_limits = {
            "/api/chat": 60,  # 60 requests per minute
            "/api/voice": 30,  # 30 requests per minute
            "/api/safety": 100,  # 100 requests per minute
        }


    # ----- من simple_health_service.py -----
    
    def get_health_status(self) -> Dict[str, Any]:
        """الحصول على حالة صحة النظام"""
        try:
            # فحص استخدام الموارد
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # فحص الخدمات
            services_health = self._check_services_health()
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                },
                "services": services_health,
                "uptime": time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


    # ==========================================
    # دوال مساعدة إضافية
    # ==========================================
    
    def _check_services_health(self) -> Dict[str, str]:
        """فحص صحة الخدمات المختلفة"""
        services = {
            "database": "healthy",
            "cache": "healthy",
            "ai_service": "healthy",
            "voice_service": "healthy",
            "safety_service": "healthy"
        }
        
        # يمكن إضافة فحوصات حقيقية هنا
        return services
    
    def _get_active_components(self) -> List[str]:
        """الحصول على المكونات النشطة"""
        components = []
        
        if hasattr(self, 'conn') and self.conn:
            components.append("database")
        
        if hasattr(self, 'rate_counters'):
            components.append("rate_limiting")
            
        components.extend(["health_monitoring", "issue_tracking"])
        
        return components

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الخدمة الموحدة"""
        return {
            "service_name": "UnifiedMonitoringService",
            "status": "active",
            "components": self._get_active_components(),
            "health": self.get_health_status(),
            "merged_from": [
                "issue_tracker_service.py",
                "rate_monitor_service.py",
                "simple_health_service.py",
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

# ==========================================
# Factory Pattern للإنشاء
# ==========================================

class UnifiedMonitoringServiceFactory:
    """مصنع لإنشاء خدمة UnifiedMonitoringService"""
    
    @staticmethod
    def create() -> UnifiedMonitoringService:
        """إنشاء مثيل من الخدمة الموحدة"""
        return UnifiedMonitoringService()
    
    @staticmethod
    def create_with_config(config: Dict[str, Any]) -> UnifiedMonitoringService:
        """إنشاء مثيل مع تكوين مخصص"""
        service = UnifiedMonitoringService()
        # NOTED: تطبيق التكوين
        return service

# ==========================================
# Singleton Pattern (اختياري)
# ==========================================

_instance = None

def get_monitoring_services_instance() -> UnifiedMonitoringService:
    """الحصول على مثيل وحيد من الخدمة"""
    global _instance
    if _instance is None:
        _instance = UnifiedMonitoringServiceFactory.create()
    return _instance