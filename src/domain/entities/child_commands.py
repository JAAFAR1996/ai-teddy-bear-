from typing import Any, Optional

"""
👶 Child Commands Implementation
===============================

CQRS Commands for child-related operations in AI Teddy Bear system.
Handles child registration, profile updates, and safety operations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ...domain.events.event_sourcing_examples import ChildAggregateExample
from ...domain.events.event_sourcing_service import get_event_sourcing_service
from ...domain.value_objects import ChildId, DeviceId, ParentId
from .command_bus import Command, CommandHandler, CommandResult, get_command_bus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegisterChildCommand(Command):
    """Command to register a new child"""

    command_id: str
    timestamp: datetime
    parent_id: str
    device_id: str
    name: str
    age: int
    udid: str
    user_id: Optional[str] = None


@dataclass(frozen=True)
class UpdateChildProfileCommand(Command):
    """Command to update child profile"""

    command_id: str
    timestamp: datetime
    child_id: str
    changes: dict
    user_id: Optional[str] = None


@dataclass(frozen=True)
class ReportSafetyViolationCommand(Command):
    """Command to report safety violation"""

    command_id: str
    timestamp: datetime
    child_id: str
    violation_type: str
    details: str
    severity: str = "medium"
    user_id: Optional[str] = None


@dataclass(frozen=True)
class DeactivateChildCommand(Command):
    """Command to deactivate child account"""

    command_id: str
    timestamp: datetime
    child_id: str
    reason: str
    user_id: Optional[str] = None


class RegisterChildCommandHandler(CommandHandler):
    """Handler for child registration command"""

    def __init__(self):
        self.event_sourcing_service = get_event_sourcing_service()

    async def validate(self, command: RegisterChildCommand) -> bool:
        """Validate child registration command"""

        # Basic validation
        if not command.name or len(command.name.strip()) < 2:
            logger.error(f"Invalid child name: {command.name}")
            return False

        if command.age < 3 or command.age > 12:
            logger.error(f"Invalid child age: {command.age}")
            return False

        if not command.udid or len(command.udid) < 10:
            logger.error(f"Invalid UDID: {command.udid}")
            return False

        return True

    async def handle(self, command: RegisterChildCommand) -> CommandResult:
        """Handle child registration"""

        try:
            # Create child aggregate
            child = ChildAggregateExample(
                id=ChildId(str(uuid4())),
                parent_id=ParentId(command.parent_id),
                device_id=DeviceId(command.device_id),
                name=command.name,
                age=command.age,
                udid=command.udid,
            )

            # Register child (generates domain events)
            child.register_child()

            # Save through event sourcing
            await self.event_sourcing_service.save_aggregate(child)

            logger.info(f"Child registered successfully: {child.name}")

            return CommandResult(
                success=True,
                message=f"Child {command.name} registered successfully",
                data={
                    "child_id": str(
                        child.id),
                    "name": child.name,
                    "age": child.age},
            )

        except Exception as e:
            logger.error(f"Failed to register child: {e}")
            return CommandResult(
                success=False, message=f"Child registration failed: {str(e)}"
            )


class UpdateChildProfileCommandHandler(CommandHandler):
    """Handler for child profile update command"""

    def __init__(self):
        self.event_sourcing_service = get_event_sourcing_service()

    async def validate(self, command: UpdateChildProfileCommand) -> bool:
        """Validate profile update command"""

        if not command.child_id:
            logger.error("Child ID is required")
            return False

        if not command.changes:
            logger.error("No changes provided")
            return False

        # Validate specific changes
        if "age" in command.changes:
            age = command.changes["age"]
            if not isinstance(age, int) or age < 3 or age > 12:
                logger.error(f"Invalid age in changes: {age}")
                return False

        return True

    async def handle(
            self,
            command: UpdateChildProfileCommand) -> CommandResult:
        """Handle profile update"""

        try:
            # Load existing child
            child = await self.event_sourcing_service.load_aggregate(
                ChildAggregateExample, command.child_id
            )

            if not child:
                return CommandResult(success=False, message="Child not found")

            # Update profile (generates domain events)
            child.update_profile(command.changes)

            # Save changes
            await self.event_sourcing_service.save_aggregate(child)

            logger.info(f"Child profile updated: {command.child_id}")

            return CommandResult(
                success=True,
                message="Child profile updated successfully",
                data={
                    "child_id": command.child_id,
                    "changes": command.changes},
            )

        except Exception as e:
            logger.error(f"Failed to update child profile: {e}")
            return CommandResult(
                success=False, message=f"Profile update failed: {str(e)}"
            )


class ReportSafetyViolationCommandHandler(CommandHandler):
    """Handler for safety violation reporting"""

    def __init__(self):
        self.event_sourcing_service = get_event_sourcing_service()

    async def validate(self, command: ReportSafetyViolationCommand) -> bool:
        """Validate safety violation command"""

        if not command.child_id:
            logger.error("Child ID is required")
            return False

        if not command.violation_type:
            logger.error("Violation type is required")
            return False

        valid_severities = ["low", "medium", "high", "critical"]
        if command.severity not in valid_severities:
            logger.error(f"Invalid severity: {command.severity}")
            return False

        return True

    async def handle(
            self,
            command: ReportSafetyViolationCommand) -> CommandResult:
        """Handle safety violation reporting"""

        try:
            # Load child
            child = await self.event_sourcing_service.load_aggregate(
                ChildAggregateExample, command.child_id
            )

            if not child:
                return CommandResult(success=False, message="Child not found")

            # Report violation (generates domain events)
            child.detect_safety_violation(
                command.violation_type, command.details)

            # Save violation
            await self.event_sourcing_service.save_aggregate(child)

            logger.warning(
                f"Safety violation reported for child {command.child_id}: {command.violation_type}"
            )

            return CommandResult(
                success=True,
                message="Safety violation reported successfully",
                data={
                    "child_id": command.child_id,
                    "violation_type": command.violation_type,
                    "severity": command.severity,
                },
            )

        except Exception as e:
            logger.error(f"Failed to report safety violation: {e}")
            return CommandResult(
                success=False,
                message=f"Safety violation reporting failed: {str(e)}")


def register_child_command_handlers() -> Any:
    """Register all child command handlers"""

    command_bus = get_command_bus()

    # Register handlers
    command_bus.register_handler(
        RegisterChildCommand,
        RegisterChildCommandHandler())

    command_bus.register_handler(
        UpdateChildProfileCommand, UpdateChildProfileCommandHandler()
    )

    command_bus.register_handler(
        ReportSafetyViolationCommand, ReportSafetyViolationCommandHandler()
    )

    logger.info("Child command handlers registered successfully")
