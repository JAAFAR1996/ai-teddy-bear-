#!/usr/bin/env python3
"""
🌐 Moderation API Clients Manager
إدارة جميع عملاء APIs الخارجيين للفلترة

المسؤوليات:
- إدارة OpenAI client
- إدارة Azure Content Safety client  
- إدارة Google Cloud NLP client
- إدارة Anthropic client
- معالجة أخطاء الاتصال
"""

import logging
import os
from typing import Optional, Dict, Any

# Optional imports - APIs may not be available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    ContentSafetyClient = None
    AzureKeyCredential = None
    AZURE_AVAILABLE = False

try:
    from google.cloud import language_v1
    GOOGLE_AVAILABLE = True
except ImportError:
    language_v1 = None
    GOOGLE_AVAILABLE = False

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    AsyncOpenAI = None
    OPENAI_AVAILABLE = False

from .moderation import ContentCategory, ModerationResult, ModerationSeverity
from .moderation_helpers import ModerationRequest, ModerationLookupTables
from src.domain.exceptions import ExternalServiceException


class ModerationAPIClients:
    """🌐 مدير عملاء APIs الخارجيين"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize clients
        self.openai_client: Optional[AsyncOpenAI] = None
        self.azure_client: Optional[ContentSafetyClient] = None
        self.google_client: Optional[language_v1.LanguageServiceClient] = None
        self.anthropic_client: Optional[anthropic.AsyncAnthropic] = None
        
        self._init_all_clients()
    
    def _init_all_clients(self) -> None:
        """🔧 تهيئة جميع العملاء"""
        self._init_openai_client()
        self._init_azure_client()
        self._init_google_client()
        self._init_anthropic_client()
    
    def _init_openai_client(self) -> None:
        """🤖 تهيئة OpenAI client"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available")
            return
        
        try:
            api_key = getattr(self.config.api_keys, "OPENAI_API_KEY", "")
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                self.logger.info("OpenAI client initialized successfully")
            else:
                self.logger.warning("OpenAI API key not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def _init_azure_client(self) -> None:
        """🔷 تهيئة Azure Content Safety client"""
        if not AZURE_AVAILABLE:
            self.logger.warning("Azure Content Safety library not available")
            return
        
        try:
            key = getattr(self.config.api_keys, "AZURE_CONTENT_SAFETY_KEY", None)
            endpoint = getattr(self.config.api_keys, "AZURE_CONTENT_SAFETY_ENDPOINT", None)
            
            if key and endpoint:
                self.azure_client = ContentSafetyClient(
                    endpoint=endpoint,
                    credential=AzureKeyCredential(key)
                )
                self.logger.info("Azure Content Safety client initialized successfully")
            else:
                self.logger.warning("Azure Content Safety credentials not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure client: {e}")
    
    def _init_google_client(self) -> None:
        """🟢 تهيئة Google Cloud NLP client"""
        if not GOOGLE_AVAILABLE:
            self.logger.warning("Google Cloud NLP library not available")
            return
        
        try:
            if getattr(self.config.api_keys, "GOOGLE_CLOUD_CREDENTIALS", None):
                self.google_client = language_v1.LanguageServiceClient()
                self.logger.info("Google Cloud NLP client initialized successfully")
            else:
                self.logger.warning("Google Cloud credentials not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google client: {e}")
    
    def _init_anthropic_client(self) -> None:
        """🧠 تهيئة Anthropic client"""
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic library not available")
            return
        
        try:
            api_key = getattr(self.config.api_keys, "ANTHROPIC_API_KEY", None)
            if api_key:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
                self.logger.info("Anthropic client initialized successfully")
            else:
                self.logger.warning("Anthropic API key not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic client: {e}")
    
    # ================== OPENAI METHODS ==================
    
    async def check_with_openai(self, request: ModerationRequest) -> ModerationResult:
        """🤖 فحص المحتوى باستخدام OpenAI"""
        if not self.openai_client:
            return self._create_unavailable_result("OpenAI client not available")
        
        try:
            response = await self.openai_client.moderations.create(
                model="text-moderation-stable",
                input=request.content
            )
            
            result = response.results[0]
            return self._process_openai_result(result)
            
        except Exception as e:
            self.logger.error(f"OpenAI moderation error: {e}")
            return self._create_error_result("OpenAI", str(e))
    
    def _process_openai_result(self, result) -> ModerationResult:
        """📊 معالجة نتيجة OpenAI"""
        flagged_categories = []
        max_score = 0.0
        
        # استخدام Lookup Tables
        for openai_category, our_category in ModerationLookupTables.OPENAI_CATEGORY_MAPPING.items():
            category_attr = openai_category.replace("/", "_").replace("-", "_")
            
            if hasattr(result.categories, category_attr):
                flagged = getattr(result.categories, category_attr)
                score = getattr(result.category_scores, category_attr, 0)
                
                if flagged:
                    flagged_categories.append(our_category)
                    max_score = max(max_score, score)
        
        severity = ModerationLookupTables.get_severity_by_score(max_score)
        
        return ModerationResult(
            is_safe=not result.flagged,
            severity=severity,
            flagged_categories=list(set(flagged_categories)),
            confidence_scores={cat: max_score for cat in flagged_categories},
            matched_rules=["OpenAI moderation"],
            context_notes=["OpenAI API check"]
        )
    
    # ================== AZURE METHODS ==================
    
    async def check_with_azure(self, request: ModerationRequest) -> ModerationResult:
        """🔷 فحص المحتوى باستخدام Azure Content Safety"""
        if not self.azure_client:
            return self._create_unavailable_result("Azure client not available")
        
        try:
            from azure.ai.contentsafety.models import AnalyzeTextOptions
            
            analyze_request = AnalyzeTextOptions(text=request.content)
            response = self.azure_client.analyze_text(analyze_request)
            
            return self._process_azure_result(response)
            
        except Exception as e:
            self.logger.error(f"Azure moderation error: {e}")
            return self._create_error_result("Azure", str(e))
    
    def _process_azure_result(self, response) -> ModerationResult:
        """📊 معالجة نتيجة Azure"""
        categories = []
        confidence_scores = {}
        max_severity = 0
        
        # معالجة نتائج Azure
        severity_mapping = {
            "hate_result": ContentCategory.HATE_SPEECH,
            "self_harm_result": ContentCategory.VIOLENCE,
            "sexual_result": ContentCategory.SEXUAL,
            "violence_result": ContentCategory.VIOLENCE,
        }
        
        for result_type, category in severity_mapping.items():
            if hasattr(response, result_type):
                result = getattr(response, result_type)
                if result.severity > 0:
                    categories.append(category)
                    confidence_scores[category] = result.severity / 6  # تحويل إلى 0-1
                    max_severity = max(max_severity, result.severity)
        
        # تحديد الخطورة العامة
        if max_severity == 0:
            severity = ModerationSeverity.SAFE
        elif max_severity <= 2:
            severity = ModerationSeverity.LOW
        elif max_severity <= 4:
            severity = ModerationSeverity.MEDIUM
        else:
            severity = ModerationSeverity.HIGH
        
        return ModerationResult(
            is_safe=max_severity <= 2,
            severity=severity,
            flagged_categories=categories,
            confidence_scores=confidence_scores,
            matched_rules=["Azure Content Safety"],
            context_notes=["Azure API check"]
        )
    
    # ================== GOOGLE METHODS ==================
    
    async def check_with_google(self, request: ModerationRequest) -> ModerationResult:
        """🟢 فحص المحتوى باستخدام Google Cloud NLP"""
        if not self.google_client:
            return self._create_unavailable_result("Google client not available")
        
        try:
            document = language_v1.Document(
                content=request.content,
                type_=language_v1.Document.Type.PLAIN_TEXT,
            )
            
            # تحليل المشاعر
            sentiment_response = self.google_client.analyze_sentiment(
                request={"document": document}
            )
            
            # تحليل الكيانات
            entities_response = self.google_client.analyze_entities(
                request={"document": document}
            )
            
            return self._process_google_result(sentiment_response, entities_response)
            
        except Exception as e:
            self.logger.error(f"Google moderation error: {e}")
            return self._create_error_result("Google", str(e))
    
    def _process_google_result(self, sentiment_response, entities_response) -> ModerationResult:
        """📊 معالجة نتيجة Google"""
        categories = []
        confidence_scores = {}
        
        # فحص المشاعر
        sentiment_score = sentiment_response.document_sentiment.score
        if sentiment_score < -0.5:
            categories.append(ContentCategory.BULLYING)
            confidence_scores[ContentCategory.BULLYING] = abs(sentiment_score)
        
        # فحص المعلومات الشخصية
        for entity in entities_response.entities:
            if entity.type_ in [
                language_v1.Entity.Type.PERSON,
                language_v1.Entity.Type.PHONE_NUMBER,
                language_v1.Entity.Type.ADDRESS,
            ]:
                categories.append(ContentCategory.PERSONAL_INFO)
                confidence_scores[ContentCategory.PERSONAL_INFO] = 0.8
                break
        
        severity = ModerationSeverity.MEDIUM if categories else ModerationSeverity.SAFE
        
        return ModerationResult(
            is_safe=len(categories) == 0,
            severity=severity,
            flagged_categories=categories,
            confidence_scores=confidence_scores,
            matched_rules=["Google Cloud NLP"],
            context_notes=["Google API check"]
        )
    
    # ================== HELPER METHODS ==================
    
    def _create_unavailable_result(self, note: str) -> ModerationResult:
        """✅ إنشاء نتيجة للخدمة غير المتوفرة"""
        return ModerationResult(
            is_safe=True,
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            matched_rules=[],
            context_notes=[note]
        )
    
    def _create_error_result(self, service: str, error: str) -> ModerationResult:
        """❌ إنشاء نتيجة للخطأ (fail safely)"""
        return ModerationResult(
            is_safe=True,  # نفشل بأمان - لا نحجب المحتوى عند خطأ API
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            matched_rules=[f"{service} failed"],
            context_notes=[f"{service} error: {error}"]
        )
    
    def get_client_status(self) -> Dict[str, bool]:
        """📊 حالة جميع العملاء"""
        return {
            "openai": self.openai_client is not None,
            "azure": self.azure_client is not None,
            "google": self.google_client is not None,
            "anthropic": self.anthropic_client is not None,
        }
    
    def is_any_client_available(self) -> bool:
        """🔍 هل أي عميل متوفر؟"""
        status = self.get_client_status()
        return any(status.values())


# ================== FACTORY FUNCTION ==================

def create_api_clients(config) -> ModerationAPIClients:
    """🏭 Factory function لإنشاء مدير العملاء"""
    return ModerationAPIClients(config) 