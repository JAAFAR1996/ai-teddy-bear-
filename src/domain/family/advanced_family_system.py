import random
import uuid
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """أنواع الرسائل التشجيعية"""

    MOTIVATION = "تحفيزية"
    ACHIEVEMENT = "إنجاز"
    REMINDER = "تذكير"
    ENCOURAGEMENT = "تشجيع"
    LEARNING = "تعليمية"
    BEDTIME = "نوم"
    WAKE_UP = "استيقاظ"


class TimeRestrictionType(Enum):
    """أنواع القيود الزمنية"""

    DAILY_LIMIT = "حد_يومي"
    TIME_WINDOW = "نافذة_زمنية"
    BEDTIME_RESTRICTION = "قيد_النوم"
    STUDY_TIME = "وقت_الدراسة"
    BREAK_INTERVALS = "فترات_راحة"


@dataclass
class ScheduledMessage:
    """رسالة مجدولة"""

    id: str
    child_name: str
    device_id: str
    message_type: MessageType
    content: str
    scheduled_time: time  # الوقت اليومي للإرسال
    days_of_week: List[int]  # أيام الأسبوع (0=الاثنين)
    is_active: bool
    created_by_parent: str
    created_at: datetime
    last_sent: Optional[datetime] = None


@dataclass
class TimeRestriction:
    """قيد زمني"""

    id: str
    child_name: str
    device_id: str
    restriction_type: TimeRestrictionType
    start_time: Optional[time]
    end_time: Optional[time]
    daily_limit_minutes: Optional[int]
    days_of_week: List[int]
    is_active: bool
    set_by_parent: str
    reason: str  # سبب القيد
    created_at: datetime


@dataclass
class FamilyMember:
    """عضو في العائلة"""

    id: str
    name: str
    role: str  # "parent", "child", "guardian"
    age: Optional[int]
    relationship: str  # "father", "mother", "son", "daughter", etc.
    device_ids: List[str]  # الأجهزة المرتبطة
    preferences: Dict[str, Any]
    created_at: datetime


@dataclass
class FamilyProfile:
    """ملف العائلة"""

    family_id: str
    family_name: str
    members: List[FamilyMember]
    shared_settings: Dict[str, Any]
    time_zone: str
    language: str
    cultural_settings: Dict[str, Any]
    subscription_type: str  # "basic", "premium", "family_plus"
    created_at: datetime
    updated_at: datetime


@dataclass
class ChildComparison:
    """مقارنة بين الأطفال"""

    family_id: str
    comparison_date: datetime
    children_data: Dict[str, Dict]  # {child_name: {metrics}}
    insights: List[str]
    recommendations: List[str]


@dataclass
class MessageScheduleDetails:
    """Details for scheduling a new message."""

    child_name: str
    device_id: str
    message_type: MessageType
    content: str
    scheduled_time: time
    days_of_week: List[int]


@dataclass
class TimeRestrictionDetails:
    """Details for adding a new time restriction."""

    child_name: str
    device_id: str
    restriction_type: TimeRestrictionType
    reason: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    daily_limit_minutes: Optional[int] = None
    days_of_week: Optional[List[int]] = None


class AdvancedFamilySystem:
    """النظام العائلي المتقدم"""

    def __init__(self):
        self.family_profiles: Dict[str, FamilyProfile] = {}
        self.scheduled_messages: List[ScheduledMessage] = []
        self.time_restrictions: List[TimeRestriction] = []
        self.family_analytics: Dict[str, Any] = {}

        # قوالب الرسائل التشجيعية
        self.message_templates = self._load_message_templates()

    def _load_message_templates(self) -> Dict[str, Dict]:
        """تحميل قوالب الرسائل التشجيعية"""
        return {
            MessageType.MOTIVATION.value: [
                "صباح الخير يا {child_name}! اليوم يوم رائع لتعلم أشياء جديدة! 🌟",
                "أنت طفل مميز يا {child_name}! استمر في كونك رائعاً! 💫",
                "كل يوم تصبح أذكى وأقوى يا {child_name}! أنا فخور بك! 🚀",
            ],
            MessageType.ACHIEVEMENT.value: [
                "مبروك يا {child_name}! لقد حققت إنجازاً رائعاً اليوم! 🎉",
                "واو! {child_name} أنت نجم حقيقي! استمر هكذا! ⭐",
                "فخور جداً بما حققته يا {child_name}! أنت بطل! 🏆",
            ],
            MessageType.REMINDER.value: [
                "تذكير لطيف يا {child_name}: حان وقت {activity}! 🔔",
                "مرحباً {child_name}! لا تنسى {activity} اليوم! 💭",
                "يا {child_name}، لديك موعد مع {activity}! 📅",
            ],
            MessageType.ENCOURAGEMENT.value: [
                "أؤمن بك يا {child_name}! يمكنك فعل أي شيء تريده! 💪",
                "أنت قادر على تحقيق المعجزات يا {child_name}! 🌈",
                "لا تستسلم أبداً يا {child_name}! أنت أقوى مما تتخيل! 🦁",
            ],
            MessageType.LEARNING.value: [
                "هل تعلم يا {child_name} أن {fun_fact}؟ 🧠",
                "اليوم سنتعلم شيئاً جديداً يا {child_name}: {learning_content} 📚",
                "معلومة ممتعة لك يا {child_name}: {educational_tip} 🔍",
            ],
            MessageType.BEDTIME.value: [
                "حان وقت النوم يا {child_name}! أحلام سعيدة! 🌙",
                "تصبح على خير يا {child_name}! غداً يوم جديد مليء بالمرح! ✨",
                "هيا إلى السرير يا {child_name}! النوم يساعدك على النمو! 😴",
            ],
            MessageType.WAKE_UP.value: [
                "صباح الخير يا نور العين {child_name}! استيقظ بطل! ☀️",
                "مرحباً بالصباح يا {child_name}! يوم جديد مليء بالمتعة ينتظرك! 🌅",
                "صباح النشاط يا {child_name}! هل أنت مستعد لمغامرة اليوم؟ 🎈",
            ],
        }

    def _create_family_members(
        self, parent_name: str, children_info: List[Dict]
    ) -> List[FamilyMember]:
        """Helper to create family member objects."""
        members = []
        parent_member = FamilyMember(
            id=f"member_{uuid.uuid4()}",
            name=parent_name,
            role="parent",
            age=None,
            relationship="parent",
            device_ids=[],
            preferences={},
            created_at=datetime.now(),
        )
        members.append(parent_member)

        for child_info in children_info:
            child_member = FamilyMember(
                id=f"member_{uuid.uuid4()}",
                name=child_info["name"],
                role="child",
                age=child_info.get("age"),
                relationship=child_info.get("relationship", "child"),
                device_ids=child_info.get("device_ids", []),
                preferences=child_info.get("preferences", {}),
                created_at=datetime.now(),
            )
            members.append(child_member)
        return members

    def _prepare_family_settings(self, settings: Optional[Dict]) -> Dict:
        """Helper to prepare shared family settings."""
        default_settings = {
            "daily_interaction_limit": 60,
            "bedtime": "21:00",
            "wake_time": "07:00",
            "break_intervals": 15,
            "parental_notifications": True,
            "content_filtering": "moderate",
            "language_learning": True,
        }
        if settings:
            default_settings.update(settings)
        return default_settings

    def create_family_profile(
        self,
        family_name: str,
        parent_name: str,
        children_info: List[Dict],
        settings: Dict = None,
    ) -> str:
        """إنشاء ملف عائلة جديد"""
        family_id = f"family_{uuid.uuid4()}"

        members = self._create_family_members(parent_name, children_info)
        shared_settings = self._prepare_family_settings(settings)

        family_profile = FamilyProfile(
            family_id=family_id,
            family_name=family_name,
            members=members,
            shared_settings=shared_settings,
            time_zone="Asia/Riyadh",
            language="ar",
            cultural_settings={"region": "middle_east", "religion": "islam"},
            subscription_type="basic",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.family_profiles[family_id] = family_profile

        self._create_default_scheduled_messages(family_profile)
        self._create_default_time_restrictions(family_profile)

        return family_id

    def _create_and_add_message(
        self,
        child: FamilyMember,
        device_id: str,
        msg_type: MessageType,
        msg_time: time,
        parent_name: str,
    ):
        """Helper to create and add a single scheduled message."""
        content_template = random.choice(
            self.message_templates.get(msg_type.value, [""])
        )
        content = content_template.format(child_name=child.name)

        message = ScheduledMessage(
            id=f"msg_{uuid.uuid4()}",
            child_name=child.name,
            device_id=device_id,
            message_type=msg_type,
            content=content,
            scheduled_time=msg_time,
            days_of_week=list(range(7)),  # All days
            is_active=True,
            created_by_parent=parent_name,
            created_at=datetime.now(),
        )
        self.scheduled_messages.append(message)

    def _create_default_scheduled_messages(
            self, family_profile: FamilyProfile) -> None:
        """إنشاء رسائل تشجيعية افتراضية للعائلة"""
        children = [m for m in family_profile.members if m.role == "child"]
        parent = next(
            (m for m in family_profile.members if m.role == "parent"),
            None)
        parent_name = parent.name if parent else "System"

        default_messages_config = [
            (MessageType.WAKE_UP, time(7, 30)),
            (MessageType.BEDTIME, time(20, 30)),
        ]

        for child in children:
            for device_id in child.device_ids:
                for msg_type, msg_time in default_messages_config:
                    self._create_and_add_message(
                        child, device_id, msg_type, msg_time, parent_name
                    )

    def _create_and_add_restriction(
        self,
        child: FamilyMember,
        device_id: str,
        config: Dict[str, Any],
        parent_name: str,
    ):
        """Helper to create and add a single time restriction."""
        restriction = TimeRestriction(
            id=f"res_{uuid.uuid4()}",
            child_name=child.name,
            device_id=device_id,
            restriction_type=config["type"],
            start_time=config.get("start_time"),
            end_time=config.get("end_time"),
            daily_limit_minutes=config.get("daily_limit_minutes"),
            days_of_week=config.get("days_of_week", list(range(7))),
            is_active=True,
            set_by_parent=parent_name,
            reason=config["reason"],
            created_at=datetime.now(),
        )
        self.time_restrictions.append(restriction)

    def _create_default_time_restrictions(
            self, family_profile: FamilyProfile) -> None:
        """إنشاء قيود زمنية افتراضية للعائلة"""
        children = [m for m in family_profile.members if m.role == "child"]
        parent = next(
            (m for m in family_profile.members if m.role == "parent"),
            None)
        parent_name = parent.name if parent else "System"

        default_restrictions_config = [
            {
                "type": TimeRestrictionType.DAILY_LIMIT,
                "daily_limit_minutes": 120,
                "reason": "Default daily play time limit.",
            },
            {
                "type": TimeRestrictionType.BEDTIME_RESTRICTION,
                "start_time": time(21, 0),
                "end_time": time(7, 0),
                "reason": "Default bedtime restriction for healthy sleep.",
            },
        ]

        for child in children:
            for device_id in child.device_ids:
                for config in default_restrictions_config:
                    self._create_and_add_restriction(
                        child, device_id, config, parent_name
                    )

    def add_scheduled_message(
        self,
        family_id: str,
        details: MessageScheduleDetails,
        parent_name: str,
    ) -> str:
        """Add a new scheduled message to a family profile."""
        if family_id not in self.family_profiles:
            raise ValueError(f"Family with ID {family_id} not found.")

        message_id = f"msg_{uuid.uuid4()}"
        new_message = ScheduledMessage(
            id=message_id,
            child_name=details.child_name,
            device_id=details.device_id,
            message_type=details.message_type,
            content=details.content,
            scheduled_time=details.scheduled_time,
            days_of_week=details.days_of_week,
            is_active=True,
            created_by_parent=parent_name,
            created_at=datetime.now(),
        )

        self.scheduled_messages.append(new_message)
        self.family_profiles[family_id].updated_at = datetime.now()
        return message_id

    def add_time_restriction(
        self,
        family_id: str,
        details: TimeRestrictionDetails,
        parent_name: str,
    ) -> str:
        """Add a new time restriction for a child."""
        if family_id not in self.family_profiles:
            raise ValueError(f"Family with ID {family_id} not found.")

        # Validation logic
        if (
            details.restriction_type == TimeRestrictionType.DAILY_LIMIT
            and not details.daily_limit_minutes
        ):
            raise ValueError(
                "Daily limit must be set for DAILY_LIMIT restriction.")
        if details.restriction_type == TimeRestrictionType.TIME_WINDOW and not (
                details.start_time and details.end_time):
            raise ValueError(
                "Start and end times must be set for TIME_WINDOW restriction."
            )

        restriction_id = f"res_{uuid.uuid4()}"
        new_restriction = TimeRestriction(
            id=restriction_id,
            child_name=details.child_name,
            device_id=details.device_id,
            restriction_type=details.restriction_type,
            start_time=details.start_time,
            end_time=details.end_time,
            daily_limit_minutes=details.daily_limit_minutes,
            days_of_week=details.days_of_week or list(range(7)),
            is_active=True,
            set_by_parent=parent_name,
            reason=details.reason,
            created_at=datetime.now(),
        )

        self.time_restrictions.append(new_restriction)
        self.family_profiles[family_id].updated_at = datetime.now()
        return restriction_id

    def _get_active_restrictions_for_child(
        self, device_id: str, child_name: str, now: datetime
    ) -> List[TimeRestriction]:
        """Get all active restrictions for a child on a specific device."""
        current_day = now.weekday()
        return [
            r
            for r in self.time_restrictions
            if r.is_active
            and r.device_id == device_id
            and r.child_name == child_name
            and current_day in r.days_of_week
        ]

    def _check_daily_limit(
        self, restriction: TimeRestriction, usage_today_minutes: int
    ) -> Optional[str]:
        """Check daily limit restriction."""
        if restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT:
            if usage_today_minutes >= restriction.daily_limit_minutes:
                return f"Exceeded daily limit of {restriction.daily_limit_minutes} minutes. Reason: {restriction.reason}"
        return None

    def _check_time_window(
        self, restriction: TimeRestriction, now_time: time
    ) -> Optional[str]:
        """Check time window or bedtime restrictions."""
        if restriction.restriction_type in [
            TimeRestrictionType.TIME_WINDOW,
            TimeRestrictionType.BEDTIME_RESTRICTION,
        ]:
            start = restriction.start_time
            end = restriction.end_time

            if start and end:
                # Handle overnight case (e.g., 9 PM to 7 AM)
                if start > end:
                    if not (end <= now_time < start):
                        return f"Not allowed due to time restriction '{restriction.reason}' (overnight)."
                # Handle same-day case
                else:
                    if not (start <= now_time < end):
                        return f"Not allowed due to time restriction '{restriction.reason}'."
        return None

    async def check_scheduled_messages(self) -> List[Dict]:
        """Check and return messages that need to be sent."""
        now = datetime.now()
        now_time = now.time()
        current_day = now.weekday()  # Monday is 0 and Sunday is 6

        messages_to_send = []

        for message in self.scheduled_messages:
            if (
                message.is_active
                and current_day in message.days_of_week
                and message.scheduled_time.hour == now_time.hour
                and message.scheduled_time.minute == now_time.minute
            ):
                if message.last_sent is None or (
                        now - message.last_sent).days >= 1:
                    messages_to_send.append(
                        {
                            "device_id": message.device_id,
                            "content": message.content,
                        }
                    )
                    message.last_sent = now

        return messages_to_send

    def check_time_restrictions(
        self, device_id: str, child_name: str
    ) -> Dict[str, Any]:
        """Check current time restrictions for a child on a device."""
        now = datetime.now()
        now_time = now.time()

        # This is a placeholder for actual usage tracking
        usage_today_minutes = 100

        active_restrictions = self._get_active_restrictions_for_child(
            device_id, child_name, now
        )

        for r in active_restrictions:
            if violation := self._check_daily_limit(r, usage_today_minutes):
                return {"allowed": False, "reason": violation}
            if violation := self._check_time_window(r, now_time):
                return {"allowed": False, "reason": violation}

        return {"allowed": True, "reason": "No active restrictions."}

    def _find_extreme_children(
            self, children_data: Dict[str, Dict]) -> Dict[str, str]:
        """Find the most and least active children from data."""
        sorted_children = sorted(
            children_data.items(),
            key=lambda item: item[1].get("interaction_minutes", 0),
            reverse=True,
        )
        return {
            "most_active": sorted_children[0][0] if sorted_children else "N/A",
            "least_active": sorted_children[-1][0] if sorted_children else "N/A",
        }

    def _generate_comparison_insights(
        self, children_data: Dict[str, Dict], extremes: Dict[str, str]
    ) -> List[str]:
        """Generate insights for the family comparison report."""
        insights = [
            f"Most active child this period: {extremes['most_active']}.",
            f"Least active child this period: {extremes['least_active']}.",
        ]
        if len(children_data) > 1:
            total_minutes = sum(
                d.get("interaction_minutes", 0) for d in children_data.values()
            )
            avg_minutes = total_minutes / len(children_data)
            insights.append(
                f"Average interaction time: {avg_minutes:.2f} minutes per child."
            )
        return insights

    def _generate_comparison_recommendations(
        self, children_data: Dict[str, Dict], extremes: Dict[str, str]
    ) -> List[str]:
        """Generate recommendations for the family comparison report."""
        recommendations = [
            f"Engage with {extremes['least_active']} on topics they enjoy to encourage interaction.",
            f"Review the activities of {extremes['most_active']} to ensure they are balanced.",
        ]
        # Add more complex recommendation logic here if needed
        return recommendations

    def generate_family_comparison_report(
        self, family_id: str, children_data: Dict[str, Dict]
    ) -> ChildComparison:
        """Generate a report comparing children's activity."""
        if family_id not in self.family_profiles:
            raise ValueError(f"Family with ID {family_id} not found.")
        if not children_data or len(children_data) < 2:
            raise ValueError(
                "Comparison requires data for at least two children.")

        extremes = self._find_extreme_children(children_data)
        insights = self._generate_comparison_insights(children_data, extremes)
        recommendations = self._generate_comparison_recommendations(
            children_data, extremes
        )

        return ChildComparison(
            family_id=family_id,
            comparison_date=datetime.now(),
            children_data=children_data,
            insights=insights,
            recommendations=recommendations,
        )

    def update_family_settings(
            self,
            family_id: str,
            new_settings: Dict) -> bool:
        """Update shared settings for a family."""

        if family_id not in self.family_profiles:
            return False

        family = self.family_profiles[family_id]
        family.shared_settings.update(new_settings)
        family.updated_at = datetime.now()

        # تحديث القيود الزمنية إذا تغيرت
        if "daily_interaction_limit" in new_settings:
            for restriction in self.time_restrictions:
                if (
                    restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT
                    and any(
                        member.name == restriction.child_name
                        for member in family.members
                        if member.role == "child"
                    )
                ):
                    restriction.daily_limit_minutes = new_settings[
                        "daily_interaction_limit"
                    ]

        return True

    def _get_dashboard_member_summary(
            self, members: List[FamilyMember]) -> Dict:
        """Generate a summary of family members for the dashboard."""
        children = [m for m in members if m.role == "child"]
        parents = [m for m in members if m.role == "parent"]
        return {
            "total_members": len(members),
            "children_count": len(children),
            "parent_count": len(parents),
            "children_names": [c.name for c in children],
        }

    def _get_dashboard_message_summary(self, family_id: str) -> Dict:
        """Generate a summary of scheduled messages for the dashboard."""
        family_messages = [
            m
            for m in self.scheduled_messages
            if m.device_id in self._get_family_device_ids(family_id)
        ]
        return {
            "total_scheduled_messages": len(family_messages),
            "active_messages": sum(1 for m in family_messages if m.is_active),
        }

    def _get_dashboard_restriction_summary(self, family_id: str) -> Dict:
        """Generate a summary of time restrictions for the dashboard."""
        family_restrictions = [
            r
            for r in self.time_restrictions
            if r.device_id in self._get_family_device_ids(family_id)
        ]
        return {
            "total_time_restrictions": len(family_restrictions),
            "active_restrictions": sum(
                1 for r in family_restrictions if r.is_active),
        }

    def _get_family_device_ids(self, family_id: str) -> List[str]:
        """Get all device IDs associated with a family."""
        family = self.family_profiles.get(family_id)
        if not family:
            return []

        device_ids = []
        for member in family.members:
            device_ids.extend(member.device_ids)
        return list(set(device_ids))

    def get_family_dashboard(self, family_id: str) -> Dict[str, Any]:
        """Get a comprehensive dashboard for a family."""
        family = self.family_profiles.get(family_id)
        if not family:
            return {"error": "Family not found"}

        dashboard = {
            "family_id": family.family_id,
            "family_name": family.family_name,
            "last_updated": family.updated_at.isoformat(),
            "subscription_type": family.subscription_type,
            "member_summary": self._get_dashboard_member_summary(
                family.members),
            "message_summary": self._get_dashboard_message_summary(family_id),
            "restriction_summary": self._get_dashboard_restriction_summary(family_id),
            "shared_settings": family.shared_settings,
        }
        return dashboard

    def create_custom_encouragement_message(
        self, child_name: str, achievement: str, personal_traits: List[str]
    ) -> str:
        """إنشاء رسالة تشجيعية مخصصة"""

        # قوالب مخصصة بناءً على الإنجاز
        achievement_templates = {
            "academic": [
                "يا {child_name} العبقري! إنجازك في {achievement} يُظهر ذكاءك الرائع!",
                "ممتاز يا {child_name}! {achievement} دليل على اجتهادك وذكائك!",
            ],
            "creative": [
                "واو {child_name}! إبداعك في {achievement} يُبهر الجميع!",
                "أنت فنان حقيقي يا {child_name}! {achievement} تحفة رائعة!",
            ],
            "social": [
                "فخور بك يا {child_name}! {achievement} يُظهر قلبك الطيب!",
                "أنت صديق رائع يا {child_name}! {achievement} دليل على طيبتك!",
            ],
            "physical": [
                "يا بطل! {child_name} قوي وسريع! {achievement} إنجاز رياضي رائع!",
                "ممتاز يا {child_name} القوي! {achievement} يُظهر لياقتك الرائعة!",
            ],
        }

        # اختيار فئة الإنجاز
        category = "academic"  # افتراضي
        if any(
            trait in ["creative", "artistic", "imaginative"]
            for trait in personal_traits
        ):
            category = "creative"
        elif any(trait in ["kind", "helpful", "friendly"] for trait in personal_traits):
            category = "social"
        elif any(
            trait in ["active", "strong", "athletic"] for trait in personal_traits
        ):
            category = "physical"

        template = random.choice(achievement_templates[category])

        return template.format(child_name=child_name, achievement=achievement)

    def get_parental_control_summary(self, family_id: str) -> Dict[str, Any]:
        """ملخص أدوات الرقابة الأبوية"""

        if family_id not in self.family_profiles:
            return {"error": "العائلة غير موجودة"}

        family = self.family_profiles[family_id]
        children = [
            member for member in family.members if member.role == "child"]

        control_summary = {
            "time_management": {
                "daily_limits_set": 0,
                "bedtime_restrictions": 0,
                "study_time_blocks": 0,
            },
            "content_filtering": {
                "level": family.shared_settings.get(
                    "content_filtering",
                    "moderate"),
                "custom_blocks": 0,
            },
            "communication": {
                "scheduled_messages": len(
                    self.scheduled_messages),
                "emergency_contacts": len(
                    family.shared_settings.get(
                        "emergency_contacts",
                        [])),
            },
            "monitoring": {
                "activity_tracking": True,
                "progress_reports": True,
                "behavioral_alerts": True,
            },
        }

        # حساب القيود الزمنية
        for restriction in self.time_restrictions:
            if restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT:
                control_summary["time_management"]["daily_limits_set"] += 1
            elif (
                restriction.restriction_type == TimeRestrictionType.BEDTIME_RESTRICTION
            ):
                control_summary["time_management"]["bedtime_restrictions"] += 1
            elif restriction.restriction_type == TimeRestrictionType.STUDY_TIME:
                control_summary["time_management"]["study_time_blocks"] += 1

        return control_summary
