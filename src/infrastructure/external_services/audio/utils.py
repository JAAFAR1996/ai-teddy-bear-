"""
Utility functions for audio processing.
"""
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import soundfile as sf

from .audio_io import AudioIO

logger = logging.getLogger(__name__)


def cleanup_temp_files(max_age_hours: int = 24) -> None:
    """Global function to clean up temporary audio files."""
    try:
        with AudioIO() as audio_io:
            audio_io.cleanup_temp_files(max_age_hours)
    except Exception as e:
        logger.error(f"Error in cleanup_temp_files: {e}")


def get_audio_files(
    directory: str, include_metadata: bool = False
) -> List[Union[str, Dict[str, Any]]]:
    """
    Get list of audio files in directory with optional metadata.

    Args:
        directory: Directory to search
        include_metadata: Whether to include metadata

    Returns:
        List of audio files or file info dictionaries
    """
    try:
        audio_files = []
        supported_extensions = [
            ".wav",
            ".mp3",
            ".ogg",
            ".flac",
            ".m4a",
            ".aac"]

        directory_path = Path(directory)
        if not directory_path.exists():
            return []

        for ext in supported_extensions:
            for file_path in directory_path.glob(f"*{ext}"):
                if include_metadata:
                    try:
                        audio_io = AudioIO()
                        metadata = audio_io.validate_audio_file(str(file_path))
                        audio_files.append(
                            {"filepath": str(file_path), "metadata": metadata}
                        )
                    except Exception as e:
                        logging.warning(
                            f"Error getting metadata for {file_path}: {e}")
                        audio_files.append(
                            {"filepath": str(file_path), "metadata": None}
                        )
                else:
                    audio_files.append(str(file_path))

        return sorted(
            audio_files, key=lambda x: x if isinstance(
                x, str) else x["filepath"])

    except Exception as e:
        logging.error(f"Error getting audio files: {e}")
        return []


def copy_audio_file(
        src: str,
        dst: str,
        preserve_metadata: bool = True) -> bool:
    """
    Copy audio file with optional metadata preservation.

    Args:
        src: Source filename
        dst: Destination filename
        preserve_metadata: Whether to preserve metadata

    Returns:
        Success status
    """
    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        # Copy file
        shutil.copy2(src, dst)

        # Copy metadata if requested and available
        if preserve_metadata:
            try:
                audio_io = AudioIO()
                metadata = audio_io.load_metadata(src)
                if metadata:
                    # Update filename in metadata
                    metadata.filename = dst
                    metadata.modified_at = datetime.now()
                    audio_io._save_metadata(dst, metadata)
            except Exception as e:
                logging.warning(f"Error copying metadata: {e}")

        logging.info(f"Copied audio file from {src} to {dst}")
        return True

    except Exception as e:
        logging.error(f"Error copying audio file: {e}")
        return False


def get_audio_duration(filename: str) -> float:
    """
    Get duration of audio file in seconds.

    Args:
        filename: Audio filename

    Returns:
        Duration in seconds
    """
    try:
        with sf.SoundFile(filename) as f:
            return float(len(f)) / f.samplerate
    except Exception as e:
        logging.error(f"Error getting audio duration: {e}")
        return 0.0


def get_audio_format(filename: str) -> Dict[str, Any]:
    """
    Get audio file format information.

    Args:
        filename: Audio filename

    Returns:
        Format information dictionary
    """
    try:
        audio_io = AudioIO()
        metadata = audio_io.validate_audio_file(filename)

        return {
            "format": metadata.format,
            "channels": metadata.channels,
            "samplerate": metadata.sample_rate,
            "duration": metadata.duration,
            "size_bytes": metadata.size_bytes,
            "created_at": metadata.created_at.isoformat(),
            "modified_at": metadata.modified_at.isoformat(),
        }

    except Exception as e:
        logging.error(f"Error getting audio format: {e}")
        return {}


def validate_audio_for_children(filename: str) -> Dict[str, Any]:
    """
    Validate audio file for children's content (safety checks).

    Args:
        filename: Audio filename

    Returns:
        Validation results
    """
    try:
        audio_io = AudioIO()
        metadata = audio_io.validate_audio_file(filename)

        validation_results = {
            "is_valid": True,
            "issues": [],
            "metadata": metadata}

        # Check duration (max 5 minutes for children)
        if metadata.duration > 300:
            validation_results["issues"].append(
                "Audio too long for children (max 5 minutes)"
            )

        # Check file size (reasonable limits)
        if metadata.size_bytes > 50 * 1024 * 1024:  # 50MB
            validation_results["issues"].append("Audio file too large")

        # Check sample rate (should be reasonable)
        if metadata.sample_rate < 8000:
            validation_results["issues"].append(
                "Sample rate too low for good quality")

        validation_results["is_valid"] = len(validation_results["issues"]) == 0

        return validation_results

    except Exception as e:
        return {
            "is_valid": False,
            "issues": [f"Validation error: {e}"],
            "metadata": None,
        }
