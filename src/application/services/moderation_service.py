# moderation_service.py - Enhanced content moderation for child safety
import uuid
import asyncio
import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict
import hashlib
import os
from openai import AsyncOpenAI
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from google.cloud import language_v1
import anthropic
from transformers import pipeline
import spacy
import redis.asyncio as aioredis
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from src.infrastructure.security.encryption import EncryptionService

from src.infrastructure.config import get_config
from src.domain.entities.conversation import Conversation, Message
from src.application.services.parent_dashboard_service import ParentDashboardService

Base = declarative_base()


class ModerationSeverity(Enum):
    """Severity levels for moderation"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Content categories for moderation"""
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    PROFANITY = "profanity"
    PERSONAL_INFO = "personal_info"
    BULLYING = "bullying"
    DRUGS = "drugs"
    WEAPONS = "weapons"
    SCARY_CONTENT = "scary_content"
    AGE_INAPPROPRIATE = "age_inappropriate"
    SPAM = "spam"
    PHISHING = "phishing"


@dataclass
class ModerationResult:
    """Enhanced moderation result with detailed information"""
    is_safe: bool
    severity: ModerationSeverity
    flagged_categories: List[ContentCategory] = field(default_factory=list)
    confidence_scores: Dict[ContentCategory,
                            float] = field(default_factory=dict)
    matched_rules: List[str] = field(default_factory=list)
    context_notes: List[str] = field(default_factory=list)
    alternative_response: Optional[str] = None
    should_alert_parent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def overall_score(self) -> float:
        """Calculate overall moderation score"""
        if not self.confidence_scores:
            return 0.0
        return max(self.confidence_scores.values())


@dataclass
class ModerationRule:
    """Custom moderation rule"""
    id: str
    name: str
    description: str
    pattern: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    category: ContentCategory = ContentCategory.AGE_INAPPROPRIATE
    severity: ModerationSeverity = ModerationSeverity.MEDIUM
    age_range: Tuple[int, int] = (0, 18)
    languages: List[str] = field(default_factory=lambda: ['en', 'ar'])
    is_regex: bool = False
    context_required: bool = False
    enabled: bool = True
    parent_override: bool = False
    action: str = "block"  # block, warn, log


class ModerationLog(Base):
    """Database model for moderation logs"""
    __tablename__ = 'moderation_logs'

    id = Column(String, primary_key=True)
    session_id = Column(String)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    content = Column(String)
    result = Column(JSON)
    severity = Column(String)
    categories = Column(JSON)
    action_taken = Column(String)
    parent_notified = Column(Boolean, default=False)


class RuleEngine:
    """Advanced rule engine for content moderation"""

    def __init__(self):
        self.rules: Dict[str, ModerationRule] = {}
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default moderation rules"""
        default_rules = [
            ModerationRule(
                id="personal_info_1",
                name="Personal Information Detection",
                description="Detects personal information like phone numbers, addresses",
                pattern=r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\d{5,}\b',
                category=ContentCategory.PERSONAL_INFO,
                severity=ModerationSeverity.HIGH,
                is_regex=True
            ),
            ModerationRule(
                id="violence_1",
                name="Violence Keywords",
                description="Detects violent language",
                keywords=["kill", "murder", "hurt", "harm", "attack", "fight"],
                category=ContentCategory.VIOLENCE,
                severity=ModerationSeverity.HIGH,
                context_required=True
            ),
            ModerationRule(
                id="scary_content_1",
                name="Scary Content for Young Children",
                description="Content that might scare young children",
                keywords=["monster", "ghost", "scary", "nightmare", "demon"],
                category=ContentCategory.SCARY_CONTENT,
                severity=ModerationSeverity.LOW,
                age_range=(3, 8)
            ),
            ModerationRule(
                id="bullying_1",
                name="Bullying Detection",
                description="Detects bullying language",
                keywords=["stupid", "dumb", "loser",
                          "hate you", "nobody likes"],
                category=ContentCategory.BULLYING,
                severity=ModerationSeverity.MEDIUM
            )
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: ModerationRule):
        """Add a moderation rule"""
        self.rules[rule.id] = rule
        if rule.pattern and rule.is_regex:
            self.compiled_patterns[rule.id] = re.compile(
                rule.pattern, re.IGNORECASE)

    def remove_rule(self, rule_id: str):
        """Remove a moderation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            if rule_id in self.compiled_patterns:
                del self.compiled_patterns[rule_id]

    async def evaluate(self, text: str, age: int = 10, language: str = 'en') -> List[Tuple[ModerationRule, float]]:
        """Evaluate text against all rules"""
        matched_rules = []

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            # Check age range
            if not (rule.age_range[0] <= age <= rule.age_range[1]):
                continue

            # Check language
            if language not in rule.languages:
                continue

            confidence = 0.0

            # Check regex pattern
            if rule.pattern and rule.is_regex and rule_id in self.compiled_patterns:
                if self.compiled_patterns[rule_id].search(text):
                    confidence = 0.9

            # Check keywords
            if rule.keywords:
                text_lower = text.lower()
                matches = sum(
                    1 for keyword in rule.keywords if keyword.lower() in text_lower)
                if matches > 0:
                    confidence = max(confidence, min(matches * 0.3, 0.9))

            if confidence > 0:
                matched_rules.append((rule, confidence))

        return matched_rules


class ModerationService:
    """
    Enhanced content moderation service for child safety
    """

    def __init__(self, config=None):
        """Initialize moderation service"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize API clients
        self._init_api_clients()

        # Initialize components
        self.rule_engine = RuleEngine()
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self._load_lists()

        # Cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

        # Alert thresholds
        self.alert_thresholds = {
            ModerationSeverity.LOW: 5,      # 5 low severity in 1 hour
            ModerationSeverity.MEDIUM: 3,    # 3 medium severity in 1 hour
            ModerationSeverity.HIGH: 1,      # 1 high severity immediately
            ModerationSeverity.CRITICAL: 1   # 1 critical immediately
        }

        # Tracking for alerts
        self.severity_tracker = defaultdict(list)

        # Parent dashboard service
        self.parent_dashboard = None

        # NLP models
        self._init_nlp_models()

    def _init_api_clients(self):
        """Initialize external API clients"""
        # Azure Content Safety
        if getattr(self.config.api_keys, "AZURE_CONTENT_SAFETY_KEY", None) and getattr(self.config.api_keys, "AZURE_CONTENT_SAFETY_ENDPOINT", None):
            self.azure_client = ContentSafetyClient(
                endpoint=self.config.api_keys.AZURE_CONTENT_SAFETY_ENDPOINT,
                credential=AzureKeyCredential(
                    self.config.api_keys.AZURE_CONTENT_SAFETY_KEY)
            )
        else:
            self.azure_client = None

         # Google Cloud Natural Language
        if getattr(self.config.api_keys, "GOOGLE_CLOUD_CREDENTIALS", None):
            self.google_client = language_v1.LanguageServiceClient()
        else:
            self.google_client = None

            # Anthropic (for Claude's content analysis)
        if getattr(self.config.api_keys, "ANTHROPIC_API_KEY", None):
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.config.api_keys.ANTHROPIC_API_KEY
            )
        else:
            self.anthropic_client = None

    def _init_nlp_models(self):

        hf_token = (
            os.environ.get("HUGGINGFACE_TOKEN")
            or os.environ.get("HUGGINGFACE_API_KEY")
            or getattr(self.config.api_keys, "HUGGINGFACE_API_KEY", "")
        )

        try:
            # Load spaCy model for entity recognition
            self.nlp = spacy.load("en_core_web_sm")

            # Load sentiment analysis model
            if hf_token:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    token=hf_token    # استخدم use_auth_token=hf_token إذا ظهرت مشكلة
                )
                self.toxicity_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    token=hf_token
                )
            else:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                self.toxicity_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert"
                )
        except Exception as e:
            self.logger.warning(f"Failed to load NLP models: {e}")
            self.nlp = None
            self.sentiment_analyzer = None
            self.toxicity_classifier = None

    def _load_lists(self):
        """Load whitelist and blacklist"""
        # Load from config or database
        whitelist_words = getattr(self.config, 'MODERATION_WHITELIST', [])
        blacklist_words = getattr(self.config, 'MODERATION_BLACKLIST', [])

        self.whitelist = set(whitelist_words)
        self.blacklist = set(blacklist_words)

        # Add common safe words for children
        self.whitelist.update([
            "play", "fun", "friend", "help", "please", "thank you",
            "love", "family", "school", "learn", "game", "story"
        ])

        # Add definitely inappropriate words
        self.blacklist.update([
            # Add explicit inappropriate words here
        ])

    async def check_content(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        age: int = 10,
        language: str = 'en',
        context: Optional[List[Message]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive content moderation check

        Returns dict with:
        - allowed: bool
        - reason: str (if not allowed)
        - severity: ModerationSeverity
        - categories: List[ContentCategory]
        - alternative_response: Optional[str]
        """

        # Check cache first
        cache_key = self._generate_cache_key(content, age, language)
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_result

        # Run all moderation checks in parallel
        results = await asyncio.gather(
            self._check_whitelist_blacklist(content),
            self._check_with_rule_engine(content, age, language),
            self._check_with_openai(content),
            self._check_with_azure(
                content) if self.azure_client else self._null_check(),
            self._check_with_google(
                content) if self.google_client else self._null_check(),
            self._check_with_nlp_models(content),
            self._check_context_appropriate(
                content, context) if context else self._null_check(),
            return_exceptions=True
        )

        # Aggregate results
        final_result = self._aggregate_results(results)
        # تجاهل تصنيف المعلومات الشخصية فقط (اجعلها غير مؤثرة على الحظر)
        if ContentCategory.PERSONAL_INFO in final_result.flagged_categories:
            final_result.flagged_categories = [cat for cat in final_result.flagged_categories if cat != ContentCategory.PERSONAL_INFO]
            # إذا لم يبق تصنيفات خطيرة، اجعل النتيجة آمنة
            if not final_result.flagged_categories:
                final_result.is_safe = True
                final_result.severity = ModerationSeverity.SAFE

        # Determine if content is allowed
        allowed = final_result.is_safe and final_result.severity in [
            ModerationSeverity.SAFE,
            ModerationSeverity.LOW
        ]

        # Generate alternative response if needed
        if not allowed and getattr(self.config, 'GENERATE_SAFE_ALTERNATIVES', True):
            final_result.alternative_response = await self._generate_safe_alternative(
                content, final_result.flagged_categories
            )

        # Log the moderation event
        await self._log_moderation(
            content=content,
            result=final_result,
            user_id=user_id,
            session_id=session_id
        )

        # Check if parent alert is needed
        if await self._should_alert_parent(final_result, user_id):
            final_result.should_alert_parent = True
            await self._send_parent_alert(user_id, content, final_result)

        # Prepare response
        response = {
            'allowed': allowed,
            'severity': final_result.severity.value,
            'categories': [cat.value for cat in final_result.flagged_categories],
            'confidence': final_result.overall_score,
            'reason': self._generate_reason(final_result) if not allowed else None,
            'alternative_response': final_result.alternative_response
        }

        # Cache the result
        self.cache[cache_key] = (response, datetime.now())

        return response

    async def _check_whitelist_blacklist(self, content: str) -> ModerationResult:
        """Check content against whitelist and blacklist"""
        content_lower = content.lower()
        words = set(content_lower.split())

        # Check blacklist
        blacklisted = words & self.blacklist
        if blacklisted:
            return ModerationResult(
                is_safe=False,
                severity=ModerationSeverity.HIGH,
                flagged_categories=[ContentCategory.PROFANITY],
                confidence_scores={ContentCategory.PROFANITY: 1.0},
                matched_rules=[f"Blacklisted: {', '.join(blacklisted)}"]
            )

        # Check if all words are whitelisted
        non_whitelisted = words - self.whitelist
        if not non_whitelisted:
            return ModerationResult(
                is_safe=True,
                severity=ModerationSeverity.SAFE,
                confidence_scores={}
            )

        return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _check_with_rule_engine(self, content: str, age: int, language: str) -> ModerationResult:
        """Check content with custom rule engine"""
        matched_rules = await self.rule_engine.evaluate(content, age, language)

        if not matched_rules:
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        # Find highest severity
        max_severity = ModerationSeverity.SAFE
        categories = []
        confidence_scores = {}
        rule_names = []

        for rule, confidence in matched_rules:
            if rule.severity.value > max_severity.value:
                max_severity = rule.severity
            categories.append(rule.category)
            confidence_scores[rule.category] = max(
                confidence_scores.get(rule.category, 0),
                confidence
            )
            rule_names.append(rule.name)

        return ModerationResult(
            is_safe=max_severity in [
                ModerationSeverity.SAFE, ModerationSeverity.LOW],
            severity=max_severity,
            flagged_categories=list(set(categories)),
            confidence_scores=confidence_scores,
            matched_rules=rule_names
        )

    async def _check_with_openai(self, content: str) -> ModerationResult:
        """Use OpenAI's moderation API"""
        try:
            if not hasattr(self, "_openai_client"):
                self._openai_client = AsyncOpenAI(
                    api_key=getattr(self.config.api_keys, "OPENAI_API_KEY", ""))
            response = await self._openai_client.moderations.create(
                model="omni-moderation-latest",
                input=content
            )
            result = response.results[0]
            # نفس المعالجة كما عندك مع النتيجة
            category_mapping = {
                'sexual': ContentCategory.SEXUAL,
                'hate': ContentCategory.HATE_SPEECH,
                'violence': ContentCategory.VIOLENCE,
                'self-harm': ContentCategory.SELF_HARM,
                'sexual/minors': ContentCategory.SEXUAL,
                'hate/threatening': ContentCategory.HATE_SPEECH,
                'violence/graphic': ContentCategory.VIOLENCE
            }
            flagged_categories = []
            confidence_scores = {}

            for category in category_mapping:
                flagged = getattr(result.categories, category, False)
                if flagged:
                    mapped_category = category_mapping[category]
                    flagged_categories.append(mapped_category)
                    confidence_scores[mapped_category] = getattr(
                        result.category_scores, category, 0)

            # Determine severity
            if not result.flagged:
                severity = ModerationSeverity.SAFE
            else:
                max_score = max(
                    dict(result.category_scores).values(), default=0)
                if max_score > 0.8:
                    severity = ModerationSeverity.HIGH
                elif max_score > 0.5:
                    severity = ModerationSeverity.MEDIUM
                else:
                    severity = ModerationSeverity.LOW

            return ModerationResult(
                is_safe=not result.flagged,
                severity=severity,
                flagged_categories=flagged_categories,
                confidence_scores=confidence_scores,
                context_notes=["OpenAI Moderation API"]
            )
        except Exception as e:
            self.logger.error(f"OpenAI moderation error: {e}")
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _check_with_azure(self, content: str) -> ModerationResult:
        """Use Azure Content Safety API"""
        if not self.azure_client:
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        try:
            from azure.ai.contentsafety.models import AnalyzeTextOptions

            request = AnalyzeTextOptions(text=content)
            response = self.azure_client.analyze_text(request)

            # Process Azure results
            categories = []
            confidence_scores = {}
            max_severity = 0

            if response.hate_result.severity > 0:
                categories.append(ContentCategory.HATE_SPEECH)
                confidence_scores[ContentCategory.HATE_SPEECH] = response.hate_result.severity / 6
                max_severity = max(max_severity, response.hate_result.severity)

            if response.self_harm_result.severity > 0:
                categories.append(ContentCategory.SELF_HARM)
                confidence_scores[ContentCategory.SELF_HARM] = response.self_harm_result.severity / 6
                max_severity = max(
                    max_severity, response.self_harm_result.severity)

            if response.sexual_result.severity > 0:
                categories.append(ContentCategory.SEXUAL)
                confidence_scores[ContentCategory.SEXUAL] = response.sexual_result.severity / 6
                max_severity = max(
                    max_severity, response.sexual_result.severity)

            if response.violence_result.severity > 0:
                categories.append(ContentCategory.VIOLENCE)
                confidence_scores[ContentCategory.VIOLENCE] = response.violence_result.severity / 6
                max_severity = max(
                    max_severity, response.violence_result.severity)

            # Map severity
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
                context_notes=["Azure Content Safety API"]
            )

        except Exception as e:
            self.logger.error(f"Azure moderation error: {e}")
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _check_with_google(self, content: str) -> ModerationResult:
        """Use Google Cloud Natural Language API"""
        if not self.google_client:
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        try:
            document = language_v1.Document(
                content=content,
                type_=language_v1.Document.Type.PLAIN_TEXT,
            )

            # Analyze sentiment
            sentiment_response = self.google_client.analyze_sentiment(
                request={'document': document}
            )

            # Analyze entities for personal information
            entities_response = self.google_client.analyze_entities(
                request={'document': document}
            )

            categories = []
            confidence_scores = {}

            # Check sentiment
            sentiment_score = sentiment_response.document_sentiment.score
            if sentiment_score < -0.5:
                categories.append(ContentCategory.BULLYING)
                confidence_scores[ContentCategory.BULLYING] = abs(
                    sentiment_score)

            # Check for personal information
            for entity in entities_response.entities:
                if entity.type_ in [
                    language_v1.Entity.Type.PERSON,
                    language_v1.Entity.Type.PHONE_NUMBER,
                    language_v1.Entity.Type.ADDRESS
                ]:
                    categories.append(ContentCategory.PERSONAL_INFO)
                    confidence_scores[ContentCategory.PERSONAL_INFO] = 0.8
                    break

            severity = ModerationSeverity.SAFE
            if categories:
                severity = ModerationSeverity.MEDIUM

            return ModerationResult(
                is_safe=len(categories) == 0,
                severity=severity,
                flagged_categories=categories,
                confidence_scores=confidence_scores,
                context_notes=["Google Cloud NLP"]
            )

        except Exception as e:
            self.logger.error(f"Google moderation error: {e}")
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _check_with_nlp_models(self, content: str) -> ModerationResult:
        """Use local NLP models for analysis"""
        if not self.nlp or not self.sentiment_analyzer:
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        try:
            categories = []
            confidence_scores = {}

            # Sentiment analysis
            sentiment = self.sentiment_analyzer(content)[0]
            if sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.8:
                categories.append(ContentCategory.BULLYING)
                confidence_scores[ContentCategory.BULLYING] = sentiment['score']

            # Entity recognition for personal info
            doc = self.nlp(content)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'GPE', 'LOC', 'PHONE', 'EMAIL']:
                    categories.append(ContentCategory.PERSONAL_INFO)
                    confidence_scores[ContentCategory.PERSONAL_INFO] = 0.7
                    break

            # Toxicity analysis
            if self.toxicity_classifier:
                toxicity = self.toxicity_classifier(content)[0]
                if toxicity['label'] == 'TOXIC' and toxicity['score'] > 0.7:
                    categories.append(ContentCategory.HATE_SPEECH)
                    confidence_scores[ContentCategory.HATE_SPEECH] = toxicity['score']

            severity = ModerationSeverity.SAFE
            if categories:
                max_score = max(confidence_scores.values())
                if max_score > 0.8:
                    severity = ModerationSeverity.MEDIUM
                else:
                    severity = ModerationSeverity.LOW

            return ModerationResult(
                is_safe=len(categories) == 0,
                severity=severity,
                flagged_categories=categories,
                confidence_scores=confidence_scores,
                context_notes=["Local NLP Models"]
            )

        except Exception as e:
            self.logger.error(f"NLP moderation error: {e}")
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _check_context_appropriate(self, content: str, context: List[Message]) -> ModerationResult:
        """Check if content is appropriate given the conversation context"""
        # Analyze conversation flow and detect inappropriate shifts
        try:
            # Simple context analysis
            recent_topics = []
            for msg in context[-5:]:  # Last 5 messages
                if msg.role == 'user':
                    # Extract main topics/keywords
                    if self.nlp:
                        doc = self.nlp(msg.content)
                        topics = [
                            token.text for token in doc if token.pos_ in ['NOUN', 'VERB']]
                        recent_topics.extend(topics)

            # Check for sudden topic shifts to inappropriate areas
            concerning_shifts = [
                'violence', 'weapon', 'hurt', 'scary', 'adult', 'private'
            ]

            content_lower = content.lower()
            shift_detected = any(
                word in content_lower and word not in ' '.join(
                    recent_topics).lower()
                for word in concerning_shifts
            )

            if shift_detected:
                return ModerationResult(
                    is_safe=False,
                    severity=ModerationSeverity.MEDIUM,
                    flagged_categories=[ContentCategory.AGE_INAPPROPRIATE],
                    confidence_scores={ContentCategory.AGE_INAPPROPRIATE: 0.6},
                    context_notes=["Inappropriate context shift detected"]
                )

            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        except Exception as e:
            self.logger.error(f"Context analysis error: {e}")
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    async def _null_check(self) -> ModerationResult:
        """Null check for disabled services"""
        return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

    def _aggregate_results(self, results: List[Any]) -> ModerationResult:
        """Aggregate multiple moderation results"""
        valid_results = [r for r in results if isinstance(r, ModerationResult)]

        if not valid_results:
            return ModerationResult(is_safe=True, severity=ModerationSeverity.SAFE)

        # Aggregate all findings
        all_categories = []
        all_confidence_scores = {}
        all_matched_rules = []
        all_context_notes = []
        max_severity = ModerationSeverity.SAFE
        is_safe = True

        for result in valid_results:
            if not result.is_safe:
                is_safe = False

            if result.severity.value > max_severity.value:
                max_severity = result.severity

            all_categories.extend(result.flagged_categories)

            for category, score in result.confidence_scores.items():
                if category not in all_confidence_scores:
                    all_confidence_scores[category] = score
                else:
                    all_confidence_scores[category] = max(
                        all_confidence_scores[category], score)

            all_matched_rules.extend(result.matched_rules)
            all_context_notes.extend(result.context_notes)

        return ModerationResult(
            is_safe=is_safe,
            severity=max_severity,
            flagged_categories=list(set(all_categories)),
            confidence_scores=all_confidence_scores,
            matched_rules=list(set(all_matched_rules)),
            context_notes=list(set(all_context_notes))
        )

    async def _generate_safe_alternative(self, original: str, categories: List[ContentCategory]) -> str:
        """Generate a safe alternative response"""
        try:
            if ContentCategory.VIOLENCE in categories:
                return "دعنا نتحدث عن شيء لطيف ومرح بدلاً من ذلك!"
            elif ContentCategory.PERSONAL_INFO in categories:
                return "من المهم أن نحافظ على معلوماتنا الشخصية آمنة. لا تشارك معلومات خاصة مع أي شخص."
            elif ContentCategory.BULLYING in categories:
                return "لنكن لطفاء مع بعضنا البعض. الكلمات اللطيفة تجعل الجميع سعداء!"
            elif ContentCategory.SCARY_CONTENT in categories:
                return "هل تريد أن نتحدث عن شيء مرح وسعيد بدلاً من ذلك؟"
            else:
                return "دعنا نغير الموضوع إلى شيء أكثر إيجابية!"

        except Exception as e:
            self.logger.error(f"Error generating safe alternative: {e}")
            return "دعنا نتحدث عن شيء آخر!"

    def _generate_reason(self, result: ModerationResult) -> str:
        """Generate human-readable reason for moderation action"""
        if ContentCategory.VIOLENCE in result.flagged_categories:
            return "المحتوى يحتوي على عنف غير مناسب للأطفال"
        elif ContentCategory.PERSONAL_INFO in result.flagged_categories:
            return "المحتوى يحتوي على معلومات شخصية حساسة"
        elif ContentCategory.BULLYING in result.flagged_categories:
            return "المحتوى قد يكون مؤذياً أو يحتوي على تنمر"
        elif ContentCategory.AGE_INAPPROPRIATE in result.flagged_categories:
            return "المحتوى غير مناسب لهذه الفئة العمرية"
        elif result.severity == ModerationSeverity.HIGH:
            return "المحتوى غير مناسب للأطفال"
        else:
            return "المحتوى قد يحتوي على مواد غير مناسبة"

    async def _log_moderation(
        self,
        content: str,
        result: ModerationResult,
        user_id: Optional[str],
        session_id: Optional[str]
    ):
        """Log moderation event"""
        try:
            # تشفير المحتوى الحساس
            encryption_service = EncryptionService(self.config.MASTER_KEY)
            encrypted_content, nonce = encryption_service.encrypt(content[:500])
            
            log_entry = ModerationLog(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                result={
                    'is_safe': result.is_safe,
                    'severity': result.severity.value,
                    'overall_score': result.overall_score,
                    # Limit stored rules
                    'matched_rules': result.matched_rules[:5]
                },
                severity=result.severity.value,
                categories=[cat.value for cat in result.flagged_categories],
                action_taken='blocked' if not result.is_safe else 'allowed'
            )
            log_entry.content = encrypted_content
            log_entry.content_nonce = nonce

            # Save to database (async)
            # await self.db_session.add(log_entry)
            # await self.db_session.commit()

            # Also log to file/monitoring system
            self.logger.info(
                f"Moderation log: user={user_id}, severity={result.severity.value}, "
                f"safe={result.is_safe}, categories={[c.value for c in result.flagged_categories]}"
            )

        except Exception as e:
            self.logger.error(f"Failed to log moderation: {e}")

    async def _should_alert_parent(self, result: ModerationResult, user_id: Optional[str]) -> bool:
        """Determine if parent should be alerted"""
        if not user_id:
            return False

        # Always alert for critical severity
        if result.severity == ModerationSeverity.CRITICAL:
            return True

        # Check threshold tracking
        self.severity_tracker[user_id].append({
            'severity': result.severity,
            'timestamp': datetime.now()
        })

        # Clean old entries (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.severity_tracker[user_id] = [
            entry for entry in self.severity_tracker[user_id]
            if entry['timestamp'] > cutoff_time
        ]

        # Count severities in last hour
        severity_counts = defaultdict(int)
        for entry in self.severity_tracker[user_id]:
            severity_counts[entry['severity']] += 1

        # Check against thresholds
        for severity, threshold in self.alert_thresholds.items():
            if severity_counts[severity] >= threshold:
                return True

        return False

    async def _send_parent_alert(self, user_id: str, content: str, result: ModerationResult):
        """Send alert to parent dashboard"""
        try:
            if self.parent_dashboard:
                await self.parent_dashboard.send_moderation_alert(
                    user_id=user_id,
                    alert_type='content_moderation',
                    severity=result.severity.value,
                    details={
                        'content_snippet': content[:100] + '...' if len(content) > 100 else content,
                        'categories': [cat.value for cat in result.flagged_categories],
                        'confidence': result.overall_score,
                        'timestamp': result.timestamp.isoformat()
                    }
                )

        except Exception as e:
            self.logger.error(f"Failed to send parent alert: {e}")

    def _generate_cache_key(self, content: str, age: int, language: str) -> str:
        """Generate cache key for moderation result"""
        key_data = f"{content}:{age}:{language}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def add_custom_rule(self, rule: ModerationRule) -> bool:
        """Add a custom moderation rule"""
        try:
            self.rule_engine.add_rule(rule)
            self.logger.info(f"Added custom rule: {rule.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add rule: {e}")
            return False

    async def remove_custom_rule(self, rule_id: str) -> bool:
        """Remove a custom moderation rule"""
        try:
            self.rule_engine.remove_rule(rule_id)
            self.logger.info(f"Removed rule: {rule_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove rule: {e}")
            return False

    async def update_whitelist(self, words: List[str], action: str = 'add') -> bool:
        """Update whitelist"""
        try:
            if action == 'add':
                self.whitelist.update(words)
            elif action == 'remove':
                self.whitelist -= set(words)
            else:
                raise ValueError(f"Invalid action: {action}")

            self.logger.info(f"Updated whitelist: {action} {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update whitelist: {e}")
            return False

    async def update_blacklist(self, words: List[str], action: str = 'add') -> bool:
        """Update blacklist"""
        try:
            if action == 'add':
                self.blacklist.update(words)
            elif action == 'remove':
                self.blacklist -= set(words)
            else:
                raise ValueError(f"Invalid action: {action}")

            self.logger.info(f"Updated blacklist: {action} {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update blacklist: {e}")
            return False

    async def get_moderation_stats(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get moderation statistics"""
        try:
            # Query from database
            # stats = await self.db_session.query(ModerationLog)...

            # For now, return sample stats
            stats = {
                'total_checks': 1000,
                'blocked_count': 50,
                'allowed_count': 950,
                'block_rate': 0.05,
                'severity_breakdown': {
                    'safe': 900,
                    'low': 30,
                    'medium': 15,
                    'high': 4,
                    'critical': 1
                },
                'category_breakdown': {
                    'violence': 10,
                    'personal_info': 20,
                    'bullying': 15,
                    'age_inappropriate': 5
                },
                'top_matched_rules': [
                    'Personal Information Detection',
                    'Violence Keywords',
                    'Bullying Detection'
                ]
            }

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {}

    async def export_moderation_logs(
        self,
        user_id: Optional[str] = None,
        format: str = 'json'
    ) -> str:
        """Export moderation logs"""
        try:
            # Query logs from database
            # logs = await self.db_session.query(ModerationLog)...

            # For now, return sample
            logs = []

            if format == 'json':
                return json.dumps(logs, indent=2, default=str)
            elif format == 'csv':
                # Convert to CSV
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(
                    output,
                    fieldnames=['timestamp', 'user_id',
                                'severity', 'categories', 'action']
                )
                writer.writeheader()
                for log in logs:
                    writer.writerow(log)
                return output.getvalue()
            else:
                raise ValueError(f"Invalid format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
            return ""

    def set_parent_dashboard(self, dashboard: ParentDashboardService):
        """Set parent dashboard service for alerts"""
        self.parent_dashboard = dashboard

    async def test_moderation(self, test_content: List[str]) -> List[Dict[str, Any]]:
        """Test moderation on sample content"""
        results = []

        for content in test_content:
            result = await self.check_content(content)
            results.append({
                'content': content,
                'result': result
            })

        return results

    async def moderate_content(self, text: str, user_context: dict = None) -> dict:
        """Moderate content using external API or rules, with input validation"""
        if not isinstance(text, str) or not text.strip():
            self.logger.error("Invalid text for moderation")
            return {"allowed": False, "reason": "Invalid input"}
        # Example: Use external moderation API or rules
        if self.external_moderation_api:
            result = await self.external_moderation_api.moderate(text)
            return result
        # Fallback: simple keyword check
        banned_keywords = ["violence", "personal info", "bully", "inappropriate"]
        for word in banned_keywords:
            if word in text.lower():
                return {"allowed": False, "reason": f"Contains banned word: {word}"}
        return {"allowed": True}


# Utility functions

def create_age_appropriate_rule(
    name: str,
    keywords: List[str],
    min_age: int,
    max_age: int = 18,
    severity: ModerationSeverity = ModerationSeverity.MEDIUM
) -> ModerationRule:
    """Create an age-appropriate content rule"""
    return ModerationRule(
        id=f"age_rule_{name.lower().replace(' ', '_')}",
        name=name,
        description=f"Age-appropriate rule for {min_age}-{max_age} years",
        keywords=keywords,
        category=ContentCategory.AGE_INAPPROPRIATE,
        severity=severity,
        age_range=(min_age, max_age),
        enabled=True
    )


def create_topic_filter_rule(
    topic: str,
    keywords: List[str],
    category: ContentCategory,
    severity: ModerationSeverity = ModerationSeverity.MEDIUM
) -> ModerationRule:
    """Create a topic-based filter rule"""
    return ModerationRule(
        id=f"topic_{topic.lower().replace(' ', '_')}",
        name=f"{topic} Filter",
        description=f"Filters content related to {topic}",
        keywords=keywords,
        category=category,
        severity=severity,
        enabled=True
    )
