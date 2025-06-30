"""
Advanced Keyword and Pattern Filter for Child Safety
"""

import re
import json
from typing import List, Dict, Set, Tuple
from pathlib import Path
from .models import FilterResult, RiskLevel

# Try to import ahocorasick, fall back to regex if not available
try:
    import ahocorasick
    HAS_AHOCORASICK = True
except ImportError:
    HAS_AHOCORASICK = False
    print("Warning: ahocorasick not available, using regex fallback")


class KeywordFilter:
    """Advanced keyword and pattern filtering for child safety"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/safety_keywords.json"
        self._load_patterns()
        if HAS_AHOCORASICK:
            self._build_automaton()
        else:
            self._build_regex_patterns()
        
    def _load_patterns(self) -> None:
        """Load keyword patterns from configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
        except FileNotFoundError:
            # Default patterns if config file doesn't exist
            self.patterns = self._get_default_patterns()
            self._save_default_config()
    
    def _get_default_patterns(self) -> Dict[str, Dict]:
        """Get default safety patterns"""
        return {
            "inappropriate_content": {
                "keywords": [
                    "violence", "violent", "kill", "death", "blood",
                    "scary", "nightmare", "fear", "afraid", "terror"
                ],
                "risk_level": "high",
                "age_restrictions": [0, 5]
            },
            "adult_themes": {
                "keywords": [
                    "adult", "mature", "romance", "dating", "love",
                    "relationship", "marriage", "kiss", "boyfriend", "girlfriend"
                ],
                "risk_level": "medium",
                "age_restrictions": [0, 8]
            },
            "negative_emotions": {
                "keywords": [
                    "hate", "stupid", "dumb", "ugly", "fat",
                    "loser", "failure", "worthless", "bad"
                ],
                "risk_level": "medium",
                "age_restrictions": [0, 12]
            },
            "privacy_risks": {
                "keywords": [
                    "address", "phone number", "password", "secret",
                    "don't tell", "our secret", "where do you live",
                    "what's your name", "personal information"
                ],
                "risk_level": "critical",
                "age_restrictions": [0, 18]
            },
            "educational_positive": {
                "keywords": [
                    "learn", "study", "read", "book", "school",
                    "smart", "clever", "good job", "well done",
                    "excellent", "wonderful", "amazing"
                ],
                "risk_level": "safe",
                "boost_score": 0.2
            }
        }
    
    def _save_default_config(self) -> None:
        """Save default configuration to file"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def _build_automaton(self) -> None:
        """Build Aho-Corasick automaton for efficient pattern matching"""
        if not HAS_AHOCORASICK:
            return
            
        self.automaton = ahocorasick.Automaton()
        
        for category, data in self.patterns.items():
            for keyword in data.get("keywords", []):
                self.automaton.add_word(keyword.lower(), (category, keyword))
        
        self.automaton.make_automaton()
    
    def _build_regex_patterns(self) -> None:
        """Build regex patterns as fallback when ahocorasick is not available"""
        self.regex_patterns = {}
        
        for category, data in self.patterns.items():
            keywords = data.get("keywords", [])
            if keywords:
                # Create regex pattern that matches any of the keywords
                escaped_keywords = [re.escape(keyword) for keyword in keywords]
                pattern = r'\b(?:' + '|'.join(escaped_keywords) + r')\b'
                self.regex_patterns[category] = {
                    'pattern': re.compile(pattern, re.IGNORECASE),
                    'keywords': keywords,
                    'data': data
                }
    
    def filter_content(self, text: str, child_age: int = 6) -> FilterResult:
        """Filter content using keyword patterns"""
        if HAS_AHOCORASICK:
            return self._filter_with_automaton(text, child_age)
        else:
            return self._filter_with_regex(text, child_age)
    
    def _filter_with_automaton(self, text: str, child_age: int) -> FilterResult:
        """Filter content using Aho-Corasick automaton"""
        text_lower = text.lower()
        matched_patterns = []
        risk_scores = []
        categories = set()
        suggestions = []
        
        # Find all matches using automaton
        for end_index, (category, keyword) in self.automaton.iter(text_lower):
            pattern_data = self.patterns[category]
            age_restrictions = pattern_data.get("age_restrictions", [0, 18])
            
            # Check age appropriateness
            if age_restrictions[0] <= child_age <= age_restrictions[1]:
                continue  # Age appropriate, skip
            
            matched_patterns.append(keyword)
            categories.add(category)
            
            # Calculate risk score
            risk_level = pattern_data.get("risk_level", "medium")
            risk_score = self._get_risk_score(risk_level)
            risk_scores.append(risk_score)
            
            # Generate suggestions
            suggestion = self._generate_suggestion(keyword, category)
            if suggestion:
                suggestions.append(suggestion)
        
        # Calculate overall risk
        overall_risk = max(risk_scores) if risk_scores else 0.0
        
        # Apply educational boost if applicable
        if "educational_positive" in categories:
            boost = self.patterns["educational_positive"].get("boost_score", 0)
            overall_risk = max(0.0, overall_risk - boost)
        
        return FilterResult(
            blocked=overall_risk > 0.3,
            matched_patterns=matched_patterns,
            risk_score=overall_risk,
            category=", ".join(categories) if categories else "safe",
            suggestions=suggestions
        )
    
    def _filter_with_regex(self, text: str, child_age: int) -> FilterResult:
        """Filter content using regex patterns (fallback method)"""
        matched_patterns = []
        risk_scores = []
        categories = set()
        suggestions = []
        
        for category, pattern_info in self.regex_patterns.items():
            pattern = pattern_info['pattern']
            pattern_data = pattern_info['data']
            keywords = pattern_info['keywords']
            
            # Find matches
            matches = pattern.findall(text)
            if matches:
                age_restrictions = pattern_data.get("age_restrictions", [0, 18])
                
                # Check age appropriateness
                if age_restrictions[0] <= child_age <= age_restrictions[1]:
                    continue  # Age appropriate, skip
                
                matched_patterns.extend(matches)
                categories.add(category)
                
                # Calculate risk score
                risk_level = pattern_data.get("risk_level", "medium")
                risk_score = self._get_risk_score(risk_level)
                risk_scores.append(risk_score)
                
                # Generate suggestions for each match
                for match in matches:
                    suggestion = self._generate_suggestion(match, category)
                    if suggestion:
                        suggestions.append(suggestion)
        
        # Calculate overall risk
        overall_risk = max(risk_scores) if risk_scores else 0.0
        
        # Apply educational boost if applicable
        if "educational_positive" in categories:
            boost = self.patterns["educational_positive"].get("boost_score", 0)
            overall_risk = max(0.0, overall_risk - boost)
        
        return FilterResult(
            blocked=overall_risk > 0.3,
            matched_patterns=matched_patterns,
            risk_score=overall_risk,
            category=", ".join(categories) if categories else "safe",
            suggestions=suggestions
        )
    
    def _get_risk_score(self, risk_level: str) -> float:
        """Convert risk level to numerical score"""
        risk_mapping = {
            "safe": 0.0,
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8,
            "critical": 1.0
        }
        return risk_mapping.get(risk_level, 0.5)
    
    def _generate_suggestion(self, keyword: str, category: str) -> str:
        """Generate content modification suggestion"""
        suggestions_map = {
            "inappropriate_content": f"Consider replacing '{keyword}' with more child-friendly language",
            "adult_themes": f"The topic '{keyword}' might be too advanced for younger children",
            "negative_emotions": f"Try using more positive language instead of '{keyword}'",
            "privacy_risks": f"Avoid asking about '{keyword}' to protect child privacy"
        }
        return suggestions_map.get(category, f"Review usage of '{keyword}'")
    
    def add_custom_pattern(self, category: str, keywords: List[str], 
                          risk_level: str = "medium", 
                          age_restrictions: List[int] = None) -> None:
        """Add custom filtering pattern"""
        if category not in self.patterns:
            self.patterns[category] = {
                "keywords": [],
                "risk_level": risk_level,
                "age_restrictions": age_restrictions or [0, 12]
            }
        
        self.patterns[category]["keywords"].extend(keywords)
        
        # Rebuild patterns
        if HAS_AHOCORASICK:
            self._build_automaton()
        else:
            self._build_regex_patterns()
            
        self._save_config()
    
    def _save_config(self) -> None:
        """Save current configuration"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def update_patterns_from_incidents(self, incidents: List[Dict]) -> None:
        """Update patterns based on safety incidents"""
        for incident in incidents:
            if incident.get("add_keywords"):
                category = incident.get("category", "custom_unsafe")
                keywords = incident.get("keywords", [])
                risk_level = incident.get("risk_level", "high")
                
                self.add_custom_pattern(category, keywords, risk_level)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get filtering statistics"""
        stats = {
            "total_categories": len(self.patterns),
            "total_keywords": sum(len(data["keywords"]) for data in self.patterns.values()),
            "using_ahocorasick": HAS_AHOCORASICK,
        }
        
        for category, data in self.patterns.items():
            stats[f"{category}_count"] = len(data["keywords"])
        
        return stats 