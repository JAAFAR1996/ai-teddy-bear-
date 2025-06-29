"""
🧸 Teddy Bear Hardware API Endpoints
Handles communication with ESP32-based physical teddy bears
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import base64
import asyncio
import httpx
from datetime import datetime
import uuid

from src.application.services.ai.modern_ai_service import ModernAIService
from src.infrastructure.modern_container import ModernContainer
import openai
from pathlib import Path
import json

router = APIRouter(prefix="/teddy", tags=["Teddy Hardware"])

# 📋 Request/Response Models
class VoiceMessageRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    device_id: str = Field(..., description="ESP32 MAC address or unique ID")
    audio_format: str = Field(default="pcm_16000", description="Audio format")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    timestamp: int = Field(..., description="Unix timestamp from device")
    volume_level: int = Field(default=50, ge=0, le=100)
    child_id: Optional[str] = None

class HeartbeatRequest(BaseModel):
    device_id: str = Field(..., description="ESP32 unique identifier")
    status: str = Field(default="online")
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    wifi_strength: Optional[int] = Field(None, description="RSSI value")
    uptime: int = Field(..., description="Device uptime in milliseconds")
    firmware_version: Optional[str] = "1.0.0"

class TeddyResponse(BaseModel):
    status: str
    text: Optional[str] = None
    audio_url: Optional[str] = None
    session_id: str
    processing_time_ms: int
    emotions: Optional[Dict[str, float]] = None
    error: Optional[str] = None

# 📊 Device Registry (In production, use Redis/Database)
connected_devices: Dict[str, Dict[str, Any]] = {}

@router.post("/voice-message", response_model=TeddyResponse)
async def handle_voice_message(
    request: VoiceMessageRequest,
    background_tasks: BackgroundTasks
):
    """
    🎤 Process voice message from physical teddy bear
    """
    start_time = datetime.now()
    
    try:
        # 📝 Log device activity
        update_device_status(request.device_id, "processing_voice")
        
        # 🎵 Decode audio data (simulate text for now)
        try:
            audio_bytes = base64.b64decode(request.audio_data)
            # For text simulation, decode as string
            if request.audio_format == "text_simulation":
                transcript = audio_bytes.decode('utf-8')
            else:
                # In production, use Azure Speech Service here
                transcript = "Simulated speech recognition result"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid audio data: {str(e)}")
        
        if not transcript.strip():
            return TeddyResponse(
                status="error",
                error="No speech detected",
                session_id=request.session_id,
                processing_time_ms=0
            )
        
        # 🤖 Generate AI response using professional services
        try:
            container = ModernContainer()
            ai_service = await container.get_ai_service()
            
            # Create child-safe context for physical teddy
            teddy_context = {
                "device_type": "physical_teddy", 
                "device_id": request.device_id,
                "session_id": request.session_id,
                "volume_level": request.volume_level,
                "is_hardware": True,
                "safety_level": "maximum"  # Extra safety for physical device
            }
            
            ai_response = await ai_service.generate_response(
                message=transcript,
                context=teddy_context
            )
            ai_response_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
            
        except Exception as ai_error:
            print(f"⚠️ AI Service error: {ai_error}")
            # Fallback to direct OpenAI call
            ai_response_text = await generate_teddy_ai_response_fallback(
                message=transcript,
                device_id=request.device_id
            )
        
        # 🎵 Generate audio response URL (mock for now)
        audio_url = f"https://teddy-audio-cdn.com/response_{request.device_id}_{int(start_time.timestamp())}.mp3"
        
        # 📊 Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 📝 Log conversation for parents
        background_tasks.add_task(
            log_teddy_conversation,
            request.device_id,
            transcript,
            ai_response.content,
            request.session_id
        )
        
        return TeddyResponse(
            status="success",
            text=ai_response_text,
            audio_url=audio_url,
            session_id=request.session_id,
            processing_time_ms=int(processing_time),
            emotions={"happiness": 0.8, "excitement": 0.6}  # Mock emotions
        )
        
    except Exception as e:
        # 🔴 Error handling
        error_msg = f"Error processing voice message: {str(e)}"
        
        return TeddyResponse(
            status="error",
            error=error_msg,
            session_id=request.session_id,
            processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
        )

@router.post("/heartbeat")
async def device_heartbeat(request: HeartbeatRequest):
    """
    💓 Handle device heartbeat and status updates
    """
    device_info = {
        "device_id": request.device_id,
        "status": request.status,
        "last_seen": datetime.now().isoformat(),
        "battery_level": request.battery_level,
        "wifi_strength": request.wifi_strength,
        "uptime": request.uptime,
        "firmware_version": request.firmware_version
    }
    
    connected_devices[request.device_id] = device_info
    
    return {
        "status": "acknowledged",
        "server_time": datetime.now().isoformat(),
        "device_id": request.device_id,
        "instructions": get_device_instructions(request.device_id)
    }

@router.get("/devices")
async def list_connected_devices():
    """
    📱 List all connected teddy bear devices
    """
    return {
        "connected_devices": connected_devices,
        "total_count": len(connected_devices),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/device/{device_id}/status")
async def get_device_status(device_id: str):
    """
    🔍 Get specific device status
    """
    if device_id not in connected_devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return connected_devices[device_id]

@router.post("/device/{device_id}/command")
async def send_device_command(device_id: str, command: Dict[str, Any]):
    """
    📤 Send command to specific device
    """
    if device_id not in connected_devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # In production, use WebSocket or MQTT to send commands
    # For now, store command for device to poll
    
    commands_queue = connected_devices[device_id].get("pending_commands", [])
    commands_queue.append({
        "command": command,
        "timestamp": datetime.now().isoformat(),
        "id": str(uuid.uuid4())
    })
    
    connected_devices[device_id]["pending_commands"] = commands_queue
    
    return {"status": "command_queued", "command_id": commands_queue[-1]["id"]}

@router.post("/device/{device_id}/update-settings")
async def update_device_settings(device_id: str, settings: Dict[str, Any]):
    """
    ⚙️ Update device settings remotely
    """
    if device_id not in connected_devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update device settings
    device_settings = connected_devices[device_id].get("settings", {})
    device_settings.update(settings)
    connected_devices[device_id]["settings"] = device_settings
    
    # Queue settings update command
    await send_device_command(device_id, {
        "type": "update_settings",
        "settings": settings
    })
    
    return {"status": "settings_updated", "new_settings": device_settings}

# 🔧 Helper Functions

def update_device_status(device_id: str, status: str):
    """Update device status in registry"""
    if device_id in connected_devices:
        connected_devices[device_id]["status"] = status
        connected_devices[device_id]["last_activity"] = datetime.now().isoformat()

def get_device_instructions(device_id: str) -> Dict[str, Any]:
    """Get pending instructions for device"""
    if device_id not in connected_devices:
        return {}
    
    return {
        "pending_commands": connected_devices[device_id].get("pending_commands", []),
        "settings_update": connected_devices[device_id].get("settings", {}),
        "firmware_update_available": False  # Check for updates
    }

async def log_teddy_conversation(
    device_id: str, 
    user_message: str, 
    ai_response: str, 
    session_id: str
):
    """Log conversation for parental dashboard"""
    # In production, save to database
    conversation_log = {
        "device_id": device_id,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "ai_response": ai_response,
        "device_type": "physical_teddy"
    }
    
    # Add to device history
    if device_id in connected_devices:
        history = connected_devices[device_id].get("conversation_history", [])
        history.append(conversation_log)
        # Keep only last 50 conversations
        connected_devices[device_id]["conversation_history"] = history[-50:]

# 🎵 Text-to-Speech Service for Hardware
class HardwareTTSService:
    """Specialized TTS service for hardware devices"""
    
    async def generate_speech_url(
        self, 
        text: str, 
        voice_id: str = "child_friendly", 
        device_id: str = None
    ) -> str:
        """Generate speech audio and return downloadable URL"""
        
        # In production:
        # 1. Generate audio using ElevenLabs/Azure
        # 2. Save to cloud storage (AWS S3, etc.)
        # 3. Return public URL for ESP32 to download
        
        # For demo, return a mock URL
        audio_filename = f"teddy_response_{device_id}_{datetime.now().timestamp()}.mp3"
        
        # Mock URL - in production this would be real audio file
        return f"https://your-cdn.com/audio/{audio_filename}"

# 🎯 Professional AI Response Generation
async def generate_teddy_ai_response_fallback(message: str, device_id: str) -> str:
    """
    Professional fallback AI response generator using OpenAI API directly
    """
    try:
        # Load API key from config
        config_file = Path(__file__).parent.parent.parent / "config" / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_api_key = config.get("API_KEYS", {}).get("OPENAI_API_KEY")
        if not openai_api_key or openai_api_key.startswith("ضع_هنا"):
            return "مرحباً عزيزي! أنا دمية ذكية وأحب اللعب معك! 🧸"
        
        # Set OpenAI API key
        openai.api_key = openai_api_key
        
        # Professional system prompt for teddy bear
        system_prompt = """أنت دمية دب ذكية ومحبوبة تتحدث مع الأطفال. خصائصك:

🧸 الشخصية:
- مرح ولطيف ومحب للأطفال
- تستخدم كلمات بسيطة ومفهومة
- تشجع التعلم واللعب
- تحب القصص والألعاب والأغاني

🛡️ قواعد الأمان:
- لا تعطي معلومات شخصية
- لا تطلب معلومات من الطفل
- ركز على الأنشطة الإيجابية
- تجنب المواضيع المخيفة أو المعقدة

🎨 أسلوب التفاعل:
- استخدم الإيموجي المناسبة
- اجعل الردود قصيرة (50 كلمة أو أقل)
- اطرح أسئلة تفاعلية
- شجع الإبداع والخيال

تذكر: أنت صديق الطفل المفضل! 🌟"""

        # Create chat completion
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.8,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Add device-specific personalization
        if "مرحبا" in message.lower() or "هلا" in message.lower():
            ai_response = f"مرحباً بك يا صديقي العزيز! 🧸 {ai_response}"
        
        return ai_response
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        # Ultimate fallback responses
        fallback_responses = [
            "مرحباً عزيزي! أنا سعيد للحديث معك! 🧸✨",
            "أهلاً وسهلاً! ماذا تريد أن نلعب اليوم؟ 🎮🌟", 
            "مرحباً يا صديقي! أحب قضاء الوقت معك! 💖🧸",
            "أهلاً بك! هل تريد أن أحكي لك قصة جميلة؟ 📖✨",
            "مرحباً! أنا هنا للعب والمرح معك! 🎈🧸"
        ]
        
        import random
        return random.choice(fallback_responses) 