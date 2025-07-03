"""
🔊 Audio Processor
High cohesion component for audio processing and buffer management
"""

import asyncio
import logging
import time
from collections import deque
from typing import Optional, Dict, Any

from .models import AudioProcessingRequest, ProcessingResult, AudioBuffer as AudioBufferConfig


class AudioBuffer:
    """Thread-safe audio buffer for real-time streaming"""

    def __init__(self, config: AudioBufferConfig):
        """Initialize audio buffer with configuration"""
        self.config = config
        self.buffer = deque(maxlen=config.max_size)
        self._lock = asyncio.Lock()
        self.total_bytes = 0
        self.dropped_bytes = 0
        self.write_count = 0
        self.read_count = 0

    async def write(self, data: bytes) -> None:
        """Write audio data to buffer"""
        async with self._lock:
            if len(self.buffer) == self.buffer.maxlen:
                dropped = self.buffer.popleft()
                self.dropped_bytes += len(dropped)
            
            self.buffer.append(data)
            self.total_bytes += len(data)
            self.write_count += 1

    async def read(self, size: Optional[int] = None) -> bytes:
        """Read audio data from buffer"""
        async with self._lock:
            if not self.buffer:
                return b""

            size = size or self.config.chunk_size
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

            self.read_count += 1
            return result

    async def clear(self) -> None:
        """Clear the buffer"""
        async with self._lock:
            self.buffer.clear()

    async def get_size(self) -> int:
        """Get current buffer size in bytes"""
        async with self._lock:
            return sum(len(chunk) for chunk in self.buffer)

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics"""
        return {
            "total_bytes": self.total_bytes,
            "dropped_bytes": self.dropped_bytes,
            "write_count": self.write_count,
            "read_count": self.read_count,
            "current_chunks": len(self.buffer),
            "max_chunks": self.buffer.maxlen,
            "chunk_size": self.config.chunk_size
        }


class AudioProcessor:
    """
    Dedicated service for audio processing and buffer management.
    High cohesion: all methods work with audio data and processing.
    """
    
    def __init__(self, input_buffer_config: AudioBufferConfig, output_buffer_config: AudioBufferConfig):
        """Initialize audio processor with buffer configurations"""
        self.logger = logging.getLogger(__name__)
        
        # Audio buffers
        self.input_buffer = AudioBuffer(input_buffer_config)
        self.output_buffer = AudioBuffer(output_buffer_config)
        
        # Processing state
        self.is_processing = False
        self.processing_start_time = None
        
        # Statistics
        self.processed_audio_count = 0
        self.total_processing_time = 0.0
        self.processing_errors = 0
    
    async def process_audio_input(self, request: AudioProcessingRequest) -> ProcessingResult:
        """
        Process incoming audio data with improved error handling.
        EXTRACT FUNCTION applied to eliminate bumpy road pattern.
        """
        start_time = time.time()
        
        try:
            # Validate input
            validation_result = self._validate_audio_request(request)
            if not validation_result.success:
                return validation_result
            
            # Add to input buffer
            await self._add_to_input_buffer(request.audio_data)
            
            # Check if buffer has enough data for processing
            buffer_result = await self._check_buffer_ready_for_processing()
            if not buffer_result.success:
                return buffer_result
            
            # Process the audio chunk
            processing_result = await self._process_audio_chunk(request)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, processing_result.success)
            
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Error processing audio input: {e}")
            self.processing_errors += 1
            return ProcessingResult.error_result(f"Audio processing failed: {str(e)}")
    
    def _validate_audio_request(self, request: AudioProcessingRequest) -> ProcessingResult:
        """
        Validate audio processing request.
        Extracted from process_audio_input to eliminate bump 1.
        """
        if not request.audio_data:
            return ProcessingResult.error_result("Audio data cannot be empty")
        
        if len(request.audio_data) > 10 * 1024 * 1024:  # 10MB limit
            return ProcessingResult.error_result("Audio data too large (max 10MB)")
        
        if request.sample_rate <= 0:
            return ProcessingResult.error_result("Invalid sample rate")
        
        return ProcessingResult.success_result({"validation": "passed"})
    
    async def _add_to_input_buffer(self, audio_data: bytes) -> None:
        """Add audio data to input buffer"""
        await self.input_buffer.write(audio_data)
        self.logger.debug(f"Added {len(audio_data)} bytes to input buffer")
    
    async def _check_buffer_ready_for_processing(self) -> ProcessingResult:
        """
        Check if buffer has enough data for processing.
        Extracted from process_audio_input to eliminate bump 2.
        """
        buffer_size = await self.input_buffer.get_size()
        chunk_size = self.input_buffer.config.chunk_size
        
        if buffer_size < chunk_size:
            return ProcessingResult.error_result(
                f"Buffer not ready: {buffer_size} < {chunk_size}",
                metadata={"buffer_size": buffer_size, "required_size": chunk_size}
            )
        
        return ProcessingResult.success_result({
            "buffer_ready": True,
            "buffer_size": buffer_size,
            "chunk_size": chunk_size
        })
    
    async def _process_audio_chunk(self, request: AudioProcessingRequest) -> ProcessingResult:
        """
        Process audio chunk from buffer.
        Extracted from process_audio_input to eliminate bump 3.
        """
        try:
            # Set processing state
            self.is_processing = True
            self.processing_start_time = time.time()
            
            # Read from buffer
            buffer_size = await self.input_buffer.get_size()
            audio_chunk = await self.input_buffer.read(buffer_size)
            
            if not audio_chunk:
                return ProcessingResult.error_result("No audio data available in buffer")
            
            # Process the chunk (placeholder for actual processing)
            processed_data = await self._apply_audio_processing(audio_chunk, request)
            
            # Add to output buffer if needed
            if processed_data:
                await self.output_buffer.write(processed_data)
            
            self.processed_audio_count += 1
            
            return ProcessingResult.success_result({
                "processed": True,
                "chunk_size": len(audio_chunk),
                "output_size": len(processed_data) if processed_data else 0
            })
            
        finally:
            self.is_processing = False
            self.processing_start_time = None
    
    async def _apply_audio_processing(self, audio_data: bytes, request: AudioProcessingRequest) -> Optional[bytes]:
        """
        Apply actual audio processing algorithms.
        Placeholder for specific audio processing logic.
        """
        # This is where you would apply:
        # - Noise reduction
        # - Audio normalization
        # - Format conversion
        # - Quality enhancement
        
        # For now, just return the original data
        return audio_data
    
    def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        self.total_processing_time += processing_time
        
        if not success:
            self.processing_errors += 1
        
        self.logger.debug(f"Audio processing completed in {processing_time:.3f}s")
    
    async def get_input_buffer_data(self, size: Optional[int] = None) -> bytes:
        """Get data from input buffer"""
        return await self.input_buffer.read(size)
    
    async def get_output_buffer_data(self, size: Optional[int] = None) -> bytes:
        """Get data from output buffer"""
        return await self.output_buffer.read(size)
    
    async def clear_buffers(self) -> ProcessingResult:
        """Clear all audio buffers"""
        try:
            await self.input_buffer.clear()
            await self.output_buffer.clear()
            
            self.logger.info("Audio buffers cleared")
            return ProcessingResult.success_result({"buffers_cleared": True})
            
        except Exception as e:
            self.logger.error(f"Error clearing buffers: {e}")
            return ProcessingResult.error_result(f"Failed to clear buffers: {str(e)}")
    
    async def get_buffer_status(self) -> Dict[str, Any]:
        """Get status of audio buffers"""
        return {
            "input_buffer": {
                "size": await self.input_buffer.get_size(),
                "stats": self.input_buffer.get_stats()
            },
            "output_buffer": {
                "size": await self.output_buffer.get_size(),
                "stats": self.output_buffer.get_stats()
            }
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get audio processing statistics"""
        avg_processing_time = (
            self.total_processing_time / self.processed_audio_count 
            if self.processed_audio_count > 0 else 0
        )
        
        return {
            "service_name": "AudioProcessor",
            "is_processing": self.is_processing,
            "processed_audio_count": self.processed_audio_count,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_processing_time,
            "processing_errors": self.processing_errors,
            "error_rate": (
                self.processing_errors / self.processed_audio_count 
                if self.processed_audio_count > 0 else 0
            ),
            "high_cohesion": True,
            "responsibility": "Audio processing and buffer management"
        }
    
    async def process_audio_stream(self, audio_stream) -> ProcessingResult:
        """Process continuous audio stream"""
        try:
            processed_chunks = 0
            
            async for chunk in audio_stream:
                request = AudioProcessingRequest(
                    audio_data=chunk,
                    session_id="stream",
                    format=AudioFormat.WAV
                )
                
                result = await self.process_audio_input(request)
                if result.success:
                    processed_chunks += 1
                else:
                    self.logger.warning(f"Failed to process stream chunk: {result.error_message}")
            
            return ProcessingResult.success_result({
                "stream_processed": True,
                "processed_chunks": processed_chunks
            })
            
        except Exception as e:
            self.logger.error(f"Error processing audio stream: {e}")
            return ProcessingResult.error_result(f"Stream processing failed: {str(e)}")
    
    async def optimize_buffers(self) -> ProcessingResult:
        """Optimize buffer performance based on usage patterns"""
        try:
            input_stats = self.input_buffer.get_stats()
            output_stats = self.output_buffer.get_stats()
            
            # Simple optimization logic
            optimizations = []
            
            # Check for excessive drops
            if input_stats["dropped_bytes"] > input_stats["total_bytes"] * 0.1:
                optimizations.append("Consider increasing input buffer size")
            
            if output_stats["dropped_bytes"] > output_stats["total_bytes"] * 0.1:
                optimizations.append("Consider increasing output buffer size")
            
            # Check for underutilization
            if input_stats["write_count"] > 0:
                avg_chunk_size = input_stats["total_bytes"] / input_stats["write_count"]
                if avg_chunk_size < self.input_buffer.config.chunk_size * 0.5:
                    optimizations.append("Consider reducing chunk size for better efficiency")
            
            return ProcessingResult.success_result({
                "optimizations": optimizations,
                "input_stats": input_stats,
                "output_stats": output_stats
            })
            
        except Exception as e:
            self.logger.error(f"Error optimizing buffers: {e}")
            return ProcessingResult.error_result(f"Buffer optimization failed: {str(e)}")

    async def process_audio(self, request: AudioProcessingRequest) -> ProcessingResult:
        return ProcessingResult.success_result({"processed": True}) 