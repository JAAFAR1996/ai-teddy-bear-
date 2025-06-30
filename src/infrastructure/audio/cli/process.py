"""CLI command for audio processing."""

import sys
import logging
import argparse
from typing import Optional

from ..audio_manager import audio_manager
from ..audio_processing import process_audio, normalize_volume, trim_silence

logger = logging.getLogger(__name__)

def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process audio files")
    parser.add_argument(
        "input",
        type=str,
        help="Input audio file path"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: input_processed.wav)"
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize audio volume"
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Trim silence from start and end"
    )
    parser.add_argument(
        "--noise-reduction",
        action="store_true",
        help="Apply noise reduction"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show audio statistics"
    )
    return parser.parse_args(args)

def show_audio_stats(audio_data: np.ndarray) -> None:
    """Display audio statistics."""
    from ..audio_processing import get_audio_stats
    
    stats = get_audio_stats(audio_data)
    logger.info("\nAudio Statistics:")
    logger.info("----------------")
    logger.info(f"Duration: {stats['duration']:.2f} seconds")
    logger.info(f"RMS Level: {stats['rms']:.3f}")
    logger.info(f"Peak Level: {stats['peak']:.3f}")
    logger.info(f"Silent Percentage: {stats['silent_percentage']:.1f}%\n")

def main(args: Optional[list] = None) -> int:
    """Main entry point for processing command."""
    try:
        parsed_args = parse_args(args)
        
        # Load audio file
        logger.info(f"Loading audio file: {parsed_args.input}")
        audio_data, sample_rate = audio_manager.audio_io.load_audio(parsed_args.input)
        
        # Show initial stats if requested
        if parsed_args.stats:
            logger.info("\nBefore Processing:")
            show_audio_stats(audio_data)
        
        # Apply processing
        if parsed_args.normalize:
            logger.info("Normalizing volume...")
            audio_data = normalize_volume(audio_data)
            
        if parsed_args.trim:
            logger.info("Trimming silence...")
            audio_data = trim_silence(audio_data)
            
        if parsed_args.noise_reduction:
            logger.info("Applying noise reduction...")
            audio_data = process_audio(audio_data)
        
        # Show final stats if requested
        if parsed_args.stats:
            logger.info("\nAfter Processing:")
            show_audio_stats(audio_data)
        
        # Save processed audio
        output_file = parsed_args.output or parsed_args.input.rsplit('.', 1)[0] + '_processed.wav'
        logger.info(f"Saving processed audio to: {output_file}")
        audio_manager.audio_io.save_audio(
            audio_data,
            output_file,
            sample_rate
        )
        
        logger.info("Processing completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Processing cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Error in processing command: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())