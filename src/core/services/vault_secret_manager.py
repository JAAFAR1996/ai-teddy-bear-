"""
Vault Secret Manager - إدارة الأسرار باستخدام HashiCorp Vault
Security Module for AI Teddy Bear Project
"""
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import hvac


@dataclass
class VaultConfig:
    """تكوين Vault"""
    url: str
    token: str
    mount_point: str = 'teddy-secrets'
    verify_ssl: bool = True


class VaultSecretManager:
    """مدير الأسرار المتقدم باستخدام Vault"""

    def __init__(self, config: VaultConfig):
        self.config = config
        self.client = None
        self.logger = self._setup_logger()
        self._init_vault_client()

    def _setup_logger(self) ->logging.Logger:
        """إعداد نظام التسجيل"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _init_vault_client(self) ->None:
        """تهيئة عميل Vault"""
        try:
            self.client = hvac.Client(url=self.config.url, token=self.
                config.token, verify=self.config.verify_ssl)
            if not self.client.is_authenticated():
                raise Exception('فشل في المصادقة مع Vault')
            self.logger.info('✅ تم الاتصال بـ Vault بنجاح')
        except Exception as e:
            self.logger.error(f'❌ خطأ في الاتصال بـ Vault: {e}')
            raise

    def store_api_keys(self, api_keys: Dict[str, str], path: str='api-keys'
        ) ->bool:
        """تخزين مفاتيح API في Vault"""
        try:
            full_path = f'{self.config.mount_point}/data/{path}'
            encrypted_keys = self._encrypt_sensitive_keys(api_keys)
            response = self.client.secrets.kv.v2.create_or_update_secret(path
                =path, secret=encrypted_keys, mount_point=self.config.
                mount_point)
            self.logger.info(
                f'✅ تم تخزين {len(api_keys)} مفتاح API في المسار: {full_path}')
            return True
        except Exception as e:
            self.logger.error(f'❌ خطأ في تخزين مفاتيح API: {e}')
            return False

    def get_api_key(self, service_name: str, path: str='api-keys') ->Optional[
        str]:
        """استرداد مفتاح API محدد"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=
                path, mount_point=self.config.mount_point)
            if response and 'data' in response and 'data' in response['data']:
                encrypted_data = response['data']['data']
                decrypted_data = self._decrypt_sensitive_keys(encrypted_data)
                return decrypted_data.get(service_name)
            return None
        except Exception as e:
            self.logger.error(f'❌ خطأ في استرداد مفتاح {service_name}: {e}')
            return None

    def get_all_api_keys(self, path: str='api-keys') ->Dict[str, str]:
        """استرداد جميع مفاتيح API"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=
                path, mount_point=self.config.mount_point)
            if response and 'data' in response and 'data' in response['data']:
                encrypted_data = response['data']['data']
                return self._decrypt_sensitive_keys(encrypted_data)
            return {}
        except Exception as e:
            self.logger.error(f'❌ خطأ في استرداد مفاتيح API: {e}')
            return {}

    def rotate_api_key(self, service_name: str, new_key: str, path: str=
        'api-keys') ->bool:
        """تدوير مفتاح API محدد"""
        try:
            current_keys = self.get_all_api_keys(path)
            current_keys[service_name] = new_key
            return self.store_api_keys(current_keys, path)
        except Exception as e:
            self.logger.error(f'❌ خطأ في تدوير مفتاح {service_name}: {e}')
            return False

    def delete_api_key(self, service_name: str, path: str='api-keys') ->bool:
        """حذف مفتاح API محدد"""
        try:
            current_keys = self.get_all_api_keys(path)
            if service_name in current_keys:
                del current_keys[service_name]
                return self.store_api_keys(current_keys, path)
            self.logger.warning(f'⚠️ المفتاح {service_name} غير موجود')
            return True
        except Exception as e:
            self.logger.error(f'❌ خطأ في حذف مفتاح {service_name}: {e}')
            return False

    def _encrypt_sensitive_keys(self, keys: Dict[str, str]) ->Dict[str, str]:
        """تشفير إضافي للمفاتيح الحساسة (placeholder)"""
        return keys

    def _decrypt_sensitive_keys(self, encrypted_keys: Dict[str, str]) ->Dict[
        str, str]:
        """فك تشفير المفاتيح الحساسة (placeholder)"""
        return encrypted_keys

    def health_check(self) ->Dict[str, Any]:
        """فحص صحة الاتصال مع Vault"""
        try:
            status = {'vault_authenticated': self.client.is_authenticated(),
                'vault_sealed': self.client.sys.is_sealed(),
                'mount_point_exists': self._check_mount_point_exists()}
            return status
        except Exception as e:
            self.logger.error(f'❌ خطأ في فحص صحة Vault: {e}')
            return {'error': str(e)}

    def _check_mount_point_exists(self) ->bool:
        """التحقق من وجود mount point"""
        try:
            mounts = self.client.sys.list_mounted_secrets_engines()
            return f'{self.config.mount_point}/' in mounts['data']
        except Exception as e:
            return False


class TeddyVaultIntegration:
    """تكامل Vault مع مشروع Teddy Bear"""

    def __init__(self, vault_url: str='http://localhost:8200'):
        self.vault_url = vault_url
        self.vault_manager = None
        self.logger = logging.getLogger(__name__)

    def initialize_from_env(self) ->bool:
        """تهيئة من متغيرات البيئة"""
        try:
            vault_token = os.getenv('VAULT_TOKEN')
            if not vault_token:
                tokens_file = Path('.vault_tokens')
                if tokens_file.exists():
                    with open(tokens_file, 'r') as f:
                        for line in f:
                            if line.startswith('VAULT_APP_TOKEN = os.getenv('ACCESS_TOKEN')=', 1)[1].strip()
                                break
            if not vault_token:
                raise ValueError('لم يتم العثور على Vault token')
            config = VaultConfig(url=self.vault_url, token=vault_token)
            self.vault_manager = VaultSecretManager(config)
            return True
        except Exception as e:
            self.logger.error(f'❌ خطأ في تهيئة Vault: {e}')
            return False

    def get_service_config(self) ->Dict[str, str]:
        """استرداد تكوين الخدمات"""
        if not self.vault_manager:
            raise Exception('Vault غير مهيأ')
        api_keys = self.vault_manager.get_all_api_keys()
        security_keys = self.vault_manager.get_all_api_keys('security')
        return {**api_keys, **security_keys}


def main():
    """الوظيفة الرئيسية للاختبار"""
    logger.info('🔐 Vault Secret Manager - اختبار الاتصال')
    logger.info('=' * 50)
    teddy_vault = TeddyVaultIntegration()
    if teddy_vault.initialize_from_env():
        logger.info('✅ تم تهيئة Vault بنجاح')
        health = teddy_vault.vault_manager.health_check()
        logger.info(f'🏥 فحص الصحة: {health}')
        try:
            config = teddy_vault.get_service_config()
            logger.info(f'🔑 تم استرداد {len(config)} مفتاح من Vault')
        except Exception as e:
            logger.info(f'❌ خطأ في استرداد المفاتيح: {e}')
    else:
        logger.info('❌ فشل في تهيئة Vault')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
