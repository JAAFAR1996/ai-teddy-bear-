"""
Security Solutions Integration
Demonstrates how to integrate all security components together
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..config.secure_configuration import (Environment,
                                           create_configuration_manager)
from ..exception_handling.global_exception_handler import (
    ChildSafetyException, CircuitBreakerStrategy, CorrelationContext,
    ExternalServiceException, FallbackStrategy, RetryStrategy,
    global_exception_handler, handle_exceptions, set_child_context)
from .safe_expression_parser import (SecurityLevel, create_safe_parser,
                                     create_safe_template_engine, safe_eval)
from .secrets_manager import SecretProvider, SecretType, create_secrets_manager

logger = logging.getLogger(__name__)


class SecureApplicationService:
    """Example service showing integrated security solutions"""

    def __init__(self):
        self.secrets_manager = None
        self.config_manager = None
        self.expression_parser = None
        self.template_engine = None
        self.initialized = False

    async def initialize(self, environment: str = "development"):
        """Initialize all security components"""
        logger.info(f"Initializing secure application service for {environment}")

        # 1. Initialize secrets manager
        self.secrets_manager = create_secrets_manager(
            environment=environment,
            vault_url="http://localhost:8200",  # Would come from env
            vault_token=None,  # Would come from env
        )
        await self.secrets_manager.initialize()

        # 2. Initialize configuration manager
        self.config_manager = await create_configuration_manager(environment)

        # 3. Initialize safe expression parser
        security_level = SecurityLevel.STRICT if environment == "production" else SecurityLevel.MODERATE
        self.expression_parser = create_safe_parser(security_level)

        # 4. Initialize template engine
        self.template_engine = create_safe_template_engine()

        # 5. Setup global exception handling strategies
        self._setup_exception_strategies()

        self.initialized = True
        logger.info("Security components initialized successfully")

    def _setup_exception_strategies(self):
        """Setup recovery strategies for different exception types"""
        # Retry strategy for external services
        global_exception_handler.register_strategy(
            ExternalServiceException, RetryStrategy(max_retries=3, base_delay=1.0)
        )

        # Circuit breaker for AI services
        global_exception_handler.register_strategy(
            ExternalServiceException, CircuitBreakerStrategy(failure_threshold=5, recovery_timeout=60.0)
        )

        # Fallback for child safety
        async def safety_fallback():
            return {"response": "I'm sorry, I couldn't understand that. Can you try again?"}

        global_exception_handler.register_strategy(ChildSafetyException, FallbackStrategy(safety_fallback))

    @handle_exceptions(recovery_strategy=RetryStrategy(), fallback_value={"error": "Service temporarily unavailable"})
    async def process_child_request(self, child_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a child's request with full security measures"""

        # Set child context for exception handling
        set_child_context(child_id)

        # Use correlation context
        with CorrelationContext() as correlation_id:
            logger.info("Processing child request", child_id=child_id, correlation_id=correlation_id)

            # 1. Get AI service credentials from secrets manager
            ai_key = await self.secrets_manager.get_secret("openai_api_key", provider=SecretProvider.HASHICORP_VAULT)

            if not ai_key:
                raise ExternalServiceException(service_name="OpenAI", message="API key not found")

            # 2. Get configuration
            ai_config = await self.config_manager.get("ai_services.openai")
            safety_config = await self.config_manager.get("child_safety")

            # 3. Safe expression evaluation (if needed)
            if "expression" in request_data:
                try:
                    result = self.expression_parser.parse(
                        request_data["expression"],
                        context={"variables": {"age": 10, "score": 85}, "allowed_names": {"age", "score"}},
                    )

                    if result.success:
                        request_data["evaluated_expression"] = result.value
                    else:
                        logger.warning(f"Expression evaluation failed: {result.error}")
                except Exception as e:
                    logger.error(f"Expression parsing error: {e}")

            # 4. Template rendering (if needed)
            if "template" in request_data:
                try:
                    rendered = self.template_engine.render(request_data["template"], {"child_name": "Alice", "age": 10})
                    request_data["rendered_template"] = rendered
                except Exception as e:
                    logger.error(f"Template rendering error: {e}")

            # 5. Process with AI service (simulated)
            response = await self._call_ai_service(ai_key, ai_config, request_data)

            # 6. Apply safety filters
            safe_response = await self._apply_safety_filters(response, safety_config)

            return {
                "success": True,
                "correlation_id": correlation_id,
                "response": safe_response,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _call_ai_service(self, api_key: str, config: Dict[str, Any], request_data: Dict[str, Any]) -> str:
        """Call AI service with proper error handling"""
        # Simulated AI call
        await asyncio.sleep(0.1)  # Simulate network delay

        # In real implementation, would use actual AI service
        return "This is a safe response for children."

    async def _apply_safety_filters(self, response: str, safety_config: Dict[str, Any]) -> str:
        """Apply child safety filters to response"""
        # In real implementation, would use content moderation

        # Simple demonstration
        unsafe_words = ["bad", "dangerous", "scary"]

        for word in unsafe_words:
            if word in response.lower():
                raise ChildSafetyException("Unsafe content detected", content_type="text", content_snippet=word)

        return response

    async def rotate_all_secrets(self):
        """Demonstrate secret rotation"""
        logger.info("Starting secret rotation")

        secrets_to_rotate = ["openai_api_key", "anthropic_api_key", "database_password", "jwt_secret_key"]

        for secret_name in secrets_to_rotate:
            try:
                success = await self.secrets_manager.rotate_secret(secret_name)
                if success:
                    logger.info(f"Successfully rotated {secret_name}")
                else:
                    logger.error(f"Failed to rotate {secret_name}")
            except Exception as e:
                logger.error(f"Error rotating {secret_name}: {e}")

    async def validate_configuration(self) -> bool:
        """Validate current configuration"""
        errors = await self.config_manager.validate()

        if errors:
            logger.error(f"Configuration validation errors: {errors}")
            return False

        logger.info("Configuration validation passed")
        return True

    async def get_audit_report(self) -> Dict[str, Any]:
        """Get security audit report"""
        return {
            "configuration_audit": self.config_manager.get_audit_log(limit=50),
            "secrets_accessed": await self.secrets_manager.list_secrets(),
            "validation_status": await self.validate_configuration(),
        }


# Example usage
async def main():
    """Demonstrate integrated security usage"""

    # Initialize service
    service = SecureApplicationService()
    await service.initialize(environment="development")

    # Example 1: Process child request with full security
    try:
        result = await service.process_child_request(
            child_id="child_123",
            request_data={
                "message": "What is 2 + 2?",
                "expression": "2 + 2",
                "template": "Hello {{ child_name }}, you are {{ age }} years old!",
            },
        )

    except Exception as e:

    # Example 2: Rotate secrets
    await service.rotate_all_secrets()

    # Example 3: Get audit report
    audit_report = await service.get_audit_report()

    # Example 4: Safe expression evaluation
    try:
        # Safe mathematical expression
        result = safe_eval("2 + 3 * 4")

        # Blocked dangerous expression
        result = safe_eval("__import__('os').system('ls')")
    except ValueError as e:

    # Example 5: Configuration access
    db_config = await service.config_manager.get("database")

# Security best practices implementation
class SecurityBestPractices:
    """Documentation of security best practices"""

    @staticmethod
    def secrets_management_guidelines():
        """Guidelines for secrets management"""
        return """
        1. Never hardcode secrets in source code
        2. Use environment-specific secret stores
        3. Rotate secrets regularly (every 90 days)
        4. Use strong encryption for secrets at rest
        5. Audit all secret access
        6. Use least privilege principle
        7. Separate secrets by environment
        8. Never log secret values
        """

    @staticmethod
    def safe_code_execution_guidelines():
        """Guidelines for safe code execution"""
        return """
        1. Never use eval() or exec() with user input
        2. Use AST-based validation for expressions
        3. Whitelist allowed operations
        4. Set execution timeouts
        5. Limit resource usage
        6. Use sandboxed environments
        7. Validate all inputs
        8. Log all execution attempts
        """

    @staticmethod
    def exception_handling_guidelines():
        """Guidelines for exception handling"""
        return """
        1. Use structured exception hierarchy
        2. Log with correlation IDs
        3. Sanitize error messages for users
        4. Implement recovery strategies
        5. Use circuit breakers for external services
        6. Alert on critical exceptions
        7. Track exception metrics
        8. Test exception scenarios
        """

    @staticmethod
    def configuration_security_guidelines():
        """Guidelines for configuration security"""
        return """
        1. Validate all configuration values
        2. Use environment-specific configs
        3. Encrypt sensitive configuration
        4. Audit configuration access
        5. Version control configurations
        6. Use schema validation
        7. Implement configuration hot-reload
        8. Separate code from configuration
        """


# Migration guide from insecure to secure
class SecurityMigrationGuide:
    """Guide for migrating from insecure to secure patterns"""

    @staticmethod
    def migrate_hardcoded_secrets():
        """Migrate from hardcoded secrets"""
        print(
            """
        # Before (INSECURE):
        api_key = "sk-1234567890abcdef"
        
        # After (SECURE):
        secrets_manager = create_secrets_manager()
        api_key = await secrets_manager.get_secret("openai_api_key")
        """
        )

    @staticmethod
    def migrate_eval_usage():
        """Migrate from eval() usage"""
        print(
            """
        # Before (INSECURE):
        result = eval(user_input)
        
        # After (SECURE):
        parser = create_safe_parser()
        result = parser.parse(user_input)
        if result.success:
            value = result.value
        """
        )

    @staticmethod
    def migrate_exception_handling():
        """Migrate exception handling"""
        print(
            """
        # Before (INSECURE):
        try:
            risky_operation()
        except Exception as e:

        # After (SECURE):
        @handle_exceptions(recovery_strategy=RetryStrategy())
        async def safe_operation():
            return await risky_operation()
        """
        )


if __name__ == "__main__":
    # Run example
    asyncio.run(main())
