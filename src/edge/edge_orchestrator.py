import asyncio
from typing import Any, Dict, Optional

from .device_manager import DeviceManager
from .edge_processor import EdgeProcessor


class EdgeOrchestrator:
    """Orchestrate edge and cloud processing"""

    def __init__(self, cloud_client):
        self.device_manager = DeviceManager()
        self.edge_processor = None
        self.cloud_client = cloud_client
        self._initialized = False

    async def initialize(self):
        """Initialize edge orchestrator"""
        if self._initialized:
            return

        # Detect device capabilities
        capabilities = await self.device_manager.detect_capabilities()

        # Initialize edge processor
        device_id = f"device_{hash(str(capabilities))}"
        self.edge_processor = EdgeProcessor(device_id, capabilities)
        await self.edge_processor.initialize()

        self._initialized = True

    async def process_request(self, audio_data, request_type: str = "conversation") -> Dict[str, Any]:
        """Process request using edge-first approach"""
        if not self._initialized:
            await self.initialize()

        # Check device resources
        resources = await self.device_manager.monitor_resources()
        if self.device_manager.should_throttle(resources):
            # Skip edge processing if device is overloaded
            return await self._process_cloud_only(audio_data, request_type)

        # Try edge processing first
        edge_results = await self.edge_processor.process_audio_edge(audio_data)

        # Decide if cloud processing is needed
        if await self.edge_processor.should_process_cloud(edge_results):
            cloud_results = await self._process_cloud(audio_data, edge_results, request_type)
            return self._merge_results(edge_results, cloud_results)

        # Return edge-only results
        return self._format_edge_results(edge_results)

    async def _process_cloud(self, audio_data, edge_results: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Process request in cloud with edge context"""
        try:
            # Send to cloud with edge context
            cloud_request = {"audio_data": audio_data, "edge_context": edge_results, "request_type": request_type}

            return await self.cloud_client.process_audio(cloud_request)
        except Exception as e:
            # Fallback to edge-only processing
            return {"error": str(e), "fallback": True}

    async def _process_cloud_only(self, audio_data, request_type: str) -> Dict[str, Any]:
        """Process request in cloud only"""
        return await self.cloud_client.process_audio({"audio_data": audio_data, "request_type": request_type})

    def _merge_results(self, edge_results: Dict[str, Any], cloud_results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge edge and cloud processing results"""
        merged = {
            "transcription": cloud_results.get("transcription", ""),
            "response": cloud_results.get("response", ""),
            "emotion": edge_results.get("emotion", cloud_results.get("emotion")),
            "confidence": cloud_results.get("confidence", 0.5),
            "processing_location": "hybrid",
            "edge_detected": edge_results,
        }

        return merged

    def _format_edge_results(self, edge_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format edge-only results"""
        return {
            "transcription": "",
            "response": "معذرة، لم أتمكن من فهم ما قلته",
            "emotion": edge_results.get("emotion", "neutral"),
            "confidence": 0.3,
            "processing_location": "edge_only",
        }
