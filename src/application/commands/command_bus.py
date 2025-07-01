"""
🚌 Command Bus Implementation
============================

CQRS Command Bus for handling write operations in AI Teddy Bear system.
Provides command dispatching, validation, and integration with Event Sourcing.
"""

import logging
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar

from ...domain.events.event_sourcing_service import get_event_sourcing_service
from ...shared.kernel import DomainEvent

logger = logging.getLogger(__name__)

TCommand = TypeVar("TCommand", bound="Command")
TResult = TypeVar("TResult")


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution"""

    success: bool
    message: str
    data: Optional[Any] = None
    events: List[DomainEvent] = None


class Command(Protocol):
    """Base protocol for all commands"""

    command_id: str
    timestamp: datetime
    user_id: Optional[str] = None


class CommandHandler(Protocol[TCommand, TResult]):
    """Protocol for command handlers"""

    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """Handle the command and return result"""
        pass

    @abstractmethod
    async def validate(self, command: TCommand) -> bool:
        """Validate command before handling"""
        pass


class CommandMiddleware(Protocol):
    """Protocol for command middleware"""

    @abstractmethod
    async def execute(self, command: TCommand, next_handler) -> TResult:
        """Execute middleware logic"""
        pass


class ValidationMiddleware(CommandMiddleware):
    """Middleware for command validation"""

    async def execute(self, command: TCommand, next_handler) -> TResult:
        """Validate command before execution"""

        # Basic validation
        if not hasattr(command, "command_id") or not command.command_id:
            raise ValueError("Command must have valid command_id")

        if not hasattr(command, "timestamp") or not command.timestamp:
            raise ValueError("Command must have timestamp")

        # Execute next handler
        return await next_handler(command)


class LoggingMiddleware(CommandMiddleware):
    """Middleware for command logging"""

    async def execute(self, command: TCommand, next_handler) -> TResult:
        """Log command execution"""

        command_name = type(command).__name__

        logger.info(f"Executing command: {command_name}")
        start_time = datetime.utcnow()

        try:
            result = await next_handler(command)

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Command {command_name} completed in {duration:.3f}s")

            return result

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Command {command_name} failed after {duration:.3f}s: {e}")
            raise


class CommandBus:
    """Central command bus for CQRS pattern"""

    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}
        self._middleware: List[CommandMiddleware] = []
        self.event_sourcing_service = get_event_sourcing_service()

    def register_handler(
        self, command_type: Type[TCommand], handler: CommandHandler[TCommand, TResult]
    ) -> None:
        """Register command handler"""

        if command_type in self._handlers:
            logger.warning(f"Handler for {command_type.__name__} already registered")

        self._handlers[command_type] = handler
        logger.info(f"Registered handler for {command_type.__name__}")

    def add_middleware(self, middleware: CommandMiddleware) -> None:
        """Add middleware to pipeline"""
        self._middleware.append(middleware)
        logger.info(f"Added middleware: {type(middleware).__name__}")

    async def execute(self, command: TCommand) -> TResult:
        """Execute command through middleware pipeline"""

        command_type = type(command)
        handler = self._handlers.get(command_type)

        if not handler:
            raise ValueError(f"No handler registered for {command_type.__name__}")

        # Build middleware pipeline
        final_handler = self._build_pipeline(handler)

        # Execute command
        return await final_handler(command)

    def _build_pipeline(self, handler: CommandHandler) -> callable:
        """Build middleware pipeline"""

        async def final_handler(command: TCommand) -> TResult:
            # Validate command first
            if hasattr(handler, "validate"):
                is_valid = await handler.validate(command)
                if not is_valid:
                    raise ValueError(
                        f"Command validation failed: {type(command).__name__}"
                    )

            # Execute handler
            return await handler.handle(command)

        # Apply middleware in reverse order
        current_handler = final_handler

        for middleware in reversed(self._middleware):
            previous_handler = current_handler

            async def wrapped_handler(
                cmd: TCommand, prev=previous_handler, mw=middleware
            ) -> TResult:
                return await mw.execute(cmd, prev)

            current_handler = wrapped_handler

        return current_handler

    def get_registered_commands(self) -> List[Type[Command]]:
        """Get list of registered command types"""
        return list(self._handlers.keys())

    async def health_check(self) -> Dict[str, Any]:
        """Health check for command bus"""

        return {
            "status": "healthy",
            "handlers_count": len(self._handlers),
            "middleware_count": len(self._middleware),
            "registered_commands": [cmd.__name__ for cmd in self._handlers.keys()],
        }


# Global command bus instance
_command_bus: Optional[CommandBus] = None


def get_command_bus() -> CommandBus:
    """Get global command bus instance"""
    global _command_bus
    if not _command_bus:
        _command_bus = CommandBus()
        # Add default middleware
        _command_bus.add_middleware(ValidationMiddleware())
        _command_bus.add_middleware(LoggingMiddleware())
    return _command_bus
