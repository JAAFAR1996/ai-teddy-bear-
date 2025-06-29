"""
🎤 Voice API Endpoints for AI Teddy Bear
FastAPI endpoints for voice processing and interaction with enhanced STT support
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Query
from typing import Optional, Dict, Any, Union
import base64
import tempfile
import os
import json
import asyncio
from datetime import datetime
from pydantic import BaseModel

from src.infrastructure.modern_container import ModernContainer
from src.application.services.ai.modern_ai_service import ModernAIService
from src.application.services.voice_service import VoiceService, AudioFormat, AudioRequest
from src.domain.services.advanced_emotion_analyzer import AdvancedEmotionAnalyzer

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice Processing"])

# Dependency injection
async def get_ai_service() -> ModernAIService:
    """Get AI service instance"""
    container = ModernContainer()
    return await container.get_ai_service()

async def get_emotion_analyzer() -> AdvancedEmotionAnalyzer:
    """Get emotion analyzer instance"""
    # TODO: Add to container
    return AdvancedEmotionAnalyzer()

async def get_voice_service() -> VoiceService:
    """Get voice service instance"""
    from src.application.services.voice_service import create_voice_service
    return create_voice_service()

# ================ ESP32 AUDIO ENDPOINTS ================

@router.post("/esp32/audio")
async def process_esp32_audio(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    session_id: Optional[str] = Form(None),
    audio_format: str = Form("mp3"),
    language: str = Form("ar"),
    child_name: Optional[str] = Form(None),
    child_age: Optional[int] = Form(None),
    voice_service: VoiceService = Depends(get_voice_service),
    ai_service: ModernAIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    🎤 Process compressed audio from ESP32 devices
    Supports MP3, OGG, WAV formats with advanced STT processing
    
    Args:
        file: Audio file from ESP32
        device_id: ESP32 device identifier
        session_id: Session identifier
        audio_format: Audio format (mp3, ogg, wav)
        language: Expected language (ar, en)
        child_name: Child's name for personalization
        child_age: Child's age for appropriate responses
        
    Returns:
        Comprehensive processing result with transcription and AI response
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"🎤 Processing ESP32 audio from device: {device_id}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read audio data
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"📊 Audio data: {len(audio_bytes)} bytes, format: {audio_format}")
        
        # Convert to base64 for voice service
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Create audio request
        audio_request = AudioRequest(
            audio_data=audio_base64,
            format=AudioFormat(audio_format.lower()),
            device_id=device_id,
            session_id=session_id,
            language=language,
            child_name=child_name,
            child_age=child_age
        )
        
        # Transcribe audio
        transcription_result = await voice_service.process_esp32_audio(audio_request)
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message=transcription_result.text,
            child_profile={
                "name": child_name or "صديقي",
                "age": child_age or 6,
                "language": language,
                "device_id": device_id
            }
        )
        
        # Calculate total processing time
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Return comprehensive result
        result = {
            "success": True,
            "device_id": device_id,
            "session_id": session_id,
            "transcription": {
                "text": transcription_result.text,
                "language": transcription_result.language,
                "confidence": transcription_result.confidence,
                "provider": transcription_result.provider,
                "processing_time_ms": transcription_result.processing_time_ms,
                "audio_duration_ms": transcription_result.audio_duration_ms,
                "segments": transcription_result.segments[:5] if transcription_result.segments else []  # Limit segments
            },
            "ai_response": {
                "text": ai_response.get("text", "مرحباً بك!"),
                "emotion": ai_response.get("emotion", "happy"),
                "category": ai_response.get("category", "conversation"),
                "learning_points": ai_response.get("learning_points", [])
            },
            "performance": {
                "total_processing_time_ms": int(total_time),
                "audio_size_bytes": len(audio_bytes),
                "compression_detected": audio_format.lower() in ["mp3", "ogg"],
                "real_time_factor": total_time / max(transcription_result.audio_duration_ms, 1)
            },
            "metadata": transcription_result.metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ ESP32 audio processed successfully: '{transcription_result.text[:30]}...'")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ESP32 audio processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )

@router.post("/esp32/audio-json") 
async def process_esp32_audio_json(
    request: AudioRequest,
    voice_service: VoiceService = Depends(get_voice_service),
    ai_service: ModernAIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    🎤 Process ESP32 audio via JSON payload (alternative to multipart)
    Useful for WebSocket or direct JSON communication
    
    Args:
        request: Audio request with base64 data
        
    Returns:
        Processing result similar to /esp32/audio
    """
    try:
        logger.info(f"🎤 Processing ESP32 JSON audio from device: {request.device_id}")
        
        # Process audio
        transcription_result = await voice_service.process_esp32_audio(request)
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message=transcription_result.text,
            child_profile={
                "name": request.child_name or "صديقي",
                "age": request.child_age or 6,
                "language": request.language,
                "device_id": request.device_id
            }
        )
        
        return {
            "success": True,
            "transcription": transcription_result.dict(),
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ ESP32 JSON audio processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    device_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    """
    Upload audio file for processing
    
    Args:
        file: Audio file (WAV, MP3, etc.)
        device_id: Device identifier
        session_id: Session identifier
    
    Returns:
        Processing result with transcription and emotion analysis
    """
    try:
        # Validate file type
        allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {allowed_types}"
            )
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        try:
            # Process audio
            result = await process_audio_file(
                temp_path,
                device_id=device_id,
                session_id=session_id
            )
            
            return {
                "status": "success",
                "filename": file.filename,
                "size": len(content),
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
async def transcribe_audio(
    audio_data: Dict[str, Any],
    ai_service: ModernAIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    Transcribe audio to text using speech-to-text service
    
    Args:
        audio_data: Base64 encoded audio or file path
        
    Returns:
        Transcription result
    """
    try:
        # Extract audio
        if "base64" in audio_data:
            audio_bytes = base64.b64decode(audio_data["base64"])
            # Save to temp file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                audio_path = tmp.name
        elif "path" in audio_data:
            audio_path = audio_data["path"]
        else:
            raise ValueError("No audio data provided")
        
        # Transcribe using AI service
        # TODO: Implement actual STT service
        transcription = "مرحبا، كيف حالك اليوم؟"  # Placeholder
        
        # Clean up temp file if created
        if "base64" in audio_data and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "status": "success",
            "transcription": transcription,
            "language": "ar",
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-emotion")
async def analyze_child_emotion(
    file: UploadFile = File(...),
    child_name: str = Form("طفل"),
    child_age: int = Form(6),
    udid: str = Form(...),
    current_container = Depends(get_container)
):
    """
    🎤 تحليل مشاعر الطفل من الصوت مباشرة باستخدام HUME AI
    
    هذا endpoint يحلل الصوت بدون تحويله لنص، 
    ويركز على المشاعر الصوتية المباشرة
    """
    try:
        logger.info(f"🎤 Starting HUME emotion analysis for {child_name} (UDID: {udid})")
        
        # قراءة الملف الصوتي
        audio_data = await file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="ملف صوتي فارغ")
        
        # الحصول على مدير الصوت المتقدم
        audio_manager = current_container.get_service('modern_audio_manager')
        
        # معالجة الصوت مع تحليل المشاعر الكامل
        result = await audio_manager.process_child_voice_with_emotion(
            audio_data=audio_data,
            child_age=child_age,
            child_name=child_name
        )
        
        if result["success"]:
            emotion_analysis = result["emotion_analysis"]
            
            # حفظ نتائج التحليل في قاعدة البيانات
            try:
                emotion_service = current_container.get_service('emotion_service')
                await emotion_service.save_emotion_analysis(
                    udid=udid,
                    child_name=child_name,
                    emotion_data=emotion_analysis,
                    transcription=result.get("transcription", ""),
                    response_text=result.get("response_text", "")
                )
            except Exception as db_error:
                logger.warning(f"Failed to save emotion analysis: {db_error}")
            
            return {
                "success": True,
                "message": f"تم تحليل مشاعر {child_name} بنجاح",
                "emotion_analysis": {
                    "dominant_emotion": emotion_analysis.dominant_emotion,
                    "emotions": {
                        "joy": emotion_analysis.joy,
                        "sadness": emotion_analysis.sadness,
                        "anger": emotion_analysis.anger,
                        "fear": emotion_analysis.fear,
                        "excitement": emotion_analysis.excitement,
                        "curiosity": emotion_analysis.curiosity,
                        "playfulness": emotion_analysis.playfulness,
                        "tiredness": emotion_analysis.tiredness
                    },
                    "confidence": emotion_analysis.confidence,
                    "emotional_intensity": emotion_analysis.emotional_intensity,
                    "energy_level": emotion_analysis.energy_level,
                    "voice_quality": emotion_analysis.voice_quality,
                    "developmental_indicators": emotion_analysis.developmental_indicators
                },
                "transcription": result.get("transcription"),
                "response": {
                    "text": result.get("response_text"),
                    "audio_available": result.get("response_audio") is not None
                },
                "parent_recommendations": result.get("recommendations", []),
                "timestamp": result.get("timestamp")
            }
        else:
            return {
                "success": False,
                "message": "فشل في تحليل المشاعر",
                "error": result.get("error"),
                "fallback_emotion": result.get("fallback_emotion", "curious")
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Emotion analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"خطأ في تحليل المشاعر: {str(e)}"
        )


@router.get("/emotion-history/{udid}")
async def get_child_emotion_history(
    udid: str,
    days: int = Query(7, description="عدد الأيام المراد استرجاعها"),
    current_container = Depends(get_container)
):
    """
    📊 استرجاع تاريخ المشاعر للطفل
    """
    try:
        emotion_service = current_container.get_service('emotion_service')
        
        history = await emotion_service.get_emotion_history(udid, days)
        
        if not history:
            return {
                "success": True,
                "message": "لا توجد بيانات مشاعر متاحة",
                "history": [],
                "summary": None
            }
        
        # تحليل الاتجاهات
        summary = await emotion_service.analyze_emotion_trends(history)
        
        return {
            "success": True,
            "udid": udid,
            "period_days": days,
            "total_interactions": len(history),
            "history": history,
            "summary": summary,
            "recommendations": summary.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting emotion history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في استرجاع تاريخ المشاعر: {str(e)}"
        )


@router.post("/emotion-feedback")
async def submit_emotion_feedback(
    udid: str = Form(...),
    interaction_id: str = Form(...),
    parent_feedback: str = Form(...),
    accuracy_rating: int = Form(..., description="تقييم دقة التحليل من 1-5"),
    current_container = Depends(get_container)
):
    """
    🎯 تقديم تغذية راجعة من الوالدين حول دقة تحليل المشاعر
    هذا يساعد في تحسين دقة النظام مع الوقت
    """
    try:
        if not 1 <= accuracy_rating <= 5:
            raise HTTPException(status_code=400, detail="التقييم يجب أن يكون بين 1 و 5")
        
        emotion_service = current_container.get_service('emotion_service')
        
        await emotion_service.save_parent_feedback(
            udid=udid,
            interaction_id=interaction_id,
            feedback=parent_feedback,
            accuracy_rating=accuracy_rating
        )
        
        return {
            "success": True,
            "message": "تم حفظ التغذية الراجعة بنجاح",
            "thank_you": "شكراً لمساعدتنا في تحسين دقة تحليل مشاعر طفلكم"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في حفظ التغذية الراجعة: {str(e)}"
        )


@router.post("/generate-speech")
async def generate_speech(
    text_data: Dict[str, Any],
    ai_service: ModernAIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    Generate speech from text using TTS service
    
    Args:
        text_data: Text to convert to speech with options
        
    Returns:
        Audio file URL or base64 data
    """
    try:
        text = text_data.get("text", "")
        voice = text_data.get("voice", "teddy_arabic")
        emotion = text_data.get("emotion", "friendly")
        
        if not text:
            raise ValueError("No text provided")
        
        # Generate speech
        # TODO: Implement actual TTS service
        audio_url = f"https://teddy-cdn.com/audio/{datetime.now().timestamp()}.mp3"
        
        return {
            "status": "success",
            "audio_url": audio_url,
            "duration": 5.2,  # Placeholder
            "voice": voice,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def process_audio_file(
    file_path: str,
    device_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process audio file through full pipeline
    """
    # TODO: Implement full audio processing pipeline
    # 1. Transcribe audio to text
    # 2. Analyze emotion from audio
    # 3. Generate AI response
    # 4. Return comprehensive result
    
    return {
        "transcription": "تم استلام الصوت",
        "emotion": "happy",
        "ai_response": "مرحباً! سعيد لسماع صوتك!"
    } 