"""
Task processors for text analysis tasks.
"""
import asyncio

from ..models import ProcessingTask


async def process_text_analysis(task: ProcessingTask) -> dict:
    """
    Processes a text analysis task, such as sentiment analysis or
    keyword extraction.
    """
    text = task.payload.get("text")
    if not text:
        raise ValueError("Text is required for analysis.")

    # Mock analysis
    await asyncio.sleep(0.1)

    return {
        "sentiment": "positive",
        "sentiment_score": 0.92,
        "keywords": ["mock", "analysis", "text"],
        "language": "en",
    }
