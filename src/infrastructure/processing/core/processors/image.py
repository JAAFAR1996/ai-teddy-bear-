"""
Task processors for image-related tasks.
"""
import asyncio

try:
    from PIL import Image
    HAS_IMAGING_LIBS = True
except ImportError:
    HAS_IMAGING_LIBS = False

from ..models import ProcessingTask


async def process_image_generation(task: ProcessingTask) -> dict:
    """
    Processes an image generation task. In a real implementation, this would
    integrate with a service like DALL-E or Stable Diffusion.
    """
    prompt = task.payload.get("prompt")
    if not prompt:
        raise ValueError("A prompt is required for image generation.")

    # Mock image generation
    await asyncio.sleep(2.5)  # Simulate longer generation time

    return {
        "image_url": f"https://example.com/generated/{task.id}.png",
        "prompt_used": prompt,
        "model": "dall-e-3",
    }


async def process_image_processing(task: ProcessingTask) -> dict:
    """
    Processes an image manipulation task, such as resizing or applying a filter.
    Requires imaging libraries like Pillow.
    """
    if not HAS_IMAGING_LIBS:
        raise RuntimeError(
            "Image processing libraries (e.g., Pillow) are not installed.")

    operation = task.payload.get("operation")
    if not operation:
        raise ValueError(
            "An operation (e.g., 'resize', 'grayscale') is required.")

    # Mock image processing
    await asyncio.sleep(0.3)

    return {
        "processed_image_path": f"/path/to/mock/processed_{task.id}.jpg",
        "operation_performed": operation,
        "status": "success",
    }
