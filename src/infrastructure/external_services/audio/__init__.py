"""
This package contains the audio I/O system.
"""

from .audio_io import AudioIO
from .exceptions import AudioProcessingError, AudioValidationError
from .models import (
    AudioFormat,
    AudioMetadata,
    AudioProcessingConfig,
    AudioQuality,
)
from .utils import (
    cleanup_temp_files,
    copy_audio_file,
    get_audio_duration,
    get_audio_files,
    get_audio_format,
    validate_audio_for_children,
)

__all__ = [
    "AudioIO",
    "AudioFormat",
    "AudioQuality",
    "AudioMetadata",
    "AudioProcessingConfig",
    "AudioValidationError",
    "AudioProcessingError",
    "cleanup_temp_files",
    "get_audio_files",
    "copy_audio_file",
    "get_audio_duration",
    "get_audio_format",
    "validate_audio_for_children",
]
