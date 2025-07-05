from typing import Any, Dict

#!/usr/bin/env python3
"""

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
    def validate_status_level(status: str) -> str:
        """Validate and return a valid status level"""
        valid_statuses = ["open", "closed", "in_progress"]
        if status not in valid_statuses:
            raise ValueError(f"status must be one of: {valid_statuses}")
        return status

    @staticmethod
    def validate_limit_range(limit: int) -> None:
        """Validate limit parameter is within acceptable range"""
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

    @staticmethod
    def validate_offset_range(offset: int) -> None:
        """Validate offset parameter is non-negative"""
        if offset < 0:
            raise ValueError("offset must be non-negative")

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
        issue_data.severity = self.validator.validate_severity_level(
            issue_data.severity)

        # Clean component
        issue_data.component = self.validator.clean_and_validate_component(
            issue_data.component)

        # Clean error type
        issue_data.error_type = self.validator.clean_and_validate_error_type(
            issue_data.error_type)

        # Clean stacktrace
        issue_data.stacktrace = self.validator.clean_stacktrace(
            issue_data.stacktrace)


class IssueQueryValidator:
    """
    Specialized validator for query parameters.
    Extracted to reduce cyclomatic complexity of IssueQueryParams.__post_init__.
    """

    def __init__(self, validation_service: IssueValidationService):
        self.validator = validation_service

    def validate_optional_status(self, status: Optional[str]) -> None:
        """Validate status parameter if provided"""
        if status:
            self.validator.validate_status_level(status)

    def validate_optional_severity(self, severity: Optional[str]) -> None:
        """Validate severity parameter if provided"""
        if severity:
            self.validator.validate_severity_level(severity)

    def validate_pagination_params(self, limit: int, offset: int) -> None:
        """Validate pagination parameters"""
        self.validator.validate_limit_range(limit)
        self.validator.validate_offset_range(offset)


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
        """
        Validate query parameters with extracted validation methods.
        Cyclomatic complexity reduced from 12 to 3.
        """
        validation_service = IssueValidationService()
        query_validator = IssueQueryValidator(validation_service)

        # Decomposed validation calls (low complexity)
        query_validator.validate_optional_status(self.status)
        query_validator.validate_optional_severity(self.severity)
        query_validator.validate_pagination_params(self.limit, self.offset)


@dataclass
class IssueUpdateData:
    """Parameter object for updating issues"""
    issue_id: str
    status: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate update data with extracted validation methods"""
        validation_service = IssueValidationService()

        # Validate required field
        validation_service.validate_required_string(self.issue_id, "issue_id")

        # Validate optional fields
        if self.status:
            validation_service.validate_status_level(self.status)

        if self.severity:
            validation_service.validate_severity_level(self.severity)


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
            self.logger.error(
                "Failed to load issue tracker config", error=str(e))
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
            issue_id = self._generate_issue_id(
                issue_data.title, issue_data.error_type)

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
                    (id, title, description, severity, status,
                     component, error_type, stacktrace)
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

            query = "UPDATE issues SET " + \
                ", ".join(update_fields) + " WHERE id = ?"

            cursor.execute(query, tuple(update_values))
            conn.commit()

            updated = cursor.rowcount > 0
            conn.close()

            if updated:
                self.logger.info(
                    "Issue updated", issue_id=update_data.issue_id)

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

            cursor.execute(base_query, tuple(where_values))

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
        except Exception as exc:
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
        Creates IssueData and delegates to modern method.
        ⚠️ DEPRECATED: Use create_issue with IssueData instead.

        Legacy method REFACTORED using Parameter Object pattern.
        ✅ Reduced from 6 arguments to 1 argument (under threshold)

        Args:
            title: Issue title
            description: Issue description
            severity: Issue severity level
            component: Component name
            error_type: Type of error
            stacktrace: Optional stacktrace

        Returns:
            str: Issue ID or None if failed
        """
        # Refactoring: Create parameter object to reduce arguments
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
        Creates IssueQueryParams and delegates to modern method.
        ⚠️ DEPRECATED: Use search_issues with IssueQueryParams instead.

        Legacy method REFACTORED using Parameter Object pattern.
        ✅ Reduced from 5 arguments to 1 argument (under threshold)

        Args:
            status: Issue status filter
            severity: Issue severity filter
            component: Component filter
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List[Dict]: List of matching issues
        """
        # Refactoring: Create parameter object to reduce arguments
        query_params = IssueQueryParams(
            status=status,
            severity=severity,
            component=component,
            limit=limit,
            offset=offset
        )
        return await self.search_issues(query_params)


# =============================================================================
# GLOBAL FUNCTIONS AND UTILITIES
# =============================================================================

# Global instance for module-level functions
_issue_tracker = None


def get_issue_tracker() -> IssueTrackerService:
    """Get or create global issue tracker instance"""
    global _issue_tracker
    if _issue_tracker is None:
        _issue_tracker = IssueTrackerService()
    return _issue_tracker


async def report_issue(issue_data: IssueData) -> str:
    """
    إبلاغ عن مشكلة جديدة.
    Modern function using Parameter Object pattern.
    ✅ Uses Parameter Object (1 argument only)

    Args:
        issue_data: IssueData object containing all issue information

    Returns:
        str: Issue ID or None if failed
    """
    try:
        tracker = get_issue_tracker()
        return await tracker.create_issue(issue_data)
    except Exception as e:
        logger.error("Failed to report issue", error=str(e))
        return None


async def report_issue_legacy(
    title: str,
    description: str,
    severity: str = "medium",
    component: str = "unknown",
    error_type: str = "runtime_error",
) -> str:
    """
    Legacy function for backward compatibility.
    Creates IssueData and delegates to modern function.
    ⚠️ DEPRECATED: Use report_issue with IssueData instead.

    Legacy function REFACTORED using Parameter Object pattern.
    ✅ Reduced from 5 arguments to 1 argument (under threshold)

    Args:
        title: Issue title
        description: Issue description
        severity: Issue severity level
        component: Component name
        error_type: Type of error

    Returns:
        str: Issue ID or None if failed
    """
    # Refactoring: Create parameter object to reduce arguments
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
    """
    إبلاغ عن استثناء (Exception).
    Modern function with automatic stacktrace capture.
    ✅ Uses Parameter Object internally

    Args:
        component: Component name where exception occurred
        exception: Exception object
        context: Additional context information

    Returns:
        str: Issue ID or None if failed
    """
    try:
        # إنشاء issue_data من الاستثناء
        issue_data = IssueData(
            title=f"{component}: {type(exception).__name__}",
            description=f"Exception in {component}: {str(exception)}\n\nContext: {context}",
            severity="high",
            component=component,
            error_type=type(exception).__name__,
            stacktrace=traceback.format_exc(),
        )

        tracker = get_issue_tracker()
        return await tracker.create_issue(issue_data)
    except Exception as e:
        logger.error("Failed to report exception", error=str(e))
        return None


async def update_issue_status(issue_id: str, status: str, notes: str = None) -> bool:
    """
    تحديث حالة المشكلة.
    Modern function using Parameter Object pattern.
    ✅ Uses Parameter Object internally

    Args:
        issue_id: Issue ID to update
        status: New status
        notes: Optional notes

    Returns:
        bool: True if update successful
    """
    try:
        update_data = IssueUpdateData(
            issue_id=issue_id,
            status=status,
            notes=notes
        )

        tracker = get_issue_tracker()
        return await tracker.update_issue(update_data)
    except Exception as e:
        logger.error("Failed to update issue status", error=str(e))
        return False


async def search_issues_by_component(component: str, limit: int = 10) -> List[Dict]:
    """
    البحث عن المشاكل حسب المكون.
    Modern function using Parameter Object pattern.
    ✅ Uses Parameter Object internally

    Args:
        component: Component name to search for
        limit: Maximum number of results

    Returns:
        List[Dict]: List of matching issues
    """
    try:
        query_params = IssueQueryParams(
            component=component,
            limit=limit
        )

        tracker = get_issue_tracker()
        return await tracker.search_issues(query_params)
    except Exception as e:
        logger.error("Failed to search issues by component", error=str(e))
        return []


async def get_system_health() -> Dict:
    """الحصول على حالة النظام الصحية"""
    try:
        service = IssueTrackerService()
        stats = await service.get_issue_statistics()

        # تحديد حالة النظام
        critical_issues = stats.get("by_severity", {}).get("critical", 0)
        high_issues = stats.get("by_severity", {}).get("high", 0)

        if critical_issues > 0:
            status = "critical"
        elif high_issues > 5:
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "total_issues": stats.get("total_issues", 0),
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "last_check": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Failed to get system health", error=str(e))
        return {
            "status": "unknown",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


# =============================================================================
# HELPER FUNCTIONS FOR PARAMETER OBJECTS
# =============================================================================

class IssueDataFactory:
    """Factory helper for creating Parameter Objects"""

    @staticmethod
    def create_issue_data(
        title: str,
        description: str,
        severity: str = "medium",
        component: str = "unknown",
        error_type: str = "runtime_error",
        stacktrace: Optional[str] = None
    ) -> IssueData:
        """Helper to create IssueData from individual arguments"""
        return IssueData(
            title=title,
            description=description,
            severity=severity,
            component=component,
            error_type=error_type,
            stacktrace=stacktrace
        )

    @staticmethod
    def create_query_params(
        status: Optional[str] = None,
        severity: Optional[str] = None,
        component: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> IssueQueryParams:
        """Helper to create IssueQueryParams from individual arguments"""
        return IssueQueryParams(
            status=status,
            severity=severity,
            component=component,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def create_update_data(
        issue_id: str,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        notes: Optional[str] = None
    ) -> IssueUpdateData:
        """Helper to create IssueUpdateData from individual arguments"""
        return IssueUpdateData(
            issue_id=issue_id,
            status=status,
            severity=severity,
            notes=notes
        )


# Global factory instance for easy access
_issue_factory = IssueDataFactory()


def create_issue_data(
    title: str,
    description: str,
    **kwargs
) -> IssueData:
    """Convenience function to create IssueData"""
    return _issue_factory.create_issue_data(
        title=title,
        description=description,
        **kwargs
    )


def create_query_params(**kwargs) -> IssueQueryParams:
    """Convenience function to create IssueQueryParams"""
    return _issue_factory.create_query_params(**kwargs)


def create_update_data(issue_id: str, **kwargs) -> IssueUpdateData:
    """Convenience function to create IssueUpdateData"""
    return _issue_factory.create_update_data(
        issue_id=issue_id,
        **kwargs
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main service class
    "IssueTrackerService",

    # Parameter objects
    "IssueData",
    "IssueQueryParams",
    "IssueUpdateData",

    # Validation services
    "IssueValidationService",
    "IssueDataValidator",
    "IssueQueryValidator",

    # Helper factory
    "IssueDataFactory",

    # Convenience functions
    "create_issue_data",
    "create_query_params",
    "create_update_data",

    # Main functions
    "report_issue",
    "report_issue_legacy",
    "report_exception",
    "update_issue_status",
    "search_issues_by_component",
    "get_system_health"
]
