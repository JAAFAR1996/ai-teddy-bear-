#!/usr/bin/env python3
"""
🥽 خدمة الواقع المعزز والافتراضي
تجارب تفاعلية ثلاثية الأبعاد للأطفال
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import base64

logger = logging.getLogger(__name__)

@dataclass
class ARExperience:
    """تجربة واقع معزز"""
    experience_id: str
    name: str
    description: str
    category: str  # educational, entertainment, interactive_story, game
    age_range: Tuple[int, int]  # (min_age, max_age)
    duration_minutes: int
    difficulty_level: str  # easy, medium, hard
    required_objects: List[str] = None  # الأجسام المطلوبة للتعرف عليها
    learning_objectives: List[str] = None
    safety_requirements: List[str] = None
    ar_models: Dict[str, str] = None  # نماذج ثلاثية الأبعاد
    interaction_points: List[Dict] = None  # نقاط التفاعل
    
    def __post_init__(self):
        if self.required_objects is None:
            self.required_objects = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.safety_requirements is None:
            self.safety_requirements = []
        if self.ar_models is None:
            self.ar_models = {}
        if self.interaction_points is None:
            self.interaction_points = []

@dataclass
class VREnvironment:
    """بيئة واقع افتراضي"""
    environment_id: str
    name: str
    theme: str  # space, underwater, forest, fantasy, educational
    description: str
    immersion_level: str  # low, medium, high
    movement_type: str  # stationary, limited, full_movement
    educational_content: Dict = None
    interactive_elements: List[Dict] = None
    safety_boundaries: Dict = None
    comfort_settings: Dict = None
    
    def __post_init__(self):
        if self.educational_content is None:
            self.educational_content = {}
        if self.interactive_elements is None:
            self.interactive_elements = []
        if self.safety_boundaries is None:
            self.safety_boundaries = {"max_session_time": 15, "break_intervals": 5}
        if self.comfort_settings is None:
            self.comfort_settings = {"motion_sickness_prevention": True, "eye_strain_protection": True}

class ARVRService:
    """خدمة الواقع المعزز والافتراضي"""
    
    def __init__(self, data_dir: str = "data/ar_vr"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.ar_experiences: Dict[str, ARExperience] = {}
        self.vr_environments: Dict[str, VREnvironment] = {}
        self.user_sessions: Dict[str, List[Dict]] = {}  # تتبع جلسات المستخدمين
        self.child_preferences: Dict[str, Dict] = {}
        
        self._initialize_default_experiences()
        self._load_data()
    
    def _initialize_default_experiences(self) -> Any:
        """تهيئة التجارب الافتراضية"""
        # تجارب الواقع المعزز التعليمية
        educational_ar = [
            ARExperience(
                experience_id="ar_alphabet",
                name="رحلة الحروف المعززة",
                description="تعلم الحروف العربية بالواقع المعزز",
                category="educational",
                age_range=(3, 7),
                duration_minutes=10,
                difficulty_level="easy",
                required_objects=["book", "table"],
                learning_objectives=["تعلم الحروف", "تحسين النطق", "تطوير الذاكرة البصرية"],
                safety_requirements=["مساحة آمنة 2x2 متر", "إشراف بالغ"],
                ar_models={"letters": "3d_arabic_letters.obj", "animations": "letter_animations.fbx"},
                interaction_points=[
                    {"type": "touch", "object": "letter", "action": "play_sound"},
                    {"type": "voice", "trigger": "say_letter", "response": "show_animation"}
                ]
            ),
            ARExperience(
                experience_id="ar_animals",
                name="حديقة الحيوانات المعززة",
                description="استكشاف الحيوانات بالواقع المعزز",
                category="educational",
                age_range=(4, 10),
                duration_minutes=15,
                difficulty_level="medium",
                required_objects=["floor_space"],
                learning_objectives=["تعلم أسماء الحيوانات", "فهم بيئات الحيوانات", "تطوير التفكير العلمي"],
                safety_requirements=["مساحة آمنة 3x3 متر", "تجنب الحركة السريعة"],
                ar_models={"animals": "3d_animals_pack.obj", "environments": "habitats.fbx"},
                interaction_points=[
                    {"type": "gesture", "object": "animal", "action": "show_info"},
                    {"type": "voice", "trigger": "animal_sound", "response": "play_animal_sound"}
                ]
            )
        ]
        
        # بيئات الواقع الافتراضي
        educational_vr = [
            VREnvironment(
                environment_id="vr_space",
                name="رحلة إلى الفضاء",
                theme="space",
                description="استكشاف النظام الشمسي والكواكب",
                immersion_level="medium",
                movement_type="limited",
                educational_content={
                    "planets": ["معلومات عن الكواكب", "حجم الكواكب", "المسافات"],
                    "solar_system": ["الشمس", "القمر", "النجوم"],
                    "space_exploration": ["المركبات الفضائية", "رواد الفضاء"]
                },
                interactive_elements=[
                    {"type": "planet_selection", "action": "show_planet_info"},
                    {"type": "spacecraft_control", "action": "navigate_space"},
                    {"type": "quiz_mode", "action": "test_knowledge"}
                ]
            ),
            VREnvironment(
                environment_id="vr_underwater",
                name="عالم المحيط السحري",
                theme="underwater",
                description="استكشاف أعماق المحيط والحياة البحرية",
                immersion_level="high",
                movement_type="limited",
                educational_content={
                    "sea_creatures": ["الأسماك", "المرجان", "الحيتان"],
                    "ocean_layers": ["السطح", "الأعماق", "القاع"],
                    "ecosystem": ["السلسلة الغذائية", "التوازن البيئي"]
                },
                interactive_elements=[
                    {"type": "creature_interaction", "action": "learn_about_creature"},
                    {"type": "diving_simulation", "action": "explore_depths"},
                    {"type": "conservation_game", "action": "protect_ocean"}
                ]
            )
        ]
        
        # إضافة التجارب للمجموعات
        for exp in educational_ar:
            self.ar_experiences[exp.experience_id] = exp
        
        for env in educational_vr:
            self.vr_environments[env.environment_id] = env
    
    def _load_data(self) -> Any:
        """تحميل البيانات من الملفات"""
        try:
            # تحميل تجارب AR
            ar_file = self.data_dir / "ar_experiences.json"
            if ar_file.exists():
                with open(ar_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for exp_id, exp_data in data.items():
                        if exp_id not in self.ar_experiences:  # تجنب استبدال الافتراضية
                            self.ar_experiences[exp_id] = ARExperience(**exp_data)
            
            # تحميل بيئات VR
            vr_file = self.data_dir / "vr_environments.json"
            if vr_file.exists():
                with open(vr_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for env_id, env_data in data.items():
                        if env_id not in self.vr_environments:
                            self.vr_environments[env_id] = VREnvironment(**env_data)
            
            # تحميل جلسات المستخدمين
            sessions_file = self.data_dir / "user_sessions.json"
            if sessions_file.exists():
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    self.user_sessions = json.load(f)
            
            # تحميل تفضيلات الأطفال
            preferences_file = self.data_dir / "child_preferences.json"
            if preferences_file.exists():
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    self.child_preferences = json.load(f)
                    
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات AR/VR: {e}")
    
    def _save_data(self) -> Any:
        """حفظ البيانات في الملفات"""
        try:
            # حفظ تجارب AR (المخصصة فقط)
            ar_file = self.data_dir / "ar_experiences.json"
            custom_ar = {
                exp_id: asdict(exp) for exp_id, exp in self.ar_experiences.items() 
                if not exp_id.startswith("ar_")  # تجنب حفظ الافتراضية
            }
            with open(ar_file, 'w', encoding='utf-8') as f:
                json.dump(custom_ar, f, ensure_ascii=False, indent=2)
            
            # حفظ بيئات VR (المخصصة فقط)
            vr_file = self.data_dir / "vr_environments.json"
            custom_vr = {
                env_id: asdict(env) for env_id, env in self.vr_environments.items() 
                if not env_id.startswith("vr_")
            }
            with open(vr_file, 'w', encoding='utf-8') as f:
                json.dump(custom_vr, f, ensure_ascii=False, indent=2)
            
            # حفظ جلسات المستخدمين
            sessions_file = self.data_dir / "user_sessions.json"
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_sessions, f, ensure_ascii=False, indent=2)
            
            # حفظ تفضيلات الأطفال
            preferences_file = self.data_dir / "child_preferences.json"
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.child_preferences, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات AR/VR: {e}")
    
    def get_available_ar_experiences(self, child_age: int = None, difficulty: str = None) -> List[ARExperience]:
        """الحصول على تجارب الواقع المعزز المتاحة"""
        experiences = list(self.ar_experiences.values())
        
        if child_age:
            experiences = [exp for exp in experiences 
                         if exp.age_range[0] <= child_age <= exp.age_range[1]]
        
        if difficulty:
            experiences = [exp for exp in experiences if exp.difficulty_level == difficulty]
        
        return experiences
    
    def get_available_vr_environments(self, child_age: int = None, theme: str = None) -> List[VREnvironment]:
        """الحصول على بيئات الواقع الافتراضي المتاحة"""
        environments = list(self.vr_environments.values())
        
        # تصفية حسب العمر (افتراض أن VR مناسب للأطفال 6+ سنوات)
        if child_age:
            if child_age < 6:
                return []  # VR غير مناسب للأطفال الصغار
            elif child_age < 10:
                environments = [env for env in environments if env.immersion_level in ["low", "medium"]]
        
        if theme:
            environments = [env for env in environments if env.theme == theme]
        
        return environments
    
    def start_ar_session(self, child_id: str, experience_id: str) -> Dict:
        """بدء جلسة واقع معزز"""
        experience = self.ar_experiences.get(experience_id)
        if not experience:
            return {"error": "التجربة غير موجودة"}
        
        # التحقق من متطلبات الأمان
        safety_check = self._check_ar_safety_requirements(experience)
        if not safety_check["safe"]:
            return {"error": "متطلبات الأمان غير مستوفاة", "details": safety_check["issues"]}
        
        # إنشاء جلسة جديدة
        session = {
            "session_id": f"ar_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "child_id": child_id,
            "experience_id": experience_id,
            "type": "ar",
            "start_time": datetime.now().isoformat(),
            "duration_minutes": experience.duration_minutes,
            "status": "active",
            "interaction_log": [],
            "learning_progress": {},
            "safety_alerts": []
        }
        
        # حفظ الجلسة
        if child_id not in self.user_sessions:
            self.user_sessions[child_id] = []
        self.user_sessions[child_id].append(session)
        
        self._save_data()
        
        # إرجاع معلومات بدء الجلسة
        return {
            "session_id": session["session_id"],
            "experience": asdict(experience),
            "setup_instructions": self._get_ar_setup_instructions(experience),
            "safety_reminders": experience.safety_requirements,
            "estimated_duration": experience.duration_minutes
        }
    
    def start_vr_session(self, child_id: str, environment_id: str, child_age: int) -> Dict:
        """بدء جلسة واقع افتراضي"""
        environment = self.vr_environments.get(environment_id)
        if not environment:
            return {"error": "البيئة غير موجودة"}
        
        # التحقق من العمر المناسب
        if child_age < 6:
            return {"error": "الواقع الافتراضي غير مناسب للأطفال تحت 6 سنوات"}
        
        # تكييف الإعدادات حسب العمر
        adapted_settings = self._adapt_vr_for_age(environment, child_age)
        
        # إنشاء جلسة جديدة
        session = {
            "session_id": f"vr_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "child_id": child_id,
            "environment_id": environment_id,
            "type": "vr",
            "start_time": datetime.now().isoformat(),
            "max_duration": adapted_settings["max_duration"],
            "comfort_settings": adapted_settings["comfort_settings"],
            "status": "active",
            "interaction_log": [],
            "comfort_breaks": [],
            "learning_achievements": []
        }
        
        # حفظ الجلسة
        if child_id not in self.user_sessions:
            self.user_sessions[child_id] = []
        self.user_sessions[child_id].append(session)
        
        self._save_data()
        
        return {
            "session_id": session["session_id"],
            "environment": asdict(environment),
            "adapted_settings": adapted_settings,
            "safety_guidelines": self._get_vr_safety_guidelines(child_age),
            "comfort_reminders": self._get_vr_comfort_reminders()
        }
    
    def _check_ar_safety_requirements(self, experience: ARExperience) -> Dict:
        """فحص متطلبات الأمان للواقع المعزز"""
        safety_check = {"safe": True, "issues": []}
        
        # فحص المساحة المطلوبة
        for requirement in experience.safety_requirements:
            if "مساحة" in requirement:
                # في التطبيق الحقيقي، سيتم فحص المساحة باستخدام الكاميرا
                safety_check["issues"].append(f"تأكد من توفر {requirement}")
        
        # فحص الأجسام المطلوبة
        if experience.required_objects:
            safety_check["issues"].append(f"تأكد من وجود: {', '.join(experience.required_objects)}")
        
        return safety_check
    
    def _adapt_vr_for_age(self, environment: VREnvironment, child_age: int) -> Dict:
        """تكييف إعدادات VR حسب العمر"""
        adapted = {
            "max_duration": environment.safety_boundaries["max_session_time"],
            "break_intervals": environment.safety_boundaries["break_intervals"],
            "comfort_settings": environment.comfort_settings.copy()
        }
        
        if child_age < 8:
            adapted["max_duration"] = min(adapted["max_duration"], 10)  # 10 دقائق كحد أقصى
            adapted["break_intervals"] = 3  # راحة كل 3 دقائق
            adapted["comfort_settings"]["motion_reduction"] = True
            adapted["comfort_settings"]["simplified_interface"] = True
        elif child_age < 12:
            adapted["max_duration"] = min(adapted["max_duration"], 15)
            adapted["break_intervals"] = 5
        
        return adapted
    
    def _get_ar_setup_instructions(self, experience: ARExperience) -> List[str]:
        """تعليمات إعداد الواقع المعزز"""
        instructions = [
            "تأكد من وجود إضاءة جيدة في المكان",
            "امسك الجهاز بثبات على مسافة مناسبة",
            "تأكد من وجود مساحة كافية للحركة الآمنة"
        ]
        
        if experience.required_objects:
            instructions.append(f"ضع الأجسام التالية في مجال الرؤية: {', '.join(experience.required_objects)}")
        
        if "مساحة" in str(experience.safety_requirements):
            instructions.append("تأكد من خلو المساحة من العوائق")
        
        return instructions
    
    def _get_vr_safety_guidelines(self, child_age: int) -> List[str]:
        """إرشادات الأمان للواقع الافتراضي"""
        guidelines = [
            "تأكد من وجود إشراف بالغ دائم",
            "خذ راحة كل 5 دقائق",
            "توقف فوراً إذا شعرت بدوار أو غثيان",
            "تأكد من أن المساحة خالية من العوائق",
            "لا تستخدم VR أكثر من 15 دقيقة متواصلة"
        ]
        
        if child_age < 8:
            guidelines.extend([
                "استخدم أقل إعدادات الحركة",
                "راحة كل 3 دقائق",
                "مدة قصوى 10 دقائق"
            ])
        
        return guidelines
    
    def _get_vr_comfort_reminders(self) -> List[str]:
        """تذكيرات الراحة للواقع الافتراضي"""
        return [
            "ارمش عينيك بشكل طبيعي",
            "اجلس إذا شعرت بالتعب",
            "اشرب الماء بانتظام",
            "تحرك ببطء وتجنب الحركات المفاجئة",
            "أخبر الكبار إذا شعرت بأي إزعاج"
        ]
    
    def log_interaction(Dict) -> None:
        """تسجيل تفاعل في الجلسة"""
        # البحث عن الجلسة
        for child_id, sessions in self.user_sessions.items():
            for session in sessions:
                if session["session_id"] == session_id:
                    interaction_data["timestamp"] = datetime.now().isoformat()
                    session["interaction_log"].append(interaction_data)
                    
                    # تحديث التقدم التعليمي
                    if interaction_data.get("learning_objective"):
                        objective = interaction_data["learning_objective"]
                        if objective not in session["learning_progress"]:
                            session["learning_progress"][objective] = 0
                        session["learning_progress"][objective] += 1
                    
                    self._save_data()
                    return True
        
        return False
    
    def end_session(self, session_id: str) -> Dict:
        """إنهاء جلسة AR/VR"""
        # البحث عن الجلسة وإنهاؤها
        for child_id, sessions in self.user_sessions.items():
            for session in sessions:
                if session["session_id"] == session_id and session["status"] == "active":
                    session["status"] = "completed"
                    session["end_time"] = datetime.now().isoformat()
                    
                    # حساب المدة الفعلية
                    start_time = datetime.fromisoformat(session["start_time"])
                    end_time = datetime.fromisoformat(session["end_time"])
                    actual_duration = (end_time - start_time).total_seconds() / 60
                    session["actual_duration_minutes"] = actual_duration
                    
                    # تحليل الأداء
                    performance_summary = self._analyze_session_performance(session)
                    session["performance_summary"] = performance_summary
                    
                    # تحديث تفضيلات الطفل
                    self._update_child_preferences(child_id, session)
                    
                    self._save_data()
                    
                    return {
                        "session_summary": performance_summary,
                        "learning_achievements": session.get("learning_progress", {}),
                        "total_interactions": len(session["interaction_log"]),
                        "duration_minutes": actual_duration,
                        "recommendations": self._get_session_recommendations(session)
                    }
        
        return {"error": "الجلسة غير موجودة أو منتهية بالفعل"}
    
    def _analyze_session_performance(self, session: Dict) -> Dict:
        """تحليل أداء الجلسة"""
        interactions = session["interaction_log"]
        
        performance = {
            "engagement_level": "medium",
            "learning_effectiveness": "good",
            "comfort_level": "high",
            "technical_issues": 0
        }
        
        if interactions:
            # تحليل مستوى التفاعل
            interaction_rate = len(interactions) / max(session.get("actual_duration_minutes", 1), 1)
            if interaction_rate > 3:
                performance["engagement_level"] = "high"
            elif interaction_rate < 1:
                performance["engagement_level"] = "low"
            
            # تحليل المشاكل التقنية
            technical_issues = sum(1 for interaction in interactions 
                                 if interaction.get("type") == "error")
            performance["technical_issues"] = technical_issues
            
            # تحليل مؤشرات عدم الراحة
            comfort_issues = sum(1 for interaction in interactions 
                               if interaction.get("comfort_issue", False))
            if comfort_issues > 0:
                performance["comfort_level"] = "medium" if comfort_issues < 3 else "low"
        
        return performance
    
    def _update_child_preferences(Dict) -> None:
        """تحديث تفضيلات الطفل"""
        if child_id not in self.child_preferences:
            self.child_preferences[child_id] = {
                "preferred_ar_categories": {},
                "preferred_vr_themes": {},
                "optimal_session_duration": 10,
                "comfort_settings": {}
            }
        
        prefs = self.child_preferences[child_id]
        
        # تحديث التفضيلات بناءً على نوع الجلسة
        if session["type"] == "ar":
            experience = self.ar_experiences.get(session["experience_id"])
            if experience:
                category = experience.category
                if category not in prefs["preferred_ar_categories"]:
                    prefs["preferred_ar_categories"][category] = 0
                
                # زيادة النقاط بناءً على الأداء
                performance = session.get("performance_summary", {})
                if performance.get("engagement_level") == "high":
                    prefs["preferred_ar_categories"][category] += 2
                elif performance.get("engagement_level") == "medium":
                    prefs["preferred_ar_categories"][category] += 1
        
        elif session["type"] == "vr":
            environment = self.vr_environments.get(session["environment_id"])
            if environment:
                theme = environment.theme
                if theme not in prefs["preferred_vr_themes"]:
                    prefs["preferred_vr_themes"][theme] = 0
                
                performance = session.get("performance_summary", {})
                if performance.get("engagement_level") == "high":
                    prefs["preferred_vr_themes"][theme] += 2
                elif performance.get("engagement_level") == "medium":
                    prefs["preferred_vr_themes"][theme] += 1
        
        # تحديث المدة المثلى
        actual_duration = session.get("actual_duration_minutes", 10)
        performance = session.get("performance_summary", {})
        
        if performance.get("comfort_level") == "high" and performance.get("engagement_level") in ["medium", "high"]:
            prefs["optimal_session_duration"] = (prefs["optimal_session_duration"] + actual_duration) / 2
    
    def _get_session_recommendations(self, session: Dict) -> List[str]:
        """الحصول على توصيات بناءً على الجلسة"""
        recommendations = []
        
        performance = session.get("performance_summary", {})
        
        if performance.get("engagement_level") == "low":
            recommendations.append("جرب تجربة أكثر تفاعلية في المرة القادمة")
        
        if performance.get("comfort_level") == "low":
            recommendations.append("خذ راحات أكثر تكراراً")
            recommendations.append("قلل من مدة الجلسة")
        
        if performance.get("technical_issues", 0) > 2:
            recommendations.append("تحقق من جودة الاتصال والإضاءة")
        
        if session.get("actual_duration_minutes", 0) > 15:
            recommendations.append("حاول تقليل مدة الجلسة للحفاظ على الراحة")
        
        return recommendations
    
    def get_child_ar_vr_report(self, child_id: str) -> Dict:
        """تقرير شامل لاستخدام الطفل لـ AR/VR"""
        sessions = self.user_sessions.get(child_id, [])
        preferences = self.child_preferences.get(child_id, {})
        
        if not sessions:
            return {"message": "لا توجد جلسات مسجلة لهذا الطفل"}
        
        # إحصائيات عامة
        ar_sessions = [s for s in sessions if s["type"] == "ar"]
        vr_sessions = [s for s in sessions if s["type"] == "vr"]
        
        total_time_ar = sum(s.get("actual_duration_minutes", 0) for s in ar_sessions)
        total_time_vr = sum(s.get("actual_duration_minutes", 0) for s in vr_sessions)
        
        report = {
            "summary": {
                "total_ar_sessions": len(ar_sessions),
                "total_vr_sessions": len(vr_sessions),
                "total_time_ar_minutes": total_time_ar,
                "total_time_vr_minutes": total_time_vr,
                "average_session_duration": (total_time_ar + total_time_vr) / len(sessions) if sessions else 0
            },
            "preferences": preferences,
            "learning_progress": self._calculate_learning_progress(sessions),
            "safety_compliance": self._assess_safety_compliance(sessions),
            "recommendations": self._generate_personalized_recommendations(child_id, sessions, preferences)
        }
        
        return report
    
    def _calculate_learning_progress(self, sessions: List[Dict]) -> Dict:
        """حساب التقدم التعليمي"""
        all_objectives = {}
        
        for session in sessions:
            for objective, count in session.get("learning_progress", {}).items():
                if objective not in all_objectives:
                    all_objectives[objective] = 0
                all_objectives[objective] += count
        
        return {
            "mastered_objectives": [obj for obj, count in all_objectives.items() if count >= 5],
            "learning_objectives": all_objectives,
            "total_learning_interactions": sum(all_objectives.values())
        }
    
    def _assess_safety_compliance(self, sessions: List[Dict]) -> Dict:
        """تقييم الالتزام بمعايير الأمان"""
        safety_assessment = {
            "average_session_duration": 0,
            "comfort_issues_count": 0,
            "technical_issues_count": 0,
            "safety_score": "excellent"
        }
        
        if sessions:
            total_duration = sum(s.get("actual_duration_minutes", 0) for s in sessions)
            safety_assessment["average_session_duration"] = total_duration / len(sessions)
            
            comfort_issues = sum(s.get("performance_summary", {}).get("comfort_level") == "low" for s in sessions)
            technical_issues = sum(s.get("performance_summary", {}).get("technical_issues", 0) for s in sessions)
            
            safety_assessment["comfort_issues_count"] = comfort_issues
            safety_assessment["technical_issues_count"] = technical_issues
            
            # تقييم النتيجة
            if comfort_issues > len(sessions) * 0.3 or technical_issues > len(sessions) * 2:
                safety_assessment["safety_score"] = "needs_improvement"
            elif comfort_issues > 0 or technical_issues > 0:
                safety_assessment["safety_score"] = "good"
        
        return safety_assessment
    
    def _generate_personalized_recommendations(self, child_id: str, sessions: List[Dict], preferences: Dict) -> List[str]:
        """توليد توصيات مخصصة"""
        recommendations = []
        
        # توصيات بناءً على التفضيلات
        if preferences.get("preferred_ar_categories"):
            top_ar_category = max(preferences["preferred_ar_categories"].items(), key=lambda x: x[1])[0]
            recommendations.append(f"يفضل الطفل تجارب الواقع المعزز من فئة: {top_ar_category}")
        
        if preferences.get("preferred_vr_themes"):
            top_vr_theme = max(preferences["preferred_vr_themes"].items(), key=lambda x: x[1])[0]
            recommendations.append(f"يفضل الطفل بيئات الواقع الافتراضي بموضوع: {top_vr_theme}")
        
        # توصيات بناءً على الأداء
        recent_sessions = sessions[-5:]  # آخر 5 جلسات
        
        if recent_sessions:
            avg_engagement = sum(
                1 if s.get("performance_summary", {}).get("engagement_level") == "high" else 0.5 if s.get("performance_summary", {}).get("engagement_level") == "medium" else 0
                for s in recent_sessions
            ) / len(recent_sessions)
            
            if avg_engagement < 0.3:
                recommendations.append("جرب تجارب أكثر تفاعلية أو قصر مدة الجلسات")
            elif avg_engagement > 0.7:
                recommendations.append("الطفل يظهر انخراطاً عالياً - يمكن تجربة تجارب أكثر تحدياً")
        
        # توصيات الأمان
        optimal_duration = preferences.get("optimal_session_duration", 10)
        if optimal_duration > 15:
            recommendations.append("احرص على أخذ راحات أكثر تكراراً")
        
        return recommendations 