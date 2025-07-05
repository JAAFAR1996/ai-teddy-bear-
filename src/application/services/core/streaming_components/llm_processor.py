"""
🧠 LLM Processor
High cohesion component for LLM processing with bumpy road fix
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .models import LLMRequest, ProcessingResult


class ModerationProcessor:
    """
    Content moderation processing logic.
    Extracted from main LLM processor to eliminate bumpy road pattern.
    """
    
    def __init__(self, moderation_service):
        self.moderation_service = moderation_service
        self.logger = logging.getLogger(__name__)
    
    async def check_input_content(self, text: str) -> ProcessingResult:
        """Check input content for moderation issues"""
        if not self.moderation_service:
            return ProcessingResult.success_result({"allowed": True, "reason": "No moderation service"})
        
        try:
            moderation_result = await self.moderation_service.check_content(text)
            
            if not moderation_result.get('allowed', True):
                reason = moderation_result.get('reason', 'Content blocked')
                self.logger.warning(f"Input content blocked: {reason}")
                
                return ProcessingResult.error_result(
                    "عذراً، لا يمكنني الإجابة على هذا السؤال. هل يمكنك طرح سؤال آخر؟",
                    metadata={"moderation_reason": reason}
                )
            
            return ProcessingResult.success_result({"allowed": True})
            
        except Exception as e:
            self.logger.error(f"Moderation check failed: {e}")
            # Fail safe - allow content if moderation fails
            return ProcessingResult.success_result({"allowed": True, "error": str(e)})
    
    async def check_output_content(self, text: str) -> ProcessingResult:
        """Check output content for moderation issues"""
        if not self.moderation_service:
            return ProcessingResult.success_result({"allowed": True})
        
        try:
            moderation_result = await self.moderation_service.check_content(text)
            
            if not moderation_result.get('allowed', True):
                reason = moderation_result.get('reason', 'Response blocked')
                self.logger.warning(f"LLM response blocked: {reason}")
                
                return ProcessingResult.error_result(
                    "عذراً، لا يمكنني الإجابة على هذا السؤال بشكل مناسب. هل يمكنك طرح سؤال آخر؟",
                    metadata={"moderation_reason": reason}
                )
            
            return ProcessingResult.success_result({"allowed": True})
            
        except Exception as e:
            self.logger.error(f"Output moderation check failed: {e}")
            # Fail safe - allow response if moderation fails
            return ProcessingResult.success_result({"allowed": True, "error": str(e)})


class SessionContextBuilder:
    """
    Session context building logic.
    Extracted from main LLM processor to eliminate bumpy road pattern.
    """
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)
    
    def build_conversation_history(self, session_id: str, max_messages: int = 5) -> list:
        """Build conversation history from session"""
        history = []
        
        if not session_id or not self.session_manager:
            return history
        
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return history
            
            # Get recent messages
            session_history = self.session_manager.session_history.get(session_id, [])
            recent_messages = session_history[-max_messages:] if session_history else []
            
            # Convert to conversation format
            for msg in recent_messages:
                if msg['type'] == 'user_audio':
                    from src.core.domain.entities.conversation import Message
                    history.append(Message(role='user', content=msg['content']))
                elif msg['type'] == 'assistant':
                    from src.core.domain.entities.conversation import Message
                    history.append(Message(role='assistant', content=msg['content']))
            
            self.logger.debug(f"Built conversation history with {len(history)} messages")
            return history
            
        except Exception as e:
            self.logger.error(f"Error building conversation history: {e}")
            return history
    
    def add_system_message(self, history: list) -> list:
        """Add system message to conversation history"""
        try:
            from src.core.domain.entities.conversation import Message
            
            system_message = Message(
                role='system', 
                content="أنت مساعد ذكي ودود للأطفال. أجب باختصار وبلغة عربية سهلة."
            )
            
            history.insert(0, system_message)
            return history
            
        except Exception as e:
            self.logger.error(f"Error adding system message: {e}")
            return history


class RetryHandler:
    """
    Retry logic for LLM requests.
    Extracted from main LLM processor to eliminate bumpy road pattern.
    """
    
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    def should_retry(self, retry_count: int, error: Exception) -> bool:
        """Determine if request should be retried"""
        if retry_count >= self.max_retries:
            return False
        
        # Retry on specific error types
        error_str = str(error).lower()
        retryable_errors = ['timeout', 'connection', 'rate limit', 'temporary']
        
        return any(err in error_str for err in retryable_errors)
    
    def get_default_response(self) -> str:
        """Get default response when all retries fail"""
        return "عذراً، لم أستطع فهم ما تقول. هل يمكنك إعادة المحاولة؟"


class LLMProcessor:
    """
    Dedicated service for LLM processing and response generation.
    High cohesion: all methods work with LLM requests and responses.
    
    ✅ Solved Bumpy Road problem by extracting complex logic into separate classes
    ✅ Each processor handles one responsibility (Single Responsibility)
    ✅ Main processor coordinates between components (high-level orchestration)
    """
    
    def __init__(self, llm_factory, moderation_service=None, session_manager=None, parent_dashboard=None):
        """Initialize LLM processor with dependencies"""
        self.llm_factory = llm_factory
        self.logger = logging.getLogger(__name__)
        
        # Initialize processors
        self.moderation_processor = ModerationProcessor(moderation_service)
        self.context_builder = SessionContextBuilder(session_manager)
        self.retry_handler = RetryHandler()
        
        # Services
        self.session_manager = session_manager
        self.parent_dashboard = parent_dashboard
        
        # Statistics
        self.request_count = 0
        self.successful_requests = 0
        self.moderation_blocks = 0
        self.retry_attempts = 0
    
    async def process_llm_request(self, request: LLMRequest) -> ProcessingResult:
        """
        Process LLM request with moderation, context building, and retry logic.
        EXTRACT FUNCTION applied - no more bumpy road pattern.
        """
        try:
            self.request_count += 1
            
            # Step 1: Input moderation
            moderation_result = await self._check_input_moderation(request.text)
            if not moderation_result.success:
                return moderation_result
            
            # Step 2: Build conversation context
            conversation = self._build_conversation_context(request)
            
            # Step 3: Generate LLM response
            llm_result = await self._generate_llm_response(conversation, request)
            if not llm_result.success:
                return await self._handle_llm_error(request, llm_result.error_message)
            
            # Step 4: Output moderation
            response_text = llm_result.data
            output_result = await self._check_output_moderation(response_text)
            if not output_result.success:
                return output_result
            
            # Step 5: Log and store
            await self._log_successful_interaction(request, response_text)
            
            self.successful_requests += 1
            return ProcessingResult.success_result(response_text)
            
        except Exception as e:
            self.logger.error(f"Error processing LLM request: {e}")
            return ProcessingResult.error_result(f"LLM processing failed: {str(e)}")
    
    async def _check_input_moderation(self, text: str) -> ProcessingResult:
        """Check input text for moderation issues"""
        result = await self.moderation_processor.check_input_content(text)
        if not result.success:
            self.moderation_blocks += 1
        return result
    
    def _build_conversation_context(self, request: LLMRequest):
        """Build conversation context with history"""
        try:
            from src.core.domain.entities.conversation import Conversation, Message
            
            # Build history
            history = self.context_builder.build_conversation_history(request.session_id)
            
            # Add current user message
            history.append(Message(role='user', content=request.text))
            
            # Add system message
            history = self.context_builder.add_system_message(history)
            
            return Conversation(messages=history)
            
        except Exception as e:
            self.logger.error(f"Error building conversation context: {e}")
            # Fallback to simple conversation
            from src.core.domain.entities.conversation import Conversation, Message
            return Conversation(messages=[
                Message(role='system', content="أنت مساعد ذكي ودود للأطفال."),
                Message(role='user', content=request.text)
            ])
    
    async def _generate_llm_response(self, conversation, request: LLMRequest) -> ProcessingResult:
        """Generate response using LLM factory"""
        try:
            from src.application.services.llm_service_factory import LLMProvider
            
            response = await self.llm_factory.generate_response(
                conversation,
                provider=LLMProvider.OPENAI,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            if not response:
                return ProcessingResult.error_result("Empty response from LLM")
            
            return ProcessingResult.success_result(response)
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return ProcessingResult.error_result(str(e))
    
    async def _check_output_moderation(self, response_text: str) -> ProcessingResult:
        """Check output text for moderation issues"""
        result = await self.moderation_processor.check_output_content(response_text)
        if not result.success:
            self.moderation_blocks += 1
        return result
    
    async def _handle_llm_error(self, request: LLMRequest, error_message: str) -> ProcessingResult:
        """Handle LLM generation errors with retry logic"""
        # Check if should retry
        if self.retry_handler.should_retry(request.retry_count, Exception(error_message)):
            self.retry_attempts += 1
            self.logger.info(f"Retrying LLM request (attempt {request.retry_count + 1})")
            
            # Create retry request
            retry_request = LLMRequest(
                text=request.text,
                session_id=request.session_id,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                retry_count=request.retry_count + 1
            )
            
            return await self.process_llm_request(retry_request)
        
        # Return default response
        default_response = self.retry_handler.get_default_response()
        return ProcessingResult.success_result(default_response)
    
    async def _log_successful_interaction(self, request: LLMRequest, response: str):
        """Log successful interaction to session and parent dashboard"""
        try:
            # Log to session
            if request.session_id and self.session_manager:
                self.session_manager.add_message(
                    request.session_id, "assistant", response
                )
            
            # Log to parent dashboard
            if self.parent_dashboard and request.session_id:
                session = self.session_manager.get_session(request.session_id) if self.session_manager else None
                user_id = session.get('user_id') if session else None
                
                if user_id:
                    await self.parent_dashboard.log_interaction(
                        user_id=user_id,
                        child_message=request.text,
                        assistant_message=response,
                        timestamp=datetime.now()
                    )
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")
            # Don't fail the main request if logging fails
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get LLM processing statistics"""
        success_rate = (
            self.successful_requests / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "service_name": "LLMProcessor",
            "total_requests": self.request_count,
            "successful_requests": self.successful_requests,
            "success_rate": success_rate,
            "moderation_blocks": self.moderation_blocks,
            "retry_attempts": self.retry_attempts,
            "high_cohesion": True,
            "responsibility": "LLM processing with moderation and retry logic"
        } 