"""
Security Migration Examples
Practical examples of migrating from insecure to secure patterns
"""

import os
import asyncio
from typing import Dict, Any, Optional
import logging

# Import secure components
from .secrets_manager import create_secrets_manager, SecretType
from .safe_expression_parser import safe_eval, create_safe_parser, SecurityLevel
from ..exception_handling.global_exception_handler import (
    handle_exceptions,
    TeddyBearException,
    ChildSafetyException,
    ExternalServiceException,
    RetryStrategy,
    CircuitBreakerStrategy,
    CorrelationContext,
    set_child_context
)

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: API Keys Migration
# ============================================================================

class InsecureAPIService:
    """❌ INSECURE: Hardcoded API keys"""
    
    def __init__(self):
        # NEVER DO THIS!
        self.openai_key = "sk-1234567890abcdef"  # Hardcoded secret
        self.anthropic_key = "sk-ant-1234567890"  # Another hardcoded secret
        self.db_password = "mySecretPassword123"  # Database password exposed
        
    async def call_ai(self, prompt: str) -> str:
        # Using hardcoded key directly
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        # ... make API call
        return "response"


class SecureAPIService:
    """✅ SECURE: Using secrets manager"""
    
    def __init__(self):
        self.secrets_manager = None
        self._api_key_cache = {}
        
    async def initialize(self):
        """Initialize with secure secrets management"""
        # Create secrets manager
        self.secrets_manager = create_secrets_manager(
            environment=os.environ.get("TEDDY_ENV", "development")
        )
        await self.secrets_manager.initialize()
        
        # Pre-load frequently used secrets into memory (still encrypted)
        await self._load_secrets()
    
    async def _load_secrets(self):
        """Load secrets securely"""
        # Secrets are fetched from vault/manager, not hardcoded
        secret_names = [
            "openai_api_key",
            "anthropic_api_key", 
            "database_password"
        ]
        
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
        # Get key from secrets manager (with caching)
        api_key = await self.secrets_manager.get_secret(
            "openai_api_key",
            use_cache=True  # Uses encrypted cache
        )
        
        if not api_key:
            raise ExternalServiceException(
                service_name="OpenAI",
                message="API key not available"
            )
        
        headers = {"Authorization": f"Bearer {api_key}"}
        # ... make API call
        return "response"


# ============================================================================
# EXAMPLE 2: eval/exec Migration
# ============================================================================

class InsecureCalculator:
    """❌ INSECURE: Uses eval for calculations"""
    
    def calculate(self, expression: str) -> float:
        """NEVER DO THIS! Can execute any Python code"""
        try:
            # Dangerous! User could input: __import__('os').system('rm -rf /')
            result = eval(expression)
            return float(result)
        except Exception as e:
            return 0.0
    
    def execute_user_code(self, code: str):
        """EXTREMELY DANGEROUS!"""
        # User could do ANYTHING here
        exec(code)
        
    def build_dynamic_code(self, template: str, values: dict):
        """Also dangerous with string formatting"""
        code = template.format(**values)
        exec(code)  # Still dangerous!


class SecureCalculator:
    """✅ SECURE: Uses safe expression parser"""
    
    def __init__(self):
        # Different security levels for different use cases
        self.strict_parser = create_safe_parser(SecurityLevel.STRICT)
        self.moderate_parser = create_safe_parser(SecurityLevel.MODERATE)
        
    def calculate(self, expression: str) -> Optional[float]:
        """Safe calculation using AST-based parser"""
        try:
            # For simple math, use the convenience function
            result = safe_eval(expression)
            return float(result)
        except ValueError as e:
            logger.warning(f"Invalid expression: {expression} - {e}")
            return None
    
    def calculate_with_variables(self, expression: str, variables: Dict[str, Any]) -> Optional[Any]:
        """Safe calculation with variables"""
        # Parse with context
        result = self.strict_parser.parse(
            expression,
            context={
                "variables": variables,
                "allowed_names": set(variables.keys())
            }
        )
        
        if result.success:
            logger.info(f"Expression evaluated successfully in {result.execution_time_ms}ms")
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


# ============================================================================
# EXAMPLE 3: Exception Handling Migration
# ============================================================================

class InsecureChildService:
    """❌ INSECURE: Poor exception handling"""
    
    async def process_child_message(self, child_id: str, message: str):
        """Bad exception handling patterns"""
        try:
            # Process message
            response = await self.ai_service.generate_response(message)
            
            # Check content (basic)
            if "bad_word" in response:
                print("Bad content detected")  # Just printing!
                return None
                
            return response
            
        except:  # Bare except - catches EVERYTHING
            pass  # Silently fails - VERY BAD!
        
        # Or slightly better but still bad:
        try:
            result = await self.database.save(message)
        except Exception as e:  # Too broad
            print(f"Error: {e}")  # No proper logging
            # No recovery attempt
            # No alerting
            # No correlation tracking
    
    async def unsafe_api_call(self):
        """No retry logic, no circuit breaker"""
        try:
            return await self.external_api.call()
        except Exception:
            return None  # Silent failure


class SecureChildService:
    """✅ SECURE: Comprehensive exception handling"""
    
    def __init__(self):
        self.correlation_id = None
        
    @handle_exceptions(
        recovery_strategy=RetryStrategy(max_retries=3, base_delay=1.0),
        fallback_value={"response": "I'm having trouble understanding. Let's try again!", "safe": True}
    )
    async def process_child_message(self, child_id: str, message: str) -> Dict[str, Any]:
        """Secure message processing with proper exception handling"""
        
        # Set child context for exception handling
        set_child_context(child_id)
        
        # Use correlation context for tracing
        with CorrelationContext() as correlation_id:
            self.correlation_id = correlation_id
            logger.info(
                "Processing child message",
                extra={
                    "child_id": child_id,
                    "correlation_id": correlation_id,
                    "message_length": len(message)
                }
            )
            
            try:
                # Process with AI
                response = await self._generate_ai_response(message)
                
                # Safety check
                safety_result = await self._check_content_safety(response)
                if not safety_result["safe"]:
                    # Specific exception for child safety
                    raise ChildSafetyException(
                        content_type="ai_response",
                        content_snippet=safety_result.get("flagged_content", ""),
                        child_id=child_id,
                        severity="high"
                    )
                
                # Save to database with proper error handling
                await self._save_interaction(child_id, message, response)
                
                return {
                    "response": response,
                    "correlation_id": correlation_id,
                    "safe": True
                }
                
            except ChildSafetyException as e:
                # Child safety issues get special handling
                logger.critical(
                    "Child safety violation detected",
                    extra={
                        "exception": e.to_dict(),
                        "child_id": child_id,
                        "correlation_id": correlation_id
                    }
                )
                # Alert parents/moderators immediately
                await self._alert_safety_team(e)
                
                # Return safe fallback
                return {
                    "response": "Let's talk about something else! What's your favorite game?",
                    "safe": True,
                    "safety_redirect": True
                }
                
            except ExternalServiceException as e:
                # External service failures are retried automatically by decorator
                logger.error(
                    "External service error",
                    extra={
                        "exception": e.to_dict(),
                        "correlation_id": correlation_id
                    }
                )
                raise  # Let decorator handle retry
                
            except Exception as e:
                # Unexpected errors still get logged properly
                logger.error(
                    "Unexpected error in message processing",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "correlation_id": correlation_id,
                        "child_id": child_id
                    },
                    exc_info=True  # Include stack trace
                )
                raise TeddyBearException(
                    message="Unexpected error during message processing",
                    cause=e,
                    correlation_id=correlation_id
                )
    
    async def _generate_ai_response(self, message: str) -> str:
        """AI response with circuit breaker"""
        # Circuit breaker prevents cascade failures
        @handle_exceptions(
            recovery_strategy=CircuitBreakerStrategy(
                failure_threshold=5,
                recovery_timeout=60.0
            )
        )
        async def call_ai():
            # Actual AI call here
            return "AI generated response"
        
        return await call_ai()
    
    async def _check_content_safety(self, content: str) -> Dict[str, bool]:
        """Content safety check with specific exceptions"""
        # Simulate safety check
        unsafe_patterns = ["violence", "inappropriate", "scary"]
        
        for pattern in unsafe_patterns:
            if pattern in content.lower():
                return {
                    "safe": False,
                    "flagged_content": pattern,
                    "severity": "high"
                }
        
        return {"safe": True}
    
    async def _save_interaction(self, child_id: str, message: str, response: str):
        """Database save with proper error handling"""
        try:
            # Database operation
            pass
        except asyncio.TimeoutError:
            raise TimeoutException(
                operation="database_save",
                timeout_seconds=5.0,
                correlation_id=self.correlation_id
            )
        except Exception as e:
            raise DatabaseException(
                message="Failed to save interaction",
                cause=e,
                correlation_id=self.correlation_id
            )
    
    async def _alert_safety_team(self, exception: ChildSafetyException):
        """Alert safety team about violations"""
        # Send to monitoring/alerting system
        logger.critical(f"SAFETY ALERT: {exception.to_dict()}")


# ============================================================================
# Migration Guide Usage Examples
# ============================================================================

async def demonstrate_migrations():
    """Show how to migrate from insecure to secure patterns"""
    
    print("=== API Keys Migration ===")
    
    # ❌ Don't do this
    insecure_service = InsecureAPIService()
    
    # ✅ Do this instead
    secure_service = SecureAPIService()
    await secure_service.initialize()
    
    print("\n=== Expression Evaluation Migration ===")
    
    # ❌ Don't do this
    insecure_calc = InsecureCalculator()
    # result = insecure_calc.calculate("__import__('os').system('ls')")  # DANGEROUS!
    
    # ✅ Do this instead
    secure_calc = SecureCalculator()
    result = secure_calc.calculate("2 + 3 * 4")  # Safe!
    print(f"Safe calculation result: {result}")
    
    # With variables
    result = secure_calc.calculate_with_variables(
        "age * 2 + score",
        {"age": 10, "score": 85}
    )
    print(f"Safe calculation with variables: {result}")
    
    print("\n=== Exception Handling Migration ===")
    
    # ❌ Don't do this
    insecure_child_service = InsecureChildService()
    
    # ✅ Do this instead  
    secure_child_service = SecureChildService()
    
    # Process a message
    result = await secure_child_service.process_child_message(
        child_id="child_123",
        message="Hello teddy bear!"
    )
    print(f"Secure processing result: {result}")


# ============================================================================
# Quick Reference Card
# ============================================================================

SECURITY_QUICK_REFERENCE = """
🔐 SECURITY MIGRATION QUICK REFERENCE

1. API KEYS & SECRETS:
   ❌ NEVER: api_key = "sk-abc123"
   ✅ ALWAYS: api_key = await secrets_manager.get_secret("api_key")

2. DYNAMIC CODE EXECUTION:
   ❌ NEVER: result = eval(user_input)
   ✅ ALWAYS: result = safe_eval(user_input)
   
   ❌ NEVER: exec(f"var = {value}")
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
    print(SECURITY_QUICK_REFERENCE)
    asyncio.run(demonstrate_migrations()) 