"""
Security audit logging component.
"""
import asyncio
import contextvars
import logging
from typing import List

import structlog

from .models import SecurityEvent, SecurityEventType, ThreatLevel

logger = structlog.get_logger()
correlation_id_var = contextvars.ContextVar("correlation_id", default=None)


class SecurityAuditLogger:
    """
    Handles the logging of all security-related events in a structured
    and reliable manner, with buffering for performance.
    """

    def __init__(self, storage_backend=None, buffer_size: int = 100, flush_interval: int = 30):
        self.storage_backend = storage_backend
        self._event_buffer: List[SecurityEvent] = []
        self._buffer_size = buffer_size
        self._flush_interval = flush_interval
        self._buffer_lock = asyncio.Lock()
        self._flush_task = asyncio.create_task(self._flush_loop())

    async def log_event(self, event: SecurityEvent):
        """
        Logs a security event, adding it to a buffer for asynchronous flushing.
        Critical events are logged immediately.
        """
        if not event.correlation_id:
            event.correlation_id = correlation_id_var.get()

        async with self._buffer_lock:
            self._event_buffer.append(event)
            if len(self._event_buffer) >= self._buffer_size:
                await self._flush_events()

        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._log_to_structlog(event, is_critical=True)

    async def _flush_events(self):
        """Flushes the event buffer to the configured storage backend or logs."""
        if not self._event_buffer:
            return

        events_to_flush, self._event_buffer = self._event_buffer, []

        try:
            if self.storage_backend:
                await self.storage_backend.store_events(events_to_flush)
            else:
                for event in events_to_flush:
                    self._log_to_structlog(event)
        except Exception as e:
            logger.error("Failed to flush security audit events",
                         error=str(e), exc_info=True)
            # Re-queue failed events for the next attempt (simple retry)
            async with self._buffer_lock:
                self._event_buffer = events_to_flush + self._event_buffer

    def _log_to_structlog(self, event: SecurityEvent, is_critical: bool = False):
        """Logs a single event using the structured logger."""
        log_method = logger.warning if is_critical else logger.info
        log_method(
            "SecurityAuditEvent",
            event_type=event.event_type.value,
            threat_level=event.threat_level.value,
            user_id=event.user_id,
            ip_address=event.ip_address,
            resource=event.resource,
            result=event.result,
            correlation_id=event.correlation_id,
            details=event.details,
        )

    async def _flush_loop(self):
        """A background task that periodically flushes the event buffer."""
        while True:
            await asyncio.sleep(self._flush_interval)
            async with self._buffer_lock:
                await self._flush_events()

    async def shutdown(self):
        """Flushes any remaining events and cancels the background task."""
        self._flush_task.cancel()
        async with self._buffer_lock:
            await self._flush_events()
        logger.info("SecurityAuditLogger has been shut down.")
