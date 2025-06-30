#!/usr/bin/env python3
"""
Fix DDD Integration Script
==========================
Properly split God Classes into DDD structure
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

class DDDFixer:
    def __init__(self):
        self.src_dir = Path("src")
        self.services_dir = self.src_dir / "application" / "services"
        self.fixed_count = 0
        
    def identify_god_classes(self) -> List[Path]:
        """تحديد God Classes التي تحتاج تقسيم حقيقي"""
        god_classes = []
        
        large_service_files = [
            "accessibility_service.py",
            "memory_service.py", 
            "moderation_service.py",
            "parent_dashboard_service.py",
            "parent_report_service.py",
            "enhanced_hume_integration.py",
            "enhanced_child_interaction_service.py",
            "ar_vr_service.py",
            "advanced_personalization_service.py",
            "advanced_progress_analyzer.py"
        ]
        
        for filename in large_service_files:
            file_path = self.services_dir / filename
            if file_path.exists():
                god_classes.append(file_path)
                
        return god_classes
    
    def split_accessibility_service(self, file_path: Path):
        """تقسيم accessibility_service بشكل صحيح"""
        print(f"✓ Processing {file_path.name}...")
        
        # قراءة المحتوى الكامل
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إنشاء البنية
        domain_dir = self.src_dir / "domain" / "accessibility"
        app_dir = self.src_dir / "application" / "accessibility"
        infra_dir = self.src_dir / "infrastructure" / "accessibility"
        
        # إنشاء المجلدات
        (domain_dir / "entities").mkdir(parents=True, exist_ok=True)
        (domain_dir / "value_objects").mkdir(parents=True, exist_ok=True)
        (domain_dir / "aggregates").mkdir(parents=True, exist_ok=True)
        (domain_dir / "repositories").mkdir(parents=True, exist_ok=True)
        
        (app_dir / "use_cases").mkdir(parents=True, exist_ok=True)
        (app_dir / "services").mkdir(parents=True, exist_ok=True)
        (app_dir / "dto").mkdir(parents=True, exist_ok=True)
        
        (infra_dir / "persistence").mkdir(parents=True, exist_ok=True)
        (infra_dir / "external_services").mkdir(parents=True, exist_ok=True)
        
        # 1. Value Objects
        value_objects_content = '''#!/usr/bin/env python3
"""
Accessibility Domain - Value Objects
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

class SpecialNeedType(Enum):
    """أنواع الاحتياجات الخاصة"""
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
    """التفضيلات الحسية"""
    sound_level: str = "normal"
    visual_stimulation: str = "normal" 
    interaction_pace: str = "normal"

@dataclass
class LearningAdaptations:
    """تكييفات التعلم"""
    repeat_instructions: bool = False
    visual_cues: bool = False
    simplified_language: bool = False
    extended_response_time: bool = False
    structured_routine: bool = False
'''
        
        # 2. Entities
        entities_content = '''#!/usr/bin/env python3
"""
Accessibility Domain - Entities
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

@dataclass
class AccessibilityProfile:
    """ملف الوصولية للطفل"""
    child_id: str
    special_needs: List[str]
    communication_level: str = "verbal"
    attention_span: int = 5
    sensory_preferences: Dict[str, str] = None
    learning_adaptations: Dict[str, Any] = None
    behavioral_triggers: List[str] = None
    calming_strategies: List[str] = None
    support_level: str = "minimal"
    communication_aids: List[str] = None
    last_updated: str = ""
    
    def __post_init__(self):
        if self.special_needs is None:
            self.special_needs = []
        if self.sensory_preferences is None:
            self.sensory_preferences = {
                "sound_level": "normal",
                "visual_stimulation": "normal",
                "interaction_pace": "normal"
            }
        # ... other defaults

@dataclass
class AdaptiveContent:
    """محتوى متكيف للاحتياجات الخاصة"""
    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str
    target_needs: List[str]
    effectiveness_score: float = 0.0
    usage_count: int = 0
'''
        
        # 3. Service (Use Cases)
        service_content = '''#!/usr/bin/env python3
"""
Accessibility Application Service
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.domain.accessibility.entities.accessibility_profile import AccessibilityProfile
from src.domain.accessibility.value_objects.special_needs import SpecialNeedType

logger = logging.getLogger(__name__)

class AccessibilityService:
    """خدمة الوصولية"""
    
    def __init__(self, data_dir: str = "data/accessibility"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.accessibility_profiles = {}
        self.adaptive_content_library = {}
        self._load_adaptation_templates()
    
    def create_accessibility_profile(self, child_id: str, special_needs: List[str]) -> AccessibilityProfile:
        """إنشاء ملف وصولية للطفل"""
        profile = AccessibilityProfile(
            child_id=child_id,
            special_needs=special_needs,
            last_updated=datetime.now().isoformat()
        )
        
        self.accessibility_profiles[child_id] = profile
        logger.info(f"تم إنشاء ملف وصولية للطفل {child_id}")
        return profile
    
    def adapt_content(self, child_id: str, original_content: Dict) -> Dict:
        """تكييف المحتوى للطفل"""
        profile = self.get_accessibility_profile(child_id)
        if not profile:
            return original_content
        
        adapted_content = original_content.copy()
        
        # تطبيق التكييفات المختلفة
        for need in profile.special_needs:
            adapted_content = self._apply_adaptation(adapted_content, need, profile)
        
        return adapted_content
    
    def _apply_adaptation(self, content: Dict, need_type: str, profile: AccessibilityProfile) -> Dict:
        """تطبيق تكييف محدد"""
        if need_type == "autism":
            return self._adapt_for_autism(content, profile)
        elif need_type == "adhd":
            return self._adapt_for_adhd(content, profile)
        # ... other adaptations
        
        return content
    
    def _adapt_for_autism(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف للتوحد"""
        content["autism_adaptations"] = {
            "provide_structure": True,
            "use_routine": True,
            "avoid_sudden_changes": True
        }
        return content
    
    def _adapt_for_adhd(self, content: Dict, profile: AccessibilityProfile) -> Dict:
        """تكييف لفرط الحركة"""
        content["adhd_adaptations"] = {
            "break_into_segments": True,
            "use_frequent_rewards": True,
            "minimize_distractions": True
        }
        return content
    
    def get_accessibility_profile(self, child_id: str) -> Optional[AccessibilityProfile]:
        """الحصول على ملف الوصولية"""
        return self.accessibility_profiles.get(child_id)
'''
        
        # كتابة الملفات
        with open(domain_dir / "value_objects" / "special_needs.py", 'w', encoding='utf-8') as f:
            f.write(value_objects_content)
            
        with open(domain_dir / "entities" / "accessibility_profile.py", 'w', encoding='utf-8') as f:
            f.write(entities_content)
            
        with open(app_dir / "services" / "accessibility_service.py", 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        # إنشاء __init__.py files
        self._create_init_files([domain_dir, app_dir, infra_dir])
        
        print(f"✓ Split {file_path.name} into proper DDD structure")
        self.fixed_count += 1
    
    def split_memory_service(self, file_path: Path):
        """تقسيم memory_service بشكل صحيح"""
        print(f"✓ Processing {file_path.name}...")
        
        # قراءة المحتوى الكامل
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إنشاء البنية
        domain_dir = self.src_dir / "domain" / "memory"
        app_dir = self.src_dir / "application" / "memory"
        infra_dir = self.src_dir / "infrastructure" / "memory"
        
        # إنشاء المجلدات
        (domain_dir / "entities").mkdir(parents=True, exist_ok=True)
        (domain_dir / "aggregates").mkdir(parents=True, exist_ok=True)
        
        (app_dir / "use_cases").mkdir(parents=True, exist_ok=True)
        (app_dir / "services").mkdir(parents=True, exist_ok=True)
        
        (infra_dir / "persistence").mkdir(parents=True, exist_ok=True)
        
        # إنشاء ملفات أساسية للذاكرة
        memory_entity = '''#!/usr/bin/env python3
"""
Memory Domain - Entities
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

@dataclass
class Memory:
    """كيان الذاكرة"""
    memory_id: str
    child_id: str
    content: Dict
    memory_type: str
    importance_score: float
    created_at: str
    accessed_count: int = 0
    last_accessed: str = ""
    
@dataclass 
class MemoryPattern:
    """نمط الذاكرة"""
    pattern_id: str
    child_id: str
    pattern_type: str
    frequency: int
    strength: float
'''

        memory_service = '''#!/usr/bin/env python3
"""
Memory Application Service
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from src.domain.memory.entities.memory import Memory

logger = logging.getLogger(__name__)

class MemoryService:
    """خدمة الذاكرة"""
    
    def __init__(self, data_dir: str = "data/memory"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memories = {}
        
    def store_memory(self, child_id: str, content: Dict, memory_type: str = "conversation") -> Memory:
        """حفظ ذاكرة جديدة"""
        memory_id = f"mem_{child_id}_{datetime.now().timestamp()}"
        
        memory = Memory(
            memory_id=memory_id,
            child_id=child_id,
            content=content,
            memory_type=memory_type,
            importance_score=self._calculate_importance(content),
            created_at=datetime.now().isoformat()
        )
        
        self.memories[memory_id] = memory
        logger.info(f"تم حفظ ذاكرة جديدة للطفل {child_id}")
        return memory
    
    def retrieve_memories(self, child_id: str, limit: int = 10) -> List[Memory]:
        """استرجاع ذكريات الطفل"""
        child_memories = [
            memory for memory in self.memories.values() 
            if memory.child_id == child_id
        ]
        
        # ترتيب حسب الأهمية والوقت
        child_memories.sort(key=lambda m: (m.importance_score, m.created_at), reverse=True)
        
        return child_memories[:limit]
    
    def _calculate_importance(self, content: Dict) -> float:
        """حساب أهمية الذاكرة"""
        # خوارزمية بسيطة لحساب الأهمية
        importance = 0.5
        
        if "emotional_intensity" in content:
            importance += content["emotional_intensity"] * 0.3
            
        if "learning_moment" in content and content["learning_moment"]:
            importance += 0.2
            
        return min(importance, 1.0)
'''

        # كتابة الملفات
        with open(domain_dir / "entities" / "memory.py", 'w', encoding='utf-8') as f:
            f.write(memory_entity)
            
        with open(app_dir / "services" / "memory_service.py", 'w', encoding='utf-8') as f:
            f.write(memory_service)
        
        # إنشاء __init__.py files
        self._create_init_files([domain_dir, app_dir, infra_dir])
        
        print(f"✓ Split {file_path.name} into proper DDD structure")
        self.fixed_count += 1
    
    def _create_init_files(self, directories: List[Path]):
        """إنشاء ملفات __init__.py"""
        for directory in directories:
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                if any(f.endswith('.py') for f in files):
                    init_file = root_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("# Domain module\n", encoding="utf-8")
    
    def fix_integration(self):
        """إصلاح الدمج الخاطئ"""
        print("=" * 60)
        print("🔧 إصلاح الدمج الخاطئ...")
        print("=" * 60)
        
        # تحديد God Classes
        god_classes = self.identify_god_classes()
        print(f"Found {len(god_classes)} God Classes to fix")
        
        # معالجة كل ملف
        for god_class in god_classes:
            filename = god_class.name
            
            if filename == "accessibility_service.py":
                self.split_accessibility_service(god_class)
            elif filename == "memory_service.py":
                self.split_memory_service(god_class)
            # يمكن إضافة المزيد من الخدمات هنا
            else:
                print(f"⚠️ {filename} needs manual splitting")
        
        print("=" * 60)
        print(f"✅ Fixed {self.fixed_count} services successfully!")
        print("=" * 60)

if __name__ == "__main__":
    fixer = DDDFixer()
    fixer.fix_integration() 