"""
🔧 Config Loader with Environment Variables
==========================================
يقرأ config.json ويستبدل المتغيرات من .env
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Union
from dotenv import load_dotenv


class ConfigLoader:
    """محمل الإعدادات مع دعم متغيرات البيئة"""
    
    def __init__(self, config_path: str = "config/config.json", env_path: str = ".env"):
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self._config = None
        
        # تحميل متغيرات البيئة
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✅ تم تحميل متغيرات البيئة من: {self.env_path}")
        else:
            print(f"⚠️ ملف .env غير موجود في: {self.env_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """تحميل config.json مع استبدال المتغيرات"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # قراءة الملف
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_text = f.read()
        
        # استبدال المتغيرات
        config_text = self._replace_env_vars(config_text)
        
        # تحويل لـ JSON
        self._config = json.loads(config_text)
        
        return self._config
    
    def _replace_env_vars(self, text: str) -> str:
        """استبدال ${VAR_NAME} بقيمة المتغير من البيئة"""
        # البحث عن pattern: ${VARIABLE_NAME}
        pattern = r'\$\{([^}]+)\}'
        
        def replacer(match):
            var_name = match.group(1)
            # الحصول على القيمة من البيئة
            value = os.getenv(var_name)
            
            if value is None:
                print(f"⚠️ متغير البيئة غير موجود: {var_name}")
                # إرجاع القيمة الأصلية إذا لم يوجد المتغير
                return match.group(0)
            
            print(f"✅ تم استبدال: ${{{var_name}}} ← {value[:20]}...")
            return value
        
        return re.sub(pattern, replacer, text)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        الحصول على قيمة من الإعدادات باستخدام مسار نقطي
        مثال: get('API_KEYS.OPENAI_API_KEY')
        """
        if self._config is None:
            self.load_config()
        
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_api_key(self, provider: str) -> str:
        """الحصول على API key لمزود معين"""
        key_mapping = {
            'openai': 'API_KEYS.OPENAI_API_KEY',
            'anthropic': 'API_KEYS.ANTHROPIC_API_KEY',
            'google': 'API_KEYS.GOOGLE_GEMINI_API_KEY',
            'elevenlabs': 'API_KEYS.ELEVENLABS_API_KEY',
            'azure': 'API_KEYS.AZURE_SPEECH_KEY',
            'hume': 'API_KEYS.HUME_API_KEY',
        }
        
        if provider.lower() not in key_mapping:
            raise ValueError(f"Unknown provider: {provider}")
        
        return self.get(key_mapping[provider.lower()], '')
    
    def validate_config(self) -> Dict[str, bool]:
        """التحقق من وجود جميع المفاتيح المطلوبة"""
        if self._config is None:
            self.load_config()
        
        required_keys = {
            'TEDDY_OPENAI_API_KEY': 'OpenAI API Key',
            'TEDDY_SECRET_KEY': 'Secret Key',
            'TEDDY_JWT_SECRET': 'JWT Secret',
            'TEDDY_ENCRYPTION_KEY': 'Encryption Key',
        }
        
        validation_results = {}
        
        print("\n🔍 فحص المتغيرات المطلوبة:")
        print("-" * 50)
        
        for env_var, description in required_keys.items():
            value = os.getenv(env_var)
            is_valid = bool(value and not value.startswith('${'))
            validation_results[env_var] = is_valid
            
            if is_valid:
                print(f"✅ {description:.<30} موجود")
            else:
                print(f"❌ {description:.<30} مفقود!")
        
        # فحص المفاتيح الاختيارية
        optional_keys = {
            'TEDDY_ELEVENLABS_API_KEY': 'ElevenLabs API Key',
            'TEDDY_ANTHROPIC_API_KEY': 'Anthropic API Key',
            'TEDDY_GOOGLE_GEMINI_API_KEY': 'Google Gemini API Key',
            'TEDDY_HUME_API_KEY': 'Hume AI API Key',
        }
        
        print("\n📋 المفاتيح الاختيارية:")
        print("-" * 50)
        
        for env_var, description in optional_keys.items():
            value = os.getenv(env_var)
            if value and not value.startswith('${'):
                print(f"✅ {description:.<30} موجود")
            else:
                print(f"⚠️  {description:.<30} غير مُعرّف")
        
        return validation_results
    
    def export_resolved_config(self, output_path: str = "config/resolved_config.json"):
        """حفظ الإعدادات بعد استبدال المتغيرات (للتحقق فقط)"""
        if self._config is None:
            self.load_config()
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # إزالة المفاتيح الحساسة قبل الحفظ
        safe_config = self._mask_sensitive_values(self._config.copy())
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(safe_config, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 تم حفظ الإعدادات المُعالجة في: {output}")
    
    def _mask_sensitive_values(self, config: Union[Dict, Any]) -> Union[Dict, Any]:
        """إخفاء القيم الحساسة"""
        if isinstance(config, dict):
            masked = {}
            for key, value in config.items():
                if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                    if isinstance(value, str) and len(value) > 10:
                        masked[key] = value[:5] + '***' + value[-3:]
                    else:
                        masked[key] = '***HIDDEN***'
                else:
                    masked[key] = self._mask_sensitive_values(value)
            return masked
        elif isinstance(config, list):
            return [self._mask_sensitive_values(item) for item in config]
        else:
            return config


def main():
    """مثال على الاستخدام"""
    print("🚀 AI Teddy Bear - Config Loader")
    print("=" * 60)
    
    # إنشاء المحمل
    loader = ConfigLoader()
    
    try:
        # تحميل الإعدادات
        config = loader.load_config()
        print("\n✅ تم تحميل الإعدادات بنجاح!")
        
        # التحقق من الإعدادات
        validation = loader.validate_config()
        
        # أمثلة على القراءة
        print("\n📖 أمثلة على قراءة الإعدادات:")
        print("-" * 50)
        
        # قراءة إعداد بسيط
        app_name = loader.get('APPLICATION.NAME')
        print(f"اسم التطبيق: {app_name}")
        
        # قراءة API key
        openai_key = loader.get_api_key('openai')
        if openai_key and not openai_key.startswith('${'):
            print(f"OpenAI Key: {openai_key[:10]}...")
        
        # قراءة إعدادات الصوت
        default_voice = loader.get('VOICE_SETTINGS.DEFAULT_VOICE_ID')
        print(f"الصوت الافتراضي: {default_voice}")
        
        # حفظ نسخة معالجة (اختياري)
        # loader.export_resolved_config()
        
        # التحقق من الجاهزية
        print("\n🎯 حالة النظام:")
        print("-" * 50)
        
        required_valid = all(validation.values())
        if required_valid:
            print("✅ جميع المتغيرات المطلوبة موجودة - النظام جاهز!")
        else:
            print("❌ بعض المتغيرات المطلوبة مفقودة - يرجى إكمال ملف .env")
            print("\n💡 نصيحة: انسخ المثال التالي في ملف .env:")
            print("-" * 50)
            print("TEDDY_OPENAI_API_KEY=sk-your_key_here")
            print("TEDDY_SECRET_KEY=your_secret_key_here")
            print("TEDDY_JWT_SECRET=your_jwt_secret_here")
            print("TEDDY_ENCRYPTION_KEY=your_32_char_encryption_key_here")
        
    except FileNotFoundError as e:
        print(f"\n❌ خطأ: {e}")
        print("تأكد من وجود ملف config/config.json")
    except json.JSONDecodeError as e:
        print(f"\n❌ خطأ في تحليل JSON: {e}")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")


if __name__ == "__main__":
    main() 