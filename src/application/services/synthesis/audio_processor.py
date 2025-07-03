#!/usr/bin/env python3
"""
🎚️ Audio Processing Service
خدمة معالجة الصوت والتعديلات الصوتية
"""

import io
import logging
from typing import Optional

import numpy as np

# Audio processing libraries
try:
    from pydub import AudioSegment
    from pydub.effects import normalize
except ImportError:
    AudioSegment = None
    normalize = None

try:
    import soundfile as sf
except ImportError:
    sf = None

from .models import VoiceCharacter, SynthesisConfig

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for audio processing and voice adjustments"""
    
    def __init__(self, config: SynthesisConfig):
        """Initialize the audio processor"""
        self.config = config
        
        # Check audio library availability
        self.pydub_available = AudioSegment is not None
        self.soundfile_available = sf is not None
        
        if not self.pydub_available:
            logger.warning("PyDub not available - limited audio processing capabilities")
        if not self.soundfile_available:
            logger.warning("SoundFile not available - limited audio format support")
        
        logger.debug("Audio processor initialized")
    
    async def apply_voice_adjustments(
        self,
        audio_data: bytes,
        character: VoiceCharacter
    ) -> bytes:
        """Apply voice adjustments (pitch, speed, volume)"""
        try:
            if not self.pydub_available:
                logger.warning("PyDub not available - returning original audio")
                return audio_data
            
            if not audio_data:
                logger.warning("No audio data provided")
                return audio_data
            
            # Convert to audio segment for processing
            audio_segment = self._bytes_to_audio_segment(audio_data)
            
            # Apply volume adjustment
            if character.volume_adjustment != 1.0:
                audio_segment = self._apply_volume_adjustment(audio_segment, character.volume_adjustment)
            
            # Apply speed adjustment (affects pitch too)
            if character.speed_adjustment != 1.0:
                audio_segment = self._apply_speed_adjustment(audio_segment, character.speed_adjustment)
            
            # Apply normalization
            audio_segment = self._apply_normalization(audio_segment)
            
            # Convert back to bytes
            processed_audio = self._audio_segment_to_bytes(audio_segment)
            
            logger.debug(f"Applied voice adjustments for character: {character.id}")
            return processed_audio
            
        except Exception as e:
            logger.error(f"❌ Voice adjustment failed: {e}")
            return audio_data
    
    def _bytes_to_audio_segment(self, audio_data: bytes) -> AudioSegment:
        """Convert raw bytes to AudioSegment"""
        try:
            return AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=self.config.bit_depth // 8,
                frame_rate=self.config.sample_rate,
                channels=self.config.channels
            )
        except Exception as e:
            logger.error(f"Failed to create AudioSegment: {e}")
            # Return empty audio segment as fallback
            return AudioSegment.silent(duration=1000)
    
    def _audio_segment_to_bytes(self, audio_segment: AudioSegment) -> bytes:
        """Convert AudioSegment back to bytes"""
        try:
            buffer = io.BytesIO()
            audio_segment.export(buffer, format="raw")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to export AudioSegment: {e}")
            return b""
    
    def _apply_volume_adjustment(self, audio_segment: AudioSegment, volume_multiplier: float) -> AudioSegment:
        """Apply volume adjustment to audio"""
        try:
            # Convert multiplier to dB
            volume_change_db = 20 * np.log10(max(0.01, volume_multiplier))  # Avoid log(0)
            
            # Clamp to reasonable range
            volume_change_db = max(-40, min(40, volume_change_db))
            
            adjusted_audio = audio_segment + volume_change_db
            logger.debug(f"Applied volume adjustment: {volume_change_db:.2f}dB")
            return adjusted_audio
            
        except Exception as e:
            logger.error(f"Volume adjustment failed: {e}")
            return audio_segment
    
    def _apply_speed_adjustment(self, audio_segment: AudioSegment, speed_multiplier: float) -> AudioSegment:
        """Apply speed adjustment to audio (affects pitch)"""
        try:
            if speed_multiplier == 1.0:
                return audio_segment
            
            # Clamp speed to reasonable range
            speed_multiplier = max(0.5, min(2.0, speed_multiplier))
            
            # Change frame rate to adjust speed (this affects pitch too)
            new_sample_rate = int(audio_segment.frame_rate * speed_multiplier)
            
            # Create new audio segment with adjusted frame rate
            adjusted_audio = audio_segment._spawn(
                audio_segment.raw_data,
                overrides={"frame_rate": new_sample_rate}
            )
            
            # Set back to original frame rate to maintain compatibility
            adjusted_audio = adjusted_audio.set_frame_rate(self.config.sample_rate)
            
            logger.debug(f"Applied speed adjustment: {speed_multiplier:.2f}x")
            return adjusted_audio
            
        except Exception as e:
            logger.error(f"Speed adjustment failed: {e}")
            return audio_segment
    
    def _apply_normalization(self, audio_segment: AudioSegment) -> AudioSegment:
        """Apply audio normalization"""
        try:
            if normalize is None:
                logger.debug("Normalization not available")
                return audio_segment
            
            normalized_audio = normalize(audio_segment)
            logger.debug("Applied audio normalization")
            return normalized_audio
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return audio_segment
    
    async def convert_audio_format(
        self,
        audio_data: bytes,
        target_format: str = "wav",
        target_sample_rate: Optional[int] = None
    ) -> bytes:
        """Convert audio to different format or sample rate"""
        try:
            if not self.pydub_available:
                logger.warning("PyDub not available - cannot convert audio format")
                return audio_data
            
            # Convert to AudioSegment
            audio_segment = self._bytes_to_audio_segment(audio_data)
            
            # Adjust sample rate if requested
            if target_sample_rate and target_sample_rate != audio_segment.frame_rate:
                audio_segment = audio_segment.set_frame_rate(target_sample_rate)
                logger.debug(f"Converted sample rate to: {target_sample_rate}Hz")
            
            # Export to target format
            buffer = io.BytesIO()
            audio_segment.export(buffer, format=target_format)
            
            logger.debug(f"Converted audio to format: {target_format}")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Audio format conversion failed: {e}")
            return audio_data
    
    async def apply_audio_effects(
        self,
        audio_data: bytes,
        effects: dict
    ) -> bytes:
        """Apply various audio effects based on configuration"""
        try:
            if not self.pydub_available:
                logger.warning("PyDub not available - cannot apply audio effects")
                return audio_data
            
            audio_segment = self._bytes_to_audio_segment(audio_data)
            
            # Apply fade in/out if specified
            if effects.get("fade_in_ms", 0) > 0:
                audio_segment = audio_segment.fade_in(effects["fade_in_ms"])
                logger.debug(f"Applied fade in: {effects['fade_in_ms']}ms")
            
            if effects.get("fade_out_ms", 0) > 0:
                audio_segment = audio_segment.fade_out(effects["fade_out_ms"])
                logger.debug(f"Applied fade out: {effects['fade_out_ms']}ms")
            
            # Apply high/low pass filters if specified
            if effects.get("high_pass_freq"):
                audio_segment = audio_segment.high_pass_filter(effects["high_pass_freq"])
                logger.debug(f"Applied high pass filter: {effects['high_pass_freq']}Hz")
            
            if effects.get("low_pass_freq"):
                audio_segment = audio_segment.low_pass_filter(effects["low_pass_freq"])
                logger.debug(f"Applied low pass filter: {effects['low_pass_freq']}Hz")
            
            return self._audio_segment_to_bytes(audio_segment)
            
        except Exception as e:
            logger.error(f"Audio effects application failed: {e}")
            return audio_data
    
    async def generate_silence(self, duration_ms: int) -> bytes:
        """Generate silent audio of specified duration"""
        try:
            if not self.pydub_available:
                # Generate silence using numpy
                duration_seconds = duration_ms / 1000.0
                samples = int(duration_seconds * self.config.sample_rate)
                silence = np.zeros(samples, dtype=np.int16)
                return silence.tobytes()
            
            # Use PyDub for better compatibility
            silence_segment = AudioSegment.silent(
                duration=duration_ms,
                frame_rate=self.config.sample_rate
            )
            
            return self._audio_segment_to_bytes(silence_segment)
            
        except Exception as e:
            logger.error(f"Failed to generate silence: {e}")
            return b""
    
    def get_audio_info(self, audio_data: bytes) -> dict:
        """Get information about audio data"""
        try:
            if not self.pydub_available:
                return {
                    "size_bytes": len(audio_data),
                    "estimated_duration_seconds": len(audio_data) / (self.config.sample_rate * 2),  # Assuming 16-bit
                    "sample_rate": self.config.sample_rate,
                    "channels": self.config.channels,
                    "bit_depth": self.config.bit_depth
                }
            
            audio_segment = self._bytes_to_audio_segment(audio_data)
            
            return {
                "size_bytes": len(audio_data),
                "duration_seconds": len(audio_segment) / 1000.0,
                "duration_ms": len(audio_segment),
                "sample_rate": audio_segment.frame_rate,
                "channels": audio_segment.channels,
                "bit_depth": audio_segment.sample_width * 8,
                "max_possible_amplitude": audio_segment.max_possible_amplitude,
                "frame_count": audio_segment.frame_count()
            }
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {"error": str(e), "size_bytes": len(audio_data)}
    
    def validate_audio_data(self, audio_data: bytes) -> bool:
        """Validate audio data integrity"""
        try:
            if not audio_data:
                return False
            
            # Basic size validation
            min_size = self.config.sample_rate * (self.config.bit_depth // 8) * self.config.channels * 0.1  # 0.1 second minimum
            if len(audio_data) < min_size:
                logger.warning(f"Audio data too small: {len(audio_data)} bytes")
                return False
            
            # Try to create AudioSegment to validate format
            if self.pydub_available:
                try:
                    self._bytes_to_audio_segment(audio_data)
                    return True
                except Exception:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False 