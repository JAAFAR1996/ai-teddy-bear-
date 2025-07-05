"""
🧸 AI Teddy Bear - Cloud Audio Service
=====================================
Cloud-compatible audio processing service that replaces PyAudio
Uses external APIs and cloud services for audio processing
"""

import asyncio
import base64
import io
import tempfile
from typing import Optional, Union, Dict, Any
from pathlib import Path
import aiofiles
import httpx
from loguru import logger
import os
from datetime import datetime

# Cloud service imports
try:
    from elevenlabs import generate, save

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs not available - TTS will use OpenAI")

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - limited audio functionality")


class CloudAudioService:
    """
    Cloud-compatible audio service for AI Teddy Bear
    Handles audio processing without PyAudio dependencies
    """

    def __init__(self):
        self.temp_dir = Path("temp/audio")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Audio processing settings
        self.max_file_size = 25 * 1024 * 1024  # 25MB max
        self.supported_formats = ["wav", "mp3", "ogg", "flac", "webm"]

        # API clients
        self.http_client = httpx.AsyncClient(timeout=30.0)

        logger.info("🎵 Cloud Audio Service initialized")

    async def process_audio_upload(
        self, audio_data: bytes, device_id: str, filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded audio from ESP32 device

        Args:
            audio_data: Raw audio bytes
            device_id: ESP32 device identifier
            filename: Optional filename for the audio

        Returns:
            Dict with processing results
        """
        try:
            # Validate audio data
            if len(audio_data) > self.max_file_size:
                raise ValueError(
                    f"Audio file too large: {len(audio_data)} bytes")

            # Save audio to temporary file
            temp_file = await self._save_temp_audio(audio_data, device_id)

            # Process audio (transcription)
            transcription = await self._transcribe_audio(temp_file)

            # Generate AI response
            ai_response = await self._generate_ai_response(transcription, device_id)

            # Generate TTS audio
            response_audio = await self._generate_speech(ai_response["text"])

            # Clean up temp file
            await self._cleanup_temp_file(temp_file)

            return {
                "status": "success",
                "transcription": transcription,
                "ai_response": ai_response,
                "response_audio": response_audio,
                "processing_time": datetime.now(),
                "device_id": device_id,
            }

        except Exception as e:
            logger.error(f"Audio processing failed for {device_id}: {e}")
            return {"status": "error", "error": str(e), "device_id": device_id}

    async def _save_temp_audio(
            self,
            audio_data: bytes,
            device_id: str) -> Path:
        """Save audio data to temporary file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = self.temp_dir / f"{device_id}_{timestamp}.wav"

        async with aiofiles.open(temp_file, "wb") as f:
            await f.write(audio_data)

        logger.info(f"💾 Saved audio to {temp_file}")
        return temp_file

    async def _transcribe_audio(self, audio_file: Path) -> str:
        """
        Transcribe audio using OpenAI Whisper API
        Fallback to basic text if API unavailable
        """
        if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
            logger.warning(
                "OpenAI not available - using fallback transcription")
            return f"Audio message received from {audio_file.stem}"

        try:
            # Use OpenAI Whisper for transcription
            async with aiofiles.open(audio_file, "rb") as f:
                audio_data = await f.read()

            # Call OpenAI Whisper API
            response = await self._call_whisper_api(audio_data)

            logger.info(f"🎯 Transcribed audio: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "I heard your message but couldn't transcribe it clearly. Could you try again?"

    async def _call_whisper_api(self, audio_data: bytes) -> str:
        """Call OpenAI Whisper API for transcription"""
        try:
            # Create temporary file for API call
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Call OpenAI API
            client = openai.AsyncOpenAI()
            with open(temp_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en",  # Can be made dynamic
                )

            # Clean up temp file
            os.unlink(temp_file_path)

            return transcript.text

        except Exception as e:
            logger.error(f"Whisper API call failed: {e}")
            raise

    async def _generate_ai_response(
        self, message: str, device_id: str
    ) -> Dict[str, str]:
        """Generate AI response to child's message"""
        try:
            if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
                # Fallback responses
                return await self._generate_fallback_response(message)

            # Use OpenAI for intelligent response
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a friendly AI teddy bear talking to a child.
                        Respond in a warm, caring, and age-appropriate way.
                        Keep responses short and engaging.
                        Use simple language suitable for children.""",
                    },
                    {"role": "user", "content": message},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            ai_text = response.choices[0].message.content

            logger.info(f"🤖 Generated AI response for {device_id}")

            return {
                "text": ai_text,
                "source": "openai",
                "model": "gpt-3.5-turbo"}

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return await self._generate_fallback_response(message)

    async def _generate_fallback_response(
            self, message: str) -> Dict[str, str]:
        """Generate fallback response when AI APIs are unavailable"""
        message_lower = message.lower()

        fallback_responses = {
            (
                "hello",
                "hi",
                "مرحبا",
            ): "Hello my little friend! I'm so happy to talk with you today! 🧸💕",
            ("play",
                "game",
                "العب",
             ): "Let's play together! Would you like me to tell you a story or sing a song? 🎵",
            ("story",
                "قصة",
             ): "Once upon a time, there was a magical teddy bear who loved to make children smile... ✨",
            ("sad",
                "upset",
                "حزين",
             ): "Aww, don't be sad little one. I'm here for you always. Let's think of happy things! 🌈",
        }

        for keywords, response in fallback_responses.items():
            if any(word in message_lower for word in keywords):
                text = response
                break
        else:
            text = "That's so interesting! Tell me more about it. I love listening to your stories! 💝"

        return {"text": text, "source": "fallback", "model": "rule-based"}

    async def _generate_speech(self, text: str) -> Optional[str]:
        """
        Generate speech audio from text using cloud TTS
        Returns base64 encoded audio or URL
        """
        try:
            if ELEVENLABS_AVAILABLE and os.getenv("ELEVENLABS_API_KEY"):
                return await self._use_elevenlabs_tts(text)
            elif OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
                return await self._use_openai_tts(text)
            else:
                logger.warning(
                    "No TTS service available - returning text only")
                return None

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return None

    async def _use_elevenlabs_tts(self, text: str) -> str:
        """Use ElevenLabs for high-quality TTS"""
        try:
            # Use a child-friendly voice
            audio = generate(
                text=text,
                voice="Bella",  # Child-friendly voice
                model="eleven_monolingual_v1",
            )

            # Save and return base64
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = self.temp_dir / f"response_{timestamp}.mp3"

            save(audio, str(audio_file))

            # Convert to base64 for API response
            async with aiofiles.open(audio_file, "rb") as f:
                audio_data = await f.read()
                audio_b64 = base64.b64encode(audio_data).decode()

            # Clean up temp file
            await self._cleanup_temp_file(audio_file)

            logger.info("🎤 Generated ElevenLabs TTS audio")
            return audio_b64

        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            raise

    async def _use_openai_tts(self, text: str) -> str:
        """Use OpenAI TTS as fallback"""
        try:
            client = openai.AsyncOpenAI()
            response = await client.audio.speech.create(
                model="tts-1", voice="nova", input=text  # Child-friendly voice
            )

            # Get audio data
            audio_data = response.content

            # Convert to base64
            audio_b64 = base64.b64encode(audio_data).decode()

            logger.info("🎤 Generated OpenAI TTS audio")
            return audio_b64

        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            raise

    async def _cleanup_temp_file(self, file_path: Path):
        """Clean up temporary files"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"🗑️ Cleaned up {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")

    async def get_device_audio_status(self, device_id: str) -> Dict[str, Any]:
        """Get audio processing status for a device"""
        return {
            "device_id": device_id,
            "audio_services": {
                "transcription": "openai_whisper" if OPENAI_AVAILABLE else "fallback",
                "tts": (
                    "elevenlabs"
                    if ELEVENLABS_AVAILABLE
                    else "openai" if OPENAI_AVAILABLE else "text_only"
                ),
                "ai_response": "openai_gpt" if OPENAI_AVAILABLE else "fallback",
            },
            "status": "ready",
            "temp_files": len(list(self.temp_dir.glob("*"))),
        }

    async def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files"""
        try:
            current_time = datetime.now()
            cleaned_count = 0

            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    )
                    if file_age.total_seconds() > max_age_hours * 3600:
                        await self._cleanup_temp_file(file_path)
                        cleaned_count += 1

            logger.info(f"🧹 Cleaned up {cleaned_count} old temp files")
            return cleaned_count

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    async def close(self):
        """Close the audio service and cleanup resources"""
        await self.http_client.aclose()
        await self.cleanup_old_files(max_age_hours=0)  # Clean all files
        logger.info("🔌 Cloud Audio Service closed")


# Global instance
cloud_audio_service = CloudAudioService()


async def get_audio_service() -> CloudAudioService:
    """Dependency injection for audio service"""
    return cloud_audio_service
