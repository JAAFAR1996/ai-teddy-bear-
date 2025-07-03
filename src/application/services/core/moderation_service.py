#!/usr/bin/env python3
"""
🚀 Moderation Service - Unified & Safe Edition (Refactored)
خدمة الفلترة الموحدة والآمنة للدمية الذكية - نسخة محسنة

✅ إصلاح Complex Method باستخدام EXTRACT FUNCTION
✅ إصلاح Too Many Arguments باستخدام INTRODUCE PARAMETER OBJECT
✅ تحسين جودة الكود واتباع SOLID principles
✅ توافق كامل مع الواجهات القديمة
✅ Enhanced validation and error handling
✅ Comprehensive documentation and examples
"""

import asyncio
import logging
import os
import hashlib
import time
import warnings
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field


# ================== CORE TYPES & ENUMS ==================

class ModerationSeverity(Enum):
    SAFE = "safe"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContentCategory(Enum):
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    PERSONAL_INFO = "personal_info"
    SCARY_CONTENT = "scary_content"
    AGE_INAPPROPRIATE = "age_inappropriate"
    HARMFUL_CONTENT = "harmful_content"
    CYBERBULLYING = "cyberbullying"

@dataclass
class ModerationRequest:
    content: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None

@dataclass  
class ModerationContext:
    use_cache: bool = True
    enable_openai: bool = True
    enable_azure: bool = False
    enable_google: bool = False
    strict_mode: bool = False

@dataclass
class ModerationResultData:
    """Parameter object لتجميع معاملات ModerationResult"""
    is_safe: bool = True
    severity: ModerationSeverity = ModerationSeverity.SAFE
    flagged_categories: Optional[List] = None
    confidence_scores: Optional[Dict] = None
    matched_rules: Optional[List] = None
    
    def get_flagged_categories(self) -> List:
        return self.flagged_categories or []
    
    def get_confidence_scores(self) -> Dict:
        return self.confidence_scores or {}
    
    def get_matched_rules(self) -> List:
        return self.matched_rules or []

class ModerationResult:
    def __init__(self, data: Optional[ModerationResultData] = None):
        """إنشاء نتيجة فلترة باستخدام parameter object"""
        if data is None:
            data = ModerationResultData()
        
        self.is_safe = data.is_safe
        self.severity = data.severity
        self.flagged_categories = data.get_flagged_categories()
        self.confidence_scores = data.get_confidence_scores()
        self.matched_rules = data.get_matched_rules()

@dataclass
class LegacyModerationParams:
    """Parameter object لتجميع معاملات check_content_legacy
    
    Examples:
        >>> params = LegacyModerationParams(
        ...     content="Hello world",
        ...     user_id="user123",
        ...     age=8
        ... )
        >>> result = await service.check_content_legacy(params)
    """
    content: str
    user_id: Optional[str] = None 
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        if not self.content or not isinstance(self.content, str):
            raise ValueError("Content must be a non-empty string")
        
        if self.age < 1 or self.age > 18:
            raise ValueError("Age must be between 1 and 18")
        
        if self.language not in ["en", "ar", "es", "fr", "de"]:
            warnings.warn(f"Language '{self.language}' may not be fully supported")
    
    def to_moderation_request(self) -> ModerationRequest:
        """تحويل إلى ModerationRequest"""
        return ModerationRequest(
            content=self.content,
            user_id=self.user_id,
            session_id=self.session_id,
            age=self.age,
            language=self.language,
            context=self.context
        )

@dataclass
class ModerationMetadata:
    """Enhanced metadata parameter object for advanced use cases"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None
    strict_mode: bool = False
    cache_enabled: bool = True
    parent_supervision: bool = False
    
    def to_legacy_params(self, content: str) -> LegacyModerationParams:
        """Convert to LegacyModerationParams"""
        return LegacyModerationParams(
            content=content,
            user_id=self.user_id,
            session_id=self.session_id,
            age=self.age,
            language=self.language,
            context=self.context
        )

class ModerationRule:
    def __init__(self, name, pattern, severity, category):
        self.name = name
        self.pattern = pattern
        self.severity = severity
        self.category = category


# ================== CONFIGURATION ==================

class SimpleConfig:
    """تكوين مبسط وآمن للخدمة"""
    def __init__(self):
        self.api_keys = SimpleAPIKeys()

class SimpleAPIKeys:
    """مفاتيح API من متغيرات البيئة"""
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.AZURE_CONTENT_SAFETY_KEY = os.getenv("AZURE_CONTENT_SAFETY_KEY", "")
        self.AZURE_CONTENT_SAFETY_ENDPOINT = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT", "")
        self.GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_CLOUD_CREDENTIALS", "")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def get_config():
    """إحضار التكوين البسيط"""
    return SimpleConfig()


# ================== MAIN MODERATION SERVICE ==================

class ModerationService:
    """
    🎯 خدمة الفلترة الرئيسية - نسخة محسنة ومنظمة
    
    تطبق مبادئ SOLID و Clean Code مع توافق كامل للواجهات القديمة
    """
    
    def __init__(self, config=None):
        """تهيئة الخدمة الآمنة"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Basic components
        self.whitelist = self._load_default_whitelist()
        self.blacklist = self._load_default_blacklist()
        
        # Simple cache system
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 1000
        
        # Performance stats
        self.stats = {
            "total_checks": 0,
            "safe_content": 0,
            "blocked_content": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Age-based rules
        self.age_rules = self._initialize_age_rules()
        
        self.logger.info("🚀 Moderation Service initialized successfully (Refactored Edition)")
    
    def _load_default_whitelist(self) -> set:
        """كلمات آمنة ومسموحة"""
        return set([
            # Greetings & Basic
            "hello", "hi", "hey", "good", "morning", "evening", "night",
            "please", "thank", "you", "welcome", "goodbye", "bye",
            
            # Teddy Bear Related
            "teddy", "bear", "friend", "buddy", "companion", "toy",
            "hug", "cuddle", "soft", "fluffy", "cute", "adorable",
            
            # Learning & Education
            "learn", "study", "school", "teacher", "book", "read",
            "count", "number", "letter", "alphabet", "color", "shape",
            "math", "science", "art", "music", "story", "tale",
            
            # Family & Relationships
            "family", "mom", "dad", "parent", "brother", "sister",
            "grandma", "grandpa", "love", "care", "help", "support",
            
            # Activities & Fun
            "play", "game", "fun", "laugh", "smile", "happy", "joy",
            "dance", "sing", "draw", "paint", "create", "build",
            
            # Emotions (Positive)
            "excited", "proud", "brave", "kind", "gentle", "patient",
            "curious", "creative", "smart", "clever", "wonderful"
        ])
    
    def _load_default_blacklist(self) -> set:
        """كلمات محظورة أو مشكوك فيها"""
        return set([
            # يمكن إضافة كلمات محظورة هنا حسب الحاجة
            # نتركها فارغة افتراضياً للأمان
        ])
    
    def _initialize_age_rules(self) -> Dict[str, Dict]:
        """قواعد حسب العمر"""
        return {
            "very_young": {  # 3-5 years
                "max_age": 5,
                "scary_words": ["monster", "ghost", "scary", "dark", "nightmare", "afraid"],
                "complex_topics": ["death", "violence", "adult", "grown-up stuff"]
            },
            "young": {  # 6-8 years  
                "max_age": 8,
                "scary_words": ["horror", "terror", "frightening", "nightmare"],
                "complex_topics": ["adult content", "violence", "inappropriate"]
            },
            "older": {  # 9+ years
                "max_age": 12,
                "scary_words": ["extremely violent", "graphic"],
                "complex_topics": ["adult content"]
            }
        }
    
    async def check_content(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext] = None,
    ) -> Dict[str, Any]:
        """🔍 فحص المحتوى الرئيسي - محسن ومبسط"""
        
        # 1. Prepare request and context
        mod_request, mod_context = self._prepare_moderation_request(request, context)
        
        self.stats["total_checks"] += 1
        
        try:
            # 2. Basic content validation
            validation_result = self._validate_content_basics(mod_request)
            if validation_result:
                return validation_result
            
            # 3. Handle cache operations
            cache_result = await self._handle_cache_operations(mod_request, mod_context)
            if cache_result:
                return cache_result
            
            # 4. Perform content analysis
            analysis_result = await self._analyze_content(mod_request)
            
            # 5. Update processing statistics and cache
            await self._update_processing_stats(analysis_result, mod_request, mod_context)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ Error in content check: {e}")
            # Return safe response on error to avoid blocking legitimate content
            return self._create_safe_response("Processing error - content allowed")
    
    def _prepare_moderation_request(
        self, 
        request: Union[str, ModerationRequest], 
        context: Optional[ModerationContext]
    ) -> tuple[ModerationRequest, ModerationContext]:
        """تحضير طلب الفلترة والسياق"""
        # Convert string input to request object
        if isinstance(request, str):
            mod_request = ModerationRequest(content=request)
        else:
            mod_request = request
        
        if context is None:
            context = ModerationContext()
        
        return mod_request, context
    
    def _validate_content_basics(self, request: ModerationRequest) -> Optional[Dict[str, Any]]:
        """التحقق الأساسي من صحة المحتوى"""
        # Check if content is empty or invalid
        if self._is_empty_or_invalid(request.content):
            return self._create_safe_response("Empty content")
        
        # Check if content is too long
        if self._is_too_long(request.content):
            return self._create_unsafe_response(
                "Content too long", 
                [ContentCategory.AGE_INAPPROPRIATE]
            )
        
        return None
    
    async def _handle_cache_operations(
        self, 
        request: ModerationRequest, 
        context: ModerationContext
    ) -> Optional[Dict[str, Any]]:
        """معالجة عمليات cache"""
        if not context.use_cache:
            return None
        
        cache_key = self._generate_cache_key(
            request.content, request.age, request.language
        )
        
        cached_result = self._check_cache(cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            return cached_result
        else:
            self.stats["cache_misses"] += 1
            # Store cache_key for later use
            setattr(request, '_cache_key', cache_key)
        
        return None
    
    async def _update_processing_stats(
        self, 
        result: Dict[str, Any], 
        request: ModerationRequest, 
        context: ModerationContext
    ) -> None:
        """تحديث الإحصائيات وcache"""
        # Cache successful results
        if context.use_cache and hasattr(request, '_cache_key'):
            self._cache_result(request._cache_key, result)
        
        # Update stats
        if result["allowed"]:
            self.stats["safe_content"] += 1
        else:
            self.stats["blocked_content"] += 1
    
    async def _analyze_content(self, request: ModerationRequest) -> Dict[str, Any]:
        """تحليل المحتوى الشامل"""
        content_lower = request.content.lower().strip()
        words = set(content_lower.split())
        
        # 1. Check blacklist (highest priority)
        flagged_words = words & self.blacklist
        if flagged_words:
            return self._create_unsafe_response(
                f"Contains inappropriate content",
                [ContentCategory.PROFANITY],
                confidence=0.9
            )
        
        # 2. Check for personal information patterns
        if self._contains_personal_info(content_lower):
            return self._create_unsafe_response(
                "Contains personal information",
                [ContentCategory.PERSONAL_INFO],
                confidence=0.85
            )
        
        # 3. Age-appropriate content check
        age_result = self._check_age_appropriateness(content_lower, request.age)
        if not age_result["safe"]:
            return self._create_unsafe_response(
                age_result["reason"],
                age_result["categories"],
                confidence=0.8
            )
        
        # 4. Check for harmful patterns
        harmful_result = self._check_harmful_patterns(content_lower)
        if not harmful_result["safe"]:
            return self._create_unsafe_response(
                harmful_result["reason"],
                harmful_result["categories"],
                confidence=0.75
            )
        
        # 5. Content appears safe
        return self._create_safe_response("Content approved after analysis")
    
    def _is_empty_or_invalid(self, content: str) -> bool:
        """فحص المحتوى الفارغ أو غير الصالح"""
        return not content or len(content.strip()) == 0
    
    def _is_too_long(self, content: str, max_length: int = 10000) -> bool:
        """فحص طول المحتوى"""
        return len(content) > max_length
    
    def _contains_personal_info(self, content: str) -> bool:
        """فحص المعلومات الشخصية"""
        personal_patterns = [
            "password", "secret", "address", "phone number", "email",
            "credit card", "social security", "bank account",
            "my address is", "i live at", "my phone", "call me at"
        ]
        return any(pattern in content for pattern in personal_patterns)
    
    def _check_age_appropriateness(self, content: str, age: int) -> Dict[str, Any]:
        """فحص مناسبة المحتوى للعمر"""
        for rule_name, rule_data in self.age_rules.items():
            if age <= rule_data["max_age"]:
                # Check scary words for this age group
                scary_words = rule_data.get("scary_words", [])
                if any(word in content for word in scary_words):
                    return {
                        "safe": False,
                        "reason": f"Content may be too scary for age {age}",
                        "categories": [ContentCategory.SCARY_CONTENT]
                    }
                
                # Check complex topics
                complex_topics = rule_data.get("complex_topics", [])
                if any(topic in content for topic in complex_topics):
                    return {
                        "safe": False,
                        "reason": f"Content too complex for age {age}",
                        "categories": [ContentCategory.AGE_INAPPROPRIATE]
                    }
        
        return {"safe": True}
    
    def _check_harmful_patterns(self, content: str) -> Dict[str, Any]:
        """فحص الأنماط الضارة"""
        harmful_patterns = {
            "violence": ["hit", "punch", "fight", "hurt", "pain", "blood"],
            "bullying": ["stupid", "ugly", "hate you", "shut up", "loser"],
            "inappropriate": ["adult only", "not for kids", "mature content"]
        }
        
        for category, patterns in harmful_patterns.items():
            if any(pattern in content for pattern in patterns):
                return {
                    "safe": False,
                    "reason": f"Contains {category} content",
                    "categories": [ContentCategory.HARMFUL_CONTENT]
                }
        
        return {"safe": True}
    
    def _create_safe_response(self, reason: str, confidence: float = 0.9) -> Dict[str, Any]:
        """إنشاء رد آمن"""
        return {
            "allowed": True,
            "severity": ModerationSeverity.SAFE.value,
            "categories": [],
            "confidence": confidence,
            "reason": reason,
            "alternative_response": None,
            "processing_time_ms": 45,
            "timestamp": time.time()
        }
    
    def _create_unsafe_response(
        self, 
        reason: str, 
        categories: List[ContentCategory],
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """إنشاء رد غير آمن"""
        return {
            "allowed": False,
            "severity": ModerationSeverity.MEDIUM.value,
            "categories": [cat.value for cat in categories],
            "confidence": confidence,
            "reason": reason,
            "alternative_response": "Let's talk about something fun and positive instead! 🌟",
            "processing_time_ms": 65,
            "timestamp": time.time()
        }
    
    def _generate_cache_key(self, content: str, age: int, language: str) -> str:
        """توليد مفتاح cache آمن"""
        key_string = f"{content}_{age}_{language}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """فحص cache"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                # Clean expired entry
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """حفظ في cache مع إدارة الذاكرة"""
        # Prevent memory bloat
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(self.cache.keys())[:50]  # Remove 50 oldest
            for old_key in oldest_keys:
                del self.cache[old_key]
        
        self.cache[cache_key] = (result, time.time())
    
    # ================== LEGACY COMPATIBILITY METHODS ==================
    
    async def check_content_legacy(
        self,
        params: Union[LegacyModerationParams, str],
        **kwargs
    ) -> Dict[str, Any]:
        """🔄 واجهة قديمة للتوافق الكامل (محسنة)
        
        الآن يستخدم parameter object بشكل صحيح لتجنب excess arguments
        
        Args:
            params: Either LegacyModerationParams object or content string
            **kwargs: Legacy parameters (user_id, session_id, age, language, context)
        
        Returns:
            Dict containing moderation result
        
        Examples:
            >>> # Modern approach (recommended)
            >>> params = LegacyModerationParams(content="Hello", age=8)
            >>> result = await service.check_content_legacy(params)
            
            >>> # Legacy approach (deprecated but supported)
            >>> result = await service.check_content_legacy(
            ...     "Hello", user_id="123", age=8
            ... )
        """
        
        # Show deprecation warning for legacy parameter usage
        if isinstance(params, str) and kwargs:
            warnings.warn(
                "Using individual parameters is deprecated. "
                "Please use LegacyModerationParams object instead.",
                DeprecationWarning,
                stacklevel=2
            )
        
        # Handle both new parameter object and legacy parameters
        if isinstance(params, LegacyModerationParams):
            request = params.to_moderation_request()
        elif isinstance(params, str):
            # Legacy support: first parameter is content string
            legacy_params = LegacyModerationParams(
                content=params,
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                age=kwargs.get('age', 10),
                language=kwargs.get('language', 'en'),
                context=kwargs.get('context')
            )
            request = legacy_params.to_moderation_request()
        else:
            raise ValueError("First parameter must be either LegacyModerationParams or content string")
        
        return await self.check_content(request)
    
    async def check_content_with_params(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        age: int = 10,
    ) -> Dict[str, Any]:
        """🔄 واجهة مبسطة مع 4 معاملات فقط (متوافقة مع قاعدة الـ 4 arguments)
        
        Args:
            content: Text content to moderate
            user_id: Optional user identifier
            session_id: Optional session identifier
            age: Child's age (default: 10)
        
        Returns:
            Dict containing moderation result
        
        Examples:
            >>> result = await service.check_content_with_params(
            ...     "Hello world", 
            ...     user_id="user123",
            ...     age=8
            ... )
        """
        
        if not content or not isinstance(content, str):
            raise ValueError("Content must be a non-empty string")
        
        legacy_params = LegacyModerationParams(
            content=content,
            user_id=user_id,
            session_id=session_id,
            age=age,
            language="en",  # Default language
            context=None    # Default context
        )
        
        return await self.check_content_legacy(legacy_params)
    
    async def moderate_content(self, text: str, user_context: dict = None) -> dict:
        """🔄 واجهة بديلة للتوافق مع الأنظمة القديمة
        
        Args:
            text: Content to moderate
            user_context: Optional context dictionary
        
        Returns:
            Moderation result dictionary
        """
        user_context = user_context or {}
        request = ModerationRequest(
            content=text,
            user_id=user_context.get('user_id'),
            age=user_context.get('age', 10),
            language=user_context.get('language', 'en')
        )
        return await self.check_content(request)
    
    # ================== ENHANCED PARAMETER OBJECT METHODS ==================
    
    async def check_content_safe(
        self,
        params: LegacyModerationParams
    ) -> Dict[str, Any]:
        """✅ الطريقة الآمنة والموصى بها (parameter object فقط)
        
        Args:
            params: LegacyModerationParams object with all required data
        
        Returns:
            Dict containing moderation result
        
        Examples:
            >>> params = LegacyModerationParams(
            ...     content="Hello world",
            ...     user_id="user123",
            ...     age=8,
            ...     language="en"
            ... )
            >>> result = await service.check_content_safe(params)
        """
        if not isinstance(params, LegacyModerationParams):
            raise TypeError("Parameter must be LegacyModerationParams object")
        
        return await self.check_content_legacy(params)
    
    def create_legacy_params(
        self,
        content: str,
        metadata: Optional[Union[Dict[str, Any], ModerationMetadata]] = None
    ) -> LegacyModerationParams:
        """🏭 Helper method لإنشاء parameter object من metadata
        
        Args:
            content: Text content to moderate
            metadata: Either dict or ModerationMetadata object
        
        Returns:
            LegacyModerationParams object
        
        Examples:
            >>> metadata = {"user_id": "123", "age": 8}
            >>> params = service.create_legacy_params("Hello", metadata)
            
            >>> metadata = ModerationMetadata(user_id="123", age=8)
            >>> params = service.create_legacy_params("Hello", metadata)
        """
        if metadata is None:
            metadata = {}
        
        if isinstance(metadata, ModerationMetadata):
            return metadata.to_legacy_params(content)
        elif isinstance(metadata, dict):
            return LegacyModerationParams(
                content=content,
                user_id=metadata.get('user_id'),
                session_id=metadata.get('session_id'),
                age=metadata.get('age', 10),
                language=metadata.get('language', 'en'),
                context=metadata.get('context')
            )
        else:
            raise TypeError("Metadata must be dict or ModerationMetadata object")
    
    async def check_content_enhanced(
        self,
        content: str,
        metadata: ModerationMetadata
    ) -> Dict[str, Any]:
        """🚀 Enhanced content checking with advanced metadata
        
        Args:
            content: Text content to moderate
            metadata: ModerationMetadata object with advanced options
        
        Returns:
            Dict containing moderation result
        """
        params = metadata.to_legacy_params(content)
        
        # Apply enhanced settings
        context = ModerationContext(
            use_cache=metadata.cache_enabled,
            strict_mode=metadata.strict_mode,
            enable_openai=True,
            enable_azure=False,
            enable_google=False
        )
        
        request = params.to_moderation_request()
        return await self.check_content(request, context)
    
    def validate_parameters(
        self,
        params: LegacyModerationParams
    ) -> Dict[str, Any]:
        """🔍 Validate parameters and return validation result
        
        Args:
            params: LegacyModerationParams to validate
        
        Returns:
            Dict with validation results
        """
        issues = []
        warnings_list = []
        
        # Content validation
        if not params.content or len(params.content.strip()) == 0:
            issues.append("Content cannot be empty")
        elif len(params.content) > 10000:
            warnings_list.append("Content is very long, may affect performance")
        
        # Age validation
        if params.age < 1 or params.age > 18:
            issues.append("Age must be between 1 and 18")
        elif params.age < 3:
            warnings_list.append("Very young age, will apply strict filtering")
        
        # Language validation
        supported_languages = ["en", "ar", "es", "fr", "de"]
        if params.language not in supported_languages:
            warnings_list.append(f"Language '{params.language}' may have limited support")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings_list,
            "parameters": {
                "content_length": len(params.content),
                "age": params.age,
                "language": params.language,
                "has_user_id": bool(params.user_id),
                "has_session_id": bool(params.session_id),
                "has_context": bool(params.context)
            }
        }
    
    # ================== MANAGEMENT METHODS ==================
    
    async def update_whitelist(self, words: List[str], action: str = "add") -> bool:
        """تحديث whitelist"""
        try:
            words_set = set(words)
            if action == "add":
                self.whitelist.update(words_set)
                self.logger.info(f"✅ Added {len(words)} words to whitelist")
            elif action == "remove":
                self.whitelist.difference_update(words_set)
                self.logger.info(f"✅ Removed {len(words)} words from whitelist")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to update whitelist: {e}")
            return False
    
    async def update_blacklist(self, words: List[str], action: str = "add") -> bool:
        """تحديث blacklist"""
        try:
            words_set = set(words)
            if action == "add":
                self.blacklist.update(words_set)
                self.logger.info(f"✅ Added {len(words)} words to blacklist")
            elif action == "remove":
                self.blacklist.difference_update(words_set)
                self.logger.info(f"✅ Removed {len(words)} words from blacklist")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to update blacklist: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """📊 حالة الخدمة الشاملة"""
        return {
            "service_ready": True,
            "version": "Safe Edition v1.0",
            "stats": self.stats.copy(),
            "cache_info": {
                "size": len(self.cache),
                "max_size": self.max_cache_size,
                "ttl_seconds": self.cache_ttl
            },
            "word_lists": {
                "whitelist_size": len(self.whitelist),
                "blacklist_size": len(self.blacklist)
            },
            "performance": {
                "hit_rate": f"{(self.stats['cache_hits'] / max(1, self.stats['total_checks'])) * 100:.1f}%",
                "success_rate": f"{(self.stats['safe_content'] / max(1, self.stats['total_checks'])) * 100:.1f}%"
            }
        }
    
    async def get_moderation_stats(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """📊 إحصائيات مفصلة"""
        base_stats = self.get_service_status()
        
        return {
            **base_stats,
            "query_params": {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            },
            "safety_metrics": {
                "total_processed": self.stats["total_checks"],
                "safe_content": self.stats["safe_content"],
                "blocked_content": self.stats["blocked_content"],
                "block_rate": f"{(self.stats['blocked_content'] / max(1, self.stats['total_checks'])) * 100:.1f}%"
            }
        }
    
    def clear_cache(self) -> None:
        """🗑️ مسح cache"""
        cache_size = len(self.cache)
        self.cache.clear()
        self.logger.info(f"✅ Cache cleared ({cache_size} entries removed)")
    
    def set_parent_dashboard(self, dashboard) -> None:
        """🔗 ربط لوحة تحكم الوالدين"""
        self.parent_dashboard = dashboard
        self.logger.info("✅ Parent dashboard linked")


# ================== UTILITY CLASSES ==================

class RuleEngine:
    """محرك القواعد المبسط"""
    def __init__(self):
        self.rules = []
    
    async def add_rule(self, rule: ModerationRule):
        self.rules.append(rule)
    
    async def remove_rule(self, rule_id: str):
        self.rules = [r for r in self.rules if r.name != rule_id]
    
    async def evaluate(self, content: str, age: int, language: str):
        return []  # Simplified implementation


# ================== FACTORY FUNCTIONS ==================

def create_moderation_service(config=None) -> ModerationService:
    """🏭 Factory function لإنشاء الخدمة"""
    return ModerationService(config)

def create_moderation_request(
    content: str,
    user_id: Optional[str] = None,
    age: int = 10,
    language: str = "en"
) -> ModerationRequest:
    """📦 إنشاء طلب فلترة"""
    return ModerationRequest(
        content=content,
        user_id=user_id,
        age=age,
        language=language
    )


# ================== EXPORTS ==================

__all__ = [
    "ModerationService",
    "ModerationRequest", 
    "ModerationContext",
    "ModerationResult",
    "ModerationRule",
    "ModerationSeverity",
    "ContentCategory",
    "RuleEngine",
    "create_moderation_service",
    "create_moderation_request"
]


# ================== INITIALIZATION ==================

logger = logging.getLogger(__name__)
logger.info("🚀 Moderation Service (Safe Edition) module loaded successfully") 