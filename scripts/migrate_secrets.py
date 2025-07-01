"""
🔐 Advanced Secrets Migration Tool
Senior DevOps Engineer: جعفر أديب
Enterprise-grade secrets management with HashiCorp Vault integration
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import hvac

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("secrets_migration.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("SecretsMigrator")


@dataclass
class SecretItem:
    """بيانات السر المكتشف"""

    file_path: str
    line_number: int
    key: str
    value: str
    secret_type: str
    confidence: float
    context: str = ""


@dataclass
class MigrationConfig:
    """إعدادات عملية النقل"""

    vault_url: str = "http://localhost:8200"
    vault_token: str = ""
    vault_mount_path: str = "ai-teddy"
    backup_enabled: bool = True
    dry_run: bool = False
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "*.log",
            "*.tmp",
            "node_modules/*",
            ".git/*",
            "venv/*",
            "__pycache__/*",
        ]
    )


class AdvancedSecretsMigrator:
    """أداة متقدمة لنقل الأسرار إلى HashiCorp Vault"""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.vault_client: Optional[hvac.Client] = None
        self.discovered_secrets: List[SecretItem] = []
        self.migration_report: Dict = {}
        self.secret_patterns = {
            "api_key": {
                "pattern": "[\"\\']?(?i)(?:api[_-]?key|apikey)[\"\\']?\\s*[:=]\\s*[\"\\']([A-Za-z0-9+/=_-]{20,})[\"\\']",
                "confidence": 0.9,
                "type": "API Key",
            },
            "secret_key": {
                "pattern": "[\"\\']?(?i)(?:secret[_-]?key|secretkey)[\"\\']?\\s*[:=]\\s*[\"\\']([A-Za-z0-9+/=_-]{20,})[\"\\']",
                "confidence": 0.95,
                "type": "Secret Key",
            },
            "jwt_secret": {
                "pattern": "[\"\\']?(?i)(?:jwt[_-]?secret|jwtsecret)[\"\\']?\\s*[:=]\\s*[\"\\']([A-Za-z0-9+/=_%-]{32,})[\"\\']",
                "confidence": 0.98,
                "type": "JWT Secret",
            },
            "encryption_key": {
                "pattern": "[\"\\']?(?i)(?:encryption[_-]?key|encryptionkey)[\"\\']?\\s*[:=]\\s*[\"\\']([A-Za-z0-9+/=_-]{24,})[\"\\']",
                "confidence": 0.95,
                "type": "Encryption Key",
            },
            "password": {
                "pattern": "[\"\\']?(?i)password[\"\\']?\\s*[:=]\\s*[\"\\']([^\"\\']{8,})[\"\\']",
                "confidence": 0.8,
                "type": "Password",
            },
            "token": {
                "pattern": "[\"\\']?(?i)(?:access[_-]?token|accesstoken|bearer[_-]?token|bearertoken)[\"\\']?\\s*[:=]\\s*[\"\\']([A-Za-z0-9+/=_.-]{20,})[\"\\']",
                "confidence": 0.85,
                "type": "Access Token",
            },
            "openai_key": {
                "pattern": "sk-[a-zA-Z0-9]{48,}",
                "confidence": 1.0,
                "type": "OpenAI API Key",
            },
            "anthropic_key": {
                "pattern": "sk-ant-[a-zA-Z0-9-]{95,}",
                "confidence": 1.0,
                "type": "Anthropic API Key",
            },
            "google_key": {
                "pattern": "AIza[0-9A-Za-z\\-_]{35}",
                "confidence": 1.0,
                "type": "Google API Key",
            },
        }

    def initialize_vault_client(self) -> bool:
        """تهيئة اتصال Vault"""
        try:
            self.vault_client = hvac.Client(
                url=self.config.vault_url, token=self.config.vault_token
            )
            if not self.vault_client.is_authenticated():
                logger.error("❌ فشل في المصادقة مع Vault")
                return False
            health = self.vault_client.sys.read_health_status()
            logger.info(f"✅ Vault متصل ويعمل - الحالة: {health}")
            self._setup_vault_mount()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ Vault: {e}")
            return False

    def _setup_vault_mount(self):
        """إعداد مسار تخزين الأسرار في Vault"""
        try:
            mounts = self.vault_client.sys.list_mounted_secrets_engines()
            mount_path = f"{self.config.vault_mount_path}/"
            if mount_path not in mounts["data"]:
                self.vault_client.sys.enable_secrets_engine(
                    backend_type="kv",
                    path=self.config.vault_mount_path,
                    options={"version": "2"},
                )
                logger.info(f"✅ تم إنشاء مسار الأسرار: {self.config.vault_mount_path}")
            else:
                logger.info(
                    f"ℹ️ مسار الأسرار موجود بالفعل: {self.config.vault_mount_path}"
                )
        except Exception as e:
            logger.warning(f"⚠️ تحذير في إعداد مسار Vault: {e}")

    def scan_for_secrets(self, root_path: str = ".") -> int:
        """مسح شامل للأسرار في المشروع"""
        logger.info("🔍 بدء المسح الشامل للأسرار...")
        root = Path(root_path)
        scanned_files = 0
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if self._should_exclude_file(file_path):
                continue
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                self._scan_file_content(str(file_path), content)
                scanned_files += 1
            except Exception as e:
                logger.warning(f"⚠️ لا يمكن قراءة الملف {file_path}: {e}")
        logger.info(
            f"✅ تم مسح {scanned_files} ملف - اكتُشف {len(self.discovered_secrets)} سر"
        )
        return len(self.discovered_secrets)

    def _should_exclude_file(self, file_path: Path) -> bool:
        """فحص ما إذا كان يجب استبعاد الملف"""
        file_str = str(file_path)
        for pattern in self.config.exclude_patterns:
            if Path(file_str).match(pattern):
                return True
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:
                    return True
        except Exception:
            return True
        return False

    def _scan_file_content(self, file_path: str, content: str):
        """فحص محتوى الملف للبحث عن الأسرار"""
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern_info in self.secret_patterns.items():
                matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
                for match in matches:
                    secret_value = match.group(1) if match.groups() else match.group(0)
                    if self._is_valid_secret(secret_value, pattern_info["type"]):
                        secret_item = SecretItem(
                            file_path=file_path,
                            line_number=line_num,
                            key=self._extract_key_name(line, pattern_name),
                            value=secret_value,
                            secret_type=pattern_info["type"],
                            confidence=pattern_info["confidence"],
                            context=line.strip(),
                        )
                        self.discovered_secrets.append(secret_item)

    def _is_valid_secret(self, value: str, secret_type: str) -> bool:
        """التحقق من صحة السر المكتشف"""
        dummy_patterns = [
            "your_",
            "example_",
            "test_",
            "demo_",
            "sample_",
            "placeholder",
            "changeme",
            "secret_here",
            "123456",
            "password",
            "admin",
            "default",
        ]
        value_lower = value.lower()
        for dummy in dummy_patterns:
            if dummy in value_lower:
                return False
        if secret_type == "OpenAI API Key":
            return len(value) >= 48 and value.startswith("sk-")
        elif secret_type == "Anthropic API Key":
            return len(value) >= 95 and value.startswith("sk-ant-")
        elif secret_type == "Google API Key":
            return len(value) == 39 and value.startswith("AIza")
        return len(value) >= 8

    def _extract_key_name(self, line: str, pattern_name: str) -> str:
        """استخراج اسم المفتاح من السطر"""
        key_match = re.search("[\"\\']?(\\w+(?:[_-]\\w+)*)[\"\\']?\\s*[:=]", line)
        if key_match:
            return key_match.group(1)
        return pattern_name

    def create_backup(self) -> str:
        """إنشاء نسخة احتياطية من الملفات المتأثرة"""
        if not self.config.backup_enabled:
            return ""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backup_secrets_{timestamp}")
        backup_dir.mkdir(exist_ok=True)
        logger.info(f"📋 إنشاء نسخة احتياطية في: {backup_dir}")
        backed_up_files = set()
        for secret in self.discovered_secrets:
            file_path = Path(secret.file_path)
            if file_path.exists() and str(file_path) not in backed_up_files:
                backup_file = backup_dir / file_path.name
                backup_file.write_text(
                    file_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
                backed_up_files.add(str(file_path))
        logger.info(f"✅ تم نسخ {len(backed_up_files)} ملف احتياطياً")
        return str(backup_dir)

    def migrate_to_vault(self) -> Dict:
        """نقل الأسرار إلى Vault"""
        if self.config.dry_run:
            logger.info("🧪 تشغيل تجريبي - لن يتم نقل الأسرار فعلياً")
            return self._simulate_migration()
        if not self.vault_client:
            raise RuntimeError("Vault client غير مهيأ")
        logger.info(f"🚀 بدء نقل {len(self.discovered_secrets)} سر إلى Vault...")
        migration_results = {"successful": [], "failed": [], "skipped": []}
        for secret in self.discovered_secrets:
            try:
                vault_path = self._generate_vault_path(secret)
                secret_data = {
                    "value": secret.value,
                    "type": secret.secret_type,
                    "source_file": secret.file_path,
                    "line_number": secret.line_number,
                    "confidence": secret.confidence,
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                    "migrated_by": "SecretsMigrator",
                }
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=vault_path, secret=secret_data
                )
                migration_results["successful"].append(
                    {
                        "key": secret.key,
                        "vault_path": vault_path,
                        "type": secret.secret_type,
                    }
                )
                logger.info(f"✅ تم نقل السر: {secret.key} -> {vault_path}")
            except Exception as e:
                logger.error(f"❌ فشل نقل السر {secret.key}: {e}")
                migration_results["failed"].append({"key": secret.key, "error": str(e)})
        return migration_results

    def _generate_vault_path(self, secret: SecretItem) -> str:
        """إنشاء مسار هرمي في Vault"""
        path_parts = Path(secret.file_path).parts
        if "config" in path_parts:
            category = "config"
        elif "scripts" in path_parts:
            category = "scripts"
        elif "api" in path_parts or "core" in path_parts:
            category = "application"
        else:
            category = "general"
        return f"{category}/{secret.secret_type.lower().replace(' ', '_')}/{secret.key}"

    def _simulate_migration(self) -> Dict:
        """محاكاة عملية النقل للتشغيل التجريبي"""
        simulation_results = {"successful": [], "failed": [], "skipped": []}
        for secret in self.discovered_secrets:
            vault_path = self._generate_vault_path(secret)
            simulation_results["successful"].append(
                {
                    "key": secret.key,
                    "vault_path": vault_path,
                    "type": secret.secret_type,
                }
            )
        logger.info(f"🧪 محاكاة نقل {len(self.discovered_secrets)} سر")
        return simulation_results

    def update_configuration_files(self, migration_results: Dict):
        """تحديث ملفات التكوين لاستخدام Vault"""
        logger.info("🔧 تحديث ملفات التكوين...")
        updated_files = set()
        for secret in self.discovered_secrets:
            if secret.file_path in updated_files:
                continue
            try:
                self._update_file_with_vault_reference(secret, migration_results)
                updated_files.add(secret.file_path)
            except Exception as e:
                logger.error(f"❌ فشل تحديث الملف {secret.file_path}: {e}")
        logger.info(f"✅ تم تحديث {len(updated_files)} ملف")

    def _update_file_with_vault_reference(
        self, secret: SecretItem, migration_results: Dict
    ):
        """تحديث ملف واحد باستخدام مرجع Vault"""
        file_path = Path(secret.file_path)
        content = file_path.read_text(encoding="utf-8")
        vault_path = None
        for result in migration_results["successful"]:
            if result["key"] == secret.key:
                vault_path = result["vault_path"]
                break
        if not vault_path:
            return
        vault_reference = f"${{vault:{vault_path}}}"
        updated_content = content.replace(secret.value, vault_reference)
        if not self.config.dry_run:
            file_path.write_text(updated_content, encoding="utf-8")
            logger.info(f"📝 تم تحديث: {file_path} -> {vault_reference}")

    def generate_vault_policies(self) -> str:
        """إنشاء سياسات Vault للتحكم في الوصول"""
        policies = {
            "ai-teddy-read": {
                "path": {
                    f"{self.config.vault_mount_path}/*": {
                        "capabilities": ["read", "list"]
                    }
                }
            },
            "ai-teddy-admin": {
                "path": {
                    f"{self.config.vault_mount_path}/*": {
                        "capabilities": ["create", "read", "update", "delete", "list"]
                    }
                }
            },
        }
        policies_dir = Path("vault/policies")
        policies_dir.mkdir(parents=True, exist_ok=True)
        for policy_name, policy_content in policies.items():
            policy_file = policies_dir / f"{policy_name}.hcl"
            hcl_content = self._convert_to_hcl(policy_content)
            policy_file.write_text(hcl_content)
            logger.info(f"📜 تم إنشاء سياسة: {policy_file}")
        return str(policies_dir)

    def _convert_to_hcl(self, policy_dict: Dict) -> str:
        """تحويل قاموس السياسة إلى تنسيق HCL"""
        hcl_lines = []
        for path, config in policy_dict["path"].items():
            hcl_lines.append(f'path "{path}" {{')
            hcl_lines.append(f"  capabilities = {config['capabilities']}")
            hcl_lines.append("}")
        return "\n".join(hcl_lines)

    def generate_migration_report(
        self, migration_results: Dict, backup_dir: str
    ) -> str:
        """إنشاء تقرير شامل عن عملية النقل"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report = {
            "migration_summary": {
                "timestamp": timestamp,
                "total_secrets_found": len(self.discovered_secrets),
                "successful_migrations": len(migration_results["successful"]),
                "failed_migrations": len(migration_results["failed"]),
                "backup_directory": backup_dir,
                "vault_url": self.config.vault_url,
                "vault_mount_path": self.config.vault_mount_path,
            },
            "secrets_by_type": self._group_secrets_by_type(),
            "migration_details": migration_results,
            "recommendations": self._generate_recommendations(),
        }
        report_file = Path(
            f"secrets_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self._generate_summary_report(report, report_file)
        logger.info(f"📊 تم إنشاء التقرير: {report_file}")
        return str(report_file)

    def _group_secrets_by_type(self) -> Dict:
        """تجميع الأسرار حسب النوع"""
        grouped = {}
        for secret in self.discovered_secrets:
            if secret.secret_type not in grouped:
                grouped[secret.secret_type] = 0
            grouped[secret.secret_type] += 1
        return grouped

    def _generate_recommendations(self) -> List[str]:
        """إنشاء توصيات أمنية"""
        recommendations = [
            "قم بتدوير جميع الأسرار المكتشفة فوراً",
            "احذف الأسرار من تاريخ Git باستخدام git-filter-repo",
            "قم بتفعيل المراقبة المستمرة للأسرار في CI/CD",
            "استخدم pre-commit hooks لمنع commit الأسرار",
            "قم بمراجعة دورية لسياسات الوصول في Vault",
            "فعل التشفير في أقراص التخزين والذاكرة",
            "استخدم أدوات مسح الأسرار في production",
        ]
        return recommendations

    def _generate_summary_report(self, report: Dict, report_file: Path):
        """إنشاء تقرير نصي مبسط"""
        summary_file = report_file.with_suffix(".md")
        summary_content = f"""# 🔐 تقرير نقل الأسرار - AI Teddy Bear

## 📊 ملخص العملية
- **التوقيت**: {report['migration_summary']['timestamp']}
- **إجمالي الأسرار المكتشفة**: {report['migration_summary']['total_secrets_found']}
- **النقل الناجح**: {report['migration_summary']['successful_migrations']}
- **النقل الفاشل**: {report['migration_summary']['failed_migrations']}
- **مجلد النسخ الاحتياطي**: {report['migration_summary']['backup_directory']}

## 🔍 الأسرار حسب النوع
"""
        for secret_type, count in report["secrets_by_type"].items():
            summary_content += f"- **{secret_type}**: {count} سر\n"
        summary_content += "\n## ✅ النقل الناجح\n"
        for success in report["migration_details"]["successful"]:
            summary_content += f"""- `{success['key']}` ({success['type']}) -> `{success['vault_path']}`
"""
        if report["migration_details"]["failed"]:
            summary_content += "\n## ❌ النقل الفاشل\n"
            for failure in report["migration_details"]["failed"]:
                summary_content += f"- `{failure['key']}`: {failure['error']}\n"
        summary_content += "\n## 🎯 التوصيات\n"
        for rec in report["recommendations"]:
            summary_content += f"- {rec}\n"
        summary_file.write_text(summary_content, encoding="utf-8")


def main():
    """الدالة الرئيسية للتنفيذ"""
    parser = argparse.ArgumentParser(description="أداة نقل الأسرار المتقدمة")
    parser.add_argument(
        "--vault-url", default="http://localhost:8200", help="عنوان Vault"
    )
    parser.add_argument("--vault-token", required=True, help="رمز المصادقة مع Vault")
    parser.add_argument("--mount-path", default="ai-teddy", help="مسار تخزين الأسرار")
    parser.add_argument("--scan-path", default=".", help="مسار المسح")
    parser.add_argument(
        "--dry-run", action="store_true", help="تشغيل تجريبي بدون تعديلات"
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="تعطيل النسخ الاحتياطي"
    )
    args = parser.parse_args()
    config = MigrationConfig(
        vault_url=args.vault_url,
        vault_token=args.vault_token,
        vault_mount_path=args.mount_path,
        backup_enabled=not args.no_backup,
        dry_run=args.dry_run,
    )
    migrator = AdvancedSecretsMigrator(config)
    try:
        logger.info("🚀 بدء عملية نقل الأسرار المتقدمة...")
        if not migrator.initialize_vault_client():
            sys.exit(1)
        secrets_count = migrator.scan_for_secrets(args.scan_path)
        if secrets_count == 0:
            logger.info("✅ لم يتم العثور على أسرار للنقل")
            return
        backup_dir = migrator.create_backup()
        migration_results = migrator.migrate_to_vault()
        migrator.update_configuration_files(migration_results)
        migrator.generate_vault_policies()
        report_file = migrator.generate_migration_report(migration_results, backup_dir)
        logger.info(f"🎉 تمت عملية النقل بنجاح! التقرير: {report_file}")
    except Exception as e:
        logger.error(f"💥 فشلت عملية النقل: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
