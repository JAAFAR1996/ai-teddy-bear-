from typing import Any, Dict, List, Optional

"""Enhanced Audio Processing Module for AI Teddy Bear Project.

This module provides comprehensive audio signal processing capabilities including:
- Real-time audio enhancement and filtering
- Advanced noise reduction
- Voice activity detection (VAD)
- Audio segmentation and chunking for streaming
- Audio format conversion
- Real-time audio analysis and metrics
"""

import asyncio
import io
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

import librosa
import numpy as np
import soundfile as sf
import webrtcvad
from scipy import signal
from scipy.fft import rfft, rfftfreq

# Configure logging
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    RAW = "raw"


class ProcessingMode(Enum):
    """Audio processing modes."""

    REALTIME = "realtime"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class AudioConfig:
    """Audio processing configuration."""

    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    frame_duration_ms: int = 20
    buffer_size: int = 1024
    noise_reduction_level: float = 0.7
    vad_aggressiveness: int = 2  # 0-3, higher is more aggressive
    normalize_audio: bool = True
    remove_silence: bool = True
    enhance_voice: bool = True


@dataclass
class AudioMetrics:
    """Audio quality metrics."""

    rms: float
    peak: float
    snr: float  # Signal-to-noise ratio
    silence_ratio: float
    clipping_ratio: float
    frequency_centroid: float
    zero_crossing_rate: float
    duration: float


class AudioProcessor:
    """Advanced audio signal processing with real-time capabilities."""

    def __init__(self, config: Optional[AudioConfig] = None):
        """Initialize audio processor with configuration."""
        self.config = config or AudioConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize components
        self._setup_filters()
        self._setup_vad()
        self._setup_buffers()

        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.logger.info("Audio processor initialized with config: %s", self.config)

    def _setup_filters(self) -> Any:
        """Set up audio filters for various processing stages."""
        fs = self.config.sample_rate

        # High-pass filter for DC removal
        self.dc_filter = signal.butter(4, 80, btype="highpass", fs=fs, output="sos")

        # Bandpass filter for voice enhancement (300-3400 Hz)
        self.voice_filter = signal.butter(
            4, [300, 3400], btype="bandpass", fs=fs, output="sos"
        )

        # Anti-aliasing filter
        self.antialiasing_filter = signal.butter(
            8, fs * 0.45, btype="lowpass", fs=fs, output="sos"
        )

        # Notch filter for 50/60 Hz hum removal
        self.notch_filter_50 = signal.iirnotch(50, 30, fs)
        self.notch_filter_60 = signal.iirnotch(60, 30, fs)

        # De-emphasis filter
        self.deemphasis_filter = signal.butter(
            2, 4000, btype="lowpass", fs=fs, output="sos"
        )

    def _setup_vad(self) -> Any:
        """Set up Voice Activity Detection."""
        self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)

        # VAD frame size (must be 10, 20, or 30 ms)
        self.vad_frame_size = self.config.frame_duration_ms
        self.vad_sample_rate = self.config.sample_rate

        # VAD buffer for smoothing decisions
        self.vad_buffer = deque(maxlen=10)

    def _setup_buffers(self) -> Any:
        """Set up audio buffers for streaming processing."""
        self.input_buffer = deque(maxlen=self.config.buffer_size * 10)
        self.output_buffer = deque(maxlen=self.config.buffer_size * 10)
        self.noise_profile = None
        self.noise_gate_threshold = 0.02

    async def process_audio_async(
        self, audio_data: np.ndarray, mode: ProcessingMode = ProcessingMode.BATCH
    ) -> np.ndarray:
        """Process audio data asynchronously."""
        loop = asyncio.get_event_loop()

        if mode == ProcessingMode.REALTIME:
            # Process in smaller chunks for lower latency
            return await self._process_realtime_async(audio_data)
        else:
            # Run CPU-intensive processing in thread pool
            return await loop.run_in_executor(
                self.executor, self.process_audio, audio_data
            )

    async def _process_realtime_async(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio in real-time with minimal latency."""
        chunk_size = self.config.buffer_size
        processed_chunks = []

        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i : i + chunk_size]
            if len(chunk) < chunk_size:
                # Pad last chunk if necessary
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)), "constant")

            # Process chunk
            processed = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_chunk, chunk
            )
            processed_chunks.append(processed)

            # Small delay to prevent blocking
            await asyncio.sleep(0)

        return np.concatenate(processed_chunks)[: len(audio_data)]

    def _process_chunk(self, chunk: np.ndarray) -> np.ndarray:
        """Process a single audio chunk."""
        # Apply DC removal
        chunk = signal.sosfilt(self.dc_filter, chunk)

        # Apply noise gate
        chunk = self._apply_noise_gate(chunk)

        # Enhance if enabled
        if self.config.enhance_voice:
            chunk = signal.sosfilt(self.voice_filter, chunk)

        # Normalize if enabled
        if self.config.normalize_audio:
            chunk = self._normalize_chunk(chunk)

        return chunk

    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio data with full enhancement pipeline."""
        try:
            if len(audio_data) == 0:
                return audio_data

            # Ensure float32 for processing
            audio_data = audio_data.astype(np.float32)

            # Step 1: Remove DC offset
            audio_data = self._remove_dc_offset(audio_data)

            # Step 2: Apply pre-emphasis
            audio_data = self._apply_preemphasis(audio_data)

            # Step 3: Spectral noise reduction
            if self.config.noise_reduction_level > 0:
                audio_data = self._spectral_noise_reduction(audio_data)

            # Step 4: Remove power line hum
            audio_data = self._remove_hum(audio_data)

            # Step 5: Voice enhancement
            if self.config.enhance_voice:
                audio_data = self._enhance_voice(audio_data)

            # Step 6: Dynamic range compression
            audio_data = self._apply_compression(audio_data)

            # Step 7: De-emphasis
            audio_data = signal.sosfilt(self.deemphasis_filter, audio_data)

            # Step 8: Remove silence if enabled
            if self.config.remove_silence:
                audio_data = self.trim_silence(audio_data)

            # Step 9: Final normalization
            if self.config.normalize_audio:
                audio_data = self.normalize_volume(audio_data)

            # Step 10: Soft limiting to prevent clipping
            audio_data = self._soft_limit(audio_data)

            return audio_data

        except Exception as e:
            self.logger.error(f"Error processing audio: {e}", exc_info=True)
            return audio_data

    def _remove_dc_offset(self, audio_data: np.ndarray) -> np.ndarray:
        """Remove DC offset from audio signal."""
        return audio_data - np.mean(audio_data)

    def _apply_preemphasis(
        self, audio_data: np.ndarray, alpha: float = 0.97
    ) -> np.ndarray:
        """Apply pre-emphasis filter to boost high frequencies."""
        return np.append(audio_data[0], audio_data[1:] - alpha * audio_data[:-1])

    def _spectral_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply spectral subtraction for noise reduction."""
        try:
            # Estimate noise profile from first 0.5 seconds or 10% of audio
            noise_sample_len = min(
                int(0.5 * self.config.sample_rate), len(audio_data) // 10
            )

            if noise_sample_len > 0:
                noise_sample = audio_data[:noise_sample_len]

                # Compute noise spectrum
                noise_fft = np.abs(rfft(noise_sample))
                noise_profile = np.mean(
                    noise_fft.reshape(-1, len(noise_fft) // 10), axis=0
                )

                # Apply spectral subtraction
                audio_fft = rfft(audio_data)
                audio_mag = np.abs(audio_fft)
                audio_phase = np.angle(audio_fft)

                # Interpolate noise profile to match audio spectrum size
                noise_profile_interp = np.interp(
                    np.linspace(0, 1, len(audio_mag)),
                    np.linspace(0, 1, len(noise_profile)),
                    noise_profile,
                )

                # Subtract noise with oversubtraction factor
                alpha = 2.0 * self.config.noise_reduction_level
                audio_mag_clean = audio_mag - alpha * noise_profile_interp
                audio_mag_clean = np.maximum(audio_mag_clean, 0.1 * audio_mag)

                # Reconstruct signal
                audio_fft_clean = audio_mag_clean * np.exp(1j * audio_phase)
                audio_clean = np.fft.irfft(audio_fft_clean, n=len(audio_data))

                return audio_clean.astype(np.float32)

            return audio_data

        except Exception as e:
            self.logger.error(f"Error in spectral noise reduction: {e}")
            return audio_data

    def _remove_hum(self, audio_data: np.ndarray) -> np.ndarray:
        """Remove 50/60 Hz power line hum."""
        # Apply both 50 Hz and 60 Hz notch filters
        b50, a50 = self.notch_filter_50
        b60, a60 = self.notch_filter_60

        audio_data = signal.filtfilt(b50, a50, audio_data)
        audio_data = signal.filtfilt(b60, a60, audio_data)

        return audio_data

    def _enhance_voice(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance voice frequencies using bandpass filtering."""
        return signal.sosfilt(self.voice_filter, audio_data)

    def _apply_compression(
        self,
        audio_data: np.ndarray,
        threshold: float = 0.7,
        ratio: float = 4.0,
        attack_time: float = 0.005,
        release_time: float = 0.05,
    ) -> np.ndarray:
        """Apply dynamic range compression."""
        # Convert times to samples
        attack_samples = int(attack_time * self.config.sample_rate)
        release_samples = int(release_time * self.config.sample_rate)

        # Initialize envelope follower
        envelope = np.zeros_like(audio_data)

        # Compute envelope
        for i in range(1, len(audio_data)):
            input_abs = abs(audio_data[i])

            if input_abs > envelope[i - 1]:
                # Attack
                alpha = 1.0 - np.exp(-1.0 / attack_samples)
                envelope[i] = alpha * input_abs + (1 - alpha) * envelope[i - 1]
            else:
                # Release
                alpha = 1.0 - np.exp(-1.0 / release_samples)
                envelope[i] = alpha * input_abs + (1 - alpha) * envelope[i - 1]

        # Apply compression
        gain = np.ones_like(audio_data)
        above_threshold = envelope > threshold

        if np.any(above_threshold):
            gain[above_threshold] = (
                threshold + (envelope[above_threshold] - threshold) / ratio
            ) / envelope[above_threshold]

        return audio_data * gain

    def _soft_limit(
        self, audio_data: np.ndarray, threshold: float = 0.95
    ) -> np.ndarray:
        """Apply soft limiting to prevent clipping."""
        # Soft clipping using tanh
        over_threshold = np.abs(audio_data) > threshold
        if np.any(over_threshold):
            audio_data[over_threshold] = threshold * np.tanh(
                audio_data[over_threshold] / threshold
            )
        return audio_data

    def _apply_noise_gate(
        self, audio_data: np.ndarray, threshold: Optional[float] = None
    ) -> np.ndarray:
        """Apply noise gate to remove low-level noise."""
        if threshold is None:
            threshold = self.noise_gate_threshold

        # Simple noise gate
        gate_mask = np.abs(audio_data) > threshold

        # Smooth the gate to avoid clicks
        from scipy.ndimage import binary_dilation

        gate_mask = binary_dilation(gate_mask, iterations=5)

        return audio_data * gate_mask

    def _normalize_chunk(
        self, chunk: np.ndarray, target_level: float = 0.7
    ) -> np.ndarray:
        """Normalize audio chunk to target level."""
        if np.max(np.abs(chunk)) > 0:
            return chunk * (target_level / np.max(np.abs(chunk)))
        return chunk

    def normalize_volume(
        self, audio_data: np.ndarray, target_dBFS: float = -20.0
    ) -> np.ndarray:
        """Normalize audio volume to target dBFS level."""
        try:
            if not np.any(audio_data):
                return audio_data

            # Calculate current RMS in dBFS
            rms = np.sqrt(np.mean(np.square(audio_data)))
            if rms == 0:
                return audio_data

            current_dBFS = 20 * np.log10(rms)

            # Calculate required gain
            gain_dB = target_dBFS - current_dBFS
            gain_linear = 10 ** (gain_dB / 20)

            # Apply gain with clipping prevention
            normalized = audio_data * gain_linear

            # Prevent clipping
            max_val = np.max(np.abs(normalized))
            if max_val > 0.99:
                normalized = normalized * (0.99 / max_val)

            return normalized

        except Exception as e:
            self.logger.error(f"Error normalizing volume: {e}")
            return audio_data

    def detect_voice_activity(
        self, audio_data: np.ndarray, frame_duration_ms: Optional[int] = None
    ) -> List[Tuple[int, int]]:
        """Detect voice activity segments using WebRTC VAD."""
        if frame_duration_ms is None:
            frame_duration_ms = self.config.frame_duration_ms

        # Ensure audio is in correct format for VAD
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).astype(np.int16)

        # Frame size in samples
        frame_size = int(self.config.sample_rate * frame_duration_ms / 1000)

        # Process frames
        voice_segments = []
        current_segment_start = None

        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_data[i : i + frame_size].tobytes()

            try:
                is_speech = self.vad.is_speech(frame, self.config.sample_rate)

                if is_speech and current_segment_start is None:
                    current_segment_start = i
                elif not is_speech and current_segment_start is not None:
                    voice_segments.append((current_segment_start, i))
                    current_segment_start = None
            except Exception as e:
                self.logger.warning(f"VAD error at frame {i}: {e}")

        # Handle final segment
        if current_segment_start is not None:
            voice_segments.append((current_segment_start, len(audio_data)))

        return voice_segments

    def segment_audio(
        self,
        audio_data: np.ndarray,
        segment_duration: float = 1.0,
        overlap: float = 0.1,
    ) -> List[np.ndarray]:
        """Segment audio into overlapping chunks for streaming."""
        segment_samples = int(segment_duration * self.config.sample_rate)
        overlap_samples = int(overlap * self.config.sample_rate)
        step_size = segment_samples - overlap_samples

        segments = []
        for i in range(0, len(audio_data) - segment_samples + 1, step_size):
            segment = audio_data[i : i + segment_samples]

            # Apply window to reduce edge artifacts
            window = np.hanning(len(segment))
            segment = segment * window

            segments.append(segment)

        # Handle remaining samples
        if len(audio_data) % step_size != 0:
            last_segment = audio_data[-segment_samples:]
            window = np.hanning(len(last_segment))
            segments.append(last_segment * window)

        return segments

    def detect_silence(
        self, audio_data: np.ndarray, threshold: float = 0.01, min_duration: int = 100
    ) -> List[Tuple[int, int]]:
        """Detect silent segments in audio."""
        try:
            # Calculate short-term energy
            frame_length = int(0.02 * self.config.sample_rate)  # 20ms frames
            hop_length = frame_length // 2

            energy = librosa.feature.rms(
                y=audio_data, frame_length=frame_length, hop_length=hop_length
            )[0]

            # Find silent frames
            silent_frames = energy < threshold

            # Convert frame indices to sample indices
            silent_segments = []
            in_silence = False
            start_frame = 0

            for i, is_silent in enumerate(silent_frames):
                if is_silent and not in_silence:
                    in_silence = True
                    start_frame = i
                elif not is_silent and in_silence:
                    in_silence = False
                    start_sample = start_frame * hop_length
                    end_sample = i * hop_length
                    duration = end_sample - start_sample

                    if duration >= min_duration:
                        silent_segments.append((start_sample, end_sample))

            # Handle trailing silence
            if in_silence:
                start_sample = start_frame * hop_length
                end_sample = len(audio_data)
                duration = end_sample - start_sample

                if duration >= min_duration:
                    silent_segments.append((start_sample, end_sample))

            return silent_segments

        except Exception as e:
            self.logger.error(f"Error detecting silence: {e}")
            return []

    def trim_silence(
        self, audio_data: np.ndarray, threshold: float = 0.01, margin: int = 100
    ) -> np.ndarray:
        """Trim silence from start and end of audio with margin."""
        try:
            if not np.any(audio_data):
                return audio_data

            # Find non-silent regions
            non_silent = np.abs(audio_data) > threshold

            if not np.any(non_silent):
                return np.array([])

            # Find start and end indices
            indices = np.where(non_silent)[0]
            start = max(0, indices[0] - margin)
            end = min(len(audio_data), indices[-1] + margin)

            return audio_data[start:end]

        except Exception as e:
            self.logger.error(f"Error trimming silence: {e}")
            return audio_data

    def calculate_metrics(self, audio_data: np.ndarray) -> AudioMetrics:
        """Calculate comprehensive audio quality metrics."""
        try:
            if len(audio_data) == 0:
                return AudioMetrics(
                    rms=0,
                    peak=0,
                    snr=0,
                    silence_ratio=1,
                    clipping_ratio=0,
                    frequency_centroid=0,
                    zero_crossing_rate=0,
                    duration=0,
                )

            # Basic metrics
            rms = float(np.sqrt(np.mean(np.square(audio_data))))
            peak = float(np.max(np.abs(audio_data)))
            duration = len(audio_data) / self.config.sample_rate

            # SNR estimation
            signal_power = np.mean(np.square(audio_data))
            noise_segments = self.detect_silence(audio_data)

            if noise_segments:
                noise_samples = []
                for start, end in noise_segments:
                    noise_samples.extend(audio_data[start:end])

                if noise_samples:
                    noise_power = np.mean(np.square(noise_samples))
                    snr = (
                        10 * np.log10(signal_power / noise_power)
                        if noise_power > 0
                        else 60
                    )
                else:
                    snr = 60  # Assume good SNR if no noise detected
            else:
                snr = 60

            # Silence ratio
            silent_samples = np.sum(np.abs(audio_data) < 0.01)
            silence_ratio = silent_samples / len(audio_data)

            # Clipping ratio
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
            clipping_ratio = clipped_samples / len(audio_data)

            # Frequency centroid
            fft = np.abs(rfft(audio_data))
            freqs = rfftfreq(len(audio_data), 1 / self.config.sample_rate)
            frequency_centroid = float(np.sum(freqs * fft) / np.sum(fft))

            # Zero crossing rate
            zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data))) > 0)
            zero_crossing_rate = zero_crossings / len(audio_data)

            return AudioMetrics(
                rms=rms,
                peak=peak,
                snr=snr,
                silence_ratio=silence_ratio,
                clipping_ratio=clipping_ratio,
                frequency_centroid=frequency_centroid,
                zero_crossing_rate=zero_crossing_rate,
                duration=duration,
            )

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return AudioMetrics(
                rms=0,
                peak=0,
                snr=0,
                silence_ratio=0,
                clipping_ratio=0,
                frequency_centroid=0,
                zero_crossing_rate=0,
                duration=0,
            )

    def convert_format(
        self,
        audio_data: np.ndarray,
        target_format: AudioFormat,
        target_sample_rate: Optional[int] = None,
    ) -> bytes:
        """Convert audio to different format."""
        try:
            if target_sample_rate and target_sample_rate != self.config.sample_rate:
                # Resample audio
                audio_data = librosa.resample(
                    audio_data,
                    orig_sr=self.config.sample_rate,
                    target_sr=target_sample_rate,
                )

            # Convert to bytes
            buffer = io.BytesIO()

            if target_format == AudioFormat.WAV:
                sf.write(buffer, audio_data, self.config.sample_rate, format="WAV")
            elif target_format == AudioFormat.FLAC:
                sf.write(buffer, audio_data, self.config.sample_rate, format="FLAC")
            elif target_format == AudioFormat.OGG:
                sf.write(buffer, audio_data, self.config.sample_rate, format="OGG")
            elif target_format == AudioFormat.RAW:
                # Convert to int16 for raw format
                audio_int16 = (audio_data * 32767).astype(np.int16)
                buffer.write(audio_int16.tobytes())
            else:
                raise ValueError(f"Unsupported format: {target_format}")

            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            self.logger.error(f"Error converting format: {e}")
            raise

    async def process_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        chunk_callback: Optional[Callable[[np.ndarray], None]] = None,
    ) -> AsyncGenerator[np.ndarray, None]:
        """Process audio stream in real-time."""
        buffer = bytearray()
        chunk_size = self.config.buffer_size * 2  # 2 bytes per sample for int16

        async for audio_bytes in audio_stream:
            buffer.extend(audio_bytes)

            while len(buffer) >= chunk_size:
                # Extract chunk
                chunk_bytes = buffer[:chunk_size]
                buffer = buffer[chunk_size:]

                # Convert to numpy array
                chunk = (
                    np.frombuffer(chunk_bytes, dtype=np.int16).astype(np.float32)
                    / 32767
                )

                # Process chunk
                processed = await self.process_audio_async(
                    chunk, ProcessingMode.REALTIME
                )

                # Callback if provided
                if chunk_callback:
                    chunk_callback(processed)

                yield processed

        # Process remaining buffer
        if buffer:
            chunk = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32767
            processed = await self.process_audio_async(chunk, ProcessingMode.REALTIME)

            if chunk_callback:
                chunk_callback(processed)

            yield processed

    def cleanup(self) -> Any:
        """Clean up resources."""
        self.executor.shutdown(wait=True)
        self.input_buffer.clear()
        self.output_buffer.clear()
        self.vad_buffer.clear()
        self.logger.info("Audio processor cleaned up")


# Convenience functions for backwards compatibility
def process_audio(
    audio_data: np.ndarray, config: Optional[AudioConfig] = None
) -> np.ndarray:
    """Process audio data with default configuration."""
    processor = AudioProcessor(config)
    try:
        return processor.process_audio(audio_data)
    finally:
        processor.cleanup()


def remove_noise(
    audio_data: np.ndarray, noise_filter: Optional[Tuple[np.ndarray, np.ndarray]] = None
) -> np.ndarray:
    """Remove background noise using spectral subtraction."""
    processor = AudioProcessor()
    return processor._spectral_noise_reduction(audio_data)


def remove_clicks(
    audio_data: np.ndarray, click_filter: Optional[Tuple[np.ndarray, np.ndarray]] = None
) -> np.ndarray:
    """Remove clicks and pops from audio."""
    # Use median filter for click removal

    window_size = 5

    # Detect clicks using difference threshold
    diff = np.abs(np.diff(audio_data))
    threshold = np.percentile(diff, 99.9)
    click_indices = np.where(diff > threshold)[0]

    # Apply median filter around clicks
    audio_cleaned = audio_data.copy()
    for idx in click_indices:
        start = max(0, idx - window_size)
        end = min(len(audio_data), idx + window_size)
        audio_cleaned[idx] = np.median(audio_data[start:end])

    return audio_cleaned


def normalize_volume(audio_data: np.ndarray) -> np.ndarray:
    """Normalize audio volume."""
    processor = AudioProcessor()
    return processor.normalize_volume(audio_data)


def detect_silence(
    audio_data: np.ndarray, threshold: float = 0.01, min_duration: int = 100
) -> List[Tuple[int, int]]:
    """Detect silent segments in audio."""
    processor = AudioProcessor()
    return processor.detect_silence(audio_data, threshold, min_duration)


def trim_silence(audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    """Trim silence from start and end of audio."""
    processor = AudioProcessor()
    return processor.trim_silence(audio_data, threshold)


def get_audio_stats(audio_data: np.ndarray) -> Dict[str, Any]:
    """Calculate audio statistics."""
    processor = AudioProcessor()
    metrics = processor.calculate_metrics(audio_data)

    return {
        "duration": metrics.duration,
        "rms": metrics.rms,
        "peak": metrics.peak,
        "silent_percentage": metrics.silence_ratio * 100,
        "snr": metrics.snr,
        "clipping_ratio": metrics.clipping_ratio,
        "frequency_centroid": metrics.frequency_centroid,
        "zero_crossing_rate": metrics.zero_crossing_rate,
    }


# Unit tests
if __name__ == "__main__":
    import unittest

    class TestAudioProcessor(unittest.TestCase):
        """Unit tests for AudioProcessor class."""

        def setUp(self) -> Any:
            """Set up test fixtures."""
            self.processor = AudioProcessor()
            self.sample_rate = 16000
            self.duration = 1.0  # 1 second

            # Generate test signals
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))

            # Pure tone
            self.tone = np.sin(2 * np.pi * 440 * t)

            # Noisy signal
            self.noisy_signal = self.tone + 0.1 * np.random.randn(len(t))

            # Silent signal
            self.silent_signal = np.zeros_like(t)

            # Clipped signal
            self.clipped_signal = np.clip(self.tone * 2, -1, 1)

        def test_initialization(self) -> Any:
            """Test processor initialization."""
            self.assertIsNotNone(self.processor)
            self.assertEqual(self.processor.config.sample_rate, 16000)

        def test_process_audio(self) -> Any:
            """Test basic audio processing."""
            processed = self.processor.process_audio(self.noisy_signal)
            self.assertEqual(len(processed), len(self.noisy_signal))

            # Check that processing reduces noise
            original_snr = 20 * np.log10(
                np.std(self.tone) / np.std(self.noisy_signal - self.tone)
            )
            processed_noise = processed - self.tone
            processed_snr = 20 * np.log10(np.std(self.tone) / np.std(processed_noise))

            # SNR should improve
            self.assertGreater(processed_snr, original_snr)

        def test_normalize_volume(self) -> Any:
            """Test volume normalization."""
            quiet_signal = self.tone * 0.1
            normalized = self.processor.normalize_volume(quiet_signal)

            # Check RMS is close to target
            rms = np.sqrt(np.mean(np.square(normalized)))
            target_rms = 10 ** (-20 / 20)  # -20 dBFS

            self.assertAlmostEqual(rms, target_rms, places=2)

        def test_detect_silence(self) -> Any:
            """Test silence detection."""
            # Create signal with silence
            signal = np.concatenate(
                [
                    self.silent_signal[:1000],
                    self.tone[1000:5000],
                    self.silent_signal[5000:7000],
                    self.tone[7000:],
                    self.silent_signal[-1000:],
                ]
            )

            silent_segments = self.processor.detect_silence(signal)

            # Should detect at least 2 silent segments
            self.assertGreaterEqual(len(silent_segments), 2)

        def test_trim_silence(self) -> Any:
            """Test silence trimming."""
            # Add silence to beginning and end
            padded_signal = np.concatenate(
                [self.silent_signal[:1000], self.tone, self.silent_signal[:1000]]
            )

            trimmed = self.processor.trim_silence(padded_signal)

            # Trimmed signal should be shorter
            self.assertLess(len(trimmed), len(padded_signal))

            # Should preserve most of the tone
            self.assertGreater(len(trimmed), len(self.tone) * 0.9)

        def test_voice_activity_detection(self) -> Any:
            """Test VAD functionality."""
            # Create signal with speech and silence
            signal = np.concatenate(
                [self.silent_signal[:1000], self.tone, self.silent_signal[:1000]]
            )

            # Convert to int16 for VAD
            signal_int16 = (signal * 32767).astype(np.int16)

            segments = self.processor.detect_voice_activity(signal_int16)

            # Should detect voice segment
            self.assertGreaterEqual(len(segments), 1)

            # Voice segment should roughly match tone position
            if segments:
                start, end = segments[0]
                self.assertLess(start, 2000)
                self.assertGreater(end, len(self.tone))

        def test_calculate_metrics(self) -> Any:
            """Test audio metrics calculation."""
            metrics = self.processor.calculate_metrics(self.tone)

            # Check metric ranges
            self.assertGreater(metrics.rms, 0)
            self.assertLessEqual(metrics.peak, 1.0)
            self.assertGreater(metrics.snr, 0)
            self.assertLessEqual(metrics.silence_ratio, 1.0)
            self.assertEqual(metrics.clipping_ratio, 0)
            self.assertGreater(metrics.frequency_centroid, 0)
            self.assertAlmostEqual(metrics.duration, self.duration, places=2)

        def test_segment_audio(self) -> Any:
            """Test audio segmentation."""
            segments = self.processor.segment_audio(
                self.tone, segment_duration=0.1, overlap=0.02
            )

            # Should create multiple segments
            self.assertGreater(len(segments), 5)

            # Each segment should have correct length
            segment_samples = int(0.1 * self.sample_rate)
            for segment in segments[:-1]:  # Except possibly the last
                self.assertEqual(len(segment), segment_samples)

        def test_format_conversion(self) -> Any:
            """Test audio format conversion."""
            # Test WAV conversion
            wav_bytes = self.processor.convert_format(self.tone, AudioFormat.WAV)
            self.assertGreater(len(wav_bytes), 0)
            self.assertEqual(wav_bytes[:4], b"RIFF")  # WAV header

            # Test RAW conversion
            raw_bytes = self.processor.convert_format(self.tone, AudioFormat.RAW)
            expected_size = len(self.tone) * 2  # int16
            self.assertEqual(len(raw_bytes), expected_size)

        async def test_async_processing(self):
            """Test asynchronous audio processing."""
            processed = await self.processor.process_audio_async(
                self.noisy_signal, ProcessingMode.REALTIME
            )

            self.assertEqual(len(processed), len(self.noisy_signal))

        async def test_stream_processing(self):
            """Test stream processing."""

            # Create mock audio stream
            async def mock_stream():
                chunk_size = 1024
                audio_int16 = (self.tone * 32767).astype(np.int16)

                for i in range(0, len(audio_int16), chunk_size):
                    chunk = audio_int16[i : i + chunk_size]
                    yield chunk.tobytes()

            # Process stream
            processed_chunks = []
            async for chunk in self.processor.process_stream(mock_stream()):
                processed_chunks.append(chunk)

            # Verify processing
            self.assertGreater(len(processed_chunks), 0)
            total_samples = sum(len(chunk) for chunk in processed_chunks)
            self.assertAlmostEqual(total_samples, len(self.tone), delta=1024)

        def tearDown(self) -> Any:
            """Clean up after tests."""
            self.processor.cleanup()

    # Run tests
    unittest.main()
