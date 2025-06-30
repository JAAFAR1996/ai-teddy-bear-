from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class Entity(ABC):
    """Base entity with common properties"""
    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events: list = []
    
    def add_domain_event(self, event -> Any: Dict[str, Any]) -> Any:
        """إضافة حدث domain للكيان"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> Any:
        """مسح أحداث domain"""
        self._domain_events.clear()
    
    def get_domain_events(self) -> Any:
        """الحصول على أحداث domain"""
        return self._domain_events.copy()
    
    def update_timestamp(self) -> Any:
        """تحديث وقت التعديل"""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id) 