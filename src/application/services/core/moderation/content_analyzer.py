"""
🔍 Content Analyzer
Extracted content analysis functionality for better cohesion
"""

from enum import Enum
from typing import Dict, Any, List, Set
import logging


class ContentCategory(Enum):
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    PERSONAL_INFO = "personal_info"
    SCARY_CONTENT = "scary_content"
    AGE_INAPPROPRIATE = "age_inappropriate"
    HARMFUL_CONTENT = "harmful_content"
    CYBERBULLYING = "cyberbullying"


class ModerationSeverity(Enum):
    SAFE = "safe"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentAnalyzer:
    """
    Dedicated content analysis and filtering.
    High cohesion: all methods work with content analysis and safety rules.
    """
    
    def __init__(self):
        """Initialize content analyzer with rules and patterns"""
        self.logger = logging.getLogger(__name__)
        
        # Content filtering data
        self.whitelist = self._load_default_whitelist()
        self.blacklist = self._load_default_blacklist()
        self.age_rules = self._initialize_age_rules()
        
        # Analysis patterns
        self.personal_info_patterns = [
            "password", "secret", "address", "phone number", "email",
            "credit card", "social security", "bank account",
            "my address is", "i live at", "my phone", "call me at"
        ]
        
        self.harmful_patterns = {
            "violence": ["hit", "punch", "fight", "hurt", "pain", "blood"],
            "bullying": ["stupid", "ugly", "hate you", "shut up", "loser"],
            "inappropriate": ["adult only", "not for kids", "mature content"]
        }
    
    def analyze_content(self, content: str, age: int = 10, language: str = "en") -> Dict[str, Any]:
        """
        Comprehensive content analysis.
        Returns analysis result with safety determination.
        """
        content_lower = content.lower().strip()
        words = set(content_lower.split())
        
        # 1. Check basic content validity
        validity_result = self._check_content_validity(content)
        if not validity_result["valid"]:
            return validity_result
        
        # 2. Check blacklist (highest priority)
        blacklist_result = self._check_blacklist(words)
        if not blacklist_result["safe"]:
            return blacklist_result
        
        # 3. Check for personal information
        personal_info_result = self._check_personal_info(content_lower)
        if not personal_info_result["safe"]:
            return personal_info_result
        
        # 4. Age-appropriate content check
        age_result = self._check_age_appropriateness(content_lower, age)
        if not age_result["safe"]:
            return age_result
        
        # 5. Check for harmful patterns
        harmful_result = self._check_harmful_patterns(content_lower)
        if not harmful_result["safe"]:
            return harmful_result
        
        # 6. Content appears safe
        return self._create_safe_result("Content approved after analysis")
    
    def _check_content_validity(self, content: str) -> Dict[str, Any]:
        """Check basic content validity"""
        if not content or len(content.strip()) == 0:
            return self._create_safe_result("Empty content", valid=True)
        
        if len(content) > 10000:  # Too long
            return self._create_unsafe_result(
                "Content too long",
                [ContentCategory.AGE_INAPPROPRIATE],
                ModerationSeverity.MEDIUM,
                valid=True
            )
        
        return {"valid": True, "safe": True}
    
    def _check_blacklist(self, words: Set[str]) -> Dict[str, Any]:
        """Check content against blacklist"""
        flagged_words = words & self.blacklist
        if flagged_words:
            return self._create_unsafe_result(
                f"Contains inappropriate content: {', '.join(flagged_words)}",
                [ContentCategory.PROFANITY],
                ModerationSeverity.HIGH,
                confidence=0.9
            )
        return {"safe": True}
    
    def _check_personal_info(self, content: str) -> Dict[str, Any]:
        """Check for personal information patterns"""
        if any(pattern in content for pattern in self.personal_info_patterns):
            return self._create_unsafe_result(
                "Contains personal information",
                [ContentCategory.PERSONAL_INFO],
                ModerationSeverity.HIGH,
                confidence=0.85
            )
        return {"safe": True}
    
    def _check_age_appropriateness(self, content: str, age: int) -> Dict[str, Any]:
        """Check if content is appropriate for age"""
        for rule_name, rule_data in self.age_rules.items():
            if age <= rule_data["max_age"]:
                # Check scary words for this age group
                scary_words = rule_data.get("scary_words", [])
                if any(word in content for word in scary_words):
                    return self._create_unsafe_result(
                        f"Content may be too scary for age {age}",
                        [ContentCategory.SCARY_CONTENT],
                        ModerationSeverity.MEDIUM,
                        confidence=0.8
                    )
                
                # Check complex topics
                complex_topics = rule_data.get("complex_topics", [])
                if any(topic in content for topic in complex_topics):
                    return self._create_unsafe_result(
                        f"Content too complex for age {age}",
                        [ContentCategory.AGE_INAPPROPRIATE],
                        ModerationSeverity.MEDIUM,
                        confidence=0.8
                    )
        
        return {"safe": True}
    
    def _check_harmful_patterns(self, content: str) -> Dict[str, Any]:
        """Check for harmful content patterns"""
        for category, patterns in self.harmful_patterns.items():
            if any(pattern in content for pattern in patterns):
                return self._create_unsafe_result(
                    f"Contains {category} content",
                    [ContentCategory.HARMFUL_CONTENT],
                    ModerationSeverity.MEDIUM,
                    confidence=0.75
                )
        
        return {"safe": True}
    
    def _create_safe_result(self, reason: str, confidence: float = 0.9, valid: bool = True) -> Dict[str, Any]:
        """Create a safe analysis result"""
        return {
            "valid": valid,
            "safe": True,
            "allowed": True,
            "severity": ModerationSeverity.SAFE.value,
            "categories": [],
            "confidence": confidence,
            "reason": reason,
            "flagged_words": [],
            "analysis_details": {
                "blacklist_check": "passed",
                "personal_info_check": "passed",
                "age_appropriate_check": "passed",
                "harmful_patterns_check": "passed"
            }
        }
    
    def _create_unsafe_result(
        self, 
        reason: str, 
        categories: List[ContentCategory],
        severity: ModerationSeverity,
        confidence: float = 0.8,
        valid: bool = True
    ) -> Dict[str, Any]:
        """Create an unsafe analysis result"""
        return {
            "valid": valid,
            "safe": False,
            "allowed": False,
            "severity": severity.value,
            "categories": [cat.value for cat in categories],
            "confidence": confidence,
            "reason": reason,
            "flagged_words": [],
            "analysis_details": {
                "triggered_rule": reason,
                "risk_level": severity.value
            }
        }
    
    def _load_default_whitelist(self) -> Set[str]:
        """Load safe words whitelist"""
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
    
    def _load_default_blacklist(self) -> Set[str]:
        """Load inappropriate words blacklist"""
        # Keep empty by default for safety - can be configured later
        return set()
    
    def _initialize_age_rules(self) -> Dict[str, Dict]:
        """Initialize age-specific content rules"""
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
    
    def update_whitelist(self, words: List[str], action: str = "add") -> bool:
        """Update the whitelist with new words"""
        try:
            if action == "add":
                self.whitelist.update(word.lower() for word in words)
            elif action == "remove":
                for word in words:
                    self.whitelist.discard(word.lower())
            else:
                return False
            
            self.logger.info(f"Whitelist updated: {action}ed {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update whitelist: {e}")
            return False
    
    def update_blacklist(self, words: List[str], action: str = "add") -> bool:
        """Update the blacklist with new words"""
        try:
            if action == "add":
                self.blacklist.update(word.lower() for word in words)
            elif action == "remove":
                for word in words:
                    self.blacklist.discard(word.lower())
            else:
                return False
            
            self.logger.info(f"Blacklist updated: {action}ed {len(words)} words")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update blacklist: {e}")
            return False
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get content analysis statistics"""
        return {
            "whitelist_size": len(self.whitelist),
            "blacklist_size": len(self.blacklist),
            "age_rules_count": len(self.age_rules),
            "personal_info_patterns": len(self.personal_info_patterns),
            "harmful_patterns": {k: len(v) for k, v in self.harmful_patterns.items()}
        } 