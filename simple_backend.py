"""
AI Teddy Bear - Simple Backend for Quick Start
==============================================
"""
import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional as Opt
from dataclasses import dataclass, asdict
import uvicorn
from loguru import logger

# Create data directories
Path("data/audio").mkdir(parents=True, exist_ok=True)
Path("data/conversations").mkdir(parents=True, exist_ok=True)

# Configure logging
logger.add("logs/app.log", rotation="500 MB", level="INFO")

# FastAPI app
app = FastAPI(
    title="AI Teddy Bear API",
    description="Backend API for AI Teddy Bear System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Data Models ==============
@dataclass
class ChildProfile:
    id: str
    name: str
    age: int
    created_at: Optional[str] = None
    parent_id: Optional[str] = None

@dataclass
class ConversationMessage:
    child_id: str
    message: str
    id: Optional[str] = None
    response: Optional[str] = None
    timestamp: Optional[str] = None
    emotion: Optional[str] = None
    
    def dict(self):
        return asdict(self)

@dataclass
class LoginRequest:
    username: str
    password: str

@dataclass
class DeviceRegistration:
    device_id: str
    child_name: str
    child_age: int

# ============== Mock Database ==============
# In-memory storage for testing
children_db: Dict[str, ChildProfile] = {}
conversations_db: Dict[str, list] = {}
active_websockets: Dict[str, WebSocket] = {}

# ============== Helper Functions ==============
def generate_id() -> str:
    """Generate unique ID"""
    import uuid
    return str(uuid.uuid4())

def get_mock_ai_response(message: str) -> str:
    """Generate mock AI response for testing"""
    responses = [
        "That's very interesting! Tell me more about that.",
        "Wow! That sounds amazing! What happened next?",
        "I love hearing about your day! You're so creative!",
        "That's wonderful! You're doing such a great job!",
        "What a fun adventure! I'm so happy to hear about it!"
    ]
    import random
    return random.choice(responses)

def analyze_emotion(message: str) -> str:
    """Mock emotion analysis"""
    import random
    emotions = ["happy", "excited", "curious", "calm", "playful"]
    return random.choice(emotions)

# ============== API Endpoints ==============
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Teddy Bear API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "ok",
            "ai_service": "mock_mode",
            "websocket": "ok"
        }
    }

@app.post("/api/auth/login")
async def login(request: Dict[str, Any] = Body(...)):
    """Mock login endpoint"""
    # For testing, accept any credentials
    return {
        "access_token": "mock-jwt-token",
        "token_type": "bearer",
        "user": {
            "id": "parent-123",
            "username": request.get("username", "parent"),
            "role": "parent"
        }
    }

@app.post("/api/device/register")
async def register_device(registration: Dict[str, Any] = Body(...)):
    """Register new device/child"""
    child_id = generate_id()
    child = ChildProfile(
        id=child_id,
        name=registration.get("child_name", ""),
        age=registration.get("child_age", 0),
        created_at=datetime.now().isoformat()
    )
    
    children_db[child_id] = child
    conversations_db[child_id] = []
    
    logger.info(f"Registered new child: {child.name} (ID: {child_id})")
    
    return {
        "child_id": child_id,
        "device_id": registration.get("device_id", ""),
        "message": "Device registered successfully"
    }

@app.get("/api/children/{child_id}")
async def get_child_profile(child_id: str):
    """Get child profile"""
    if child_id not in children_db:
        raise HTTPException(status_code=404, detail="Child not found")
    
    return asdict(children_db[child_id])

@app.get("/api/conversations")
async def get_conversations(child_id: Optional[str] = None):
    """Get conversations"""
    if child_id:
        if child_id not in conversations_db:
            return {"items": [], "total": 0}
        return {
            "items": conversations_db[child_id],
            "total": len(conversations_db[child_id])
        }
    
    # Return all conversations
    all_conversations = []
    for child_id, convs in conversations_db.items():
        all_conversations.extend(convs)
    
    return {
        "items": all_conversations,
        "total": len(all_conversations)
    }

@app.post("/api/conversations")
async def create_conversation(data: Dict[str, Any] = Body(...)):
    """Create new conversation"""
    message = ConversationMessage(
        id=generate_id(),
        child_id=data.get("child_id", ""),
        message=data.get("message", ""),
        timestamp=datetime.now().isoformat(),
        emotion=analyze_emotion(data.get("message", "")),
        response=get_mock_ai_response(data.get("message", ""))
    )
    
    if message.child_id not in conversations_db:
        conversations_db[message.child_id] = []
    
    conversations_db[message.child_id].append(message.dict())
    
    # Send notification via WebSocket if connected
    if message.child_id in active_websockets:
        await active_websockets[message.child_id].send_json({
            "type": "new_conversation",
            "data": message.dict()
        })
    
    return message.dict()

@app.post("/api/audio/upload")
async def upload_audio(
    file: UploadFile = File(...),
    child_id: str = None
):
    """Upload audio file"""
    if not child_id:
        raise HTTPException(status_code=400, detail="child_id is required")
    
    # Save audio file
    file_path = f"data/audio/{child_id}_{datetime.now().timestamp()}.wav"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Mock transcription
    transcribed_text = "This is a mock transcription of the audio"
    
    # Create conversation
    message_data = {
        "child_id": child_id,
        "message": transcribed_text
    }
    
    return await create_conversation(message_data)

@app.get("/api/analytics/emotions")
async def get_emotion_analytics(child_id: str, period: str = "week"):
    """Get emotion analytics"""
    # Mock analytics data
    return {
        "child_id": child_id,
        "period": period,
        "emotions": {
            "happy": 45,
            "excited": 25,
            "curious": 15,
            "calm": 10,
            "playful": 5
        },
        "trend": "positive",
        "total_interactions": len(conversations_db.get(child_id, []))
    }

@app.get("/api/alerts/emergency")
async def get_emergency_alerts(child_id: str):
    """Get emergency alerts"""
    return {
        "alerts": [],
        "total": 0,
        "has_emergency": False
    }

# ============== WebSocket Endpoint ==============
@app.websocket("/ws/{child_id}")
async def websocket_endpoint(websocket: WebSocket, child_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_websockets[child_id] = websocket
    
    try:
        logger.info(f"WebSocket connected for child: {child_id}")
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "child_id": child_id
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif data.get("type") == "message":
                # Create conversation
                message_data = {
                    "child_id": child_id,
                    "message": data.get("message", "")
                }
                response = await create_conversation(message_data)
                
                await websocket.send_json({
                    "type": "response",
                    "data": response
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        if child_id in active_websockets:
            del active_websockets[child_id]
        logger.info(f"WebSocket disconnected for child: {child_id}")

# ============== Main Entry Point ==============
if __name__ == "__main__":
    logger.info("Starting AI Teddy Bear Backend...")
    
    # Create test data
    test_child = ChildProfile(
        id="test-child-123",
        name="Test Child",
        age=5,
        created_at=datetime.now().isoformat()
    )
    children_db[test_child.id] = test_child
    conversations_db[test_child.id] = []
    
    logger.info("Test data created")
    logger.info("Starting server on http://localhost:8000")
    logger.info("API docs available at http://localhost:8000/docs")
    
    # Run server
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 