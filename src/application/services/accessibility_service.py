#!/usr/bin/env python3
"""
♿ خدمة الوصولية ودعم ذوي الاحتياجات الخاصة
تخصيص التجربة للأطفال من ذوي الاحتياجات الخاصة والتعلم المختلف
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class SpecialNeedType(Enum):
    """أنواع الاحتياجات الخاصة"""
    AUTISM = "autism"  # التوحد
    ADHD = "adhd"  # فرط الحركة وتشتت الانتباه
    SPEECH_DELAY = "speech_delay"  # تأخر النطق
    HEARING_IMPAIRED = "hearing_impaired"  # ضعف السمع
    VISUAL_IMPAIRED = "visual_impaired"  # ضعف البصر
    LEARNING_DISABILITY = "learning_disability"  # صعوبات التعلم
    DYSLEXIA = "dyslexia"  # عسر القراءة
    DOWN_SYNDROME = "down_syndrome"  # متلازمة داون
    CEREBRAL_PALSY = "cerebral_palsy"  # الشلل الدماغي
    SENSORY_PROCESSING = "sensory_processing"  # اضطراب المعالجة الحسية

@dataclass
class AccessibilityProfile:
    """ملف الوصولية للطفل"""
    child_id: str
    special_needs: List[str] = None  # قائمة الاحتياجات الخاصة
    communication_level: str = "verbal"  # verbal, non_verbal, limited_verbal
    attention_span: int = 5  # بالدقائق
    sensory_preferences: Dict[str, str] = None  # تفضيلات حسية
    learning_adaptations: Dict[str, Any] = None  # تكييفات التعلم
    behavioral_triggers: List[str] = None  # محفزات السلوك
    calming_strategies: List[str] = None  # استراتيجيات التهدئة
    support_level: str = "minimal"  # minimal, moderate, intensive
    communication_aids: List[str] = None  # وسائل التواصل المساعدة
    last_updated: str = ""
    
    def __post_init__(self):
        if self.special_needs is None:
            self.special_needs = []
        if self.sensory_preferences is None:
            self.sensory_preferences = {
                "sound_level": "normal",  # quiet, normal, loud
                "visual_stimulation": "normal",  # minimal, normal, high
                "interaction_pace": "normal"  # slow, normal, fast
            }
        if self.learning_adaptations is None:
            self.learning_adaptations = {
                "repeat_instructions": False,
                "visual_cues": False,
                "simplified_language": False,
                "extended_response_time": False,
                "structured_routine": False
            }
        if self.behavioral_triggers is None:
            self.behavioral_triggers = []
        if self.calming_strategies is None:
            self.calming_strategies = []
        if self.communication_aids is None:
            self.communication_aids = []

@dataclass
class AdaptiveContent:
    """محتوى متكيف للاحتياجات الخاصة"""
    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str  # visual, auditory, cognitive, behavioral
    target_needs: List[str]
    effectiveness_score: float = 0.0
    usage_count: int = 0

class AccessibilityService:
    """خدمة الوصولية"""
    
    def __init__(self, data_dir: str = "data/accessibility"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.accessibility_profiles: Dict[str, AccessibilityProfile] = {}
        self.adaptive_content_library: Dict[str, List[AdaptiveContent]] = {}
        self.interaction_adaptations: Dict[str, Dict] = {}
        
        # قوالب التكييف للأنواع المختلفة
        self.adaptation_templates = self._load_adaptation_templates()
        
        self._load_data()
    
    def _load_adaptation_templates(self) -> Dict:
        """تحميل قوالب التكييف"""
        return {
            "autism": {
                "communication": {
                    "use_simple_language": True,
                    "provide_visual_supports": True,
                    "maintain_routine": True,
                    "avoid_sudden_changes": True,
                    "use_clear_structure": True
                },
                "sensory": {
                    "reduce_background_noise": True,
                    "soft_lighting": True,
                    "avoid_overwhelming_stimuli": True,
                    "provide_sensory_breaks": True
                },
                "behavioral": {
                    "use_positive_reinforcement": True,
                    "provide_warnings_for_transitions": True,
                    "offer_choices": True,
                    "maintain_predictability": True
                }
            },
            "adhd": {
                "attention": {
                    "break_tasks_into_small_steps": True,
                    "use_frequent_breaks": True,
                    "minimize_distractions": True,
                    "provide_immediate_feedback": True
                },
                "engagement": {
                    "use_interactive_activities": True,
                    "incorporate_movement": True,
                    "vary_activity_types": True,
                    "use_timers": True
                }
            },
            "speech_delay": {
                "communication": {
                    "use_visual_cues": True,
                    "provide_extra_time": True,
                    "model_correct_speech": True,
                    "use_gestures": True,
                    "encourage_attempts": True
                },
                "activities": {
                    "focus_on_sounds": True,
                    "use_songs_and_rhymes": True,
                    "practice_simple_words": True
                }
            },
            "hearing_impaired": {
                "communication": {
                    "use_visual_communication": True,
                    "provide_captions": True,
                    "use_sign_language": True,
                    "face_the_child": True
                },
                "content": {
                    "emphasize_visual_elements": True,
                    "use_vibrations": True,
                    "provide_written_instructions": True
                }
            },
            "visual_impaired": {
                "communication": {
                    "use_clear_audio": True,
                    "describe_visual_elements": True,
                    "use_tactile_elements": True,
                    "provide_audio_cues": True
                },
                "navigation": {
                    "use_consistent_layout": True,
                    "provide_audio_navigation": True,
                    "use_high_contrast": True
                }
            },
            "learning_disability": {
                "instruction": {
                    "use_multi_sensory_approach": True,
                    "provide_repetition": True,
                    "break_down_complex_tasks": True,
                    "use_concrete_examples": True
                },
                "support": {
                    "provide_extra_time": True,
                    "offer_alternative_formats": True,
                    "use_memory_aids": True
                }
            }
        }
    
    def _load_data(self) -> Any:
        """تحميل البيانات من الملفات"""
        try:
            # تحميل ملفات الوصولية
            profiles_file = self.data_dir / "accessibility_profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for child_id, profile_data in data.items():
                        self.accessibility_profiles[child_id] = AccessibilityProfile(**profile_data)
            
            # تحميل المحتوى المتكيف
            content_file = self.data_dir / "adaptive_content.json"
            if content_file.exists():
                with open(content_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for content_type, contents in data.items():
                        self.adaptive_content_library[content_type] = [
                            AdaptiveContent(**content) for content in contents
                        ]
            
            # تحميل تكييفات التفاعل
            adaptations_file = self.data_dir / "interaction_adaptations.json"
            if adaptations_file.exists():
                with open(adaptations_file, 'r', encoding='utf-8') as f:
                    self.interaction_adaptations = json.load(f)
                    
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات الوصولية: {e}")
    
    def _save_data(self) -> Any:
        """حفظ البيانات في الملفات"""
        try:
            # حفظ ملفات الوصولية
            profiles_file = self.data_dir / "accessibility_profiles.json"
            profiles_data = {
                child_id: asdict(profile) 
                for child_id, profile in self.accessibility_profiles.items()
            }
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, ensure_ascii=False, indent=2)
            
            # حفظ المحتوى المتكيف
            content_file = self.data_dir / "adaptive_content.json"
            content_data = {
                content_type: [asdict(content) for content in contents]
                for content_type, contents in self.adaptive_content_library.items()
            }
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)
            
            # حفظ تكييفات التفاعل
            adaptations_file = self.data_dir / "interaction_adaptations.json"
            with open(adaptations_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_adaptations, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات الوصولية: {e}")
    
    def create_accessibility_profile(self, child_id: str, special_needs: List[str], 
                                   communication_level: str = "verbal") -> AccessibilityProfile:
        """إنشاء ملف وصولية للطفل"""
        profile = AccessibilityProfile(
            child_id=child_id,
            special_needs=special_needs,
            communication_level=communication_level,
            last_updated=datetime.now().isoformat()
        )
        
        # تطبيق الإعدادات الافتراضية بناءً على نوع الاحتياجات
        for need in special_needs:
            if need in self.adaptation_templates:
                self._apply_default_adaptations(profile, need)
        
        self.accessibility_profiles[child_id] = profile
        self._save_data()
        
        logger.info(f"تم إنشاء ملف وصولية للطفل {child_id} مع الاحتياجات: {special_needs}")
        return profile
    
    def _apply_default_adaptations(self, profile -> Any: AccessibilityProfile, need_type -> Any: str) -> Any:
        """تطبيق التكييفات الافتراضية"""
        template = self.adaptation_templates.get(need_type, {})
        
        # تكييفات التعلم
        if "attention" in template:
            attention_settings = template["attention"]
            if attention_settings.get("break_tasks_into_small_steps"):
                profile.learning_adaptations["repeat_instructions"] = True
            if attention_settings.get("use_frequent_breaks"):
                profile.attention_span = min(profile.attention_span, 10)
        
        # التفضيلات الحسية
        if "sensory" in template:
            sensory_settings = template["sensory"]
            if sensory_settings.get("reduce_background_noise"):
                profile.sensory_preferences["sound_level"] = "quiet"
            if sensory_settings.get("avoid_overwhelming_stimuli"):
                profile.sensory_preferences["visual_stimulation"] = "minimal"
        
        # التواصل
        if "communication" in template:
            comm_settings = template["communication"]
            if comm_settings.get("use_simple_language"):
                profile.learning_adaptations["simplified_language"] = True
            if comm_settings.get("provide_extra_time"):
                profile.learning_adaptations["extended_response_time"] = True
            if comm_settings.get("use_visual_supports"):
                profile.learning_adaptations["visual_cues"] = True
            if comm_settings.get("use_visual_communication"):
                profile.communication_aids.append("visual_symbols")
            if comm_settings.get("use_sign_language"):
                profile.communication_aids.append("sign_language")
    
    def get_accessibility_profile(self, child_id: str) -> Optional[AccessibilityProfile]:
        """الحصول على ملف الوصولية"""
        return self.accessibility_profiles.get(child_id)
    
    def adapt_content(self, child_id: str, original_content: Dict) -> Dict:
        """تكييف المحتوى للطفل"""
        profile = self.get_accessibility_profile(child_id)
        if not profile:
            return original_content
        
        adapted_content = original_content.copy()
        
        # تكييف النص
        if profile.learning_adaptations.get("simplified_language"):
            adapted_content = self._simplify_language(adapted_content)
        
        # تكييف التفاعل
        if profile.learning_adaptations.get("extended_response_time"):
            adapted_content["response_timeout"] = adapted_content.get("response_timeout", 30) * 2
        
        # تكييف المحتوى المرئي
        if profile.sensory_preferences["visual_stimulation"] == "minimal":
            adapted_content = self._reduce_visual_stimulation(adapted_content)
        
        # تكييف المحتوى الصوتي
        if profile.sensory_preferences["sound_level"] == "quiet":
            adapted_content = self._adjust_audio_level(adapted_content)
        
        # إضافة دعائم بصرية
        if profile.learning_adaptations.get("visual_cues"):
            adapted_content = self._add_visual_cues(adapted_content)
        
        # تكييف للتوحد
        if "autism" in profile.special_needs:
            adapted_content = self._adapt_for_autism(adapted_content, profile)
        
        # تكييف لفرط الحركة
        if "adhd" in profile.special_needs:
            adapted_content = self._adapt_for_adhd(adapted_content, profile)
        
        # تكييف لتأخر النطق
        if "speech_delay" in profile.special_needs:
            adapted_content = self._adapt_for_speech_delay(adapted_content, profile)
        
        # تكييف لضعف السمع
        if "hearing_impaired" in profile.special_needs:
            adapted_content = self._adapt_for_hearing_impaired(adapted_content, profile)
        
        # تكييف لضعف البصر
        if "visual_impaired" in profile.special_needs:
            adapted_content = self._adapt_for_visual_impaired(adapted_content, profile)
        
        return adapted_content
    
    def _simplify_language(self, content: Dict) -> Dict:
        """تبسيط اللغة"""
        # قاموس المرادفات البسيطة
        simple_replacements = {
            "استكشف": "انظر",
            "مغامرة": "رحلة",
            "رائع": "جميل",
            "مذهل": "جيد جداً",
            "اكتشف": "اعرف",
            "تحدي": "لعبة صعبة",
            "مهارة": "شيء تتعلمه"
        }
        
        if "text" in content:
            text = content["text"]
            for complex_word, simple_word in simple_replacements.items():
                text = text.replace(complex_word, simple_word)
            content["text"] = text
        
        if "instructions" in content:
            instructions = content["instructions"]
            # تقسيم التعليمات إلى خطوات أصغر
            if len(instructions) > 50:  # إذا كانت التعليمات طويلة
                content["instructions"] = instructions[:50] + "..."
                content["simplified"] = True
        
        return content
    
    def _reduce_visual_stimulation(self, content: Dict) -> Dict:
        """تقليل التحفيز البصري"""
        content["visual_style"] = "minimal"
        content["animation_speed"] = "slow"
        content["color_scheme"] = "soft"
        content["background_complexity"] = "simple"
        return content
    
    def _adjust_audio_level(self, content: Dict) -> Dict:
        """ضبط مستوى الصوت"""
        content["audio_volume"] = 0.7  # تقليل مستوى الصوت
        content["background_music"] = False  # إزالة الموسيقى في الخلفية
        content["sound_effects"] = "minimal"  # تقليل المؤثرات الصوتية
        return content
    
    def _add_visual_cues(self, content: Dict) -> Dict:
        """إضافة دعائم بصرية"""
        content["visual_cues"] = {
            "show_instructions_visually": True,
            "use_icons": True,
            "highlight_important_elements": True,
            "use_progress_indicators": True
        }
        return content
    
    def _adapt_for_autism(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف للتوحد"""
        content["autism_adaptations"] = {
            "provide_structure": True,
            "use_routine": True,
            "avoid_sudden_changes": True,
            "offer_predictability": True,
            "use_clear_boundaries": True,
            "provide_transition_warnings": True
        }
        
        # تقليل فترة النشاط
        if "duration" in content:
            content["duration"] = min(content["duration"], profile.attention_span)
        
        # إضافة خيارات للتهدئة
        content["calming_options"] = {
            "allow_breaks": True,
            "provide_quiet_space": True,
            "offer_sensory_tools": True
        }
        
        return content
    
    def _adapt_for_adhd(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف لفرط الحركة وتشتت الانتباه"""
        content["adhd_adaptations"] = {
            "break_into_segments": True,
            "use_frequent_rewards": True,
            "minimize_distractions": True,
            "incorporate_movement": True,
            "provide_immediate_feedback": True
        }
        
        # تقسيم المحتوى إلى أجزاء صغيرة
        if "duration" in content and content["duration"] > 10:
            content["segments"] = content["duration"] // 5  # تقسيم كل 5 دقائق
            content["break_duration"] = 2  # دقيقتين راحة بين الأجزاء
        
        return content
    
    def _adapt_for_speech_delay(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف لتأخر النطق"""
        content["speech_adaptations"] = {
            "use_simple_vocabulary": True,
            "repeat_key_words": True,
            "model_correct_pronunciation": True,
            "encourage_attempts": True,
            "use_gestures": True,
            "provide_extra_response_time": True
        }
        
        # زيادة وقت الاستجابة
        if "response_timeout" in content:
            content["response_timeout"] *= 3
        
        return content
    
    def _adapt_for_hearing_impaired(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف لضعف السمع"""
        content["hearing_adaptations"] = {
            "provide_captions": True,
            "use_visual_alerts": True,
            "emphasize_visual_communication": True,
            "provide_sign_language": True,
            "use_vibration_cues": True
        }
        
        # إضافة ترجمة بصرية
        if "audio_content" in content:
            content["visual_transcript"] = True
            content["sign_language_video"] = True
        
        return content
    
    def _adapt_for_visual_impaired(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف لضعف البصر"""
        content["visual_adaptations"] = {
            "provide_audio_description": True,
            "use_high_contrast": True,
            "increase_text_size": True,
            "use_tactile_feedback": True,
            "provide_audio_navigation": True
        }
        
        # تحسين المحتوى الصوتي
        if "visual_elements" in content:
            content["audio_description"] = "وصف صوتي مفصل للعناصر البصرية"
        
        return content
    
    def get_interaction_guidelines(self, child_id: str) -> Dict:
        """الحصول على إرشادات التفاعل"""
        profile = self.get_accessibility_profile(child_id)
        if not profile:
            return {"guidelines": "لا توجد احتياجات خاصة محددة"}
        
        guidelines = {
            "communication_approach": self._get_communication_guidelines(profile),
            "behavioral_support": self._get_behavioral_guidelines(profile),
            "learning_support": self._get_learning_guidelines(profile),
            "sensory_considerations": self._get_sensory_guidelines(profile),
            "emergency_strategies": self._get_emergency_strategies(profile)
        }
        
        return guidelines
    
    def _get_communication_guidelines(self, profile: AccessibilityProfile) -> List[str]:
        """إرشادات التواصل"""
        guidelines = []
        
        if profile.communication_level == "non_verbal":
            guidelines.extend([
                "استخدم الإشارات والرموز البصرية",
                "امنح وقتاً إضافياً للاستجابة",
                "ابحث عن وسائل التواصل البديلة"
            ])
        elif profile.communication_level == "limited_verbal":
            guidelines.extend([
                "استخدم جمل قصيرة وبسيطة",
                "كرر المعلومات المهمة",
                "ادعم الكلام بالإشارات"
            ])
        
        if "autism" in profile.special_needs:
            guidelines.extend([
                "تحدث بوضوح وبطء",
                "تجنب المعاني المجازية",
                "استخدم التكرار والروتين"
            ])
        
        if "hearing_impaired" in profile.special_needs:
            guidelines.extend([
                "واجه الطفل عند التحدث",
                "استخدم الإشارات والكتابة",
                "تأكد من الإضاءة الجيدة"
            ])
        
        return guidelines
    
    def _get_behavioral_guidelines(self, profile: AccessibilityProfile) -> List[str]:
        """إرشادات السلوك"""
        guidelines = []
        
        if "autism" in profile.special_needs:
            guidelines.extend([
                "حافظ على الروتين والنظام",
                "قدم تحذيرات للتغييرات",
                "وفر بيئة هادئة ومنظمة",
                "استخدم التعزيز الإيجابي"
            ])
        
        if "adhd" in profile.special_needs:
            guidelines.extend([
                "قسم المهام إلى خطوات صغيرة",
                "وفر فترات راحة متكررة",
                "امدح الجهود المبذولة",
                "قلل من المشتتات"
            ])
        
        for trigger in profile.behavioral_triggers:
            guidelines.append(f"تجنب {trigger} - قد يسبب ضغطاً")
        
        return guidelines
    
    def _get_learning_guidelines(self, profile: AccessibilityProfile) -> List[str]:
        """إرشادات التعلم"""
        guidelines = []
        
        if profile.learning_adaptations.get("visual_cues"):
            guidelines.append("استخدم الصور والرموز لدعم التعلم")
        
        if profile.learning_adaptations.get("simplified_language"):
            guidelines.append("استخدم لغة بسيطة ومفردات مألوفة")
        
        if profile.learning_adaptations.get("repeat_instructions"):
            guidelines.append("كرر التعليمات وتأكد من الفهم")
        
        if profile.learning_adaptations.get("extended_response_time"):
            guidelines.append("امنح وقتاً إضافياً للتفكير والاستجابة")
        
        if profile.attention_span < 10:
            guidelines.append(f"اجعل الأنشطة قصيرة ({profile.attention_span} دقائق أو أقل)")
        
        return guidelines
    
    def _get_sensory_guidelines(self, profile: AccessibilityProfile) -> List[str]:
        """إرشادات حسية"""
        guidelines = []
        
        if profile.sensory_preferences["sound_level"] == "quiet":
            guidelines.append("خفف الأصوات وتجنب الضوضاء العالية")
        
        if profile.sensory_preferences["visual_stimulation"] == "minimal":
            guidelines.append("قلل من المثيرات البصرية والألوان الساطعة")
        
        if "sensory_processing" in profile.special_needs:
            guidelines.extend([
                "راقب علامات الحمل الحسي الزائد",
                "وفر بدائل حسية مهدئة",
                "احترم الحاجة للفواصل الحسية"
            ])
        
        return guidelines
    
    def _get_emergency_strategies(self, profile: AccessibilityProfile) -> List[str]:
        """استراتيجيات الطوارئ"""
        strategies = []
        
        for strategy in profile.calming_strategies:
            strategies.append(f"استخدم {strategy} للتهدئة")
        
        if "autism" in profile.special_needs:
            strategies.extend([
                "وفر مكاناً هادئاً للانسحاب",
                "استخدم الأشياء المألوفة للراحة",
                "تجنب الضغط للتفاعل الفوري"
            ])
        
        if "adhd" in profile.special_needs:
            strategies.extend([
                "اسمح بالحركة أو التململ",
                "قدم خيارات للنشاط البديل",
                "استخدم تقنيات التنفس"
            ])
        
        return strategies
    
    def assess_content_accessibility(self, content: Dict, target_needs: List[str]) -> Dict:
        """تقييم إمكانية الوصول للمحتوى"""
        accessibility_score = {
            "overall_score": 0.0,
            "category_scores": {},
            "recommendations": [],
            "compliance_issues": []
        }
        
        # تقييم فئات مختلفة
        categories = ["visual", "auditory", "cognitive", "motor", "communication"]
        
        for category in categories:
            score = self._evaluate_category_accessibility(content, category, target_needs)
            accessibility_score["category_scores"][category] = score
        
        # حساب النتيجة الإجمالية
        total_score = sum(accessibility_score["category_scores"].values())
        accessibility_score["overall_score"] = total_score / len(categories)
        
        # توليد التوصيات
        accessibility_score["recommendations"] = self._generate_accessibility_recommendations(
            accessibility_score["category_scores"], target_needs
        )
        
        return accessibility_score
    
    def _evaluate_category_accessibility(self, content: Dict, category: str, target_needs: List[str]) -> float:
        """تقييم إمكانية الوصول لفئة محددة"""
        score = 1.0
        
        if category == "visual" and "visual_impaired" in target_needs:
            if "audio_description" not in content:
                score -= 0.3
            if "high_contrast" not in content:
                score -= 0.2
            if "text_size" not in content or content.get("text_size", "normal") == "small":
                score -= 0.2
        
        elif category == "auditory" and "hearing_impaired" in target_needs:
            if "captions" not in content:
                score -= 0.4
            if "visual_alerts" not in content:
                score -= 0.3
            if "sign_language" not in content:
                score -= 0.3
        
        elif category == "cognitive" and any(need in target_needs for need in ["autism", "adhd", "learning_disability"]):
            if content.get("complexity", "medium") == "high":
                score -= 0.3
            if "clear_structure" not in content:
                score -= 0.2
            if content.get("duration", 30) > 15:
                score -= 0.2
        
        return max(0.0, score)
    
    def _generate_accessibility_recommendations(self, category_scores: Dict, target_needs: List[str]) -> List[str]:
        """توليد توصيات إمكانية الوصول"""
        recommendations = []
        
        for category, score in category_scores.items():
            if score < 0.7:  # إذا كانت النتيجة منخفضة
                if category == "visual":
                    recommendations.append("إضافة وصف صوتي للعناصر البصرية")
                    recommendations.append("استخدام تباين عالي للألوان")
                elif category == "auditory":
                    recommendations.append("إضافة ترجمة نصية للمحتوى الصوتي")
                    recommendations.append("استخدام إشارات بصرية")
                elif category == "cognitive":
                    recommendations.append("تبسيط اللغة والمفاهيم")
                    recommendations.append("تقسيم المحتوى إلى أجزاء أصغر")
        
        return recommendations
    
    def generate_accessibility_report(self, child_id: str) -> Dict:
        """توليد تقرير إمكانية الوصول"""
        profile = self.get_accessibility_profile(child_id)
        if not profile:
            return {"error": "لا يوجد ملف وصولية للطفل"}
        
        report = {
            "child_profile": asdict(profile),
            "interaction_guidelines": self.get_interaction_guidelines(child_id),
            "recommended_adaptations": self._get_recommended_adaptations(profile),
            "progress_tracking": self._get_progress_metrics(child_id),
            "family_resources": self._get_family_resources(profile.special_needs)
        }
        
        return report
    
    def _get_recommended_adaptations(self, profile: AccessibilityProfile) -> Dict:
        """الحصول على التكييفات الموصى بها"""
        adaptations = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }
        
        # تكييفات فورية
        if profile.learning_adaptations.get("simplified_language"):
            adaptations["immediate"].append("استخدام لغة مبسطة")
        
        if profile.sensory_preferences["sound_level"] == "quiet":
            adaptations["immediate"].append("تقليل مستوى الصوت")
        
        # تكييفات قصيرة المدى
        if profile.attention_span < 10:
            adaptations["short_term"].append("تطوير أنشطة قصيرة مخصصة")
        
        # تكييفات طويلة المدى
        if "speech_delay" in profile.special_needs:
            adaptations["long_term"].append("برنامج تطوير النطق التدريجي")
        
        return adaptations
    
    def _get_progress_metrics(self, child_id: str) -> Dict:
        """الحصول على مقاييس التقدم"""
        # هذا مكان لتتبع تقدم الطفل عبر الوقت
        return {
            "engagement_improvement": "تحسن بنسبة 15% في الانخراط",
            "communication_progress": "زيادة في استخدام الكلمات البسيطة",
            "attention_span_growth": "زيادة فترة التركيز من 5 إلى 8 دقائق",
            "behavioral_improvements": "تقليل نوبات الإحباط بنسبة 20%"
        }
    
    def _get_family_resources(self, special_needs: List[str]) -> List[Dict]:
        """الحصول على موارد للعائلة"""
        resources = []
        
        for need in special_needs:
            if need == "autism":
                resources.append({
                    "title": "دليل التوحد للأسر",
                    "description": "نصائح وأنشطة يومية للأطفال التوحديين",
                    "type": "guide"
                })
            elif need == "adhd":
                resources.append({
                    "title": "استراتيجيات إدارة فرط الحركة",
                    "description": "تقنيات عملية للمساعدة في التركيز",
                    "type": "strategy_guide"
                })
            elif need == "speech_delay":
                resources.append({
                    "title": "أنشطة تطوير النطق المنزلية",
                    "description": "تمارين بسيطة لتحسين النطق واللغة",
                    "type": "activity_guide"
                })
        
        return resources 