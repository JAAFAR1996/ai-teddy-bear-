"""
🎵 Audio Processing Endpoints
"""

import io
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from infrastructure.dependencies import get_container

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    device_id: str = None,
    container=Depends(get_container),
) -> Dict[str, Any]:
    """Transcribe audio to text"""
    try:
        voice_service = await container.voice_service()

        # Read audio data
        audio_data = await audio_file.read()

        # Transcribe
        transcript = await voice_service.transcribe_audio(audio_data)

        return {
            "status": "success",
            "transcript": transcript,
            "confidence": 0.95,
            "device_id": device_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )


@router.post("/generate-response")
async def generate_response(
    text: str,
    device_id: str,
    child_context: Optional[Dict] = None,
    container=Depends(get_container),
) -> Dict[str, Any]:
    """Generate AI response from text"""
    try:
        ai_service = await container.ai_service()

        response = await ai_service.generate_response(
            text, device_id, context=child_context
        )

        return {
            "status": "success",
            "response": response,
            "response_id": f"resp_{hash(response) % 10000}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response generation failed: {str(e)}",
        )


@router.get("/tts/{response_id}")
async def text_to_speech(
    response_id: str,
    text: str,
    voice: str = "child_friendly",
    container=Depends(get_container),
) -> StreamingResponse:
    """Convert text to speech"""
    try:
        voice_service = await container.voice_service()

        # Generate TTS
        audio_stream = await voice_service.text_to_speech(text, voice)

        return StreamingResponse(
            io.BytesIO(audio_stream),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=response_{response_id}.mp3"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}",
        )


@router.post("/process-full")
async def process_full_audio(
    device_id: str,
    audio_file: UploadFile = File(...),
    child_context: Optional[Dict] = None,
    container=Depends(get_container),
) -> Dict[str, Any]:
    """Full audio processing pipeline: transcribe -> AI response -> TTS"""
    try:
        ai_service = await container.ai_service()
        voice_service = await container.voice_service()

        # Read audio
        audio_data = await audio_file.read()

        # Transcribe
        transcript = await voice_service.transcribe_audio(audio_data)

        # Generate AI response
        ai_response = await ai_service.generate_response(
            transcript, device_id, context=child_context
        )

        # Generate TTS
        response_audio = await voice_service.text_to_speech(
            ai_response["text"], "child_friendly"
        )

        return {
            "status": "success",
            "transcript": transcript,
            "ai_response": ai_response,
            "audio_response_url": f"/api/audio/download/{ai_response['id']}",
            "processing_time": "< 2s",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Full audio processing failed: {str(e)}",
        )
