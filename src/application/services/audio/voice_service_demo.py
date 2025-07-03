"""
Voice Service Demo
Demonstrates usage of the refactored voice service with clean architecture
"""

import asyncio
import logging
from typing import Optional

from . import (
    VoiceServiceFactory,
    Settings,
    IVoiceService
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceServiceDemo:
    """Demo class showing voice service usage"""
    
    def __init__(self):
        # Configure settings
        self.settings = Settings()
        self.settings.azure_speech_key = "your-azure-key"  # Configure as needed
        self.settings.azure_speech_region = "eastus"
        self.settings.elevenlabs_api_key = "your-elevenlabs-key"  # Configure as needed
        
        # Create voice service
        self.voice_service = VoiceServiceFactory.create(self.settings)
    
    async def demo_transcription(self, audio_base64: str):
        """Demo transcription functionality"""
        logger.info("🎤 Starting transcription demo...")
        
        # Transcribe audio
        transcript = await self.voice_service.transcribe_audio(
            audio_data=audio_base64,
            language="Arabic"
        )
        
        if transcript:
            logger.info(f"✅ Transcription successful: {transcript}")
        else:
            logger.warning("❌ Transcription failed")
        
        return transcript
    
    async def demo_synthesis(self, text: str):
        """Demo synthesis functionality"""
        logger.info("🔊 Starting synthesis demo...")
        
        # Synthesize speech
        audio_data = await self.voice_service.synthesize_speech(
            text=text,
            emotion="happy",
            language="Arabic"
        )
        
        if audio_data:
            logger.info(f"✅ Synthesis successful, audio length: {len(audio_data)} chars")
        else:
            logger.warning("❌ Synthesis failed")
        
        return audio_data
    
    async def demo_provider_status(self):
        """Demo provider status functionality"""
        logger.info("📊 Checking provider status...")
        
        status = self.voice_service.get_provider_status()
        
        logger.info("Provider Status:")
        for operation, providers in status.items():
            logger.info(f"  {operation.upper()}:")
            for provider in providers:
                status_icon = "✅" if provider["available"] else "❌"
                logger.info(f"    {status_icon} {provider['name']} (Priority: {provider['priority']})")
    
    async def demo_full_conversation_flow(self):
        """Demo complete conversation flow"""
        logger.info("🤖 Starting full conversation flow demo...")
        
        # Simulate receiving voice input
        sample_audio_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAgAA..."  # Sample base64
        
        # 1. Transcribe incoming audio
        transcript = await self.demo_transcription(sample_audio_base64)
        
        if transcript:
            # 2. Process the transcript (simulate AI response)
            ai_response = f"مرحباً! لقد قلت: {transcript}. كيف يمكنني مساعدتك؟"
            
            # 3. Synthesize response
            response_audio = await self.demo_synthesis(ai_response)
            
            if response_audio:
                logger.info("🎉 Complete conversation cycle successful!")
                return {
                    "transcript": transcript,
                    "ai_response": ai_response,
                    "audio_response": response_audio
                }
        
        logger.warning("❌ Conversation flow incomplete")
        return None
    
    async def demo_error_handling(self):
        """Demo error handling and fallback"""
        logger.info("⚠️  Testing error handling...")
        
        # Test with invalid audio data
        result = await self.voice_service.transcribe_audio("invalid_audio")
        logger.info(f"Invalid audio result: {result}")
        
        # Test synthesis with empty text
        result = await self.voice_service.synthesize_speech("")
        logger.info(f"Empty text synthesis result: {result}")
        
        # Update provider availability
        self.voice_service.update_provider_availability("whisper", False)
        logger.info("Disabled Whisper provider for testing")
        
        # Check updated status
        await self.demo_provider_status()


async def main():
    """Main demo function"""
    demo = VoiceServiceDemo()
    
    logger.info("🚀 Starting Voice Service Demo")
    logger.info("=" * 50)
    
    try:
        # Run all demos
        await demo.demo_provider_status()
        await demo.demo_synthesis("مرحباً بك في نظام الدببة الذكية!")
        await demo.demo_error_handling()
        
        # Run full conversation flow if audio data is available
        # await demo.demo_full_conversation_flow()
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
    
    logger.info("=" * 50)
    logger.info("✅ Voice Service Demo Complete")


if __name__ == "__main__":
    asyncio.run(main()) 