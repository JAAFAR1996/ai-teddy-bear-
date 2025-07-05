#!/usr/bin/env python3
"""
🏗️ Cleanup Policy Aggregate - DDD Implementation
Root aggregate for managing data cleanup policies
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import structlog

logger = structlog.get_logger()


class PolicyStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class ComplianceStandard(Enum):
    GDPR = "gdpr"
    COPPA = "coppa"
    CCPA = "ccpa"


@dataclass
class PolicyRule:
    """قاعدة في سياسة التنظيف"""

    data_category: str
    retention_days: int
    conditions: Dict[str, Any]

    def applies_to(self, data_item: Dict[str, Any]) -> bool:
        """تحديد ما إذا كانت القاعدة تنطبق على عنصر البيانات"""
        return data_item.get("category") == self.data_category


class CleanupPolicy:
    """
    🎯 Root Aggregate: Cleanup Policy

    Business Rules:
    - سياسة واحدة لكل نطاق (domain)
    - يجب أن تكون متوافقة مع معايير الامتثال
    - لا يمكن تغيير سياسة نشطة بدون موافقة
    """

    def __init__(self, policy_id: str = None, name: str = ""):
        self.policy_id = policy_id or str(uuid.uuid4())
        self.name = name
        self.status = PolicyStatus.DRAFT
        self.rules: List[PolicyRule] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        logger.info("Cleanup policy created", policy_id=self.policy_id, name=self.name)

    def add_rule(
        self, data_category: str, retention_days: int, conditions: Dict[str, Any] = None
    ) -> PolicyRule:
        """إضافة قاعدة جديدة للسياسة"""
        self._ensure_can_modify()

        rule = PolicyRule(
            data_category=data_category,
            retention_days=retention_days,
            conditions=conditions or {},
        )

        self.rules.append(rule)
        self.updated_at = datetime.utcnow()

        logger.info(
            "Policy rule added",
            policy_id=self.policy_id,
            data_category=data_category,
            retention_days=retention_days,
        )

        return rule

    def activate(self, activated_by: str) -> None:
        """تفعيل السياسة"""
        if not self.rules:
            raise PolicyValidationError("Cannot activate policy without rules")

        self.status = PolicyStatus.ACTIVE
        self.updated_at = datetime.utcnow()

        logger.info(
            "Cleanup policy activated",
            policy_id=self.policy_id,
            activated_by=activated_by,
        )

    def get_applicable_rules(self, data_item: Dict[str, Any]) -> List[PolicyRule]:
        """الحصول على القواعد المنطبقة على عنصر بيانات معين"""
        return [rule for rule in self.rules if rule.applies_to(data_item)]

    def _ensure_can_modify(self) -> None:
        """التحقق من إمكانية تعديل السياسة"""
        if self.status == PolicyStatus.ACTIVE:
            raise PolicyValidationError("Cannot modify active policy")


class PolicyValidationError(Exception):
    """خطأ في التحقق من صحة السياسة"""

    pass
