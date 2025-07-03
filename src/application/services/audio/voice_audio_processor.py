"""
Voice Audio Processor
Handles audio processing operations for voice services
"""

import asyncio
import base64
import tempfile
import os
import logging
from typing import Dict, Optional

import aiofiles

logger = logging.getLogger(__name__)


class VoiceAudioProcessor:
    """Centralized audio processing utilities"""
    
    @staticmethod
    async def decode_base64_audio(audio_base64: str) -> bytes:
        """Decode base64 audio data asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, base64.b64decode, audio_base64)
    
    @staticmethod
    async def encode_audio_base64(audio_bytes: bytes) -> str:
        """Encode audio bytes to base64 asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: base64.b64encode(audio_bytes).decode('utf-8')
        )
    
    @staticmethod
    async def save_temp_file(data: bytes, suffix: str) -> str:
        """Save data to temporary file asynchronously"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = temp_file.name
        temp_file.close()
        
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(data)
        
        return temp_path
    
    @staticmethod
    async def read_temp_file(file_path: str) -> bytes:
        """Read temporary file asynchronously"""
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    @staticmethod
    async def convert_mp3_to_wav(mp3_path: str) -> str:
        """Convert MP3 to WAV asynchronously using ffmpeg"""
        wav_path = mp3_path.replace('.mp3', '.wav')
        
        # Run ffmpeg in subprocess
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg',
            '-i', mp3_path,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # Mono channel
            '-y',            # Overwrite output
            wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {stderr.decode()}")
            raise RuntimeError("Audio conversion failed")
        
        return wav_path
    
    @staticmethod
    async def process_audio_file(audio_data: str) -> Dict[str, str]:
        """Process base64 audio data and prepare files"""
        try:
            # Decode audio data
            audio_bytes = await VoiceAudioProcessor.decode_base64_audio(audio_data)
            
            # Save to temporary file
            temp_mp3 = await VoiceAudioProcessor.save_temp_file(audio_bytes, '.mp3')
            
            # Convert to WAV for processing
            temp_wav = await VoiceAudioProcessor.convert_mp3_to_wav(temp_mp3)
            
            return {"mp3": temp_mp3, "wav": temp_wav}
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise
    
    @staticmethod
    async def cleanup_files(file_paths: list):
        """Clean up temporary files"""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, os.unlink, path
                    )
                    logger.debug(f"Cleaned up file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {path}: {e}")
    
    @staticmethod
    def clean_transcription_text(text: str) -> str:
        """Clean transcribed text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Fix common Arabic issues
        text = text.replace('إ', 'ا')  # Normalize hamza
        
        # Remove leading/trailing whitespace
        return text.strip() 