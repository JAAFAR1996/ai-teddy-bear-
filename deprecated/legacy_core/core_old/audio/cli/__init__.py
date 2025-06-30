"""Command-line interface package for the audio system.

This package provides CLI commands for:
- Audio recording
- Audio processing
- Text-to-speech conversion

Example usage:
    # Record audio
    $ audio-record -d 10 -o recording.wav

    # Process audio
    $ audio-process input.wav --normalize --trim

    # Text-to-speech
    $ audio-tts "Hello, world!" --play
"""

from . import record
from . import process
from . import tts

__all__ = ['record', 'process', 'tts']

# Version info
__version__ = '1.0.0'

# Command mapping
commands = {
    'record': record.main,
    'process': process.main,
    'tts': tts.main,
}
