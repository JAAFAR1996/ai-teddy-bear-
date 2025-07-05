from typing import Any

"""
Enterprise Message Sender for AI Teddy Bear
Advanced message handling with retry logic, compression, and chunking
"""

import asyncio
import base64
import gzip
import json
import platform
import uuid
from datetime import datetime
from typing import Any

import structlog
from PySide6.QtCore import QObject, QTimer, Signal

logger = structlog.get_logger()


class EnterpriseMessageSender(QObject):
    """Advanced message sender with retry logic and metadata support"""

    message_sent = Signal(str)  # message_id
    message_delivered = Signal(str, dict)  # message_id, response
    message_failed = Signal(str, str)  # message_id, error
    sending_progress = Signal(str, int)  # message_id, progress_percent
    connection_restored = Signal()

    def __init__(self, websocket_client, parent=None):
        super().__init__(parent)
        self.websocket_client = websocket_client
        self.pending_messages = {}  # message_id -> message_data
        self.retry_queue = []  # Failed messages for retry
        self.max_retry_attempts = 3
        self.retry_delay = 2.0  # seconds
        self.chunk_size = 32768  # 32KB chunks
        self.compression_threshold = 1024  # 1KB

        self._setup_retry_system()

    def _setup_retry_system(self) -> Any:
        """Setup automatic retry system"""
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self._process_retry_queue)
        self.retry_timer.start(5000)  # Check every 5 seconds

        # Monitor connection status
        self.websocket_client.connected.connect(self._on_connection_restored)
        self.websocket_client.message_received.connect(
            self._handle_server_response)

    async def send_audio_message(
            self,
            audio_file: bytes,
            metadata: dict) -> str:
        """Send audio message with comprehensive metadata"""
        message_id = self._generate_message_id()

        # Prepare message data
        message_data = {
            "id": message_id,
            "type": "audio_message",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                **metadata,
                "device_info": self._get_device_info(),
                "session_context": self._get_session_context(),
            },
            "audio_data": base64.b64encode(audio_file).decode("utf-8"),
            "audio_size": len(audio_file),
            "retry_attempts": 0,
        }

        return await self._send_message_with_retry(message_id, message_data)

    async def send_text_message(self, text: str, metadata: dict) -> str:
        """Send text message with metadata"""
        message_id = self._generate_message_id()

        message_data = {
            "id": message_id,
            "type": "text_message",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                **metadata,
                "device_info": self._get_device_info(),
                "session_context": self._get_session_context(),
            },
            "text": text,
            "retry_attempts": 0,
        }

        return await self._send_message_with_retry(message_id, message_data)

    async def _send_message_with_retry(
        self, message_id: str, message_data: dict
    ) -> str:
        """Send message with automatic retry logic"""
        try:
            # Store message for potential retry
            self.pending_messages[message_id] = message_data

            # Check if message should be compressed
            if self._should_compress_message(message_data):
                message_data = await self._compress_message(message_data)

            # Check if message should be chunked
            if self._should_chunk_message(message_data):
                await self._send_chunked_message(message_id, message_data)
            else:
                # Send as single message
                self.websocket_client.send_message(message_data)
                self.sending_progress.emit(message_id, 100)

            self.message_sent.emit(message_id)
            logger.info("Message sent successfully", message_id=message_id)

            return message_id

        except Exception as e:
            logger.error(
                "Failed to send message",
                message_id=message_id,
                error=str(e))
            self._queue_for_retry(message_data)
            self.message_failed.emit(message_id, str(e))
            raise

    async def _send_chunked_message(self, message_id: str, message_data: dict):
        """Send large message in chunks"""
        # Convert message to JSON string
        json_str = json.dumps(message_data)
        total_size = len(json_str.encode("utf-8"))
        chunks = []

        # Split into chunks
        for i in range(0, len(json_str), self.chunk_size):
            chunk = json_str[i: i + self.chunk_size]
            chunks.append(chunk)

        # Send chunk metadata first
        chunk_metadata = {
            "type": "chunk_start",
            "message_id": message_id,
            "total_chunks": len(chunks),
            "total_size": total_size,
        }

        self.websocket_client.send_message(chunk_metadata)

        # Send each chunk
        for idx, chunk in enumerate(chunks):
            chunk_message = {
                "type": "chunk_data",
                "message_id": message_id,
                "chunk_index": idx,
                "chunk_data": chunk,
            }

            self.websocket_client.send_message(chunk_message)

            # Update progress
            progress = int((idx + 1) / len(chunks) * 100)
            self.sending_progress.emit(message_id, progress)

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)

        # Send completion signal
        completion_message = {
            "type": "chunk_complete",
            "message_id": message_id}

        self.websocket_client.send_message(completion_message)

    def _should_compress_message(self, message_data: dict) -> bool:
        """Check if message should be compressed"""
        message_size = len(json.dumps(message_data).encode("utf-8"))
        return message_size > self.compression_threshold

    def _should_chunk_message(self, message_data: dict) -> bool:
        """Check if message should be chunked"""
        message_size = len(json.dumps(message_data).encode("utf-8"))
        return message_size > self.chunk_size

    async def _compress_message(self, message_data: dict) -> dict:
        """Compress large message data"""
        try:
            # Compress audio data if present
            if "audio_data" in message_data:
                audio_data = message_data["audio_data"]
                compressed_data = gzip.compress(audio_data.encode("utf-8"))
                message_data["audio_data"] = base64.b64encode(
                    compressed_data).decode("utf-8")
                message_data["compressed"] = True
                message_data["compression_ratio"] = len(compressed_data) / len(
                    audio_data.encode("utf-8")
                )

                logger.debug(
                    "Message compressed",
                    compression_ratio=message_data["compression_ratio"],
                )

            return message_data

        except Exception as e:
            logger.warning(
                "Failed to compress message, sending uncompressed",
                error=str(e))
            return message_data

    def _queue_for_retry(self, message_data: dict) -> None:
        """Queue message for retry"""
        message_data["retry_attempts"] = message_data.get(
            "retry_attempts", 0) + 1

        if message_data["retry_attempts"] <= self.max_retry_attempts:
            message_data["retry_timestamp"] = datetime.now().isoformat()
            self.retry_queue.append(message_data)

            logger.info(
                "Message queued for retry",
                message_id=message_data["id"],
                attempt=message_data["retry_attempts"],
            )
        else:
            logger.error(
                "Max retry attempts reached",
                message_id=message_data["id"])

            # Remove from pending messages
            self.pending_messages.pop(message_data["id"], None)
            self.message_failed.emit(
                message_data["id"],
                "Max retry attempts reached")

    def _process_retry_queue(self) -> Any:
        """Process queued retry messages"""
        if not self.retry_queue or not self.websocket_client.is_connected:
            return

        # Process up to 3 messages per cycle to avoid overwhelming
        for _ in range(min(3, len(self.retry_queue))):
            if not self.retry_queue:
                break

            message_data = self.retry_queue.pop(0)

            try:
                asyncio.create_task(
                    self._send_message_with_retry(
                        message_data["id"], message_data))
            except Exception as e:
                logger.error(
                    "Retry failed", message_id=message_data["id"], error=str(e)
                )

    def _on_connection_restored(self) -> Any:
        """Handle connection restoration"""
        logger.info(
            "Connection restored, processing retry queue",
            pending_count=len(self.retry_queue),
        )
        self.connection_restored.emit()

        # Process retry queue immediately
        if self.retry_queue:
            self._process_retry_queue()

    def _handle_server_response(self, response: dict) -> None:
        """Handle server response for sent messages"""
        if response.get("type") == "message_ack":
            message_id = response.get("message_id")
            if message_id and message_id in self.pending_messages:
                # Remove from pending
                del self.pending_messages[message_id]
                self.message_delivered.emit(message_id, response)

                logger.debug("Message acknowledged", message_id=message_id)

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"msg_{timestamp}_{unique_id}"

    def _get_device_info(self) -> dict:
        """Get device information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    def _get_session_context(self) -> dict:
        """Get current session context"""
        return {
            "session_start": datetime.now().isoformat(),
            "ui_version": "2025.1.0",
            "feature_flags": ["enterprise_mode", "advanced_audio"],
        }

    def get_pending_messages_count(self) -> int:
        """Get count of pending messages"""
        return len(self.pending_messages)

    def clear_pending_messages(self) -> Any:
        """Clear all pending messages"""
        cleared_count = len(self.pending_messages)
        self.pending_messages.clear()
        self.retry_queue.clear()

        logger.info("Cleared pending messages", count=cleared_count)
