"""CLI command for audio recording."""

import sys
import logging
import argparse
from typing import Optional

from ..audio_manager import audio_manager

logger = logging.getLogger(__name__)

def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Record audio")
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=5,
        help="Recording duration in seconds"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path"
    )
    parser.add_argument(
        "--device",
        type=int,
        help="Audio input device ID"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices"
    )
    return parser.parse_args(args)

def list_devices() -> None:
    """List available audio input devices."""
    devices = audio_manager.get_supported_devices()
    if not devices:
        logger.info("No audio input devices found")
        return
        
    logger.info("\nAvailable audio input devices:")
    logger.info("------------------------------")
    for device_id, device_name in devices:
        logger.info(f"ID: {device_id}, Name: {device_name}")
    logger.info()

def main(args: Optional[list] = None) -> int:
    """Main entry point for recording command."""
    try:
        parsed_args = parse_args(args)
        
        # List devices if requested
        if parsed_args.list_devices:
            list_devices()
            return 0
            
        # Set input device if specified
        if parsed_args.device is not None:
            try:
                audio_manager.set_input_device(parsed_args.device)
            except Exception as e:
                logger.error(f"Error setting input device: {e}")
                return 1
        
        # Record audio
        logger.info(f"Recording for {parsed_args.duration} seconds...")
        audio_data = audio_manager.record(
            duration=parsed_args.duration,
            save=bool(parsed_args.output),
            filename=parsed_args.output
        )
        
        if audio_data is None:
            logger.error("Recording failed")
            return 1
            
        # Save output if filename provided
        if parsed_args.output:
            logger.info(f"Recording saved to: {parsed_args.output}")
        
        logger.info("Recording completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Recording cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Error in recording command: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())