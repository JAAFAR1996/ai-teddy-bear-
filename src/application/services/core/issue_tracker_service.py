from typing import Any, Dict, Optional, List
from pathlib import Path
import json
import sqlite3
import structlog
from dataclasses import dataclass

from .issue_creator import IssueCreator
from .issue_updater import IssueUpdater
from .issue_searcher import IssueSearcher
from .issue_validator import IssueValidationService, IssueDataValidator, IssueQueryValidator

logger = structlog.get_logger()


@dataclass
class IssueData:
    title: str
    description: str
    severity: str = "medium"
    component: str = "unknown"
    error_type: str = "runtime_error"
    stacktrace: Optional[str] = None

    def __post_init__(self):
        validation_service = IssueValidationService()
        issue_validator = IssueDataValidator(validation_service)
        issue_validator.validate_required_fields(self.title, self.description)
        issue_validator.validate_and_clean_optional_fields(self)


@dataclass
class IssueQueryParams:
    status: Optional[str] = None
    severity: Optional[str] = None
    component: Optional[str] = None
    limit: int = 10
    offset: int = 0

    def __post_init__(self):
        validation_service = IssueValidationService()
        query_validator = IssueQueryValidator(validation_service)
        query_validator.validate_optional_status(self.status)
        query_validator.validate_optional_severity(self.severity)
        query_validator.validate_pagination_params(self.limit, self.offset)


@dataclass
class IssueUpdateData:
    issue_id: str
    status: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        validation_service = IssueValidationService()
        validation_service.validate_required_string(self.issue_id, "issue_id")
        if self.status:
            validation_service.validate_status_level(self.status)
        if self.severity:
            validation_service.validate_severity_level(self.severity)


class IssueTrackerService:
    def __init__(self, config_path: str = "config/staging_config.json"):
        self.logger = logger.bind(service="issue_tracker")
        self.config_path = config_path
        self._load_config()
        self._init_database()
        self.creator = IssueCreator(self.db_path)
        self.updater = IssueUpdater(self.db_path)
        self.searcher = IssueSearcher(self.db_path)

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            monitoring_config = config.get("MONITORING_CONFIG", {})
            self.config = {
                "enable_issue_tracking": monitoring_config.get("enable_issue_tracking", True),
                "alert_email": monitoring_config.get("alert_email", "admin@aiteddybear.com"),
                "log_retention_days": monitoring_config.get("log_retention_days", 30),
            }
        except Exception as e:
            self.logger.error(
                "Failed to load issue tracker config", error=str(e))
            self.config = {"enable_issue_tracking": True}

    def _init_database(self):
        try:
            self.db_path = "logs/issues.db"
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT,
                    severity TEXT DEFAULT 'medium', status TEXT DEFAULT 'open',
                    component TEXT, error_type TEXT, stacktrace TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    occurrence_count INTEGER DEFAULT 1,
                    last_occurrence DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)
            conn.commit()
            conn.close()
            self.logger.info("Issue tracker database initialized")
        except Exception as e:
            self.logger.error("Failed to initialize database", error=str(e))

    async def create_issue(self, issue_data: IssueData) -> str:
        return await self.creator.create(issue_data)

    async def update_issue(self, update_data: IssueUpdateData) -> bool:
        return await self.updater.update(update_data)

    async def search_issues(self, query_params: IssueQueryParams) -> List[Dict]:
        return await self.searcher.search(query_params)

    async def get_issue_statistics(self) -> Dict:
        return await self.searcher.get_statistics()
