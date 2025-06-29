import grpc
from concurrent import futures
import asyncio

class AIServiceImpl:
    """gRPC AI Service Implementation"""
    
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
    
    async def GenerateResponse(self, request, context):
        """Generate AI response"""
        try:
            # Extract request data
            message = request.get("message", "")
            child_id = request.get("child_id", "")
            context_data = request.get("context", {})
            response_type = request.get("response_type", "general")
            
            # Generate response
            result = await self._generate_response(
                message, child_id, context_data, response_type
            )
            
            return {
                "response_text": result["text"],
                "emotion": result["emotion"],
                "confidence": result["confidence"],
                "suggestions": result.get("suggestions", [])
            }
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"AI generation failed: {str(e)}")
            return {}
    
    async def StreamResponse(self, request, context):
        """Stream AI response generation"""
        try:
            message = request.get("message", "")
            
            # Mock streaming response
            response_chunks = [
                "مرحبا", " بك", " يا", " صديقي!", " كيف", " يمكنني", " مساعدتك؟"
            ]
            
            for i, chunk in enumerate(response_chunks):
                yield {
                    "text": chunk,
                    "is_final": i == len(response_chunks) - 1
                }
                await asyncio.sleep(0.1)  # Simulate processing time
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Streaming failed: {str(e)}")
    
    async def _generate_response(self, message, child_id, context, response_type):
        """Generate AI response based on input"""
        # Mock AI response generation
        responses = {
            "educational": f"دعني أعلمك شيئا عن {message}",
            "playful": f"واو! {message} شيء ممتع جداً!",
            "story": f"كان يا ما كان، قصة عن {message}",
            "general": f"أهلاً وسهلاً! تحدثت عن {message}"
        }
        
        return {
            "text": responses.get(response_type, responses["general"]),
            "emotion": "friendly",
            "confidence": 0.9,
            "suggestions": ["احكي لي أكثر", "ما رأيك في لعبة؟"]
        }

async def serve_ai_service(port: int = 50052):
    """Start gRPC AI Service"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add service
    ai_engine = None  # Initialize your AI engine
    service_impl = AIServiceImpl(ai_engine)
    
    # Start server
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    await server.start()
    print(f"AI Service started on {listen_addr}")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await server.stop(0)