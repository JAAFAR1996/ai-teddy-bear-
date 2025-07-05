"""
Access Control Domain Service
============================

Domain service for managing access control and parental controls.
"""

from datetime import datetime, time
from typing import List, Optional, Tuple

from ..models.control_models import (
    AccessSchedule,
    AccessScheduleType,
    ParentalControl,
    TimeUsageStats,
)


class AccessControlService:
    """Domain service for access control logic"""

    def check_access_allowed(
        self, schedules: List[AccessSchedule], current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if access is currently allowed"""

        if current_time is None:
            current_time = datetime.now()

        current_day = current_time.weekday()
        current_time_only = current_time.time()

        if not schedules:
            # No schedule means always allowed
            return True, None

        # Check if current time is within any allowed period
        for schedule in schedules:
            if (
                schedule.enabled
                and schedule.day_of_week == current_day
                and schedule.start_time <= current_time_only <= schedule.end_time
            ):
                return True, None

        # Not within allowed time
        next_allowed = self._get_next_allowed_time(schedules, current_time)
        return False, f"Access not allowed. Next available: {next_allowed}"

    def validate_parental_controls(
            self, controls: ParentalControl) -> List[str]:
        """Validate parental control settings and return errors"""
        errors = []

        try:
            # This will trigger validation in __post_init__
            controls.validate_time_limits()
            controls.validate_topics()
        except ValueError as e:
            errors.append(str(e))

        return errors

    def calculate_time_usage_stats(
        self,
        controls: ParentalControl,
        daily_minutes_used: int,
        session_minutes_used: int,
    ) -> TimeUsageStats:
        """Calculate time usage statistics"""

        warning_threshold = controls.get_warning_threshold_minutes()

        return TimeUsageStats(
            daily_minutes_used=daily_minutes_used,
            session_minutes_used=session_minutes_used,
            daily_limit=controls.max_daily_minutes,
            session_limit=controls.max_session_minutes,
            warning_threshold=warning_threshold,
        )

    def should_trigger_time_warning(self, usage_stats: TimeUsageStats) -> bool:
        """Check if time warning should be triggered"""
        return usage_stats.is_approaching_daily_limit()

    def should_block_access_time_limit(
            self, usage_stats: TimeUsageStats) -> bool:
        """Check if access should be blocked due to time limits"""
        return (
            usage_stats.is_daily_limit_exceeded()
            or usage_stats.is_session_limit_exceeded()
        )

    def is_topic_allowed(self, controls: ParentalControl, topic: str) -> bool:
        """Check if topic is allowed based on controls"""
        return controls.is_topic_allowed(topic)

    def should_alert_for_topic(
            self,
            controls: ParentalControl,
            topic: str) -> bool:
        """Check if should send alert for this topic"""
        return controls.should_alert_for_topic(topic)

    def create_default_schedule(
        self, child_id: str, schedule_type: AccessScheduleType
    ) -> List[AccessSchedule]:
        """Create default access schedule based on type"""

        schedules = []
        default_config = schedule_type.get_default_schedule()

        for config in default_config:
            schedule = AccessSchedule(
                child_id=child_id,
                day_of_week=config["day"],
                start_time=time(config["start_hour"], config["start_minute"]),
                end_time=time(config["end_hour"], config["end_minute"]),
                enabled=True,
            )
            schedules.append(schedule)

        return schedules

    def get_remaining_access_time(
            self,
            schedules: List[AccessSchedule],
            current_time: Optional[datetime] = None) -> Optional[int]:
        """Get remaining access time in minutes for current session"""

        if current_time is None:
            current_time = datetime.now()

        current_day = current_time.weekday()
        current_time_only = current_time.time()

        # Find active schedule
        for schedule in schedules:
            if (
                schedule.enabled
                and schedule.day_of_week == current_day
                and schedule.start_time <= current_time_only <= schedule.end_time
            ):

                return schedule.get_remaining_access_minutes()

        return None

    def _get_next_allowed_time(
        self, schedules: List[AccessSchedule], current_time: datetime
    ) -> str:
        """Get next allowed access time as human-readable string"""

        current_day = current_time.weekday()
        current_time_only = current_time.time()

        # Check if there's a later time today
        for schedule in schedules:
            if (
                schedule.enabled
                and schedule.day_of_week == current_day
                and schedule.start_time > current_time_only
            ):
                return f"Today at {schedule.start_time.strftime('%I:%M %p')}"

        # Check next 7 days
        for days_ahead in range(1, 8):
            next_day = (current_day + days_ahead) % 7

            for schedule in schedules:
                if schedule.enabled and schedule.day_of_week == next_day:
                    day_names = [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]

                    if days_ahead == 1:
                        day_str = "Tomorrow"
                    else:
                        day_str = day_names[next_day]

                    return f"{day_str} at {schedule.start_time.strftime('%I:%M %p')}"

        return "No scheduled access time found"

    def get_access_summary(
            self,
            schedules: List[AccessSchedule],
            current_time: Optional[datetime] = None) -> dict:
        """Get summary of access schedule and current status"""

        if current_time is None:
            current_time = datetime.now()

        is_allowed, next_time = self.check_access_allowed(
            schedules, current_time)
        remaining_time = self.get_remaining_access_time(
            schedules, current_time)

        # Count total weekly hours
        total_weekly_minutes = 0
        for schedule in schedules:
            if schedule.enabled:
                # Calculate duration for this schedule
                start_minutes = (
                    schedule.start_time.hour * 60 + schedule.start_time.minute
                )
                end_minutes = schedule.end_time.hour * 60 + schedule.end_time.minute
                duration = end_minutes - start_minutes
                total_weekly_minutes += duration

        return {
            "is_currently_allowed": is_allowed,
            "next_allowed_time": next_time,
            "remaining_minutes": remaining_time,
            "total_weekly_hours": total_weekly_minutes / 60,
            "schedule_count": len([s for s in schedules if s.enabled]),
        }
