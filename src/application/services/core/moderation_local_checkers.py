#!/usr/bin/env python3
"""
🏠 Moderation Local Checkers
الفحص المحلي للمحتوى بدون APIs خارجية

المسؤوليات:
- فحص whitelist/blacklist
- فحص Rule Engine المخصص
- فحص NLP models المحلية
- فحص context السياق
- فحص العمر المناسب
"""

import logging
import os
from typing import Set, List, Optional, Tuple
from collections import defaultdict

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    try:
        from src.infrastructure.external_services.mock.transformers import pipeline
        TRANSFORMERS_AVAILABLE = True
    except ImportError:
        pipeline = None
        TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

from .moderation import (
    ContentCategory, 
    ModerationResult, 
    ModerationSeverity, 
    RuleEngine
)
from .moderation_helpers import (
    ModerationRequest, 
    ModerationLookupTables, 
    ConditionalDecomposer
)
from src.core.domain.entities.conversation import Message


class ModerationLocalCheckers:
    """🏠 فاحص المحتوى المحلي"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.rule_engine = RuleEngine()
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        
        # NLP models
        self.nlp = None
        self.sentiment_analyzer = None
        self.toxicity_classifier = None
        
        # Initialize
        self._load_word_lists()
        self._init_nlp_models()
    
    def _load_word_lists(self) -> None:
        """📝 تحميل قوائم الكلمات"""
        whitelist_words = getattr(self.config, "MODERATION_WHITELIST", [])
        blacklist_words = getattr(self.config, "MODERATION_BLACKLIST", [])
        
        self.whitelist = set(whitelist_words)
        self.blacklist = set(blacklist_words)
        
        # إضافة كلمات آمنة
        self.whitelist.update([
            "play", "fun", "friend", "help", "please", "thank you",
            "love", "family", "school", "learn", "game", "story"
        ])
        
        self.logger.info(f"Loaded {len(self.whitelist)} safe words, {len(self.blacklist)} banned words")
    
    def _init_nlp_models(self) -> None:
        """🧠 تهيئة نماذج NLP المحلية"""
        if not SPACY_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            self.logger.warning("NLP libraries not available, using basic checks only")
            self.nlp = None
            self.sentiment_analyzer = None
            self.toxicity_classifier = None
            return
        
        try:
            # تحميل spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # تحميل Hugging Face models
            hf_token = (
                os.environ.get("HUGGINGFACE_TOKEN") or 
                os.environ.get("HUGGINGFACE_API_KEY") or
                getattr(self.config.api_keys, "HUGGINGFACE_API_KEY", "")
            )
            
            if hf_token:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    token=hf_token
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
            
            self.logger.info("NLP models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load NLP models: {e}")
            self.nlp = None
            self.sentiment_analyzer = None
            self.toxicity_classifier = None
    
    # ================== MAIN CHECKING METHODS ==================
    
    async def check_whitelist_blacklist(self, request: ModerationRequest) -> ModerationResult:
        """📝 فحص whitelist/blacklist"""
        content_lower = request.content.lower()
        words = set(content_lower.split())
        
        # فحص blacklist
        blacklisted_words = words & self.blacklist
        if blacklisted_words:
            return ModerationResult(
                is_safe=False,
                severity=ModerationSeverity.HIGH,
                flagged_categories=[ContentCategory.PROFANITY],
                confidence_scores={ContentCategory.PROFANITY: 1.0},
                matched_rules=[f"Blacklisted words found"],
                context_notes=["Local blacklist check"]
            )
        
        return ModerationResult(
            is_safe=True,
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            matched_rules=["Passed word list check"],
            context_notes=["Local check completed"]
        )
    
    async def check_with_rule_engine(self, request: ModerationRequest) -> ModerationResult:
        """⚙️ فحص باستخدام Rule Engine المخصص"""
        try:
            matched_rules = await self.rule_engine.evaluate(
                request.content, 
                request.age, 
                request.language
            )
            
            if not matched_rules:
                return ModerationResult(
                    is_safe=True, 
                    severity=ModerationSeverity.SAFE,
                    flagged_categories=[],
                    confidence_scores={},
                    matched_rules=["No rules matched"],
                    context_notes=["Rule engine check"]
                )
            
            # معالجة القواعد المطابقة
            max_severity = ModerationSeverity.SAFE
            categories = []
            confidence_scores = {}
            rule_names = []
            
            for rule, confidence in matched_rules:
                if rule.severity.value > max_severity.value:
                    max_severity = rule.severity
                categories.append(rule.category)
                confidence_scores[rule.category] = max(
                    confidence_scores.get(rule.category, 0), confidence
                )
                rule_names.append(rule.name)
            
            return ModerationResult(
                is_safe=max_severity in [ModerationSeverity.SAFE, ModerationSeverity.LOW],
                severity=max_severity,
                flagged_categories=list(set(categories)),
                confidence_scores=confidence_scores,
                matched_rules=rule_names[:5],  # حد أقصى 5 قواعد
                context_notes=["Custom rule engine check"]
            )
            
        except Exception as e:
            self.logger.error(f"Rule engine error: {e}")
            return self._create_safe_result("Rule engine error")
    
    async def check_with_nlp_models(self, request: ModerationRequest) -> ModerationResult:
        """🧠 فحص باستخدام NLP models المحلية"""
        if not self._are_nlp_models_available():
            return self._create_safe_result("NLP models not available")
        
        try:
            return await self._perform_nlp_analysis(request)
        except Exception as e:
            self.logger.error(f"NLP analysis error: {e}")
            return self._create_safe_result(f"NLP error: {str(e)}")
    
    async def _perform_nlp_analysis(self, request: ModerationRequest) -> ModerationResult:
        """🔍 تحليل NLP مفصل"""
        categories = []
        confidence_scores = {}
        
        # 1. تحليل المشاعر
        sentiment_category, sentiment_score = self._analyze_sentiment(request.content)
        if sentiment_category:
            categories.append(sentiment_category)
            confidence_scores[sentiment_category] = sentiment_score
        
        # 2. فحص المعلومات الشخصية
        personal_info_score = self._check_personal_info(request.content)
        if personal_info_score > 0:
            categories.append(ContentCategory.PERSONAL_INFO)
            confidence_scores[ContentCategory.PERSONAL_INFO] = personal_info_score
        
        # 3. فحص السمية
        toxicity_category, toxicity_score = self._check_toxicity(request.content)
        if toxicity_category:
            categories.append(toxicity_category)
            confidence_scores[toxicity_category] = toxicity_score
        
        # تحديد الخطورة النهائية
        max_score = max(confidence_scores.values()) if confidence_scores else 0.0
        severity = ModerationLookupTables.get_severity_by_score(max_score)
        
        return ModerationResult(
            is_safe=len(categories) == 0,
            severity=severity,
            flagged_categories=categories,
            confidence_scores=confidence_scores,
            matched_rules=["Local NLP analysis"],
            context_notes=["NLP models check"]
        )
    
    async def check_context_appropriate(self, request: ModerationRequest, context: List[Message]) -> ModerationResult:
        """🗨️ فحص مناسبة السياق"""
        if not context:
            return self._create_safe_result("No context provided")
        
        try:
            # تحليل الموضوعات الأخيرة
            recent_topics = self._extract_topics_from_context(context[-5:])
            
            # فحص التحولات المفاجئة للمواضيع الخطيرة
            concerning_shifts = [
                "violence", "weapon", "hurt", "scary", "adult", "private"
            ]
            
            content_lower = request.content.lower()
            shift_detected = any(
                word in content_lower and word not in " ".join(recent_topics).lower()
                for word in concerning_shifts
            )
            
            if shift_detected:
                return ModerationResult(
                    is_safe=False,
                    severity=ModerationSeverity.MEDIUM,
                    flagged_categories=[ContentCategory.AGE_INAPPROPRIATE],
                    confidence_scores={ContentCategory.AGE_INAPPROPRIATE: 0.6},
                    matched_rules=["Context shift detection"],
                    context_notes=["Inappropriate context shift detected"]
                )
            
            return self._create_safe_result("Context appropriate")
            
        except Exception as e:
            self.logger.error(f"Context analysis error: {e}")
            return self._create_safe_result("Context analysis error")
    
    async def check_age_specific_content(self, request: ModerationRequest) -> ModerationResult:
        """👶 فحص المحتوى حسب العمر"""
        content_lower = request.content.lower()
        flagged_categories = []
        confidence_scores = {}
        
        # فحص المحتوى المخيف للأطفال الصغار
        if ConditionalDecomposer.is_young_child(request.age):
            scary_words = ["monster", "ghost", "scary", "nightmare", "death", "dark"]
            if any(word in content_lower for word in scary_words):
                flagged_categories.append(ContentCategory.SCARY_CONTENT)
                confidence_scores[ContentCategory.SCARY_CONTENT] = 0.8
        
        # فحص المحتوى العنيف
        violence_words = ["kill", "hurt", "fight", "weapon", "blood", "war"]
        if any(word in content_lower for word in violence_words):
            flagged_categories.append(ContentCategory.VIOLENCE)
            confidence_scores[ContentCategory.VIOLENCE] = 0.9
        
        # فحص المحتوى غير المناسب للعمر
        if not ModerationLookupTables.is_age_appropriate(ContentCategory.VIOLENCE, request.age):
            if any(word in content_lower for word in violence_words):
                flagged_categories.append(ContentCategory.AGE_INAPPROPRIATE)
                confidence_scores[ContentCategory.AGE_INAPPROPRIATE] = 0.7
        
        max_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
        severity = ModerationLookupTables.get_severity_by_score(max_confidence)
        
        return ModerationResult(
            is_safe=len(flagged_categories) == 0,
            severity=severity,
            flagged_categories=flagged_categories,
            confidence_scores=confidence_scores,
            matched_rules=["Age-specific content check"],
            context_notes=["Local age-appropriate check"]
        )
    
    # ================== HELPER METHODS ==================
    
    def _are_nlp_models_available(self) -> bool:
        """🔍 هل النماذج متوفرة؟"""
        return self.nlp is not None and self.sentiment_analyzer is not None
    
    def _analyze_sentiment(self, content: str) -> Tuple[Optional[ContentCategory], float]:
        """😊 تحليل المشاعر"""
        if not self.sentiment_analyzer:
            return None, 0.0
        
        try:
            sentiment = self.sentiment_analyzer(content)[0]
            
            if (sentiment["label"] == "NEGATIVE" and 
                ConditionalDecomposer.is_score_above_threshold(sentiment["score"], 0.8)):
                return ContentCategory.BULLYING, sentiment["score"]
                
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
        
        return None, 0.0
    
    def _check_personal_info(self, content: str) -> float:
        """🔒 فحص المعلومات الشخصية"""
        if not self.nlp:
            return 0.0
        
        try:
            doc = self.nlp(content)
            risky_entity_types = {"PERSON", "GPE", "LOC", "PHONE", "EMAIL"}
            
            for ent in doc.ents:
                if ent.label_ in risky_entity_types:
                    return 0.7
                    
        except Exception as e:
            self.logger.error(f"Personal info check error: {e}")
        
        return 0.0
    
    def _check_toxicity(self, content: str) -> Tuple[Optional[ContentCategory], float]:
        """☣️ فحص السمية"""
        if not self.toxicity_classifier:
            return None, 0.0
        
        try:
            toxicity = self.toxicity_classifier(content)[0]
            
            if (toxicity["label"] == "TOXIC" and 
                ConditionalDecomposer.is_score_above_threshold(toxicity["score"], 0.7)):
                return ContentCategory.HATE_SPEECH, toxicity["score"]
                
        except Exception as e:
            self.logger.error(f"Toxicity check error: {e}")
        
        return None, 0.0
    
    def _extract_topics_from_context(self, messages: List[Message]) -> List[str]:
        """📝 استخراج الموضوعات من السياق"""
        topics = []
        
        if not self.nlp:
            return topics
        
        try:
            for msg in messages:
                if msg.role == "user":
                    doc = self.nlp(msg.content)
                    topics.extend([
                        token.text.lower() 
                        for token in doc 
                        if token.pos_ in ["NOUN", "VERB"] and len(token.text) > 2
                    ])
        except Exception as e:
            self.logger.error(f"Topic extraction error: {e}")
        
        return topics
    
    def _create_safe_result(self, note: str) -> ModerationResult:
        """✅ إنشاء نتيجة آمنة"""
        return ModerationResult(
            is_safe=True,
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            matched_rules=[],
            context_notes=[note]
        )
    
    # ================== MANAGEMENT METHODS ==================
    
    async def update_whitelist(self, words: List[str], action: str = "add") -> bool:
        """📝 تحديث whitelist"""
        try:
            if action == "add":
                self.whitelist.update(words)
            elif action == "remove":
                self.whitelist -= set(words)
            else:
                raise ValueError(f"Invalid action: {action}")
            
            self.logger.info(f"Updated whitelist: {action} {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update whitelist: {e}")
            return False
    
    async def update_blacklist(self, words: List[str], action: str = "add") -> bool:
        """📝 تحديث blacklist"""
        try:
            if action == "add":
                self.blacklist.update(words)
            elif action == "remove":
                self.blacklist -= set(words)
            else:
                raise ValueError(f"Invalid action: {action}")
            
            self.logger.info(f"Updated blacklist: {action} {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update blacklist: {e}")
            return False
    
    def get_status(self) -> dict:
        """📊 حالة الفاحص المحلي"""
        return {
            "whitelist_count": len(self.whitelist),
            "blacklist_count": len(self.blacklist),
            "nlp_available": self._are_nlp_models_available(),
            "rule_engine_ready": self.rule_engine is not None,
        }


# ================== FACTORY FUNCTION ==================

def create_local_checkers(config) -> ModerationLocalCheckers:
    """🏭 Factory function"""
    return ModerationLocalCheckers(config) 