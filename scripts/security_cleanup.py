"""
🔒 AI Teddy Bear - Security Cleanup Script
Removes hardcoded secrets and implements secure environment-based configuration
"""

import json
import logging
import re
import secrets
import shutil
from pathlib import Path
from typing import Dict, List, Set

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityCleanup:
    """Comprehensive security cleanup for AI Teddy Bear project"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.secrets_found: List[Dict] = []
        self.files_modified: Set[Path] = set()
        self.secret_patterns = {
            "openai_key": "sk-[a-zA-Z0-9]{48,}",
            "anthropic_key": "sk-ant-[a-zA-Z0-9-]{95,}",
            "google_key": "AIza[0-9A-Za-z\\-_]{35}",
            "jwt_secret": "[a-zA-Z0-9%!@#$&*+=\\-_]{32,}",
            "encryption_key": "[A-Za-z0-9+/]{32,}={0,2}",
            "bearer_token": "Bearer [a-zA-Z0-9\\-_\\.]+",
            "basic_auth": "Basic [A-Za-z0-9+/]+=*",
        }

    def scan_for_secrets(self) -> None:
        """Scan the entire codebase for hardcoded secrets"""
        logger.info("🔍 Scanning for hardcoded secrets...")
        exclude_patterns = {
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            "env",
            ".pytest_cache",
            "*.pyc",
            "*.log",
            ".env*",
            "README.md",
            "LICENSE",
            "*.md",
        }
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_exclude(
                file_path, exclude_patterns
            ):
                self._scan_file(file_path)

    def _should_exclude(self, file_path: Path, exclude_patterns: Set[str]) -> bool:
        """Check if file should be excluded from scanning"""
        for pattern in exclude_patterns:
            if pattern in str(file_path) or file_path.name.endswith(
                pattern.replace("*", "")
            ):
                return True
        return False

    def _scan_file(self, file_path: Path) -> None:
        """Scan individual file for secrets"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for secret_type, pattern in self.secret_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.secrets_found.append(
                        {
                            "file": str(file_path),
                            "type": secret_type,
                            "value": match.group()[:20] + "...",
                            "line_number": content[: match.start()].count("\n") + 1,
                            "full_match": match.group(),
                        }
                    )
        except Exception as e:
            logger.warning(f"Could not scan {file_path}: {e}")

    def clean_config_files(self) -> None:
        """Remove secrets from configuration files"""
        logger.info("🧹 Cleaning configuration files...")
        config_files = [
            "config/config.json",
            "config/config/config.json",
            "tests/config/config.json",
            "tests/tests/config/config.json",
        ]
        for config_path_str in config_files:
            config_path = self.project_root / config_path_str
            if config_path.exists():
                self._clean_json_config(config_path)

    def _clean_json_config(self, config_path: Path) -> None:
        """Clean secrets from JSON configuration file"""
        try:
            backup_path = config_path.with_suffix(".json.backup")
            shutil.copy2(config_path, backup_path)
            logger.info(f"📋 Backed up {config_path} to {backup_path}")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "SECURITY" in config:
                security = config["SECURITY"]
                if "encryption_key" in security:
                    security["encryption_key"] = "${TEDDY_ENCRYPTION_KEY}"
                if "jwt_secret" in security:
                    security["jwt_secret"] = "${TEDDY_JWT_SECRET}"
            if "APPLICATION" in config:
                app_config = config["APPLICATION"]
                if "SECRET_KEY" in app_config:
                    app_config["SECRET_KEY"] = "${TEDDY_SECRET_KEY}"
            if "API_KEYS" in config:
                api_keys = config["API_KEYS"]
                env_mappings = {
                    "OPENAI_API_KEY": "${TEDDY_OPENAI_API_KEY}",
                    "ANTHROPIC_API_KEY": "${TEDDY_ANTHROPIC_API_KEY}",
                    "GOOGLE_GEMINI_API_KEY": "${TEDDY_GOOGLE_GEMINI_API_KEY}",
                    "ELEVENLABS_API_KEY": "${TEDDY_ELEVENLABS_API_KEY}",
                    "AZURE_SPEECH_KEY": "${TEDDY_AZURE_SPEECH_KEY}",
                    "HUGGINGFACE_API_KEY": "${TEDDY_HUGGINGFACE_API_KEY}",
                    "COHERE_API_KEY": "${TEDDY_COHERE_API_KEY}",
                    "HUME_API_KEY": "${TEDDY_HUME_API_KEY}",
                    "PERSPECTIVE_API_KEY": "${TEDDY_PERSPECTIVE_API_KEY}",
                    "SENTRY_DSN": "${TEDDY_SENTRY_DSN}",
                }
                for key, env_var in env_mappings.items():
                    if key in api_keys:
                        api_keys[key] = env_var
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.files_modified.add(config_path)
            logger.info(f"✅ Cleaned {config_path}")
        except Exception as e:
            logger.error(f"❌ Failed to clean {config_path}: {e}")

    def update_gitignore(self) -> None:
        """Update .gitignore with comprehensive security exclusions"""
        logger.info("📝 Updating .gitignore...")
        gitignore_path = self.project_root / ".gitignore"
        security_entries = [
            "",
            "# ===============================",
            "# ADDITIONAL SECURITY (Auto-generated)",
            "# ===============================",
            ".env.local",
            ".env.production",
            ".env.staging",
            "*.env",
            "secrets/",
            "keys/",
            "certificates/",
            "*.backup",
            "*.bak",
            "backup_*",
            "emergency_keys*",
            "api_keys*",
            "!api_keys.json.example",
            "vault_*",
            "*.vault",
            "",
            "# Git secrets scanning",
            ".secrets.baseline",
            ".trufflehog_output",
            "",
            "# Configuration backups",
            "config/*.backup",
            "config/*.bak",
            "config/config.json.backup",
            "",
            "# Temporary secret files",
            "temp_keys*",
            "*.secret",
            "*.private",
            "",
        ]
        try:
            if gitignore_path.exists():
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                if "ADDITIONAL SECURITY (Auto-generated)" not in existing_content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n".join(security_entries))
                    logger.info(
                        "✅ Updated .gitignore with additional security exclusions"
                    )
                else:
                    logger.info("ℹ️ .gitignore already contains security exclusions")
        except Exception as e:
            logger.error(f"❌ Failed to update .gitignore: {e}")

    def generate_secure_keys(self) -> Dict[str, str]:
        """Generate secure keys for environment variables"""
        logger.info("🔐 Generating secure keys...")
        secure_keys = {
            "TEDDY_ENCRYPTION_KEY": secrets.token_urlsafe(32),
            "TEDDY_JWT_SECRET": secrets.token_urlsafe(64),
            "TEDDY_SECRET_KEY": secrets.token_hex(32),
            "BACKUP_ENCRYPTION_KEY": secrets.token_urlsafe(32),
            "TEDDY_DATABASE_ENCRYPTION_KEY": secrets.token_urlsafe(32),
        }
        keys_file = self.project_root / "generated_keys.env"
        with open(keys_file, "w", encoding="utf-8") as f:
            f.write("# GENERATED SECURE KEYS\n")
            f.write("# Copy these to your .env file and DELETE this file\n\n")
            for key, value in secure_keys.items():
                f.write(f"{key}={value}\n")
        logger.info(f"✅ Generated secure keys in {keys_file}")
        logger.warning("⚠️  Copy keys to .env and DELETE generated_keys.env file!")
        return secure_keys

    def create_secure_config_loader(self) -> None:
        """Create a secure configuration loader"""
        logger.info("🔧 Creating secure configuration loader...")
        config_loader_path = (
            self.project_root / "core" / "infrastructure" / "secure_config_loader.py"
        )
        config_loader_path.parent.mkdir(parents=True, exist_ok=True)
        config_loader_code = """""\"
🔒 Secure Configuration Loader
Loads configuration from environment variables with proper validation
""\"

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SecureConfig:
    ""\"Secure configuration management""\"
    
    # Security keys
    encryption_key: str = field(repr=False)
    jwt_secret: str = field(repr=False)
    secret_key: str = field(repr=False)
    
    # API keys
    openai_api_key: str = field(repr=False)
    anthropic_api_key: str = field(repr=False)
    google_gemini_api_key: str = field(repr=False)
    elevenlabs_api_key: str = field(repr=False)
    
    # Optional API keys
    azure_speech_key: Optional[str] = field(default=None, repr=False)
    azure_speech_region: Optional[str] = field(default=None)
    huggingface_api_key: Optional[str] = field(default=None, repr=False)
    cohere_api_key: Optional[str] = field(default=None, repr=False)
    hume_api_key: Optional[str] = field(default=None, repr=False)
    perspective_api_key: Optional[str] = field(default=None, repr=False)
    sentry_dsn: Optional[str] = field(default=None, repr=False)
    
    # Database
    database_url: str = "sqlite:///data/teddy.db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        ""\"Validate configuration after initialization""\"
        self._validate_required_keys()
        self._validate_key_formats()
    
    def _validate_required_keys(self) -> None:
        ""\"Validate that all required keys are present""\"
        required_keys = [
            'encryption_key', 'jwt_secret', 'secret_key',
            'openai_api_key'  # At minimum, need OpenAI
        ]
        
        for key in required_keys:
            value = getattr(self, key)
            if not value or value.startswith('${') or len(value) < 10:
                raise ValueError(f"Invalid or missing required key: {key}")
    
    def _validate_key_formats(self) -> None:
        ""\"Validate API key formats""\"
        key_patterns = {
            'openai_api_key': r'^sk-',
            'anthropic_api_key': r'^sk-ant-',
            'google_gemini_api_key': r'^AIza',
        }
        
        for key, pattern in key_patterns.items():
            value = getattr(self, key)
            if value and not value.startswith(pattern.replace('^', '')):
                logger.warning(f"⚠️ Unexpected format for {key}")
    
    @classmethod
    def load_from_env(cls) -> 'SecureConfig':
        ""\"Load configuration from environment variables""\"
        
        # Load .env file if present
        env_file = Path('.env')
        if env_file.exists():
            cls._load_env_file(env_file)
        
        return cls(
            # Security keys
            encryption_key=cls._get_env_var('TEDDY_ENCRYPTION_KEY'),
            jwt_secret=cls._get_env_var('TEDDY_JWT_SECRET'),
            secret_key=cls._get_env_var('TEDDY_SECRET_KEY'),
            
            # Required API keys
            openai_api_key=cls._get_env_var('TEDDY_OPENAI_API_KEY'),
            anthropic_api_key=cls._get_env_var('TEDDY_ANTHROPIC_API_KEY', required=False),
            google_gemini_api_key=cls._get_env_var('TEDDY_GOOGLE_GEMINI_API_KEY', required=False),
            elevenlabs_api_key=cls._get_env_var('TEDDY_ELEVENLABS_API_KEY', required=False),
            
            # Optional API keys
            azure_speech_key=cls._get_env_var('TEDDY_AZURE_SPEECH_KEY', required=False),
            azure_speech_region=cls._get_env_var('TEDDY_AZURE_SPEECH_REGION', required=False),
            huggingface_api_key=cls._get_env_var('TEDDY_HUGGINGFACE_API_KEY', required=False),
            cohere_api_key=cls._get_env_var('TEDDY_COHERE_API_KEY', required=False),
            hume_api_key=cls._get_env_var('TEDDY_HUME_API_KEY', required=False),
            perspective_api_key=cls._get_env_var('TEDDY_PERSPECTIVE_API_KEY', required=False),
            sentry_dsn=cls._get_env_var('TEDDY_SENTRY_DSN', required=False),
            
            # Database
            database_url=cls._get_env_var('TEDDY_DATABASE_URL', 'sqlite:///data/teddy.db'),
            redis_url=cls._get_env_var('TEDDY_REDIS_URL', 'redis://localhost:6379/0'),
            
            # Environment
            environment=cls._get_env_var('TEDDY_ENVIRONMENT', 'development'),
            debug=cls._get_env_var('TEDDY_DEBUG', 'true').lower() == 'true',
            log_level=cls._get_env_var('TEDDY_LOG_LEVEL', 'INFO'),
        )
    
    @staticmethod
    def _get_env_var(key: str, default: str = None, required: bool = True) -> str:
        ""\"Get environment variable with validation""\"
        value = os.getenv(key, default)
        
        if required and not value:
            raise ValueError(f"Required environment variable {key} is not set")
        
        if value and value.startswith('${') and value.endswith('}'):
            raise ValueError(f"Environment variable {key} contains unresolved placeholder: {value}")
        
        return value
    
    @staticmethod
    def _load_env_file(env_file: Path) -> None:
        ""\"Load environment variables from .env file""\"
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        if key and value:
                            os.environ[key] = value
                            
        except Exception as e:
            logger.warning(f"Could not load .env file: {e}")
    
    def get_cipher(self) -> Fernet:
        ""\"Get encryption cipher""\"
        return Fernet(self.encryption_key.encode())
    
    def is_production(self) -> bool:
        ""\"Check if running in production""\"
        return self.environment.lower() == 'production'
    
    def is_development(self) -> bool:
        ""\"Check if running in development""\"
        return self.environment.lower() == 'development'


# Global configuration instance
_config: Optional[SecureConfig] = None

def get_config() -> SecureConfig:
    ""\"Get global configuration instance""\"
    global _config
    if _config is None:
        _config = SecureConfig.load_from_env()
    return _config

def reload_config() -> SecureConfig:
    ""\"Reload configuration (useful for testing)""\"
    global _config
    _config = None
    return get_config()
"""
        with open(config_loader_path, "w", encoding="utf-8") as f:
            f.write(config_loader_code)
        self.files_modified.add(config_loader_path)
        logger.info(f"✅ Created secure config loader at {config_loader_path}")

    def create_git_secrets_config(self) -> None:
        """Create git-secrets configuration"""
        logger.info("🔒 Creating git-secrets configuration...")
        git_secrets_path = self.project_root / ".gitsecrets"
        patterns = [
            "sk-[a-zA-Z0-9]{48,}",
            "sk-ant-[a-zA-Z0-9-]{95,}",
            "AIza[0-9A-Za-z\\-_]{35}",
            "password\\s*=\\s*['\"][^'\"]{8,}['\"]",
            "secret\\s*=\\s*['\"][^'\"]{8,}['\"]",
            "token\\s*=\\s*['\"][^'\"]{16,}['\"]",
            "[A-Za-z0-9+/]{32,}={0,2}",
        ]
        with open(git_secrets_path, "w", encoding="utf-8") as f:
            f.write("# Git Secrets Configuration\n")
            f.write("# Patterns to detect secrets in commits\n\n")
            for pattern in patterns:
                f.write(f"{pattern}\n")
        logger.info(f"✅ Created git-secrets config at {git_secrets_path}")

    def generate_cleanup_report(self) -> str:
        """Generate comprehensive cleanup report"""
        report = []
        report.append("🔒 SECURITY CLEANUP REPORT")
        report.append("=" * 50)
        report.append("")
        if self.secrets_found:
            report.append(f"⚠️ SECRETS FOUND: {len(self.secrets_found)}")
            report.append("-" * 30)
            for secret in self.secrets_found:
                report.append(f"File: {secret['file']}")
                report.append(f"Type: {secret['type']}")
                report.append(f"Line: {secret['line_number']}")
                report.append(f"Preview: {secret['value']}")
                report.append("")
        else:
            report.append("✅ NO HARDCODED SECRETS FOUND")
            report.append("")
        if self.files_modified:
            report.append(f"📝 FILES MODIFIED: {len(self.files_modified)}")
            report.append("-" * 30)
            for file_path in sorted(self.files_modified):
                report.append(f"• {file_path}")
            report.append("")
        report.append("📋 NEXT STEPS")
        report.append("-" * 30)
        report.append("1. Copy .env.template to .env")
        report.append("2. Fill in your actual API keys in .env")
        report.append("3. Copy keys from generated_keys.env to .env")
        report.append("4. DELETE generated_keys.env file")
        report.append("5. Run git-secrets scan (install if needed)")
        report.append("6. Clean Git history using BFG Repo-Cleaner")
        report.append("7. Test application with new configuration")
        report.append("")
        report.append("🗑️ GIT HISTORY CLEANUP")
        report.append("-" * 30)
        report.append("# Install BFG Repo-Cleaner")
        report.append("# Download from: https://rtyley.github.io/bfg-repo-cleaner/")
        report.append("")
        report.append("# Remove specific secrets")
        report.append("java -jar bfg.jar --replace-text secrets.txt")
        report.append("")
        report.append("# Create secrets.txt with patterns like:")
        report.append("sk-proj-BiAc9H***===>***REMOVED***")
        report.append("AIzaSyCXDVCT***===>***REMOVED***")
        report.append("")
        report.append("# Clean and push")
        report.append("git reflog expire --expire=now --all")
        report.append("git gc --prune=now --aggressive")
        report.append("git push --force-with-lease origin main")
        report.append("")
        return "\n".join(report)

    def run_full_cleanup(self) -> str:
        """Run complete security cleanup"""
        logger.info("🚀 Starting comprehensive security cleanup...")
        try:
            self.scan_for_secrets()
            self.clean_config_files()
            self.update_gitignore()
            self.generate_secure_keys()
            self.create_secure_config_loader()
            self.create_git_secrets_config()
            report = self.generate_cleanup_report()
            report_path = self.project_root / "SECURITY_CLEANUP_REPORT.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"✅ Security cleanup complete! Report saved to {report_path}")
            return report
        except Exception as e:
            logger.error(f"❌ Security cleanup failed: {e}")
            raise


def main():
    """Main execution function"""
    cleanup = SecurityCleanup()
    report = cleanup.run_full_cleanup()
    logger.info("\n" + report)


if __name__ == "__main__":
    main()
