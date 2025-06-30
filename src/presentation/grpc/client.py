import logging

logger = logging.getLogger(__name__)

import grpc
import asyncio

class GRPCClient:
    """gRPC Client for internal services"""
    
    def __init__(self, audio_service_url: str = "localhost:50051", ai_service_url: str = "localhost:50052"):
        self.audio_service_url = audio_service_url
        self.ai_service_url = ai_service_url
        self.audio_channel = None
        self.ai_channel = None
    
    async def connect(self):
        """Connect to gRPC services"""
        self.audio_channel = grpc.aio.insecure_channel(self.audio_service_url)
        self.ai_channel = grpc.aio.insecure_channel(self.ai_service_url)
    
    async def process_audio(self, audio_data: bytes, format: str = "wav", sample_rate: int = 16000):
        """Process audio through gRPC"""
        if not self.audio_channel:
            await self.connect()
        
        # Mock gRPC call
        request = {
            "audio_data": audio_data,
            "format": format,
            "sample_rate": sample_rate
        }
        
        # Simulate gRPC response
        return {
            "transcription": "مرحبا كيف حالك؟",
            "emotions": ["happy"],
            "confidence": 0.85
        }
    
    async def generate_ai_response(self, message: str, child_id: str, context: dict = None):
        """Generate AI response through gRPC"""
        if not self.ai_channel:
            await self.connect()
        
        request = {
            "message": message,
            "child_id": child_id,
            "context": context or {},
            "response_type": "general"
        }
        
        # Simulate gRPC response
        return {
            "response_text": f"مرحبا! تحدثت عن {message}",
            "emotion": "friendly",
            "confidence": 0.9
        }
    
    async def stream_ai_response(self, message: str, child_id: str):
        """Stream AI response through gRPC"""
        if not self.ai_channel:
            await self.connect()
        
        # Mock streaming response
        chunks = ["مرحبا", " بك", " يا", " صديقي!"]
        
        for i, chunk in enumerate(chunks):
            yield {
                "text": chunk,
                "is_final": i == len(chunks) - 1
            }
            await asyncio.sleep(0.1)
    
    async def close(self):
        """Close gRPC connections"""
        if self.audio_channel:
            await self.audio_channel.close()
        if self.ai_channel:
            await self.ai_channel.close()

# Usage example
async def main():
    client = GRPCClient()
    
    # Process audio
    audio_result = await client.process_audio(b"audio_data")
    logger.info(f"Transcription: {audio_result['transcription']}")
    
    # Generate AI response
    ai_result = await client.generate_ai_response("مرحبا", "child-123")
    logger.info(f"AI Response: {ai_result['response_text']}")
    
    # Stream response
    async for chunk in client.stream_ai_response("احكي قصة", "child-123"):
        logger.info(chunk["text"], end="")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())