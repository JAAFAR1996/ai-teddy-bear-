import asyncio
from collections import deque
from typing import Optional


class AudioBufferService:
    """
    Dedicated service for audio buffering operations.
    EXTRACTED CLASS to resolve Low Cohesion - Single Responsibility: Audio Buffer Management
    """

    def __init__(self, max_size: int = 8192, chunk_size: int = 1024):
        self.buffer = deque(maxlen=max_size)
        self._lock = asyncio.Lock()
        self.chunk_size = chunk_size
        self.total_bytes = 0
        self.dropped_bytes = 0

    async def write(self, data: bytes) -> None:
        """Write audio data to buffer"""
        async with self._lock:
            if len(self.buffer) == self.buffer.maxlen:
                dropped = self.buffer.popleft()
                self.dropped_bytes += len(dropped)
            self.buffer.append(data)
            self.total_bytes += len(data)

    async def read(self, size: Optional[int] = None) -> bytes:
        """Read audio data from buffer"""
        async with self._lock:
            if not self.buffer:
                return b""

            size = size or self.chunk_size
            result = b""

            while self.buffer and len(result) < size:
                chunk = self.buffer.popleft()
                if len(result) + len(chunk) <= size:
                    result += chunk
                else:
                    needed = size - len(result)
                    result += chunk[:needed]
                    self.buffer.appendleft(chunk[needed:])
                    break

            return result

    async def clear(self) -> None:
        """Clear the buffer"""
        async with self._lock:
            self.buffer.clear()

    @property
    async def size(self) -> int:
        """Get current buffer size in bytes"""
        async with self._lock:
            return sum(len(chunk) for chunk in self.buffer)

    def get_stats(self) -> dict:
        """Get buffer statistics"""
        return {
            "total_bytes_processed": self.total_bytes,
            "dropped_bytes": self.dropped_bytes,
            "current_buffer_length": len(self.buffer),
            "max_buffer_size": self.buffer.maxlen,
            "chunk_size": self.chunk_size
        } 