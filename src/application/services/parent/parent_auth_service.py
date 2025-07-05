#!/usr/bin/env python3
"""
Parent Authentication Service - Single Responsibility
====================================================
مسؤول فقط عن مصادقة الوالدين
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ParentCredentials:
    """بيانات اعتماد الوالدين"""

    email: str
    password: str
    child_id: Optional[str] = None


@dataclass
class AuthToken:
    """رمز المصادقة"""

    token: str
    parent_id: str
    child_id: str
    expires_at: datetime
    is_valid: bool = True


class ParentAuthenticationService:
    """مسؤول فقط عن authentication الوالدين"""

    def __init__(self, database_service=None):
        self.db = database_service
        self.token_expiry_hours = 24

    async def authenticate(
            self,
            credentials: ParentCredentials) -> Optional[AuthToken]:
        """
        مصادقة الوالدين - المسؤولية الوحيدة لهذا الكلاس

        Args:
            credentials: بيانات الدخول

        Returns:
            AuthToken if successful, None if failed
        """
        try:
            # التحقق من صحة البيانات
            if not self._validate_credentials(credentials):
                logger.warning(
                    f"Invalid credentials format for {credentials.email}")
                return None

            # البحث عن الوالد في قاعدة البيانات
            parent = await self._find_parent_by_email(credentials.email)
            if not parent:
                logger.warning(f"Parent not found: {credentials.email}")
                return None

            # التحقق من كلمة المرور
            if not self._verify_password(
                    credentials.password,
                    parent["password_hash"]):
                logger.warning(f"Invalid password for {credentials.email}")
                return None

            # التحقق من ربط الطفل
            if credentials.child_id and not self._verify_child_access(
                parent["id"], credentials.child_id
            ):
                logger.warning(
                    f"Unauthorized child access: {credentials.child_id}")
                return None

            # إنشاء رمز المصادقة
            token = self._generate_auth_token()
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)

            auth_token = AuthToken(
                token=token,
                parent_id=parent["id"],
                child_id=credentials.child_id or parent["default_child_id"],
                expires_at=expires_at,
            )

            # حفظ الرمز في قاعدة البيانات
            await self._store_auth_token(auth_token)

            logger.info(f"Authentication successful for parent {parent['id']}")
            return auth_token

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def validate_token(self, token: str) -> Optional[AuthToken]:
        """التحقق من صحة رمز المصادقة"""
        try:
            stored_token = await self._get_stored_token(token)

            if not stored_token:
                return None

            if stored_token.expires_at <= datetime.now():
                await self._invalidate_token(token)
                return None

            return stored_token

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    async def logout(self, token: str) -> bool:
        """تسجيل خروج الوالد"""
        try:
            await self._invalidate_token(token)
            logger.info(f"Logout successful for token {token[:10]}...")
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False

    def _validate_credentials(self, credentials: ParentCredentials) -> bool:
        """التحقق من صحة تنسيق البيانات"""
        if not credentials.email or "@" not in credentials.email:
            return False
        if not credentials.password or len(credentials.password) < 6:
            return False
        return True

    async def _find_parent_by_email(self, email: str) -> Optional[dict]:
        """البحث عن الوالد بالإيميل"""
        if not self.db:
            return {
                "id": "test_parent",
                "email": email,
                "password_hash": "test_hash",
                "default_child_id": "test_child",
            }

        return await self.db.get_parent_by_email(email)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """التحقق من كلمة المرور"""
        # في التطبيق الحقيقي، نستخدم bcrypt أو مشابه
        computed_hash = hashlib.sha256(password.encode()).hexdigest()
        return computed_hash == password_hash

    def _verify_child_access(self, parent_id: str, child_id: str) -> bool:
        """التحقق من صلاحية الوالد للوصول للطفل"""
        # في التطبيق الحقيقي، نتحقق من قاعدة البيانات
        return True

    def _generate_auth_token(self) -> str:
        """إنشاء رمز مصادقة آمن"""
        return secrets.token_urlsafe(32)

    async def _store_auth_token(self, auth_token: AuthToken) -> None:
        """حفظ رمز المصادقة"""
        if self.db:
            await self.db.store_auth_token(auth_token)

    async def _get_stored_token(self, token: str) -> Optional[AuthToken]:
        """استرجاع رمز محفوظ"""
        if self.db:
            return await self.db.get_auth_token(token)
        return None

    async def _invalidate_token(self, token: str) -> None:
        """إلغاء رمز المصادقة"""
        if self.db:
            await self.db.invalidate_token(token)
