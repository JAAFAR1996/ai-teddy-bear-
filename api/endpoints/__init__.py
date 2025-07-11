"""API Endpoints Package"""

from .audio import router as audio_router
from .children import router as children_router
from .dashboard import router as dashboard_router
from .device import router as device_router

__all__ = [
    "device_router",
    "audio_router",
    "children_router",
    "dashboard_router"]
