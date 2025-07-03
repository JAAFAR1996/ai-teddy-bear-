from typing import Any, Dict

#!/usr/bin/env python3
"""
🐛 Issue Tracker Service - نظام تتبع الأخطاء والمشاكل
تسجيل وتتبع الأخطاء مع Stacktrace وسجلات تفصيلية
"""

import hashlib
import json
import sqlite3
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

import structlog

# إعداد logger
logger = structlog.get_logger(__name__)


# =============================================================================
# VALIDATION SERVICES (EXTRACT FUNCTION REFACTORING)
# =============================================================================

class IssueValidationService:
    """
    Extracted validation logic to reduce cyclomatic complexity.
    Each validation method has a single responsibility.
    """
    
    @staticmethod
    def validate_required_string(value: str, field_name: str) -> None:
        """Validate that a field is a non-empty string"""
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} must be a non-empty string")
    
    @staticmethod
    def validate_severity_level(severity: str) -> str:
        """Validate and return a valid severity level"""
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            raise ValueError(f"severity must be one of: {valid_severities}")
        return severity
    
    @staticmethod
    def clean_and_validate_component(component: str) -> str:
        """Clean and validate component name"""
        if not component or not isinstance(component, str):
            return "unknown"
        return component.strip().lower()
    
    @staticmethod
    def clean_and_validate_error_type(error_type: str) -> str:
        """Clean and validate error type"""
        if not error_type or not isinstance(error_type, str):
            return "runtime_error"
        return error_type.strip()
    
    @staticmethod
    def clean_stacktrace(stacktrace: Optional[str]) -> Optional[str]:
        """Clean and validate stacktrace"""
        if stacktrace and not isinstance(stacktrace, str):
            return str(stacktrace)
        return stacktrace


class IssueDataValidator:
    """
    Specialized validator for issue data.
    Decomposed from complex __post_init__ method.
    """
    
    def __init__(self, validation_service: IssueValidationService):
        self.validator = validation_service
    
    def validate_required_fields(self, title: str, description: str) -> None:
        """Validate required string fields"""
        self.validator.validate_required_string(title, "title")
        self.validator.validate_required_string(description, "description")
    
    def validate_and_clean_optional_fields(self, issue_data) -> None:
        """Validate and clean optional fields"""
        # Validate severity
        issue_data.severity = self.validator.validate_severity_level(issue_data.severity)
        
        # Clean component
        issue_data.component = self.validator.clean_and_validate_component(issue_data.component)
        
        # Clean error type
        issue_data.error_type = self.validator.clean_and_validate_error_type(issue_data.error_type)
        
        # Clean stacktrace
        issue_data.stacktrace = self.validator.clean_stacktrace(issue_data.stacktrace)


# =============================================================================
# PARAMETER OBJECTS (IMPROVED WITH LOW COMPLEXITY VALIDATION)
# =============================================================================

@dataclass
class IssueData:
    """
    Parameter object for issue creation and reporting.
    Encapsulates all data needed to create or report an issue.
    """
    title: str
    description: str
    severity: str = "medium"
    component: str = "unknown"
    error_type: str = "runtime_error"
    stacktrace: Optional[str] = None
    
    def __post_init__(self):
        """
        Validate issue data with extracted validation methods.
        Cyclomatic complexity reduced from 17 to 2.
        """
        validation_service = IssueValidationService()
        issue_validator = IssueDataValidator(validation_service)
        
        # Decomposed validation calls (low complexity)
        issue_validator.validate_required_fields(self.title, self.description)
        issue_validator.validate_and_clean_optional_fields(self)


@dataclass 
class IssueQueryParams:
    """Parameter object for issue queries to reduce argument count"""
    status: Optional[str] = None
    severity: Optional[str] = None
    component: Optional[str] = None
    limit: int = 10
    offset: int = 0
    
    def __post_init__(self):
        """Validate query parameters"""
        if self.status and self.status not in ["open", "closed", "in_progress"]:
            raise ValueError("status must be one of: open, closed, in_progress")
        
        if self.severity and self.severity not in ["low", "medium", "high", "critical"]:
            raise ValueError("severity must be one of: low, medium, high, critical")
        
        if self.limit < 1 or self.limit > 100:
            raise ValueError("limit must be between 1 and 100")
        
        if self.offset < 0:
            raise ValueError("offset must be non-negative")


@dataclass
class IssueUpdateData:
    """Parameter object for updating issues"""
    issue_id: str
    status: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate update data"""
        IssueValidationService.validate_required_string(self.issue_id, "issue_id")
        
        if self.status and self.status not in ["open", "closed", "in_progress"]:
            raise ValueError("status must be one of: open, closed, in_progress")
        
        if self.severity and self.severity not in ["low", "medium", "high", "critical"]:
            raise ValueError("severity must be one of: low, medium, high, critical")


class IssueTrackerService:
    """
    🐛 نظام تتبع الأخطاء والمشاكل

    الميزات:
    - تسجيل تلقائي للأخطاء مع Stacktrace
    - تجميع الأخطاء المتشابهة
    - تتبع حالة المشاكل
    - إحصائيات تفصيلية
    """

    def __init__(self, config_path: str = "config/staging_config.json"):
        self.logger = logger.bind(service="issue_tracker")
        self.config_path = config_path
        self._load_config()
        self._init_database()

    def _load_config(self) -> Any:
        """تحميل إعدادات تتبع الأخطاء"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            monitoring_config = config.get("MONITORING_CONFIG", {})

            self.config = {
                "enable_issue_tracking": monitoring_config.get(
                    "enable_issue_tracking", True
                ),
                "alert_email": monitoring_config.get(
                    "alert_email", "admin@aiteddybear.com"
                ),
                "log_retention_days": monitoring_config.get("log_retention_days", 30),
            }

        except Exception as e:
            self.logger.error("Failed to load issue tracker config", error=str(e))
            self.config = {"enable_issue_tracking": True}

    def _init_database(self) -> Any:
        """تهيئة قاعدة بيانات تتبع الأخطاء"""
        try:
            self.db_path = "logs/issues.db"
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    component TEXT,
                    error_type TEXT,
                    stacktrace TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    occurrence_count INTEGER DEFAULT 1,
                    last_occurrence DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """
            )

            conn.commit()
            conn.close()

            self.logger.info("Issue tracker database initialized")

        except Exception as e:
            self.logger.error(
                "Failed to initialize issue tracker database", error=str(e)
            )

    async def create_issue(self, issue_data: IssueData) -> str:
        """
        إنشاء تقرير مشكلة جديد.
        Refactored to use parameter object pattern.
        
        Args:
            issue_data: IssueData object containing all issue information
            
        Returns:
            str: Issue ID or None if failed
        """
        try:
            # إنشاء ID فريد للمشكلة
            issue_id = self._generate_issue_id(issue_data.title, issue_data.error_type)

            # حفظ في قاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # فحص إذا كانت المشكلة موجودة مسبقاً
            cursor.execute(
                "SELECT occurrence_count FROM issues WHERE id = ?", (issue_id,)
            )
            existing = cursor.fetchone()

            if existing:
                # تحديث عدد التكرارات
                cursor.execute(
                    """
                    UPDATE issues 
                    SET occurrence_count = occurrence_count + 1,
                        last_occurrence = ?
                    WHERE id = ?
                """,
                    (datetime.utcnow(), issue_id),
                )
            else:
                # إدراج مشكلة جديدة
                cursor.execute(
                    """
                    INSERT INTO issues 
                    (id, title, description, severity, status, component, error_type, stacktrace)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        issue_id,
                        issue_data.title,
                        issue_data.description,
                        issue_data.severity,
                        "open",
                        issue_data.component,
                        issue_data.error_type,
                        issue_data.stacktrace or "",
                    ),
                )

            conn.commit()
            conn.close()

            self.logger.info(
                "Issue created",
                issue_id=issue_id,
                severity=issue_data.severity,
                component=issue_data.component,
            )

            return issue_id

        except Exception as e:
            self.logger.error("Failed to create issue", error=str(e))
            return None

    async def update_issue(self, update_data: IssueUpdateData) -> bool:
        """
        تحديث بيانات مشكلة موجودة.
        Refactored to use parameter object pattern.
        
        Args:
            update_data: IssueUpdateData object containing update information
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = []
            update_values = []
            
            if update_data.status:
                update_fields.append("status = ?")
                update_values.append(update_data.status)
            
            if update_data.severity:
                update_fields.append("severity = ?")
                update_values.append(update_data.severity)
            
            if update_data.notes:
                update_fields.append("notes = ?")
                update_values.append(update_data.notes)
            
            if not update_fields:
                return False  # Nothing to update
            
            # Add issue_id for WHERE clause
            update_values.append(update_data.issue_id)
            
            query = f"""
                UPDATE issues 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            cursor.execute(query, update_values)
            conn.commit()
            
            updated = cursor.rowcount > 0
            conn.close()
            
            if updated:
                self.logger.info("Issue updated", issue_id=update_data.issue_id)
            
            return updated

        except Exception as e:
            self.logger.error("Failed to update issue", error=str(e))
            return False

    async def search_issues(self, query_params: IssueQueryParams) -> List[Dict]:
        """
        البحث في المشاكل بناءً على المعايير المحددة.
        Refactored to use parameter object pattern.
        
        Args:
            query_params: IssueQueryParams object containing search criteria
            
        Returns:
            List[Dict]: List of matching issues
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic WHERE clause
            where_conditions = []
            where_values = []
            
            if query_params.status:
                where_conditions.append("status = ?")
                where_values.append(query_params.status)
            
            if query_params.severity:
                where_conditions.append("severity = ?")
                where_values.append(query_params.severity)
            
            if query_params.component:
                where_conditions.append("component = ?")
                where_values.append(query_params.component)
            
            # Build final query
            base_query = """
                SELECT id, title, description, severity, status, component, 
                       error_type, timestamp, occurrence_count
                FROM issues
            """
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            where_values.extend([query_params.limit, query_params.offset])
            
            cursor.execute(base_query, where_values)
            
            columns = [desc[0] for desc in cursor.description]
            issues = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            return issues

        except Exception as e:
            self.logger.error("Failed to search issues", error=str(e))
            return []

    def _generate_issue_id(self, title: str, error_type: str) -> str:
        """إنشاء ID فريق للمشكلة"""
        try:
            content = f"{title}:{error_type}"
            hash_object = hashlib.md5(content.encode())
            return f"ISS-{hash_object.hexdigest()[:8].upper()}"
        except Exception:
            return f"ISS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    async def get_issue_statistics(self) -> Dict:
        """الحصول على إحصائيات المشاكل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_issues,
                    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_issues,
                    SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_issues
                FROM issues
            """
            )

            stats = cursor.fetchone()

            cursor.execute(
                """
                SELECT component, COUNT(*) as count
                FROM issues 
                WHERE status = 'open'
                GROUP BY component
                ORDER BY count DESC
                LIMIT 5
            """
            )

            component_stats = cursor.fetchall()

            conn.close()

            return {
                "total_issues": stats[0] if stats else 0,
                "open_issues": stats[1] if stats else 0,
                "critical_issues": stats[2] if stats else 0,
                "by_component": [
                    {"component": comp, "count": count}
                    for comp, count in component_stats
                ],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error("Failed to get issue statistics", error=str(e))
            return {"error": str(e)}

    # =============================================================================
    # LEGACY COMPATIBILITY METHODS (Reduced Argument Count)
    # =============================================================================

    async def create_issue_legacy(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        component: str = "unknown",
        error_type: str = "runtime_error",
        stacktrace: str = None,
    ) -> str:
        """
        Legacy method for backward compatibility.
        Creates IssueData and delegates to new method.
        ⚠️ DEPRECATED: Use create_issue with IssueData instead.
        """
        issue_data = IssueData(
            title=title,
            description=description,
            severity=severity,
            component=component,
            error_type=error_type,
            stacktrace=stacktrace
        )
        return await self.create_issue(issue_data)

    async def search_issues_legacy(
        self,
        status: str = None,
        severity: str = None,
        component: str = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        Legacy method for backward compatibility.
        ⚠️ DEPRECATED: Use search_issues with IssueQueryParams instead.
        """
        query_params = IssueQueryParams(
            status=status,
            severity=severity,
            component=component,
            limit=limit,
            offset=offset
        )
        return await self.search_issues(query_params)


# مثيل نظام تتبع الأخطاء العام
issue_tracker = IssueTrackerService()


# =============================================================================
# HELPER FUNCTIONS (Refactored with Parameter Objects)
# =============================================================================

async def report_issue(issue_data: IssueData) -> str:
    """
    تسجيل مشكلة جديدة.
    Refactored to use parameter object pattern.
    
    Args:
        issue_data: IssueData object containing all issue information
        
    Returns:
        str: Issue ID or None if failed
    """
    return await issue_tracker.create_issue(issue_data)


async def report_issue_legacy(
    title: str,
    description: str,
    severity: str = "medium",
    component: str = "unknown",
    error_type: str = "runtime_error",
) -> str:
    """
    Legacy function for backward compatibility.
    Creates IssueData and delegates to new function.
    ⚠️ DEPRECATED: Use report_issue with IssueData instead.
    """
    issue_data = IssueData(
        title=title,
        description=description,
        severity=severity,
        component=component,
        error_type=error_type
    )
    return await report_issue(issue_data)


async def report_exception(
    component: str, exception: Exception, context: str = ""
) -> str:
    """تسجيل استثناء مع stacktrace"""
    stacktrace = traceback.format_exc()

    issue_data = IssueData(
        title=f"{component}: {type(exception).__name__}",
        description=f"{str(exception)}\n\nContext: {context}",
        severity="high",
        component=component,
        error_type=type(exception).__name__,
        stacktrace=stacktrace
    )
    
    return await issue_tracker.create_issue(issue_data)


async def update_issue_status(issue_id: str, status: str, notes: str = None) -> bool:
    """تحديث حالة المشكلة"""
    update_data = IssueUpdateData(
        issue_id=issue_id,
        status=status,
        notes=notes
    )
    return await issue_tracker.update_issue(update_data)


async def search_issues_by_component(component: str, limit: int = 10) -> List[Dict]:
    """البحث في المشاكل حسب المكون"""
    query_params = IssueQueryParams(
        component=component,
        limit=limit
    )
    return await issue_tracker.search_issues(query_params)


async def get_system_health() -> Dict:
    """الحصول على حالة النظام"""
    return await issue_tracker.get_issue_statistics()
