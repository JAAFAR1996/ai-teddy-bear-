#!/usr/bin/env python3
"""
🎵 Streaming Audio Buffer Service
خدمة إدارة مخزن الصوت المتدفق
"""

import asyncio
import logging

from .models import SynthesisConfig

logger = logging.getLogger(__name__)


class StreamingAudioBuffer:
    """Buffer for streaming audio output with async thread-safe operations"""
    
    def __init__(self, config: SynthesisConfig):
        """Initialize the audio buffer with configuration"""
        self.config = config
        self.buffer = bytearray()
        self.lock = asyncio.Lock()
        self.total_bytes = 0
        self._closed = False
        
        logger.debug(f"Audio buffer initialized with chunk_size={config.chunk_size}")
        
    async def write(self, audio_chunk: bytes) -> None:
        """Write audio chunk to buffer"""
        if self._closed:
            logger.warning("Attempting to write to closed buffer")
            return
            
        async with self.lock:
            self.buffer.extend(audio_chunk)
            self.total_bytes += len(audio_chunk)
            logger.debug(f"Written {len(audio_chunk)} bytes, total: {self.total_bytes}")
    
    async def read(self, size: int = None) -> bytes:
        """Read audio chunk from buffer"""
        async with self.lock:
            if size is None:
                size = self.config.chunk_size
            
            if len(self.buffer) >= size:
                chunk = bytes(self.buffer[:size])
                self.buffer = self.buffer[size:]
                logger.debug(f"Read {len(chunk)} bytes from buffer")
                return chunk
            
            return bytes()
    
    async def read_all(self) -> bytes:
        """Read all audio from buffer"""
        async with self.lock:
            audio = bytes(self.buffer)
            self.buffer.clear()
            logger.debug(f"Read all {len(audio)} bytes from buffer")
            return audio
    
    async def peek(self, size: int = None) -> bytes:
        """Peek at buffer contents without removing them"""
        async with self.lock:
            if size is None:
                size = self.config.chunk_size
            
            return bytes(self.buffer[:size])
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.buffer) == 0
    
    def is_ready(self, size: int = None) -> bool:
        """Check if buffer has enough data for reading"""
        if size is None:
            size = self.config.chunk_size
        return len(self.buffer) >= size
    
    @property
    def size(self) -> int:
        """Current buffer size in bytes"""
        return len(self.buffer)
    
    @property
    def total_written(self) -> int:
        """Total bytes written to buffer"""
        return self.total_bytes
    
    async def clear(self) -> None:
        """Clear the buffer"""
        async with self.lock:
            self.buffer.clear()
            logger.debug("Buffer cleared")
    
    async def close(self) -> None:
        """Close the buffer and prevent further writes"""
        async with self.lock:
            self._closed = True
            logger.debug("Buffer closed")
    
    def is_closed(self) -> bool:
        """Check if buffer is closed"""
        return self._closed
    
    async def get_stats(self) -> dict:
        """Get buffer statistics"""
        async with self.lock:
            return {
                "current_size": len(self.buffer),
                "total_written": self.total_bytes,
                "is_empty": len(self.buffer) == 0,
                "is_closed": self._closed,
                "chunk_size": self.config.chunk_size,
                "buffer_utilization": len(self.buffer) / self.config.buffer_size if self.config.buffer_size > 0 else 0
            } 