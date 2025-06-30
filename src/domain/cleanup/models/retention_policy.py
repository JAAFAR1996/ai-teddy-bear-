#!/usr/bin/env python3
"""
Data Retention Policy Value Object
Represents the rules and policies for data retention and cleanup
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class DataRetentionPolicy:
    """شاملة سياسة الاحتفاظ بالبيانات"""
    
    # Basic retention periods (days)
    conversations_retention_days: int = 30
    messages_retention_days: int = 30
    emotional_states_retention_days: int = 90
    audio_files_retention_days: int = 7
    child_profiles_retention_days: int = 365
    parent_reports_retention_days: int = 365
    
    # Advanced settings
    backup_before_delete: bool = True
    notify_parents_before_delete: bool = True
    notification_days_before: int = 7
    require_parent_confirmation: bool = True
    soft_delete_enabled: bool = True
    
    # Compliance settings
    gdpr_compliant: bool = True
    coppa_compliant: bool = True
    auto_delete_on_request: bool = True
    
    # Emergency settings
    emergency_cleanup_threshold_gb: float = 5.0
    max_database_size_gb: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataRetentionPolicy':
        """Create policy from dictionary"""
        return cls(**data)
    
    def is_gdpr_compliant(self) -> bool:
        """Check if policy meets GDPR requirements"""
        return (
            self.gdpr_compliant and
            self.conversations_retention_days <= 30 and
            self.backup_before_delete and
            self.notify_parents_before_delete
        )
    
    def is_coppa_compliant(self) -> bool:
        """Check if policy meets COPPA requirements"""
        return (
            self.coppa_compliant and
            self.conversations_retention_days <= 14 and
            self.audio_files_retention_days <= 7 and
            self.require_parent_confirmation
        )
    
    def create_emergency_policy(self) -> 'DataRetentionPolicy':
        """Create emergency cleanup policy with shorter retention"""
        return DataRetentionPolicy(
            conversations_retention_days=7,
            messages_retention_days=7,
            emotional_states_retention_days=14,
            audio_files_retention_days=1,
            backup_before_delete=False,
            notify_parents_before_delete=False,
            gdpr_compliant=self.gdpr_compliant,
            coppa_compliant=self.coppa_compliant
        ) 