import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.domain.entities.conversation import Conversation, Message


class LLMResponseProcessingService:
    """
    Dedicated service for LLM response processing operations.
    EXTRACTED CLASS to resolve Low Cohesion - Single Responsibility: LLM Response Processing
    """

    def __init__(
            self,
            llm_factory,
            moderation_service=None,
            parent_dashboard=None):
        self.llm_factory = llm_factory
        self.moderation_service = moderation_service
        self.parent_dashboard = parent_dashboard
        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_llm_request(
        self,
        text: str,
        session_id: str = None,
        retry_count: int = 0,
        session_manager=None,
    ) -> str:
        """Process LLM request using strategy pattern"""
        processor = LLMRequestProcessor(
            service=self,
            text=text,
            session_id=session_id,
            retry_count=retry_count,
            session_manager=session_manager,
        )
        return await processor.process()


class LLMRequestProcessor:
    """
    Strategy pattern for LLM request processing to reduce cyclomatic complexity.
    PATTERN: STRATEGY + PIPELINE eliminates complex conditionals.
    """

    def __init__(
        self,
        service,
        text: str,
        session_id: str = None,
        retry_count: int = 0,
        session_manager=None,
    ):
        self.service = service
        self.text = text
        self.session_id = session_id
        self.retry_count = retry_count
        self.session_manager = session_manager
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self) -> List[Dict[str, Any]]:
        """Create processing pipeline using TABLE LOOKUP pattern"""
        return [
            {"name": "input_moderation", "handler": self._check_input_moderation},
            {"name": "context_building", "handler": self._build_context},
            {"name": "llm_generation", "handler": self._generate_response},
            {"name": "output_moderation", "handler": self._check_output_moderation},
            {"name": "logging", "handler": self._log_interaction},
        ]

    async def process(self) -> str:
        """Process LLM request through pipeline"""
        try:
            return await self._execute_pipeline()
        except Exception as e:
            return await self._handle_error(e)

    async def _execute_pipeline(self) -> str:
        """Execute processing pipeline"""
        context = {}

        for step in self.pipeline:
            result = await step["handler"](context)
            if not result.get("continue", True):
                return result["response"]

        return context["llm_response"]

    async def _check_input_moderation(self, context: Dict) -> Dict:
        """Check input moderation"""
        if not self.service.moderation_service:
            return {"continue": True}

        try:
            moderation_result = await self.service.moderation_service.check_content(
                self.text
            )

            if not moderation_result.get("allowed", True):
                reason = moderation_result.get("reason", "Content blocked")
                self.service.logger.warning(
                    f"Content moderation blocked message: {reason}"
                )

                return {
                    "continue": False,
                    "response": "عذراً، لا يمكنني الإجابة على هذا السؤال. هل يمكنك طرح سؤال آخر؟",
                }

            return {"continue": True}

        except Exception as e:
            self.service.logger.error(f"Moderation check failed: {e}")
            return {"continue": True}  # Fail safe

    async def _build_context(self, context: Dict) -> Dict:
        """Build conversation context"""
        context["conversation"] = self._build_conversation_context()
        return {"continue": True}

    async def _generate_response(self, context: Dict) -> Dict:
        """Generate LLM response"""
        context["llm_response"] = await self._generate_llm_response(
            context["conversation"]
        )
        return {"continue": True}

    async def _check_output_moderation(self, context: Dict) -> Dict:
        """Check output moderation"""
        if not self.service.moderation_service:
            return {"continue": True}

        try:
            response = context["llm_response"]
            moderation_result = await self.service.moderation_service.check_content(
                response
            )

            if not moderation_result.get("allowed", True):
                reason = moderation_result.get("reason", "Response blocked")
                self.service.logger.warning(
                    f"LLM response blocked by moderation: {reason}"
                )

                return {
                    "continue": False,
                    "response": "عذراً، لا يمكنني الإجابة على هذا السؤال بشكل مناسب. هل يمكنك طرح سؤال آخر؟",
                }

            return {"continue": True}

        except Exception as e:
            self.service.logger.error(f"Output moderation check failed: {e}")
            return {"continue": True}  # Fail safe

    async def _log_interaction(self, context: Dict) -> Dict:
        """Log interaction"""
        await self._log_interaction_to_services(context["llm_response"])
        return {"continue": True}

    def _build_conversation_context(self) -> Conversation:
        """Build conversation context with history - REFACTORED to reduce nesting depth"""
        try:
            # Extract function: build conversation history
            history = self._build_conversation_history()

            # Add current user message
            history.append(Message(role="user", content=self.text))

            # Add system message at the beginning
            system_message = Message(
                role="system",
                content="أنت مساعد ذكي ودود للأطفال. أجب باختصار وبلغة عربية سهلة.",
            )
            history.insert(0, system_message)

            return Conversation(messages=history)

        except Exception as e:
            self.service.logger.error(
                f"Error building conversation context: {e}")
            return self._create_fallback_conversation()

    def _build_conversation_history(self) -> List[Message]:
        """Extract function: Build conversation history from session"""
        history = []

        # Guard clause: early return if no session ID
        if not self.session_id or not self.session_manager:
            return history

        # Guard clause: early return if no session
        session = self.session_manager.get_session(self.session_id)
        if not session:
            return history

        # Extract function: process recent messages
        self._add_recent_messages_to_history(history)
        return history

    def _add_recent_messages_to_history(self, history: List[Message]) -> None:
        """Extract function: Add recent messages to history - reduced nesting"""
        # Get recent messages (last 5)
        recent_messages = self.session_manager.get_recent_messages(
            self.session_id, limit=5
        )

        for msg in recent_messages:
            # Extract function: convert message to history entry
            message_entry = self._convert_message_to_history_entry(msg)
            if message_entry:
                history.append(message_entry)

    def _convert_message_to_history_entry(
            self, msg: Dict) -> Optional[Message]:
        """Extract function: Convert session message to conversation Message"""
        # Table lookup pattern instead of nested if-elif
        message_type_mapping = {
            "user_audio": lambda content: Message(
                role="user", content=content), "assistant": lambda content: Message(
                role="assistant", content=content), }

        msg_type = msg.get("type")
        content = msg.get("content")

        if msg_type in message_type_mapping and content:
            return message_type_mapping[msg_type](content)

        return None

    def _create_fallback_conversation(self) -> Conversation:
        """Extract function: Create fallback conversation when context building fails"""
        return Conversation(
            messages=[
                Message(role="system", content="أنت مساعد ذكي ودود للأطفال."),
                Message(role="user", content=self.text),
            ]
        )

    async def _generate_llm_response(self, conversation: Conversation) -> str:
        """Generate response using LLM factory"""
        try:
            from src.application.services.ai.llm_service_factory import LLMProvider

            llm_response = await self.service.llm_factory.generate_response(
                conversation,
                provider=LLMProvider.OPENAI,
                max_tokens=150,
                temperature=0.7,
            )

            if not llm_response:
                raise ValueError("Empty response from LLM")

            return llm_response

        except Exception as e:
            self.service.logger.error(f"LLM generation failed: {e}")
            raise

    async def _log_interaction_to_services(self, response: str) -> None:
        """Log interaction to session and parent dashboard"""
        try:
            # Log to session
            if self.session_id and self.session_manager:
                self.session_manager.add_message(
                    self.session_id, "assistant", response)

            # Log to parent dashboard
            if (
                self.session_id
                and self.service.parent_dashboard
                and self.session_manager
            ):
                await self._log_to_parent_dashboard(response)

        except Exception as e:
            self.service.logger.error(f"Error logging interaction: {e}")

    async def _log_to_parent_dashboard(self, response: str) -> None:
        """Log interaction to parent dashboard"""
        session = self.session_manager.get_session(self.session_id)
        if session:
            user_id = session.get("user_id")
            if user_id:
                await self.service.parent_dashboard.log_interaction(
                    user_id=user_id,
                    child_message=self.text,
                    assistant_message=response,
                    timestamp=datetime.now(),
                )

    async def _handle_error(self, error: Exception) -> str:
        """Handle processing errors with retry logic"""
        # Check if should retry
        if self.retry_count < 2:
            # Simple retry logic for specific errors
            error_str = str(error).lower()
            retryable_errors = ["timeout", "connection", "rate limit"]

            if any(err in error_str for err in retryable_errors):
                self.service.logger.info(
                    f"Retrying LLM request (attempt {self.retry_count + 1})"
                )
                await asyncio.sleep(1)  # Brief delay

                # Create new processor with incremented retry count
                retry_processor = LLMRequestProcessor(
                    self.service,
                    self.text,
                    self.session_id,
                    self.retry_count + 1,
                    self.session_manager,
                )
                return await retry_processor.process()

        # Return default response
        self.service.logger.error(f"LLM processing failed: {error}")
        return "عذراً، لم أستطع فهم ما تقول. هل يمكنك إعادة المحاولة؟"
