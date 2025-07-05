import re
import statistics
from collections import defaultdict
from typing import Dict, List, Optional

from .models import (
    Conversation,
    EmotionalState,
    Message,
    MessageRole,
    ContentType,
)


class ConversationService:
    """
    Provides services for analyzing and processing Conversation objects.
    This includes metrics calculation, topic extraction, and quality scoring.
    """

    def update_metrics(self, conversation: Conversation, message: Message) -> None:
        """Update conversation metrics with a new message."""
        conversation.metrics.total_messages += 1
        self._update_turn_taking_metrics(conversation, message)
        self._update_word_and_question_metrics(conversation, message)
        if message.metadata.moderation_flags:
            conversation.metrics.moderation_flags += 1

    def _update_turn_taking_metrics(self, conversation: Conversation, message: Message) -> None:
        """Update turn-taking specific metrics."""
        if message.role == MessageRole.USER:
            conversation.turn_taking.user_turns += 1
            if len(conversation.messages) > 1:
                last_assistant_message = next(
                    (m for m in reversed(
                        conversation.messages[:-1]) if m.role == MessageRole.ASSISTANT), None
                )
                if last_assistant_message:
                    conversation.turn_taking.response_times.append(
                        (message.timestamp -
                         last_assistant_message.timestamp).total_seconds()
                    )
        elif message.role == MessageRole.ASSISTANT:
            conversation.turn_taking.assistant_turns += 1

    def _update_word_and_question_metrics(self, conversation: Conversation, message: Message) -> None:
        """Update word count and question related metrics."""
        word_count = message.get_word_count()
        if word_count > 0:
            conversation.metrics.total_words += word_count
            all_words = " ".join(
                m.content for m in conversation.messages).lower()
            conversation.metrics.unique_words = len(set(all_words.split()))

        # A simple regex for questions
        questions = re.findall(r"\b\w+\b\s*\?", message.content)
        if questions:
            conversation.metrics.questions_asked += len(questions)

    def extract_topics(self, conversation: Conversation) -> List[str]:
        """Extract topics from conversation using keyword matching."""
        full_text = " ".join(m.content.lower(
        ) for m in conversation.messages if m.content_type == ContentType.TEXT)
        if not full_text:
            return []
        topic_keywords = self._get_topic_keywords()
        detected_topics = defaultdict(int)
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if re.search(r"\b" + re.escape(keyword) + r"\b", full_text):
                    detected_topics[topic] += 1
        if not detected_topics:
            return ["general"]
        sorted_topics = sorted(detected_topics.items(),
                               key=lambda item: item[1], reverse=True)
        conversation.topics = [topic for topic, count in sorted_topics]
        return conversation.topics

    def _get_topic_keywords(self) -> Dict[str, List[str]]:
        """Returns a dictionary of topic keywords for extraction."""
        return {
            "science": ["science", "space", "planet", "star", "animal", "nature"],
            "art": ["art", "draw", "paint", "color", "music", "sing", "dance"],
            "feelings": ["happy", "sad", "angry", "scared", "love", "friend"],
            "learning": ["learn", "school", "book", "read", "number", "letter"],
        }

    def analyze_emotional_journey(self, conversation: Conversation) -> List[EmotionalState]:
        """Analyze emotional progression and identify key moments."""
        significant_moments = []
        for i, state in enumerate(conversation.emotional_states):
            if i > 0:
                prev_state = conversation.emotional_states[i - 1]
                shift = self._calculate_emotional_shift(prev_state, state)
                if self._is_significant_emotional_moment(state, shift):
                    significant_moments.append(state)
            elif self._is_significant_emotional_moment(state):
                significant_moments.append(state)
        return significant_moments

    def _calculate_emotional_shift(self, prev_state: EmotionalState, current_state: EmotionalState) -> float:
        return abs(current_state.valence - prev_state.valence) + abs(current_state.arousal - prev_state.arousal)

    def _is_significant_emotional_moment(self, state: EmotionalState, shift: Optional[float] = None) -> bool:
        if state.valence < -0.5 and state.arousal > 0.6:
            return True
        if shift and shift > 0.8:
            return True
        return False

    def calculate_engagement_score(self, conversation: Conversation) -> float:
        if not conversation.messages:
            return 0.0
        weights = {"interaction": 0.4, "turn_taking": 0.3, "questions": 0.3}
        interaction_score = self._calculate_interaction_score(conversation)
        turn_taking_score = self._calculate_turn_taking_score(conversation)
        question_score = self._calculate_question_score(conversation)
        final_score = (
            interaction_score * weights["interaction"]
            + turn_taking_score * weights["turn_taking"]
            + question_score * weights["questions"]
        )
        conversation.metrics.engagement_score = final_score
        return final_score

    def _calculate_interaction_score(self, conversation: Conversation) -> float:
        if conversation.duration.total_seconds() == 0:
            return 0.0
        messages_per_minute = len(
            conversation.messages) / (conversation.duration.total_seconds() / 60)
        return 1.0 if messages_per_minute > 5 else 0.7 if messages_per_minute > 2 else 0.4

    def _calculate_turn_taking_score(self, conversation: Conversation) -> float:
        total_turns = conversation.turn_taking.user_turns + \
            conversation.turn_taking.assistant_turns
        if total_turns == 0:
            return 0.0
        balance = 1.0 - abs(conversation.turn_taking.user_turns -
                            conversation.turn_taking.assistant_turns) / total_turns
        return balance

    def _calculate_question_score(self, conversation: Conversation) -> float:
        if conversation.turn_taking.user_turns == 0:
            return 0.0
        questions_per_turn = conversation.metrics.questions_asked / \
            conversation.turn_taking.user_turns
        return 1.0 if questions_per_turn > 0.5 else 0.7 if questions_per_turn > 0.2 else 0.3

    def calculate_quality_score(self, conversation: Conversation) -> float:
        """Calculate overall conversation quality score"""
        scores = [
            self.calculate_engagement_score(conversation),
            self.calculate_educational_score(conversation) * 0.8,
            conversation.safety_score
        ]
        if conversation.emotional_states:
            positive_emotions = sum(
                1 for state in conversation.emotional_states if state.valence > 0.2)
            scores.append(positive_emotions /
                          len(conversation.emotional_states))

        assistant_messages = [
            m for m in conversation.messages if m.role == MessageRole.ASSISTANT]
        if assistant_messages:
            good_responses = sum(
                1 for m in assistant_messages if m.get_word_count() > 10)
            scores.append(good_responses / len(assistant_messages))

        conversation.quality_score = statistics.mean(scores) if scores else 0.0
        return conversation.quality_score

    def calculate_educational_score(self, conversation: Conversation) -> float:
        if not conversation.messages:
            return 0.0
        weights = {"topics": 0.4, "content": 0.4, "inquiry": 0.2}
        topic_score = self._calculate_topic_diversity_score(conversation)
        content_score = self._calculate_content_quality_score(conversation)
        inquiry_score = self._calculate_inquiry_score(conversation)
        final_score = (topic_score * weights["topics"] + content_score *
                       weights["content"] + inquiry_score * weights["inquiry"])
        conversation.educational_score = final_score
        return final_score

    def _calculate_topic_diversity_score(self, conversation: Conversation) -> float:
        educational_topics = {"science", "learning", "art"}
        covered_topics = set(conversation.topics).intersection(
            educational_topics)
        count = len(covered_topics)
        if count >= 3:
            return 1.0
        if count > 0:
            return 0.6
        return 0.1

    def _calculate_content_quality_score(self, conversation: Conversation) -> float:
        educational_messages = sum(
            1 for m in conversation.messages if m.metadata.educational_content)
        if not conversation.messages:
            return 0.0
        return min(educational_messages / (len(conversation.messages) / 2), 1.0)

    def _calculate_inquiry_score(self, conversation: Conversation) -> float:
        if conversation.metrics.questions_asked == 0:
            return 0.2
        answered_ratio = conversation.turn_taking.assistant_turns / \
            conversation.metrics.questions_asked
        return min(answered_ratio, 1.0)
