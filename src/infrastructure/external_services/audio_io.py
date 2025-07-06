"""Enhanced Audio I/O operations and management system for AI Teddy Bear."""

import json
import logging
import os
import tempfile
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import librosa
    import numpy as np
    import soundfile as sf
    from pydub import AudioSegment
    from pydub.effects import compress_dynamic_range
except ImportError as e:
    logging.warning(f"Some audio libraries not available: {e}")

from .exceptions import AudioProcessingError, AudioValidationError
from .models import (
    AudioFormat,
    AudioMetadata,
    AudioProcessingConfig,
    AudioQuality,
)


class AudioIO:
    """Enhanced audio file I/O operations and management."""

    def __init__(
        self,
        temp_dir: Optional[str] = None,
        max_temp_files: int = 100,
        auto_cleanup: bool = True,
        default_config: Optional[AudioProcessingConfig] = None,
    ):
        """
        Initialize enhanced audio I/O handler.

        Args:
            temp_dir: Temporary directory path
            max_temp_files: Maximum number of temp files to keep
            auto_cleanup: Whether to auto-cleanup old files
            default_config: Default audio processing configuration
        """
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir or os.path.join(
            tempfile.gettempdir(), "teddy_audio")
        self.max_temp_files = max_temp_files
        self.auto_cleanup = auto_cleanup
        self.default_config = default_config or AudioProcessingConfig()

        # Thread safety
        self._lock = threading.Lock()
        self._temp_files = set()

        # Audio format mappings
        self.format_extensions = {
            AudioFormat.WAV: ".wav",
            AudioFormat.MP3: ".mp3",
            AudioFormat.OGG: ".ogg",
            AudioFormat.FLAC: ".flac",
            AudioFormat.M4A: ".m4a",
            AudioFormat.AAC: ".aac",
        }

        self._ensure_temp_dir()

        if self.auto_cleanup:
            self._start_cleanup_scheduler()

    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory exists with proper permissions."""
        try:
            temp_path = Path(self.temp_dir)
            temp_path.mkdir(parents=True, exist_ok=True)

            # Set proper permissions (readable/writable by owner)
            os.chmod(self.temp_dir, 0o755)

            self.logger.info(f"Using temporary directory: {self.temp_dir}")

        except Exception as e:
            self.logger.error(f"Error creating temp directory: {e}")
            raise AudioProcessingError(f"Failed to create temp directory: {e}")

    def _start_cleanup_scheduler(self) -> None:
        """Start background cleanup scheduler."""

        def cleanup_worker() -> Any:
            while True:
                try:
                    self.cleanup_temp_files()
                    threading.Event().wait(3600)  # Cleanup every hour
                except Exception as e:
                    self.logger.error(f"Error in cleanup scheduler: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _check_file_existence_and_size(
            self, filename: str, max_size: int) -> Path:
        """Checks if the file exists and is within the size limit."""
        if not os.path.exists(filename):
            raise AudioValidationError(f"Audio file not found: {filename}")

        file_path = Path(filename)
        if file_path.stat().st_size > max_size:
            raise AudioValidationError(
                f"Audio file too large: {file_path.stat().st_size} bytes"
            )

        return file_path

    def _extract_and_validate_metadata(self, filename: str) -> AudioMetadata:
        """Extracts and validates metadata from the audio file."""
        try:
            with sf.SoundFile(filename) as f:
                metadata = AudioMetadata(
                    filename=filename,
                    format=f.format,
                    duration=float(
                        len(f)) / f.samplerate,
                    sample_rate=f.samplerate,
                    channels=f.channels,
                    size_bytes=os.path.getsize(filename),
                    created_at=datetime.fromtimestamp(
                        os.path.getctime(filename)),
                    modified_at=datetime.fromtimestamp(
                        os.path.getmtime(filename)),
                )
                if metadata.duration > 300:
                    raise AudioValidationError(
                        "Audio file too long (max 5 minutes)")
                if metadata.sample_rate < 8000 or metadata.sample_rate > 48000:
                    raise AudioValidationError(
                        f"Unsupported sample rate: {metadata.sample_rate}"
                    )
                return metadata
        except Exception as e:
            raise AudioValidationError(f"Invalid audio file format: {e}")

    def validate_audio_file(self, filename: str) -> AudioMetadata:
        """Validate and extract metadata from audio file."""
        try:
            self._check_file_existence_and_size(filename, 100 * 1024 * 1024)
            return self._extract_and_validate_metadata(filename)
        except AudioValidationError:
            raise
        except Exception as e:
            raise AudioValidationError(f"Error validating audio file: {e}")

    def save_audio(
        self,
        audio_data: np.ndarray,
        filename: str,
        sample_rate: int = 16000,
        audio_format: AudioFormat = AudioFormat.WAV,
        quality: Optional[AudioQuality] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AudioMetadata:
        """Save audio data to file with enhanced options."""
        try:
            # Use default quality if not specified
            if quality is None:
                quality = self.default_config.quality

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Process audio data
            processed_audio = self._process_audio_data(
                audio_data, sample_rate, quality)

            # Determine output format and parameters
            if audio_format == AudioFormat.WAV:
                sf.write(
                    filename,
                    processed_audio,
                    quality.value["sample_rate"],
                    subtype="PCM_16",
                )
            else:
                # Convert using pydub for other formats
                self._save_with_pydub(
                    processed_audio, filename, quality, audio_format)

            # Create metadata
            file_metadata = self.validate_audio_file(filename)

            if metadata:
                file_metadata.tags.update(metadata)

            # Save metadata file
            self._save_metadata(filename, file_metadata)

            self.logger.info(f"Audio saved to {filename}")
            return file_metadata

        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            raise AudioProcessingError(f"Failed to save audio: {e}")

    def _process_audio_data(
        self, audio_data: np.ndarray, sample_rate: int, quality: AudioQuality
    ) -> np.ndarray:
        """Process audio data according to quality settings."""
        try:
            processed = audio_data.copy()
            target_rate = quality.value["sample_rate"]

            # Convert to mono if needed
            if len(processed.shape) > 1:
                processed = np.mean(processed, axis=1)

            # Resample if needed
            if sample_rate != target_rate:
                processed = librosa.resample(
                    processed, orig_sr=sample_rate, target_sr=target_rate
                )

            # Normalize audio
            if self.default_config.normalize_audio:
                max_val = np.max(np.abs(processed))
                if max_val > 0:
                    processed = processed / max_val * 0.95

            # Remove silence if configured
            if self.default_config.remove_silence:
                processed = self._remove_silence(processed, target_rate)

            return processed

        except Exception as e:
            self.logger.error(f"Error processing audio data: {e}")
            return audio_data

    def _remove_silence(
            self,
            audio_data: np.ndarray,
            sample_rate: int) -> np.ndarray:
        """Remove silence from audio data."""
        try:
            # Use librosa to detect non-silent intervals
            intervals = librosa.effects.split(
                audio_data,
                top_db=20,
                frame_length=2048,
                hop_length=512,  # Threshold for silence detection
            )

            if len(intervals) == 0:
                return audio_data

            # Concatenate non-silent segments
            non_silent = []
            for start, end in intervals:
                non_silent.append(audio_data[start:end])

            return np.concatenate(non_silent) if non_silent else audio_data

        except Exception as e:
            self.logger.warning(f"Error removing silence: {e}")
            return audio_data

    def _save_with_pydub(
        self,
        audio_data: np.ndarray,
        filename: str,
        quality: AudioQuality,
        audio_format: AudioFormat,
    ) -> None:
        """Save audio using pydub for format conversion."""
        try:
            # Convert numpy array to pydub AudioSegment
            # Ensure audio is 16-bit
            audio_16bit = (audio_data * 32767).astype(np.int16)

            audio_segment = AudioSegment(
                audio_16bit.tobytes(),
                frame_rate=quality.value["sample_rate"],
                sample_width=2,  # 16-bit
                channels=1,  # Mono
            )

            # Apply dynamic range compression
            audio_segment = compress_dynamic_range(audio_segment)

            # Export with format-specific parameters
            export_params = {
                "format": audio_format.value,
                "bitrate": quality.value["bitrate"],
            }

            if audio_format == AudioFormat.MP3:
                export_params.update({"parameters": ["-q:a", "2"]})
            elif audio_format == AudioFormat.OGG:
                export_params.update({"codec": "libvorbis"})

            audio_segment.export(filename, **export_params)

        except Exception as e:
            raise AudioProcessingError(f"Error saving with pydub: {e}")

    def load_audio(
        self,
        filename: str,
        target_sample_rate: Optional[int] = None,
        normalize: bool = True,
    ) -> Tuple[np.ndarray, int, AudioMetadata]:
        """Load audio data from file with enhanced processing."""
        try:
            # Validate file first
            metadata = self.validate_audio_file(filename)

            # Load audio file
            audio_data, sample_rate = sf.read(filename)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Resample if requested
            if target_sample_rate and target_sample_rate != sample_rate:
                audio_data = librosa.resample(
                    audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
                sample_rate = target_sample_rate

            # Normalize if requested
            if normalize:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val

            self.logger.info(
                f"Loaded audio from {filename} "
                f"(rate: {sample_rate}Hz, length: {len(audio_data)}, "
                f"duration: {metadata.duration:.2f}s)"
            )

            return audio_data, sample_rate, metadata

        except Exception as e:
            self.logger.error(f"Error loading audio: {e}")
            raise AudioProcessingError(f"Failed to load audio: {e}")

    def create_temp_file(
        self,
        prefix: str = "audio_",
        suffix: str = ".wav",
        audio_format: AudioFormat = AudioFormat.WAV,
    ) -> str:
        """Create temporary audio file with cleanup tracking."""
        try:
            with self._lock:
                # Use format-specific extension if not provided
                if suffix == ".wav" and audio_format != AudioFormat.WAV:
                    suffix = self.format_extensions[audio_format]

                # Create unique filename
                unique_id = str(uuid.uuid4())[:8]
                temp_filename = f"{prefix}{unique_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
                temp_filepath = os.path.join(self.temp_dir, temp_filename)

                # Track temp file
                self._temp_files.add(temp_filepath)

                # Cleanup if too many temp files
                if len(self._temp_files) > self.max_temp_files:
                    self._cleanup_oldest_temp_files()

                self.logger.info(f"Created temporary file: {temp_filepath}")
                return temp_filepath

        except Exception as e:
            self.logger.error(f"Error creating temp file: {e}")
            raise AudioProcessingError(f"Failed to create temp file: {e}")

    def _cleanup_oldest_temp_files(self) -> None:
        """Clean up oldest temporary files."""
        try:
            temp_files_with_time = []

            for temp_file in list(self._temp_files):
                if os.path.exists(temp_file):
                    mtime = os.path.getmtime(temp_file)
                    temp_files_with_time.append((mtime, temp_file))
                else:
                    self._temp_files.discard(temp_file)

            # Sort by modification time and remove oldest
            temp_files_with_time.sort()
            files_to_remove = len(temp_files_with_time) - \
                self.max_temp_files + 10

            for _, temp_file in temp_files_with_time[:files_to_remove]:
                self._remove_temp_file(temp_file)

        except Exception as e:
            self.logger.error(f"Error cleaning up oldest temp files: {e}")

    def _remove_temp_file(self, filepath: str) -> None:
        """Remove a temporary file and its metadata."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)

            # Remove metadata file if exists
            metadata_file = filepath + ".meta"
            if os.path.exists(metadata_file):
                os.remove(metadata_file)

            self._temp_files.discard(filepath)

        except Exception as e:
            self.logger.warning(f"Error removing temp file {filepath}: {e}")

    def _cleanup_tracked_files(self, cutoff_time: datetime) -> int:
        """Cleans up tracked temporary files older than the cutoff time."""
        count = 0
        for temp_file in list(self._temp_files):
            try:
                if os.path.exists(temp_file):
                    mtime = datetime.fromtimestamp(os.path.getmtime(temp_file))
                    if mtime < cutoff_time:
                        self._remove_temp_file(temp_file)
                        count += 1
                else:
                    self._temp_files.discard(temp_file)
            except Exception as e:
                self.logger.warning(
                    f"Error checking temp file {temp_file}: {e}")
        return count

    def _cleanup_untracked_files(
            self,
            temp_path: Path,
            cutoff_time: datetime) -> int:
        """Cleans up untracked temporary files older than the cutoff time."""
        count = 0
        for pattern in ["audio_*.wav", "audio_*.mp3", "*.tmp"]:
            for file in temp_path.glob(pattern):
                try:
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime < cutoff_time:
                        file.unlink()
                        count += 1
                except Exception as e:
                    self.logger.warning(
                        f"Error removing untracked file {file}: {e}")
        return count

    def cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """
        Clean up old temporary files.
        """
        try:
            with self._lock:
                temp_path = Path(self.temp_dir)
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

                tracked_cleaned = self._cleanup_tracked_files(cutoff_time)
                untracked_cleaned = self._cleanup_untracked_files(
                    temp_path, cutoff_time
                )

                total_cleaned = tracked_cleaned + untracked_cleaned
                self.logger.info(f"Cleaned up {total_cleaned} temporary files")

        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")

    def _save_metadata(
            self,
            audio_filename: str,
            metadata: AudioMetadata) -> None:
        """Save metadata to companion file."""
        try:
            metadata_filename = audio_filename + ".meta"

            metadata_dict = {
                "filename": metadata.filename,
                "format": metadata.format,
                "duration": metadata.duration,
                "sample_rate": metadata.sample_rate,
                "channels": metadata.channels,
                "bitrate": metadata.bitrate,
                "size_bytes": metadata.size_bytes,
                "created_at": metadata.created_at.isoformat(),
                "modified_at": metadata.modified_at.isoformat(),
                "checksum": metadata.checksum,
                "tags": metadata.tags,
            }

            with open(metadata_filename, "w") as f:
                json.dump(metadata_dict, f, indent=2)

        except Exception as e:
            self.logger.warning(f"Error saving metadata: {e}")

    def load_metadata(self, audio_filename: str) -> Optional[AudioMetadata]:
        """Load metadata from companion file."""
        try:
            metadata_filename = audio_filename + ".meta"

            if not os.path.exists(metadata_filename):
                return None

            with open(metadata_filename, "r") as f:
                metadata_dict = json.load(f)

            return AudioMetadata(
                filename=metadata_dict["filename"],
                format=metadata_dict["format"],
                duration=metadata_dict["duration"],
                sample_rate=metadata_dict["sample_rate"],
                channels=metadata_dict["channels"],
                bitrate=metadata_dict.get("bitrate"),
                size_bytes=metadata_dict["size_bytes"],
                created_at=(
                    datetime.fromisoformat(metadata_dict["created_at"])
                    if hasattr(datetime, "fromisoformat")
                    else datetime.strptime(
                        metadata_dict["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                ),
                modified_at=(
                    datetime.fromisoformat(metadata_dict["modified_at"])
                    if hasattr(datetime, "fromisoformat")
                    else datetime.strptime(
                        metadata_dict["modified_at"], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                ),
                checksum=metadata_dict.get("checksum"),
                tags=metadata_dict.get("tags", {}),
            )

        except Exception as e:
            self.logger.warning(f"Error loading metadata: {e}")
            return None

    @contextmanager
    def temp_audio_file(
            self,
            audio_format: AudioFormat = AudioFormat.WAV,
            cleanup_on_exit: bool = True):
        """
        Context manager for temporary audio files.

        Args:
            audio_format: Audio format
            cleanup_on_exit: Whether to cleanup file on exit

        Yields:
            Temporary filename
        """
        temp_file = None
        try:
            temp_file = self.create_temp_file(audio_format=audio_format)
            yield temp_file
        finally:
            if temp_file and cleanup_on_exit:
                self._remove_temp_file(temp_file)

    def convert_audio_format(
        self,
        input_file: str,
        output_file: str,
        target_format: AudioFormat,
        quality: Optional[AudioQuality] = None,
    ) -> AudioMetadata:
        """
        Convert audio file to different format.

        Args:
            input_file: Input filename
            output_file: Output filename
            target_format: Target audio format
            quality: Audio quality preset

        Returns:
            AudioMetadata of converted file
        """
        try:
            # Load original audio
            audio_data, sample_rate, _ = self.load_audio(input_file)

            # Save in new format
            return self.save_audio(
                audio_data, output_file, sample_rate, target_format, quality
            )

        except Exception as e:
            self.logger.error(f"Error converting audio format: {e}")
            raise AudioProcessingError(f"Failed to convert audio format: {e}")

    def get_audio_statistics(self) -> Dict[str, Any]:
        """Get statistics about temporary audio files."""
        try:
            with self._lock:
                temp_path = Path(self.temp_dir)

                total_files = 0
                total_size = 0
                formats = {}

                for temp_file in self._temp_files:
                    if os.path.exists(temp_file):
                        total_files += 1
                        total_size += os.path.getsize(temp_file)

                        ext = Path(temp_file).suffix.lower()
                        formats[ext] = formats.get(ext, 0) + 1

                return {
                    "temp_directory": str(temp_path),
                    "total_temp_files": total_files,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "format_distribution": formats,
                    "max_temp_files": self.max_temp_files,
                    "auto_cleanup": self.auto_cleanup,
                }

        except Exception as e:
            self.logger.error(f"Error getting audio statistics: {e}")
            return {}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        try:
            self.cleanup_temp_files()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
