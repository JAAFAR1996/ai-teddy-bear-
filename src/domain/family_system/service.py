import random
import uuid
from datetime import datetime, time
from typing import Any, Dict, List, Optional

from .models import (
    FamilyMember,
    FamilyProfile,
    MessageScheduleDetails,
    MessageType,
    ScheduledMessage,
    TimeRestriction,
    TimeRestrictionDetails,
    TimeRestrictionType,
    ChildComparison,
)
from .repository import FamilyRepository


class FamilyService:
    """
    Handles business logic related to family profiles, messages, and restrictions.
    """

    def __init__(self, repository: FamilyRepository):
        self.repository = repository
        self.message_templates = self._load_message_templates()

    def _load_message_templates(self) -> Dict[str, List[str]]:
        return {
            MessageType.MOTIVATION.value: ["صباح الخير يا {child_name}! يوم رائع لتعلم أشياء جديدة! 🌟"],
            MessageType.ACHIEVEMENT.value: ["مبروك يا {child_name}! لقد حققت إنجازاً رائعاً اليوم! 🎉"],
            MessageType.REMINDER.value: ["تذكير لطيف يا {child_name}: حان وقت {activity}! 🔔"],
            MessageType.ENCOURAGEMENT.value: ["أؤمن بك يا {child_name}! يمكنك فعل أي شيء تريده! 💪"],
            MessageType.LEARNING.value: ["هل تعلم يا {child_name} أن {fun_fact}؟ 🧠"],
            MessageType.BEDTIME.value: ["حان وقت النوم يا {child_name}! أحلام سعيدة! 🌙"],
            MessageType.WAKE_UP.value: ["صباح الخير يا نور العين {child_name}! استيقظ بطل! ☀️"],
        }

    async def create_family_profile(self, family_name: str, parent_name: str, children_info: List[Dict], settings: Optional[Dict] = None) -> str:
        family_id = f"family_{uuid.uuid4()}"
        members = self._create_family_members(parent_name, children_info)
        shared_settings = self._prepare_family_settings(settings)

        family_profile = FamilyProfile(
            family_id=family_id, family_name=family_name, members=members,
            shared_settings=shared_settings, time_zone="Asia/Riyadh", language="ar",
            cultural_settings={"region": "middle_east"}, subscription_type="basic",
            created_at=datetime.now(), updated_at=datetime.now(),
        )
        await self.repository.save_family_profile(family_profile)
        await self._create_default_scheduled_messages(family_profile)
        await self._create_default_time_restrictions(family_profile)
        return family_id

    def _create_family_members(self, parent_name: str, children_info: List[Dict]) -> List[FamilyMember]:
        members = [FamilyMember(id=f"member_{uuid.uuid4()}", name=parent_name, role="parent", age=None,
                                relationship="parent", device_ids=[], preferences={}, created_at=datetime.now())]
        for child_info in children_info:
            members.append(FamilyMember(id=f"member_{uuid.uuid4()}", name=child_info["name"], role="child", age=child_info.get(
                "age"), relationship="child", device_ids=child_info.get("device_ids", []), preferences=child_info.get("preferences", {}), created_at=datetime.now()))
        return members

    def _prepare_family_settings(self, settings: Optional[Dict]) -> Dict:
        default_settings = {"daily_interaction_limit": 60,
                            "bedtime": "21:00", "content_filtering": "moderate"}
        if settings:
            default_settings.update(settings)
        return default_settings

    async def _create_default_scheduled_messages(self, family_profile: FamilyProfile) -> None:
        children = [m for m in family_profile.members if m.role == "child"]
        parent_name = next(
            (m.name for m in family_profile.members if m.role == "parent"), "System")
        for child in children:
            for device_id in child.device_ids:
                for msg_type, msg_time in [(MessageType.WAKE_UP, time(7, 30)), (MessageType.BEDTIME, time(20, 30))]:
                    await self._create_and_add_message(child, device_id, msg_type, msg_time, parent_name)

    async def _create_and_add_message(self, child: FamilyMember, device_id: str, msg_type: MessageType, msg_time: time, parent_name: str):
        content = random.choice(self.message_templates.get(
            msg_type.value, [""])).format(child_name=child.name)
        message = ScheduledMessage(
            id=f"msg_{uuid.uuid4()}", child_name=child.name, device_id=device_id,
            message_type=msg_type, content=content, scheduled_time=msg_time,
            days_of_week=list(range(7)), is_active=True, created_by_parent=parent_name,
            created_at=datetime.now()
        )
        await self.repository.save_scheduled_message(message)

    async def add_scheduled_message(self, family_id: str, details: MessageScheduleDetails, parent_name: str) -> str:
        profile = await self.repository.get_family_profile(family_id)
        if not profile:
            raise ValueError("Family not found.")

        message_id = f"msg_{uuid.uuid4()}"
        new_message = ScheduledMessage(id=message_id, **details.dict(
        ), is_active=True, created_by_parent=parent_name, created_at=datetime.now())
        await self.repository.save_scheduled_message(new_message)
        profile.updated_at = datetime.now()
        await self.repository.save_family_profile(profile)
        return message_id

    async def add_time_restriction(self, family_id: str, details: TimeRestrictionDetails, parent_name: str) -> str:
        profile = await self.repository.get_family_profile(family_id)
        if not profile:
            raise ValueError("Family not found.")

        restriction_id = f"res_{uuid.uuid4()}"
        new_restriction = TimeRestriction(id=restriction_id, **details.dict(), days_of_week=details.days_of_week or list(
            range(7)), is_active=True, set_by_parent=parent_name, created_at=datetime.now())
        await self.repository.save_time_restriction(new_restriction)
        profile.updated_at = datetime.now()
        await self.repository.save_family_profile(profile)
        return restriction_id

    async def check_scheduled_messages(self, family_id: str) -> List[Dict]:
        now = datetime.now()
        messages = await self.repository.get_scheduled_messages(family_id)
        messages_to_send = []
        for message in messages:
            if (message.is_active and now.weekday() in message.days_of_week and
                    message.scheduled_time.hour == now.hour and message.scheduled_time.minute == now.minute):
                if not message.last_sent or (now - message.last_sent).days >= 1:
                    messages_to_send.append(
                        {"device_id": message.device_id, "content": message.content})
                    message.last_sent = now
                    await self.repository.save_scheduled_message(message)
        return messages_to_send

    async def check_time_restrictions(self, family_id: str, device_id: str, child_name: str, usage_today_minutes: int) -> Dict[str, Any]:
        now = datetime.now()
        restrictions = await self.repository.get_time_restrictions(family_id)
        active_restrictions = [r for r in restrictions if r.is_active and r.device_id ==
                               device_id and r.child_name == child_name and now.weekday() in r.days_of_week]

        for r in active_restrictions:
            if r.restriction_type == TimeRestrictionType.DAILY_LIMIT and usage_today_minutes >= r.daily_limit_minutes:
                return {"allowed": False, "reason": f"Exceeded daily limit. Reason: {r.reason}"}
            if r.restriction_type in [TimeRestrictionType.TIME_WINDOW, TimeRestrictionType.BEDTIME_RESTRICTION] and r.start_time and r.end_time:
                if (r.start_time > r.end_time and not (r.end_time <= now.time() < r.start_time)) or \
                   (r.start_time < r.end_time and not (r.start_time <= now.time() < r.end_time)):
                    return {"allowed": False, "reason": f"Time restriction active. Reason: {r.reason}"}
        return {"allowed": True, "reason": "No active restrictions."}

    async def generate_family_comparison_report(self, family_id: str, children_data: Dict[str, Dict]) -> ChildComparison:
        profile = await self.repository.get_family_profile(family_id)
        if not profile:
            raise ValueError("Family not found.")
        if len(children_data) < 2:
            raise ValueError("Comparison requires at least two children.")

        sorted_children = sorted(children_data.items(), key=lambda item: item[1].get(
            "interaction_minutes", 0), reverse=True)
        most_active, least_active = sorted_children[0][0], sorted_children[-1][0]

        insights = [f"Most active: {most_active}.",
                    f"Least active: {least_active}."]
        recommendations = [
            f"Engage with {least_active}.", f"Review activities of {most_active}."]

        return ChildComparison(
            family_id=family_id, comparison_date=datetime.now(),
            children_data=children_data, insights=insights, recommendations=recommendations
        )
