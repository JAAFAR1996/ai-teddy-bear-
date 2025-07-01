#!/usr/bin/env python3
"""
🎭 Cleanup Orchestrator - DDD Implementation
Orchestrator pattern for coordinating complex cleanup operations
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import structlog
from dependency_injector.wiring import Provide, inject

logger = structlog.get_logger()


@dataclass
class CleanupContext:
    """Context object للحفاظ على state أثناء عملية التنظيف"""

    operation_id: str
    start_time: datetime
    parameters: Dict[str, Any]
    results: Dict[str, Any] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.results is None:
            self.results = {}
        if self.errors is None:
            self.errors = []


class CleanupOrchestrator:
    """
    🎭 Orchestrator pattern for cleanup domain

    Responsibilities:
    - Coordinate complex cleanup operations
    - Manage transaction boundaries
    - Handle cross-aggregate operations
    - Implement saga patterns for distributed operations
    """

    @inject
    def __init__(
        self,
        repository=Provide["cleanup_repository"],
        event_bus=Provide["event_bus"],
        metrics=Provide["metrics_collector"],
    ):
        self.repository = repository
        self.event_bus = event_bus
        self.metrics = metrics
        self._strategies = {}
        self._compensation_actions = []

    def register_strategy(self, operation_type: str, strategy: Any) -> None:
        """تسجيل استراتيجيات العمليات المختلفة"""
        self._strategies[operation_type] = strategy
        logger.info("Strategy registered", operation_type=operation_type)

    async def execute_operation(
        self, operation_type: str, parameters: Dict[str, Any]
    ) -> "CleanupResult":
        """
        تنفيذ عملية معقدة مع Saga pattern

        Args:
            operation_type: نوع العملية
            parameters: معاملات العملية

        Returns:
            نتيجة العملية
        """
        context = CleanupContext(
            operation_id=f"{operation_type}_{datetime.utcnow().timestamp()}",
            start_time=datetime.utcnow(),
            parameters=parameters,
        )

        logger.info(
            "Operation started",
            operation_id=context.operation_id,
            operation_type=operation_type,
        )

        try:
            # Pre-operation validation
            await self._validate_operation_conditions(context, operation_type)

            # Execute operation with compensation tracking
            async with self._create_operation_saga(context) as saga:
                results = await self._execute_operation_steps(
                    context, operation_type, saga
                )

            # Post-operation actions
            await self._finalize_operation(context, results)

            duration = (datetime.utcnow() - context.start_time).total_seconds()

            logger.info(
                "Operation completed successfully",
                operation_id=context.operation_id,
                duration_seconds=duration,
            )

            return CleanupResult(
                success=True,
                operation_id=context.operation_id,
                results=context.results,
                duration_seconds=duration,
            )

        except Exception as e:
            await self._handle_operation_failure(context, e)
            raise CleanupOperationError(
                f"Operation {operation_type} failed: {str(e)}"
            ) from e

    async def _validate_operation_conditions(
        self, context: CleanupContext, operation_type: str
    ):
        """التحقق من شروط العملية قبل التنفيذ"""
        if operation_type not in self._strategies:
            raise ValueError(f"Unknown operation type: {operation_type}")

        strategy = self._strategies[operation_type]
        await strategy.validate_preconditions(context.parameters)

        logger.debug(
            "Operation conditions validated", operation_id=context.operation_id
        )

    async def _execute_operation_steps(
        self, context: CleanupContext, operation_type: str, saga
    ) -> List:
        """تنفيذ خطوات العملية مع إمكانية الـ rollback"""
        strategy = self._strategies[operation_type]
        steps = await strategy.get_execution_steps(context.parameters)

        results = []
        for step in steps:
            try:
                step_result = await step.execute(context)
                saga.add_compensation(step.name, step_result.compensation_action)
                results.append(step_result)

                # Update context with step results
                context.results[step.name] = step_result.data

                logger.debug(
                    "Step completed",
                    operation_id=context.operation_id,
                    step_name=step.name,
                )

            except Exception as e:
                logger.error(
                    "Step failed, initiating rollback",
                    operation_id=context.operation_id,
                    step_name=step.name,
                    error=str(e),
                )
                await saga.compensate()  # Rollback all previous steps
                raise OperationStepFailure(f"Step {step.name} failed: {str(e)}") from e

        return results

    async def _finalize_operation(self, context: CleanupContext, results: List):
        """إنهاء العملية وتحديث المقاييس"""
        # Update metrics
        if self.metrics:
            self.metrics.increment_counter(
                "operation_completed",
                tags={"operation_type": context.operation_id.split("_")[0]},
            )

        # Publish domain events
        if self.event_bus:
            await self.event_bus.publish(
                {"operation_id": context.operation_id, "results": context.results}
            )

        logger.info("Operation finalized", operation_id=context.operation_id)

    async def _handle_operation_failure(
        self, context: CleanupContext, error: Exception
    ):
        """التعامل مع فشل العملية"""
        context.errors.append(str(error))

        # Update error metrics
        if self.metrics:
            self.metrics.increment_counter(
                "operation_failed",
                tags={"operation_type": context.operation_id.split("_")[0]},
            )

        logger.error(
            "Operation failed", operation_id=context.operation_id, error=str(error)
        )

    async def _create_operation_saga(self, context: CleanupContext):
        """إنشاء Saga pattern للعملية"""
        return OperationSaga(context.operation_id)


# Result classes
@dataclass
class CleanupResult:
    success: bool
    operation_id: str
    results: Dict[str, Any]
    duration_seconds: float
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


# Saga pattern implementation
class OperationSaga:
    """تنفيذ Saga pattern للعمليات الموزعة"""

    def __init__(self, operation_id: str):
        self.operation_id = operation_id
        self.compensation_actions = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.compensate()

    def add_compensation(self, step_name: str, compensation_action: Any) -> None:
        """إضافة إجراء تعويضي لخطوة"""
        self.compensation_actions.append((step_name, compensation_action))

    async def compensate(self):
        """تنفيذ الإجراءات التعويضية (rollback)"""
        logger.warning("Starting compensation", operation_id=self.operation_id)

        for step_name, action in reversed(self.compensation_actions):
            try:
                await action()
                logger.debug(
                    "Compensation completed",
                    operation_id=self.operation_id,
                    step=step_name,
                )
            except Exception as e:
                logger.error(
                    "Compensation failed",
                    operation_id=self.operation_id,
                    step=step_name,
                    error=str(e),
                )


# Custom exceptions
class CleanupOperationError(Exception):
    """خطأ في عملية cleanup"""

    pass


class OperationStepFailure(Exception):
    """خطأ في خطوة من خطوات العملية"""

    pass
