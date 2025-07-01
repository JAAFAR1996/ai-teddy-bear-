"""CLI command for text-to-speech conversion."""

import sys
import logging
import argparse
from typing import Optional

from ..audio_manager import audio_manager

logger = logging.getLogger(__name__)

def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Text-to-speech conversion")
    parser.add_argument(
        "text",
        type=str,
        help="Text to convert to speech"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output audio file path"
    )
    parser.add_argument(
        "-l", "--language",
        type=str,
        default="en",
        help="Language code (default: en)"
    )
    parser.add_argument(
        "-s", "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable TTS caching"
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="Play the generated audio"
    )
    return parser.parse_args(args)

def main(args: Optional[list] = None) -> int:
    """Main entry point for TTS command."""
    try:
        parsed_args = parse_args(args)
        
        # Convert text to speech
        logger.info("Converting text to speech...")
        
        # Generate speech
        success = audio_manager.speak(
            text=parsed_args.text,
            language=parsed_args.language,
            speed=parsed_args.speed,
            cache=not parsed_args.no_cache
        )
        
        if not success:
            logger.error("Text-to-speech conversion failed")
            return 1
        
        # Save to file if requested
        if parsed_args.output:
            logger.info(f"Saving audio to: {parsed_args.output}")
            # Note: The audio_manager.speak() function already handles saving
            # when an output file is provided
        
        # Play audio if requested
        if parsed_args.play:
            logger.info("Playing generated audio...")
            if not audio_manager.play_audio(filename=parsed_args.output):
                logger.error("Audio playback failed")
                return 1
        
        logger.info("Text-to-speech conversion completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Text-to-speech conversion cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Error in TTS command: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())