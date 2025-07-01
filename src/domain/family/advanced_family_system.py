import asyncio
import json
import random
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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

    def create_family_profile(
        self, family_name: str, parent_name: str, children_info: List[Dict], settings: Dict = None
    ) -> str:
        """إنشاء ملف عائلة جديد"""

        family_id = f"family_{uuid.uuid4()}"

        # إنشاء الأعضاء
        members = []

        # إضافة الوالد
        parent_member = FamilyMember(
            id=f"member_{uuid.uuid4()}",
            name=parent_name,
            role="parent",
            age=None,  # اختياري للوالدين
            relationship="parent",
            device_ids=[],
            preferences={},
            created_at=datetime.now(),
        )
        members.append(parent_member)

        # إضافة الأطفال
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

        # الإعدادات الافتراضية
        default_settings = {
            "daily_interaction_limit": 60,  # دقيقة
            "bedtime": "21:00",
            "wake_time": "07:00",
            "break_intervals": 15,  # فترة راحة كل 15 دقيقة
            "parental_notifications": True,
            "content_filtering": "moderate",
            "language_learning": True,
        }

        if settings:
            default_settings.update(settings)

        # إنشاء الملف العائلي
        family_profile = FamilyProfile(
            family_id=family_id,
            family_name=family_name,
            members=members,
            shared_settings=default_settings,
            time_zone="Asia/Riyadh",  # افتراضي
            language="ar",
            cultural_settings={"region": "middle_east", "religion": "islam"},
            subscription_type="basic",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.family_profiles[family_id] = family_profile

        # إنشاء رسائل تشجيعية افتراضية
        self._create_default_scheduled_messages(family_profile)

        # إنشاء قيود زمنية افتراضية
        self._create_default_time_restrictions(family_profile)

        return family_id

    def _create_default_scheduled_messages(FamilyProfile) -> None:
        """إنشاء رسائل تشجيعية افتراضية للعائلة"""

        children = [member for member in family.members if member.role == "child"]
        parent = next((member for member in family.members if member.role == "parent"), None)

        for child in children:
            for device_id in child.device_ids:
                # رسالة صباحية تحفيزية
                morning_msg = ScheduledMessage(
                    id=f"msg_{uuid.uuid4()}",
                    child_name=child.name,
                    device_id=device_id,
                    message_type=MessageType.MOTIVATION,
                    content=random.choice(self.message_templates[MessageType.MOTIVATION.value]).format(
                        child_name=child.name
                    ),
                    scheduled_time=time(8, 0),  # 8:00 ص
                    days_of_week=[0, 1, 2, 3, 4],  # الاثنين إلى الجمعة
                    is_active=True,
                    created_by_parent=parent.name if parent else "system",
                    created_at=datetime.now(),
                )

                # رسالة مسائية للنوم
                bedtime_msg = ScheduledMessage(
                    id=f"msg_{uuid.uuid4()}",
                    child_name=child.name,
                    device_id=device_id,
                    message_type=MessageType.BEDTIME,
                    content=random.choice(self.message_templates[MessageType.BEDTIME.value]).format(
                        child_name=child.name
                    ),
                    scheduled_time=time(20, 30),  # 8:30 م
                    days_of_week=[0, 1, 2, 3, 4, 5, 6],  # كل يوم
                    is_active=True,
                    created_by_parent=parent.name if parent else "system",
                    created_at=datetime.now(),
                )

                self.scheduled_messages.extend([morning_msg, bedtime_msg])

    def _create_default_time_restrictions(FamilyProfile) -> None:
        """إنشاء قيود زمنية افتراضية"""

        children = [member for member in family.members if member.role == "child"]
        parent = next((member for member in family.members if member.role == "parent"), None)

        for child in children:
            for device_id in child.device_ids:
                # حد زمني يومي
                daily_limit = TimeRestriction(
                    id=f"restriction_{uuid.uuid4()}",
                    child_name=child.name,
                    device_id=device_id,
                    restriction_type=TimeRestrictionType.DAILY_LIMIT,
                    start_time=None,
                    end_time=None,
                    daily_limit_minutes=family.shared_settings.get("daily_interaction_limit", 60),
                    days_of_week=[0, 1, 2, 3, 4, 5, 6],
                    is_active=True,
                    set_by_parent=parent.name if parent else "system",
                    reason="صحة رقمية للطفل",
                    created_at=datetime.now(),
                )

                # قيد وقت النوم
                bedtime_restriction = TimeRestriction(
                    id=f"restriction_{uuid.uuid4()}",
                    child_name=child.name,
                    device_id=device_id,
                    restriction_type=TimeRestrictionType.BEDTIME_RESTRICTION,
                    start_time=time(21, 0),  # 9:00 م
                    end_time=time(7, 0),  # 7:00 ص
                    daily_limit_minutes=None,
                    days_of_week=[0, 1, 2, 3, 4, 5, 6],
                    is_active=True,
                    set_by_parent=parent.name if parent else "system",
                    reason="وقت النوم الصحي",
                    created_at=datetime.now(),
                )

                self.time_restrictions.extend([daily_limit, bedtime_restriction])

    def add_scheduled_message(
        self,
        family_id: str,
        child_name: str,
        device_id: str,
        message_type: MessageType,
        content: str,
        scheduled_time: time,
        days_of_week: List[int],
        parent_name: str,
    ) -> str:
        """إضافة رسالة مجدولة جديدة"""

        message = ScheduledMessage(
            id=f"msg_{uuid.uuid4()}",
            child_name=child_name,
            device_id=device_id,
            message_type=message_type,
            content=content,
            scheduled_time=scheduled_time,
            days_of_week=days_of_week,
            is_active=True,
            created_by_parent=parent_name,
            created_at=datetime.now(),
        )

        self.scheduled_messages.append(message)
        return message.id

    def add_time_restriction(
        self,
        family_id: str,
        child_name: str,
        device_id: str,
        restriction_type: TimeRestrictionType,
        parent_name: str,
        reason: str,
        start_time: time = None,
        end_time: time = None,
        daily_limit_minutes: int = None,
        days_of_week: List[int] = None,
    ) -> str:
        """إضافة قيد زمني جديد"""

        if days_of_week is None:
            days_of_week = [0, 1, 2, 3, 4, 5, 6]  # كل الأيام افتراضياً

        restriction = TimeRestriction(
            id=f"restriction_{uuid.uuid4()}",
            child_name=child_name,
            device_id=device_id,
            restriction_type=restriction_type,
            start_time=start_time,
            end_time=end_time,
            daily_limit_minutes=daily_limit_minutes,
            days_of_week=days_of_week,
            is_active=True,
            set_by_parent=parent_name,
            reason=reason,
            created_at=datetime.now(),
        )

        self.time_restrictions.append(restriction)
        return restriction.id

    async def check_scheduled_messages(self) -> List[Dict]:
        """فحص الرسائل المجدولة المستحقة للإرسال"""

        current_time = datetime.now().time()
        current_weekday = datetime.now().weekday()
        today = datetime.now().date()

        messages_to_send = []

        for message in self.scheduled_messages:
            if not message.is_active:
                continue

            # فحص اليوم
            if current_weekday not in message.days_of_week:
                continue

            # فحص الوقت
            if message.scheduled_time.hour != current_time.hour:
                continue

            # فحص إذا تم الإرسال اليوم
            if message.last_sent and message.last_sent.date() == today:
                continue

            # إعداد الرسالة للإرسال
            messages_to_send.append(
                {
                    "message_id": message.id,
                    "device_id": message.device_id,
                    "child_name": message.child_name,
                    "content": message.content,
                    "message_type": message.message_type.value,
                }
            )

            # تحديث وقت آخر إرسال
            message.last_sent = datetime.now()

        return messages_to_send

    def check_time_restrictions(self, device_id: str, child_name: str) -> Dict[str, Any]:
        """فحص القيود الزمنية للطفل"""

        current_time = datetime.now().time()
        current_weekday = datetime.now().weekday()

        restrictions_status = {"allowed": True, "restrictions": [], "time_remaining": None, "next_allowed_time": None}

        child_restrictions = [
            r for r in self.time_restrictions if r.device_id == device_id and r.child_name == child_name and r.is_active
        ]

        for restriction in child_restrictions:
            # فحص اليوم
            if current_weekday not in restriction.days_of_week:
                continue

            violation = False

            if restriction.restriction_type == TimeRestrictionType.BEDTIME_RESTRICTION:
                # فحص وقت النوم
                if restriction.start_time and restriction.end_time:
                    if restriction.start_time > restriction.end_time:
                        # يمتد عبر منتصف الليل
                        if current_time >= restriction.start_time or current_time <= restriction.end_time:
                            violation = True
                    else:
                        # في نفس اليوم
                        if restriction.start_time <= current_time <= restriction.end_time:
                            violation = True

            elif restriction.restriction_type == TimeRestrictionType.TIME_WINDOW:
                # نافذة زمنية محددة
                if (
                    restriction.start_time
                    and restriction.end_time
                    and not (restriction.start_time <= current_time <= restriction.end_time)
                ):
                    violation = True

            elif restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT:
                # فحص الحد اليومي - يحتاج لتتبع الوقت المستخدم
                # هذا يتطلب دمج مع نظام تتبع الاستخدام
                pass

            if violation:
                restrictions_status["allowed"] = False
                restrictions_status["restrictions"].append(
                    {
                        "type": restriction.restriction_type.value,
                        "reason": restriction.reason,
                        "set_by": restriction.set_by_parent,
                    }
                )

        return restrictions_status

    def generate_family_comparison_report(self, family_id: str, children_data: Dict[str, Dict]) -> ChildComparison:
        """توليد تقرير مقارنة بين الأطفال في العائلة"""

        if family_id not in self.family_profiles:
            return None

        family = self.family_profiles[family_id]
        children = [member for member in family.members if member.role == "child"]

        insights = []
        recommendations = []

        # تحليل الأداء الأكاديمي
        academic_scores = {}
        for child_name, data in children_data.items():
            academic_scores[child_name] = data.get("academic_performance", 0)

        if academic_scores:
            top_performer = max(academic_scores.items(), key=lambda x: x[1])
            insights.append(f"{top_performer[0]} يُظهر أداءً أكاديمياً ممتازاً")

            for child_name, score in academic_scores.items():
                if score < 70:  # أقل من 70%
                    recommendations.append(f"يحتاج {child_name} دعماً إضافياً في التعليم")

        # تحليل الوقت المستخدم
        usage_times = {}
        for child_name, data in children_data.items():
            usage_times[child_name] = data.get("daily_usage_minutes", 0)

        if usage_times:
            avg_usage = sum(usage_times.values()) / len(usage_times)
            for child_name, usage in usage_times.items():
                if usage > avg_usage * 1.5:
                    recommendations.append(f"قلل وقت استخدام {child_name} للجهاز")
                elif usage < avg_usage * 0.5:
                    insights.append(f"{child_name} يستخدم الجهاز بشكل معتدل")

        # تحليل المهارات الاجتماعية
        social_scores = {}
        for child_name, data in children_data.items():
            social_scores[child_name] = data.get("social_skills", 0)

        if social_scores:
            for child_name, score in social_scores.items():
                if score > 80:
                    insights.append(f"{child_name} يتمتع بمهارات اجتماعية ممتازة")
                elif score < 50:
                    recommendations.append(f"شجع {child_name} على المزيد من الأنشطة الاجتماعية")

        comparison = ChildComparison(
            family_id=family_id,
            comparison_date=datetime.now(),
            children_data=children_data,
            insights=insights,
            recommendations=recommendations,
        )

        return comparison

    def update_family_settings(self, family_id: str, new_settings: Dict) -> bool:
        """تحديث إعدادات العائلة"""

        if family_id not in self.family_profiles:
            return False

        family = self.family_profiles[family_id]
        family.shared_settings.update(new_settings)
        family.updated_at = datetime.now()

        # تحديث القيود الزمنية إذا تغيرت
        if "daily_interaction_limit" in new_settings:
            for restriction in self.time_restrictions:
                if restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT and any(
                    member.name == restriction.child_name for member in family.members if member.role == "child"
                ):
                    restriction.daily_limit_minutes = new_settings["daily_interaction_limit"]

        return True

    def get_family_dashboard(self, family_id: str) -> Dict[str, Any]:
        """الحصول على لوحة تحكم العائلة"""

        if family_id not in self.family_profiles:
            return {"error": "العائلة غير موجودة"}

        family = self.family_profiles[family_id]
        children = [member for member in family.members if member.role == "child"]

        # إحصائيات سريعة
        total_children = len(children)
        active_devices = sum(len(child.device_ids) for child in children)
        active_messages = len([msg for msg in self.scheduled_messages if msg.is_active])
        active_restrictions = len([r for r in self.time_restrictions if r.is_active])

        return {
            "family_info": {
                "name": family.family_name,
                "total_children": total_children,
                "subscription": family.subscription_type,
                "language": family.language,
            },
            "quick_stats": {
                "active_devices": active_devices,
                "scheduled_messages": active_messages,
                "time_restrictions": active_restrictions,
            },
            "children": [
                {
                    "name": child.name,
                    "age": child.age,
                    "devices": len(child.device_ids),
                    "last_active": "غير متوفر",  # سيتم ربطه بنظام التتبع
                }
                for child in children
            ],
            "recent_activity": [],  # سيتم ملؤه من أنظمة أخرى
            "upcoming_messages": [
                {"child": msg.child_name, "time": msg.scheduled_time.strftime("%H:%M"), "type": msg.message_type.value}
                for msg in self.scheduled_messages[-5:]  # آخر 5 رسائل
            ],
        }

    def create_custom_encouragement_message(self, child_name: str, achievement: str, personal_traits: List[str]) -> str:
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
        if any(trait in ["creative", "artistic", "imaginative"] for trait in personal_traits):
            category = "creative"
        elif any(trait in ["kind", "helpful", "friendly"] for trait in personal_traits):
            category = "social"
        elif any(trait in ["active", "strong", "athletic"] for trait in personal_traits):
            category = "physical"

        template = random.choice(achievement_templates[category])

        return template.format(child_name=child_name, achievement=achievement)

    def get_parental_control_summary(self, family_id: str) -> Dict[str, Any]:
        """ملخص أدوات الرقابة الأبوية"""

        if family_id not in self.family_profiles:
            return {"error": "العائلة غير موجودة"}

        family = self.family_profiles[family_id]
        children = [member for member in family.members if member.role == "child"]

        control_summary = {
            "time_management": {"daily_limits_set": 0, "bedtime_restrictions": 0, "study_time_blocks": 0},
            "content_filtering": {
                "level": family.shared_settings.get("content_filtering", "moderate"),
                "custom_blocks": 0,
            },
            "communication": {
                "scheduled_messages": len(self.scheduled_messages),
                "emergency_contacts": len(family.shared_settings.get("emergency_contacts", [])),
            },
            "monitoring": {"activity_tracking": True, "progress_reports": True, "behavioral_alerts": True},
        }

        # حساب القيود الزمنية
        for restriction in self.time_restrictions:
            if restriction.restriction_type == TimeRestrictionType.DAILY_LIMIT:
                control_summary["time_management"]["daily_limits_set"] += 1
            elif restriction.restriction_type == TimeRestrictionType.BEDTIME_RESTRICTION:
                control_summary["time_management"]["bedtime_restrictions"] += 1
            elif restriction.restriction_type == TimeRestrictionType.STUDY_TIME:
                control_summary["time_management"]["study_time_blocks"] += 1

        return control_summary
