"""
Dashboard Orchestrator
=====================

Main orchestrator for parent dashboard operations.
Coordinates between domain services and infrastructure components.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.domain.parentdashboard import (
    AccessControlService,
    AnalyticsDomainService,
    ChildProfile,
    ContentAnalysisService,
    ParentalControl,
    ParentUser,
)
from src.infrastructure.persistence.child_repository import ChildRepository
from src.infrastructure.persistence.conversation_repository import ConversationRepository


class DashboardOrchestrator:
    """
    Main orchestrator for Parent Dashboard operations.
    Follows Clean Architecture principles by orchestrating domain services.
    """

    def __init__(
        self,
        child_repository: ChildRepository,
        conversation_repository: ConversationRepository,
        analytics_service: AnalyticsDomainService,
        access_service: AccessControlService,
        content_service: ContentAnalysisService,
    ):
        self.child_repository = child_repository
        self.conversation_repository = conversation_repository
        self.analytics_service = analytics_service
        self.access_service = access_service
        self.content_service = content_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_parent_account(
        self, email: str, name: str, phone: Optional[str] = None, timezone: str = "UTC"
    ) -> ParentUser:
        """Create a new parent account with validation"""

        # Validate email format
        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        # Create parent user
        parent = ParentUser(email=email, name=name, phone=phone, timezone=timezone)

        # Validate business rules
        if not parent.validate_email_format():
            raise ValueError("Email validation failed")

        self.logger.info(f"Created parent account for {email}")
        return parent

    async def create_child_profile(
        self, parent_id: str, name: str, age: int, interests: List[str], language: str = "en"
    ) -> ChildProfile:
        """Create child profile with age-appropriate defaults"""

        # Validate age
        if not 3 <= age <= 17:
            raise ValueError("Child age must be between 3 and 17")

        # Create child profile
        child = ChildProfile(
            parent_id=parent_id,
            name=name,
            age=age,
            language_preference=language,
            learning_level=self._determine_learning_level(age),
        )

        # Filter age-appropriate interests
        child.update_interests(interests)

        # Set default parental controls
        default_controls = self._create_default_controls(child)
        child.parental_controls = default_controls.__dict__

        self.logger.info(f"Created child profile for {name}, age {age}")
        return child

    async def update_parental_controls(self, child_id: str, controls_data: Dict[str, Any]) -> bool:
        """Update parental controls with validation"""

        try:
            # Create controls object
            controls = ParentalControl(child_id=child_id, **controls_data)

            # Validate using domain service
            errors = self.access_service.validate_parental_controls(controls)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")

            # Additional business validation
            child = await self.child_repository.get_by_id(child_id)
            if child:
                # Age-appropriate validation
                if not self._validate_controls_for_age(controls, child.age):
                    raise ValueError("Controls not appropriate for child's age")

            self.logger.info(f"Updated parental controls for child {child_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating parental controls: {e}")
            return False

    async def get_dashboard_data(self, parent_id: str, include_analytics: bool = True) -> Dict[str, Any]:
        """Get comprehensive dashboard data for parent"""

        try:
            dashboard_data = {
                "parent_info": {},
                "children": [],
                "alerts": [],
                "summary_stats": {},
                "analytics": {} if include_analytics else None,
            }

            # Get parent info (would come from parent repository)
            dashboard_data["parent_info"] = {"id": parent_id, "timezone": "UTC"}  # Would come from database

            # Get children for parent
            children = await self.child_repository.get_children_by_parent(parent_id)

            for child in children:
                child_data = {
                    "id": child.id,
                    "name": child.name,
                    "age": child.age,
                    "is_active": child.is_active,
                    "current_status": await self._get_child_current_status(child.id),
                }

                if include_analytics:
                    # Get analytics for child
                    logs = await self.conversation_repository.get_by_child_id(
                        child.id, start_date=datetime.now() - timedelta(days=7)
                    )

                    analytics = self.analytics_service.calculate_analytics(logs)
                    child_data["weekly_analytics"] = analytics.__dict__

                dashboard_data["children"].append(child_data)

            # Get summary statistics
            dashboard_data["summary_stats"] = await self._calculate_summary_stats(children)

            return dashboard_data

        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {}

    async def check_child_access(self, child_id: str) -> Dict[str, Any]:
        """Check if child can access the system"""

        try:
            child = await self.child_repository.get_by_id(child_id)
            if not child or not child.is_active:
                return {"allowed": False, "reason": "Child profile not found or inactive"}

            # Get parental controls
            controls = ParentalControl(child_id=child_id, **(child.parental_controls or {}))

            # Check access schedule
            # Note: In real implementation, would get schedules from database
            schedules = []  # Would load from database

            is_allowed, reason = self.access_service.check_access_allowed(schedules)

            if not is_allowed:
                return {"allowed": False, "reason": reason}

            # Check time limits
            # Would calculate actual usage from logs
            usage_stats = self.access_service.calculate_time_usage_stats(
                controls, daily_minutes_used=0, session_minutes_used=0  # Would calculate from today's logs
            )

            if self.access_service.should_block_access_time_limit(usage_stats):
                return {"allowed": False, "reason": "Time limit exceeded", "usage_stats": usage_stats.__dict__}

            return {
                "allowed": True,
                "remaining_time": usage_stats.get_remaining_daily_minutes(),
                "warning_threshold": usage_stats.warning_threshold,
            }

        except Exception as e:
            self.logger.error(f"Error checking child access: {e}")
            return {"allowed": False, "reason": "System error"}

    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        return "@" in email and "." in email.split("@")[1]

    def _determine_learning_level(self, age: int) -> str:
        """Determine learning level based on age"""
        if age < 5:
            return "preschool"
        elif age < 8:
            return "early_elementary"
        elif age < 11:
            return "elementary"
        elif age < 14:
            return "middle_school"
        else:
            return "high_school"

    def _create_default_controls(self, child: ChildProfile) -> ParentalControl:
        """Create age-appropriate default parental controls"""

        # Get age-appropriate limits
        daily_limit = child.get_recommended_daily_limit()
        session_limit = min(daily_limit // 2, 30)  # Half of daily or 30 min max

        return ParentalControl(
            child_id=child.id,
            max_daily_minutes=daily_limit,
            max_session_minutes=session_limit,
            content_filter_level="strict" if child.age < 10 else "moderate",
        )

    def _validate_controls_for_age(self, controls: ParentalControl, age: int) -> bool:
        """Validate that controls are appropriate for child's age"""

        # Stricter limits for younger children
        if age < 8 and controls.max_daily_minutes > 60:
            return False

        if age < 12 and controls.content_filter_level == "relaxed":
            return False

        return True

    async def _get_child_current_status(self, child_id: str) -> Dict[str, Any]:
        """Get current status for a child"""

        # Would check active sessions, etc.
        return {"is_online": False, "last_activity": None, "current_session_minutes": 0}

    async def _calculate_summary_stats(self, children: List[ChildProfile]) -> Dict[str, Any]:
        """Calculate summary statistics across all children"""

        return {
            "total_children": len(children),
            "active_children": len([c for c in children if c.is_active]),
            "total_alerts": 0,  # Would query from alerts table
            "unread_alerts": 0,
        }
