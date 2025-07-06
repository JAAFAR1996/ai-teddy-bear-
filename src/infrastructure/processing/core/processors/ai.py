"""
Task processors for AI-related tasks.
"""
import asyncio

from ..models import ProcessingTask


async def process_ai_response(task: ProcessingTask) -> dict:
    """
    Processes a request to generate an AI response. In a real implementation,
    this would call a large language model API (e.g., OpenAI, Anthropic).
    """
    prompt = task.payload.get("prompt")
    if not prompt:
        raise ValueError("A prompt is required for AI response generation.")

    model = task.payload.get("model", "gpt-4-turbo")

    # Mock AI response generation
    await asyncio.sleep(0.8)  # Simulate API latency

    return {
        "response_text": f"This is a mock AI response to the prompt: '{prompt[:50]}...'",
        "model_used": model,
        "tokens_consumed": 256,
        "finish_reason": "stop",
    }


async def process_emotion_analysis(task: ProcessingTask) -> dict:
    """
    Processes an emotion analysis task from text or audio. In a real
    implementation, this would use a specialized service like Hume AI.
    """
    if not task.payload.get("text") and not task.payload.get("audio_data"):
        raise ValueError(
            "Text or audio data is required for emotion analysis.")

    # Mock emotion analysis
    await asyncio.sleep(0.4)  # Simulate API latency

    return {
        "dominant_emotion": "joy",
        "emotion_scores": {
            "joy": 0.85,
            "sadness": 0.05,
            "anger": 0.02,
            "surprise": 0.08,
        },
        "analysis_source": "text" if task.payload.get("text") else "audio",
    }
