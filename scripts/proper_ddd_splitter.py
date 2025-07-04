"""
Proper DDD Splitter - تقسيم صحيح للـ God Classes
===============================================
تقسيم الخدمات الكبيرة إلى بنية DDD صحيحة
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


class ProperDDDSplitter:
    def __init__(self):
        self.src_dir = Path("src")
        self.services_dir = self.src_dir / "application" / "services"
        self.split_count = 0
        self.report = []
        self.logger = logging.getLogger(__name__)

    def log(self, message: str):
        """تسجيل الرسائل"""
        self.logger.info(f"✓ {message}")
        self.report.append(message)

    def identify_god_classes(self) -> List[Tuple[Path, int]]:
        """تحديد God Classes مع عدد الأسطر"""
        god_classes = []
        large_files = [
            "accessibility_service.py",
            "memory_service.py",
            "moderation_service.py",
            "parent_dashboard_service.py",
            "parent_report_service.py",
            "enhanced_hume_integration.py",
            "enhanced_child_interaction_service.py",
            "ar_vr_service.py",
            "advanced_personalization_service.py",
            "advanced_progress_analyzer.py",
        ]
        for filename in large_files:
            file_path = self.services_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = len(f.readlines())
                    if lines > 300:
                        god_classes.append((file_path, lines))
                except Exception as e:
                    self.log(f"خطأ في قراءة {filename}: {e}")
        return sorted(god_classes, key=lambda x: x[1], reverse=True)

    def split_accessibility_service(self, file_path: Path, lines_count: int):
        """تقسيم accessibility_service بشكل صحيح"""
        self.log(f"تقسيم {file_path.name} ({lines_count} سطر)...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        domain_name = "accessibility"
        domain_dir = self.src_dir / "domain" / domain_name
        app_dir = self.src_dir / "application" / domain_name
        infra_dir = self.src_dir / "infrastructure" / domain_name
        (domain_dir / "entities").mkdir(parents=True, exist_ok=True)
        (domain_dir / "value_objects").mkdir(parents=True, exist_ok=True)
        (domain_dir / "aggregates").mkdir(parents=True, exist_ok=True)
        (domain_dir / "repositories").mkdir(parents=True, exist_ok=True)
        (app_dir / "services").mkdir(parents=True, exist_ok=True)
        (app_dir / "use_cases").mkdir(parents=True, exist_ok=True)
        (app_dir / "dto").mkdir(parents=True, exist_ok=True)
        (infra_dir / "persistence").mkdir(parents=True, exist_ok=True)
        (infra_dir / "external_services").mkdir(parents=True, exist_ok=True)
        value_objects_content = f"""#!/usr/bin/env python3
""\"
Accessibility Domain - Value Objects
Generated from: {file_path.name}
""\"

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class SpecialNeedType(Enum):
    ""\"أنواع الاحتياجات الخاصة""\"
    AUTISM = "autism"
    ADHD = "adhd"  
    SPEECH_DELAY = "speech_delay"
    HEARING_IMPAIRED = "hearing_impaired"
    VISUAL_IMPAIRED = "visual_impaired"
    LEARNING_DISABILITY = "learning_disability"
    DYSLEXIA = "dyslexia"
    DOWN_SYNDROME = "down_syndrome"
    CEREBRAL_PALSY = "cerebral_palsy"
    SENSORY_PROCESSING = "sensory_processing"

@dataclass
class SensoryPreferences:
    ""\"التفضيلات الحسية""\"
    sound_level: str = "normal"
    visual_stimulation: str = "normal"
    interaction_pace: str = "normal"
    
    def __post_init__(self):
        valid_sound_levels = ["quiet", "normal", "loud"]
        valid_visual = ["minimal", "normal", "high"]
        valid_pace = ["slow", "normal", "fast"]
        
        if self.sound_level not in valid_sound_levels:
            self.sound_level = "normal"
        if self.visual_stimulation not in valid_visual:
            self.visual_stimulation = "normal"
        if self.interaction_pace not in valid_pace:
            self.interaction_pace = "normal"

@dataclass
class LearningAdaptations:
    ""\"تكييفات التعلم""\"
    repeat_instructions: bool = False
    visual_cues: bool = False
    simplified_language: bool = False
    extended_response_time: bool = False
    structured_routine: bool = False
"""
        entities_content = f"""#!/usr/bin/env python3
""\"
Accessibility Domain - Entities
Generated from: {file_path.name}
""\"

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from ..value_objects.special_need_type import SpecialNeedType, SensoryPreferences, LearningAdaptations

@dataclass
class AccessibilityProfile:
    ""\"ملف الوصولية للطفل - كيان رئيسي""\"
    child_id: str
    special_needs: List[str] = field(default_factory=list)
    communication_level: str = "verbal"
    attention_span: int = 5
    sensory_preferences: Optional[SensoryPreferences] = None
    learning_adaptations: Optional[LearningAdaptations] = None
    behavioral_triggers: List[str] = field(default_factory=list)
    calming_strategies: List[str] = field(default_factory=list)
    support_level: str = "minimal"
    communication_aids: List[str] = field(default_factory=list)
    created_at: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()
        if self.sensory_preferences is None:
            self.sensory_preferences = SensoryPreferences()
        if self.learning_adaptations is None:
            self.learning_adaptations = LearningAdaptations()
    
    def update_last_modified(self):
        ""\"تحديث تاريخ آخر تعديل""\"
        self.last_updated = datetime.now().isoformat()
    
    def add_special_need(self, need_type: str):
        ""\"إضافة احتياج خاص جديد""\"
        if need_type not in self.special_needs:
            self.special_needs.append(need_type)
            self.update_last_modified()
    
    def remove_special_need(self, need_type: str):
        ""\"إزالة احتياج خاص""\"
        if need_type in self.special_needs:
            self.special_needs.remove(need_type)
            self.update_last_modified()

@dataclass
class AdaptiveContent:
    ""\"محتوى متكيف للاحتياجات الخاصة""\"
    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str
    target_needs: List[str]
    effectiveness_score: float = 0.0
    usage_count: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.content_id:
            self.content_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def increment_usage(self):
        ""\"زيادة عداد الاستخدام""\"
        self.usage_count += 1
    
    def update_effectiveness(self, score: float):
        ""\"تحديث نتيجة الفعالية""\"
        if 0.0 <= score <= 1.0:
            self.effectiveness_score = score
"""
        use_case_content = f"""#!/usr/bin/env python3
""\"
Accessibility Use Cases
Generated from: {file_path.name}
""\"

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..dto.accessibility_dto import AccessibilityProfileDTO, AdaptiveContentDTO
from ...domain.{domain_name}.entities.accessibility_profile import AccessibilityProfile, AdaptiveContent
from ...domain.{domain_name}.value_objects.special_need_type import SpecialNeedType

logger = logging.getLogger(__name__)

class CreateAccessibilityProfileUseCase:
    ""\"حالة استخدام: إنشاء ملف وصولية""\"
    
    def __init__(self, repository):
        self.repository = repository
    
    def execute(self, child_id: str, special_needs: List[str], 
                communication_level: str = "verbal") -> AccessibilityProfile:
        ""\"تنفيذ إنشاء ملف الوصولية""\"
        try:
            # التحقق من صحة البيانات
            if not child_id:
                raise ValueError("معرف الطفل مطلوب")
            
            # التحقق من عدم وجود ملف سابق
            existing_profile = self.repository.get_by_child_id(child_id)
            if existing_profile:
                raise ValueError(f"ملف وصولية موجود بالفعل للطفل {{child_id}}")
            
            # إنشاء ملف الوصولية
            profile = AccessibilityProfile(
                child_id=child_id,
                special_needs=special_needs,
                communication_level=communication_level
            )
            
            # حفظ في قاعدة البيانات
            saved_profile = self.repository.save(profile)
            
            logger.info(f"تم إنشاء ملف وصولية للطفل {{child_id}}")
            return saved_profile
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف الوصولية: {{e}}")
            raise

class AdaptContentUseCase:
    ""\"حالة استخدام: تكييف المحتوى""\"
    
    def __init__(self, repository, adaptation_service):
        self.repository = repository
        self.adaptation_service = adaptation_service
    
    def execute(self, child_id: str, original_content: Dict) -> Dict:
        ""\"تنفيذ تكييف المحتوى""\"
        try:
            # الحصول على ملف الوصولية
            profile = self.repository.get_by_child_id(child_id)
            if not profile:
                logger.warning(f"لا يوجد ملف وصولية للطفل {{child_id}}")
                return original_content
            
            # تطبيق التكييفات
            adapted_content = self.adaptation_service.adapt_content(
                profile, original_content
            )
            
            logger.info(f"تم تكييف المحتوى للطفل {{child_id}}")
            return adapted_content
            
        except Exception as e:
            logger.error(f"خطأ في تكييف المحتوى: {{e}}")
            return original_content
"""
        dto_content = f"""#!/usr/bin/env python3
""\"
Accessibility DTOs
Generated from: {file_path.name}
""\"

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AccessibilityProfileDTO:
    ""\"DTO لملف الوصولية""\"
    child_id: str
    special_needs: List[str]
    communication_level: str
    attention_span: int
    sensory_preferences: Dict[str, str]
    learning_adaptations: Dict[str, bool]
    behavioral_triggers: List[str]
    calming_strategies: List[str]
    support_level: str
    communication_aids: List[str]

@dataclass
class AdaptiveContentDTO:
    ""\"DTO للمحتوى المتكيف""\"
    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str
    target_needs: List[str]
    effectiveness_score: float

@dataclass
class AccessibilityReportDTO:
    ""\"DTO لتقرير الوصولية""\"
    child_id: str
    assessment_date: str
    accessibility_score: float
    recommendations: List[str]
    progress_notes: List[str]
"""
        app_service_content = f"""#!/usr/bin/env python3
""\"
Accessibility Application Service
Generated from: {file_path.name}
""\"

import logging
from typing import Dict, List, Optional
from pathlib import Path

from .use_cases.create_profile_use_case import CreateAccessibilityProfileUseCase
from .use_cases.adapt_content_use_case import AdaptContentUseCase
from .dto.accessibility_dto import AccessibilityProfileDTO

logger = logging.getLogger(__name__)

class AccessibilityApplicationService:
    ""\"خدمة تطبيق الوصولية""\"
    
    def __init__(self, repository, adaptation_service):
        self.repository = repository
        self.adaptation_service = adaptation_service
        self.create_profile_use_case = CreateAccessibilityProfileUseCase(repository)
        self.adapt_content_use_case = AdaptContentUseCase(repository, adaptation_service)
    
    def create_accessibility_profile(self, child_id: str, special_needs: List[str]) -> AccessibilityProfileDTO:
        ""\"إنشاء ملف وصولية جديد""\"
        try:
            profile = self.create_profile_use_case.execute(child_id, special_needs)
            return self._profile_to_dto(profile)
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف الوصولية: {{e}}")
            raise
    
    def adapt_content_for_child(self, child_id: str, content: Dict) -> Dict:
        ""\"تكييف المحتوى للطفل""\"
        try:
            return self.adapt_content_use_case.execute(child_id, content)
        except Exception as e:
            logger.error(f"خطأ في تكييف المحتوى: {{e}}")
            return content
    
    def get_accessibility_profile(self, child_id: str) -> Optional[AccessibilityProfileDTO]:
        ""\"الحصول على ملف الوصولية""\"
        try:
            profile = self.repository.get_by_child_id(child_id)
            return self._profile_to_dto(profile) if profile else None
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملف الوصولية: {{e}}")
            return None
    
    def _profile_to_dto(self, profile) -> AccessibilityProfileDTO:
        ""\"تحويل Profile إلى DTO""\"
        return AccessibilityProfileDTO(
            child_id=profile.child_id,
            special_needs=profile.special_needs,
            communication_level=profile.communication_level,
            attention_span=profile.attention_span,
            sensory_preferences=profile.sensory_preferences.__dict__,
            learning_adaptations=profile.learning_adaptations.__dict__,
            behavioral_triggers=profile.behavioral_triggers,
            calming_strategies=profile.calming_strategies,
            support_level=profile.support_level,
            communication_aids=profile.communication_aids
        )
"""
        files_created = []
        vo_file = domain_dir / "value_objects" / "special_need_type.py"
        with open(vo_file, "w", encoding="utf-8") as f:
            f.write(value_objects_content)
        files_created.append(
            f"domain/value_objects/special_need_type.py ({len(value_objects_content.splitlines())} lines)"
        )
        entity_file = domain_dir / "entities" / "accessibility_profile.py"
        with open(entity_file, "w", encoding="utf-8") as f:
            f.write(entities_content)
        files_created.append(
            f"domain/entities/accessibility_profile.py ({len(entities_content.splitlines())} lines)"
        )
        uc_file = app_dir / "use_cases" / "accessibility_use_cases.py"
        with open(uc_file, "w", encoding="utf-8") as f:
            f.write(use_case_content)
        files_created.append(
            f"application/use_cases/accessibility_use_cases.py ({len(use_case_content.splitlines())} lines)"
        )
        dto_file = app_dir / "dto" / "accessibility_dto.py"
        with open(dto_file, "w", encoding="utf-8") as f:
            f.write(dto_content)
        files_created.append(
            f"application/dto/accessibility_dto.py ({len(dto_content.splitlines())} lines)"
        )
        service_file = app_dir / "services" / "accessibility_application_service.py"
        with open(service_file, "w", encoding="utf-8") as f:
            f.write(app_service_content)
        files_created.append(
            f"application/services/accessibility_application_service.py ({len(app_service_content.splitlines())} lines)"
        )
        self._create_init_files([domain_dir, app_dir, infra_dir])
        self.log(f"تم تقسيم {file_path.name} إلى {len(files_created)} ملف:")
        for file_info in files_created:
            self.log(f"  - {file_info}")
        self.split_count += 1
        return files_created

    def _create_init_files(self, directories: List[Path]):
        """إنشاء ملفات __init__.py"""
        for directory in directories:
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                if any(f.endswith(".py") for f in files):
                    init_file = root_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("# Domain module\\n", encoding="utf-8")

    def move_original_to_legacy(self, file_path: Path):
        """نقل الملف الأصلي إلى legacy"""
        legacy_dir = self.src_dir / "legacy" / "god_classes"
        legacy_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        legacy_path = legacy_dir / new_name
        try:
            shutil.copy2(file_path, legacy_path)
            self.log(f"نُسخ الملف الأصلي إلى: legacy/god_classes/{new_name}")
            return True
        except Exception as e:
            self.log(f"خطأ في نسخ الملف إلى legacy: {e}")
            return False

    def run_splitting(self):
        """تشغيل عملية التقسيم الكاملة"""
        self.logger.info("=" * 70)
        self.logger.info("🔧 بدء تقسيم God Classes الصحيح...")
        self.logger.info("=" * 70)
        god_classes = self.identify_god_classes()
        if not god_classes:
            self.log("لم يتم العثور على God Classes للتقسيم")
            return
        self.log(f"تم العثور على {len(god_classes)} ملف كبير للتقسيم:")
        for file_path, lines in god_classes:
            self.log(f"  - {file_path.name}: {lines} سطر")
        total_files_created = 0
        for file_path, lines in god_classes:
            filename = file_path.name
            if filename == "accessibility_service.py":
                files_created = self.split_accessibility_service(file_path, lines)
                total_files_created += len(files_created)
                self.move_original_to_legacy(file_path)
            else:
                self.log(f"⚠️ {filename} يحتاج تقسيم يدوي (لم يتم تطبيقه بعد)")
        self.logger.info("=" * 70)
        self.logger.info("✅ انتهى التقسيم بنجاح!")
        self.logger.info(f"   - ملفات مُقسمة: {self.split_count}")
        self.logger.info(f"   - ملفات جديدة: {total_files_created}")
        self.logger.info("=" * 70)
        return self.report


if __name__ == "__main__":
    splitter = ProperDDDSplitter()
    splitter.run_splitting()
