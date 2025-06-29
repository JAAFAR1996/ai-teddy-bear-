"""
Advanced Context Analyzer for Conversation Safety
"""

from typing import List, Dict, Optional
from collections import deque
from .models import ContextAnalysisResult


class ContextAnalyzer:
    """Advanced context analysis for conversation safety"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversation_memory = deque(maxlen=max_history)
        
    async def analyze(self, current_text: str, 
                     conversation_history: List[str],
                     child_age: int = 6) -> ContextAnalysisResult:
        """Analyze conversation context for safety"""
        
        # Update conversation memory
        self.conversation_memory.append(current_text)
        
        # Perform safety analysis
        context_safe = await self._assess_context_safety(
            conversation_history, current_text, child_age
        )
        flow_score = self._analyze_conversation_flow(conversation_history)
        topic_appropriateness = self._assess_topic_appropriateness(
            conversation_history, child_age
        )
        behavioral_concerns = self._detect_behavioral_concerns(conversation_history)
        quality_score = self._evaluate_conversation_quality(conversation_history)
        
        return ContextAnalysisResult(
            context_safe=context_safe,
            conversation_flow_score=flow_score,
            topic_appropriateness=topic_appropriateness,
            behavioral_concerns=behavioral_concerns,
            conversation_quality=quality_score
        )
    
    async def _assess_context_safety(self, history: List[str], 
                                   current_text: str, child_age: int) -> bool:
        """Assess overall context safety"""
        safety_checks = [
            self._check_topic_progression(history, child_age),
            self._check_session_duration(history, child_age),
            self._check_content_escalation(history),
            self._check_interaction_patterns(history)
        ]
        
        return all(safety_checks)
    
    def _check_topic_progression(self, history: List[str], child_age: int) -> bool:
        """Check if topic progression is appropriate"""
        if len(history) < 2:
            return True
        
        # Check for inappropriate content escalation
        concerning_keywords = [
            "scary", "afraid", "hurt", "secret", "don't tell",
            "password", "address", "phone", "where you live"
        ]
        
        recent_content = history[-3:] if len(history) >= 3 else history
        concern_count = 0
        
        for text in recent_content:
            text_lower = text.lower()
            for keyword in concerning_keywords:
                if keyword in text_lower:
                    concern_count += 1
                    break
        
        return concern_count < 2
    
    def _check_session_duration(self, history: List[str], child_age: int) -> bool:
        """Check if session duration is appropriate"""
        # Estimate duration: ~30 seconds per interaction
        estimated_duration = len(history) * 0.5
        
        max_duration_by_age = {
            3: 10, 4: 15, 5: 20, 6: 25, 7: 30, 8: 35
        }
        
        max_duration = max_duration_by_age.get(child_age, 35)
        return estimated_duration <= max_duration
    
    def _check_content_escalation(self, history: List[str]) -> bool:
        """Check for concerning content escalation"""
        if len(history) < 3:
            return True
        
        recent_content = history[-3:]
        concerning_keywords = [
            "angry", "mad", "hate", "hurt", "bad", "scary", "afraid"
        ]
        
        escalation_scores = []
        for text in recent_content:
            score = sum(1 for keyword in concerning_keywords 
                       if keyword in text.lower())
            escalation_scores.append(score)
        
        # Check if concerning content is increasing
        return not (len(escalation_scores) >= 2 and 
                   escalation_scores[-1] > escalation_scores[0])
    
    def _check_interaction_patterns(self, history: List[str]) -> bool:
        """Check for concerning interaction patterns"""
        if len(history) < 2:
            return True
        
        # Check for repetitive concerning questions
        privacy_patterns = [
            "what.*name", "where.*live", "phone.*number", 
            "address", "secret", "don't.*tell"
        ]
        
        import re
        concern_count = 0
        for text in history[-5:]:  # Check last 5 interactions
            for pattern in privacy_patterns:
                if re.search(pattern, text.lower()):
                    concern_count += 1
                    break
        
        return concern_count < 2
    
    def _analyze_conversation_flow(self, history: List[str]) -> float:
        """Analyze the naturalness and flow of conversation"""
        if len(history) < 2:
            return 1.0
        
        # Check conversation coherence
        coherence_score = self._calculate_coherence(history)
        
        # Check response appropriateness
        response_score = self._assess_response_quality(history)
        
        # Check interaction rhythm
        rhythm_score = self._assess_rhythm(history)
        
        return (coherence_score + response_score + rhythm_score) / 3.0
    
    def _calculate_coherence(self, history: List[str]) -> float:
        """Calculate conversation coherence"""
        if len(history) < 2:
            return 1.0
        
        # Simple coherence check based on topic keywords
        topic_keywords = {
            "animals": ["dog", "cat", "bird", "animal"],
            "colors": ["red", "blue", "green", "color"],
            "numbers": ["one", "two", "count", "number"],
            "games": ["play", "game", "toy", "fun"]
        }
        
        recent_topics = []
        for text in history[-5:]:
            text_lower = text.lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    recent_topics.append(topic)
                    break
        
        if not recent_topics:
            return 0.8
        
        # Check topic consistency
        unique_topics = len(set(recent_topics))
        coherence = 1.0 - (unique_topics - 1) * 0.2
        return max(0.0, min(1.0, coherence))
    
    def _assess_response_quality(self, history: List[str]) -> float:
        """Assess quality of responses"""
        if len(history) < 2:
            return 1.0
        
        # Check for encouraging language
        positive_indicators = [
            "great", "good", "wonderful", "excellent", "amazing", "well done"
        ]
        
        # Check for questions (engagement)
        question_indicators = ["?", "what", "how", "why", "can you"]
        
        recent_responses = history[-3:] if len(history) >= 3 else history
        quality_scores = []
        
        for response in recent_responses:
            response_lower = response.lower()
            
            # Check positivity
            positive_score = 1.0 if any(word in response_lower 
                                      for word in positive_indicators) else 0.8
            
            # Check engagement
            engagement_score = 1.0 if any(indicator in response_lower 
                                        for indicator in question_indicators) else 0.9
            
            # Check length appropriateness
            word_count = len(response.split())
            length_score = 1.0 if 5 <= word_count <= 30 else 0.7
            
            response_quality = (positive_score + engagement_score + length_score) / 3.0
            quality_scores.append(response_quality)
        
        return sum(quality_scores) / len(quality_scores)
    
    def _assess_rhythm(self, history: List[str]) -> float:
        """Assess conversation rhythm"""
        interaction_count = len(history)
        
        # Ideal pace for children: not too fast, not too slow
        if interaction_count <= 2:
            return 1.0
        elif interaction_count <= 10:
            return 1.0
        elif interaction_count <= 20:
            return 0.8
        else:
            return 0.6
    
    def _assess_topic_appropriateness(self, history: List[str], 
                                    child_age: int) -> float:
        """Assess how appropriate topics are for child's age"""
        if not history:
            return 1.0
        
        age_appropriate_topics = self._get_age_appropriate_topics(child_age)
        
        appropriate_count = 0
        total_interactions = len(history)
        
        for text in history:
            text_lower = text.lower()
            if any(topic in text_lower for topic in age_appropriate_topics):
                appropriate_count += 1
        
        return appropriate_count / total_interactions if total_interactions > 0 else 1.0
    
    def _get_age_appropriate_topics(self, child_age: int) -> List[str]:
        """Get list of age-appropriate topics"""
        base_topics = ["animals", "colors", "shapes", "numbers", "toys"]
        
        if child_age >= 4:
            base_topics.extend(["stories", "family", "friends"])
        
        if child_age >= 6:
            base_topics.extend(["school", "books", "games"])
        
        if child_age >= 8:
            base_topics.extend(["science", "nature", "art"])
        
        return base_topics
    
    def _detect_behavioral_concerns(self, history: List[str]) -> List[str]:
        """Detect behavioral concerns in conversation"""
        concerns = []
        
        if len(history) < 2:
            return concerns
        
        # Check for repetitive concerning themes
        concerning_themes = {
            "loneliness": ["alone", "lonely", "no friends"],
            "sadness": ["sad", "cry", "upset"],
            "fear": ["scared", "afraid", "nightmare"],
            "anger": ["angry", "mad", "hate"]
        }
        
        recent_history = history[-5:]
        
        for theme, keywords in concerning_themes.items():
            theme_count = 0
            for text in recent_history:
                if any(keyword in text.lower() for keyword in keywords):
                    theme_count += 1
            
            if theme_count >= 2:
                concerns.append(f"repetitive_{theme}")
        
        # Check for privacy concerns
        privacy_keywords = ["address", "phone", "password", "secret"]
        for text in recent_history:
            if any(keyword in text.lower() for keyword in privacy_keywords):
                concerns.append("privacy_risk")
                break
        
        return concerns
    
    def _evaluate_conversation_quality(self, history: List[str]) -> float:
        """Evaluate overall conversation quality"""
        if not history:
            return 1.0
        
        # Check engagement level
        engagement_score = self._calculate_engagement(history)
        
        # Check educational value
        educational_score = self._calculate_educational_content(history)
        
        # Check emotional warmth
        warmth_score = self._calculate_emotional_warmth(history)
        
        return (engagement_score + educational_score + warmth_score) / 3.0
    
    def _calculate_engagement(self, history: List[str]) -> float:
        """Calculate engagement level"""
        # Check for questions and interactive elements
        interactive_indicators = ["?", "what", "how", "can you", "let's", "try"]
        
        interactive_count = 0
        for text in history:
            if any(indicator in text.lower() for indicator in interactive_indicators):
                interactive_count += 1
        
        return min(1.0, interactive_count / len(history))
    
    def _calculate_educational_content(self, history: List[str]) -> float:
        """Calculate educational content level"""
        educational_keywords = [
            "learn", "teach", "count", "color", "shape", "letter",
            "number", "read", "story", "animal", "science"
        ]
        
        educational_count = 0
        for text in history:
            if any(keyword in text.lower() for keyword in educational_keywords):
                educational_count += 1
        
        return min(1.0, educational_count / len(history))
    
    def _calculate_emotional_warmth(self, history: List[str]) -> float:
        """Calculate emotional warmth level"""
        warm_keywords = [
            "love", "care", "friend", "nice", "kind", "sweet",
            "happy", "wonderful", "great", "good job"
        ]
        
        warm_count = 0
        for text in history:
            if any(keyword in text.lower() for keyword in warm_keywords):
                warm_count += 1
        
        return min(1.0, warm_count / len(history)) 