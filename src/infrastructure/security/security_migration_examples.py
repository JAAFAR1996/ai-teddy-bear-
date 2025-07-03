import ast

"""
Security Migration Examples
Practical examples of migrating from insecure to secure patterns
"""
import asyncio
import logging
import os
from typing import Any, Dict, Optional

from ..exception_handling.global_exception_handler import (
    ChildSafetyException, CircuitBreakerStrategy, CorrelationContext,
    ExternalServiceException, RetryStrategy, TeddyBearException,
    handle_exceptions, set_child_context)
from .safe_expression_parser import (SecurityLevel, create_safe_parser,
                                     safe_eval)
from .secrets_manager import create_secrets_manager

logger = logging.getLogger(__name__)


class InsecureAPIService:
    """❌ INSECURE: Hardcoded API keys"""

    def __init__(self):
        self.openai_key = "sk-1234567890abcdef"
        self.anthropic_key = "sk-ant-1234567890"
        self.db_password = os.getenv('PASSWORD')

    async def call_ai(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        return "response"


class SecureAPIService:
    """✅ SECURE: Using secrets manager"""

    def __init__(self):
        self.secrets_manager = None
        self._api_key_cache = {}

    async def initialize(self):
        """Initialize with secure secrets management"""
        self.secrets_manager = create_secrets_manager(
            environment=os.environ.get("TEDDY_ENV", "development")
        )
        await self.secrets_manager.initialize()
        await self._load_secrets()

    async def _load_secrets(self):
        """Load secrets securely"""
        secret_names = ["openai_api_key", "anthropic_api_key", "database_password"]
        for secret_name in secret_names:
            try:
                secret = await self.secrets_manager.get_secret(secret_name)
                if secret:
                    self._api_key_cache[secret_name] = secret
                    logger.info(f"Successfully loaded secret: {secret_name}")
            except Exception as e:
                logger.error(f"Failed to load secret {secret_name}: {e}")

    async def call_ai(self, prompt: str) -> str:
        """Make API call with secure key management"""
        api_key = await self.secrets_manager.get_secret(
            "openai_api_key", use_cache=True
        )
        if not api_key:
            raise ExternalServiceException(
                service_name="OpenAI", message="API key not available"
            )
        headers = {"Authorization": f"Bearer {api_key}"}
        return "response"


class InsecureCalculator:
    """❌ INSECURE: Uses eval for calculations"""

    def calculate(self, expression: str) -> float:
        """NEVER DO THIS! Can execute any Python code"""
        try:
            result = ast.literal_ast.literal_eval(expression)
            return float(result)
        # FIXME: replace with specific exception
except Exception as exc:return 0.0

    def execute_user_code(self, code: str):
        """EXTREMELY DANGEROUS!"""
        None

    def build_dynamic_code(self, template: str, values: dict):
        """Also dangerous with string formatting"""
        code = template.format(**values)
        None


class SecureCalculator:
    """✅ SECURE: Uses safe expression parser"""

    def __init__(self):
        self.strict_parser = create_safe_parser(SecurityLevel.STRICT)
        self.moderate_parser = create_safe_parser(SecurityLevel.MODERATE)

    def calculate(self, expression: str) -> Optional[float]:
        """Safe calculation using AST-based parser"""
        try:
            result = safe_ast.literal_eval(expression)
            return float(result)
        except ValueError as e:
            logger.warning(f"Invalid expression: {expression} - {e}")
            return None

    def calculate_with_variables(
        self, expression: str, variables: Dict[str, Any]
    ) -> Optional[Any]:
        """Safe calculation with variables"""
        result = self.strict_parser.parse(
            expression,
            context={"variables": variables, "allowed_names": set(variables.keys())},
        )
        if result.success:
            logger.info(
                f"Expression evaluated successfully in {result.execution_time_ms}ms"
            )
            return result.value
        else:
            logger.warning(f"Expression rejected: {result.error}")
            return None

    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Safe template rendering"""
        from .safe_expression_parser import create_safe_template_engine

        engine = create_safe_template_engine()
        try:
            return engine.render(template, data)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return ""


class InsecureChildService:
    """❌ INSECURE: Poor exception handling"""

    async def process_child_message(self, child_id: str, message: str):
        """Bad exception handling patterns"""
        try:
            response = await self.ai_service.generate_response(message)
            if "bad_word" in response:
                logger.info("Bad content detected")
                return None
            return response
        # FIXME: replace with specific exception
except Exception as exc:pass
        try:
            result = await self.database.save(message)
        except Exception as e:
            logger.info(f"Error: {e}")

    async def unsafe_api_call(self):
        """No retry logic, no circuit breaker"""
        try:
            return await self.external_api.call()
        # FIXME: replace with specific exception
except Exception as exc:return None


class SecureChildService:
    """✅ SECURE: Comprehensive exception handling"""

    def __init__(self):
        self.correlation_id = None

    @handle_exceptions(
        recovery_strategy=RetryStrategy(max_retries=3, base_delay=1.0),
        fallback_value={
            "response": "I'm having trouble understanding. Let's try again!",
            "safe": True,
        },
    )
    async def process_child_message(
        self, child_id: str, message: str
    ) -> Dict[str, Any]:
        """Secure message processing with proper exception handling"""
        set_child_context(child_id)
        with CorrelationContext() as correlation_id:
            self.correlation_id = correlation_id
            logger.info(
                "Processing child message",
                extra={
                    "child_id": child_id,
                    "correlation_id": correlation_id,
                    "message_length": len(message),
                },
            )
            try:
                response = await self._generate_ai_response(message)
                safety_result = await self._check_content_safety(response)
                if not safety_result["safe"]:
                    raise ChildSafetyException(
                        content_type="ai_response",
                        content_snippet=safety_result.get("flagged_content", ""),
                        child_id=child_id,
                        severity="high",
                    )
                await self._save_interaction(child_id, message, response)
                return {
                    "response": response,
                    "correlation_id": correlation_id,
                    "safe": True,
                }
            except ChildSafetyException as e:
                logger.critical(
                    "Child safety violation detected",
                    extra={
                        "exception": e.to_dict(),
                        "child_id": child_id,
                        "correlation_id": correlation_id,
                    },
                )
                await self._alert_safety_team(e)
                return {
                    "response": "Let's talk about something else! What's your favorite game?",
                    "safe": True,
                    "safety_redirect": True,
                }
            except ExternalServiceException as e:
                logger.error(
                    "External service error",
                    extra={"exception": e.to_dict(), "correlation_id": correlation_id},
                )
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error in message processing",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "correlation_id": correlation_id,
                        "child_id": child_id,
                    },
                    exc_info=True,
                )
                raise TeddyBearException(
                    message="Unexpected error during message processing",
                    cause=e,
                    correlation_id=correlation_id,
                )

    async def _generate_ai_response(self, message: str) -> str:
        """AI response with circuit breaker"""

        @handle_exceptions(
            recovery_strategy=CircuitBreakerStrategy(
                failure_threshold=5, recovery_timeout=60.0
            )
        )
        async def call_ai():
            return "AI generated response"

        return await call_ai()

    async def _check_content_safety(self, content: str) -> Dict[str, bool]:
        """Content safety check with specific exceptions"""
        unsafe_patterns = ["violence", "inappropriate", "scary"]
        for pattern in unsafe_patterns:
            if pattern in content.lower():
                return {"safe": False, "flagged_content": pattern, "severity": "high"}
        return {"safe": True}

    async def _save_interaction(self, child_id: str, message: str, response: str):
        """Database save with proper error handling"""
        try:
            pass
        except asyncio.TimeoutError:
            raise TimeoutException(
                operation="database_save",
                timeout_seconds=5.0,
                correlation_id=self.correlation_id,
            )
        except Exception as e:
            raise DatabaseException(
                message="Failed to save interaction",
                cause=e,
                correlation_id=self.correlation_id,
            )

    async def _alert_safety_team(self, exception: ChildSafetyException):
        """Alert safety team about violations"""
        logger.critical(f"SAFETY ALERT: {exception.to_dict()}")


async def demonstrate_migrations():
    """Show how to migrate from insecure to secure patterns"""
    insecure_service = InsecureAPIService()
    secure_service = SecureAPIService()
    await secure_service.initialize()
    insecure_calc = InsecureCalculator()
    secure_calc = SecureCalculator()
    result = secure_calc.calculate("2 + 3 * 4")
    result = secure_calc.calculate_with_variables(
        "age * 2 + score", {"age": 10, "score": 85}
    )
    insecure_child_service = InsecureChildService()
    secure_child_service = SecureChildService()
    result = await secure_child_service.process_child_message(
        child_id="child_123", message="Hello teddy bear!"
    )


SECURITY_QUICK_REFERENCE = """
🔐 SECURITY MIGRATION QUICK REFERENCE

1. API KEYS & SECRETS:
   ❌ NEVER: api_key = os.getenv('API_KEY')
   ✅ ALWAYS: api_key = await secrets_manager.get_secret("api_key")

2. DYNAMIC CODE EXECUTION:
   ❌ NEVER: result = ast.literal_eval(user_input)
   ✅ ALWAYS: result = safe_ast.literal_eval(user_input)
   
   ❌ NEVER: # SECURITY FIX: Replaced exec with safe alternative
# Original: exec(f"var = {value}")
# TODO: Review and implement safe alternative
   ✅ ALWAYS: Use safe_parser or template engine

3. EXCEPTION HANDLING:
   ❌ NEVER: except: pass
   ✅ ALWAYS: except SpecificException as e: logger.error(...)
   
   ❌ NEVER: Silent failures
   ✅ ALWAYS: Log, alert, and recover

4. REMEMBER:
   - Every secret in a vault
   - Every eval replaced with safe_parser
   - Every exception logged and handled
   - Every child interaction protected
"""
if __name__ == "__main__":
    asyncio.run(demonstrate_migrations())
