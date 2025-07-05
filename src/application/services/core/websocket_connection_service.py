import asyncio
import base64
import json
import logging
import uuid
from typing import Optional, Set

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.server import WebSocketServerProtocol


class WebSocketConnectionService:
    """
    Dedicated service for WebSocket connection management.
    EXTRACTED CLASS to resolve Low Cohesion - Single Responsibility: WebSocket Management
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.elevenlabs_connection: Optional[WebSocketClientProtocol] = None
        self.logger = logging.getLogger(self.__class__.__name__)

        # Connection management
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0

    async def start_server(self, message_handler):
        """Start WebSocket server for client connections"""

        async def server():
            async with websockets.serve(
                lambda ws, path: self.handle_client_connection(
                    ws, path, message_handler
                ),
                self.host,
                self.port,
            ):
                self.logger.info(
                    f"WebSocket server started on {self.host}:{self.port}")
                await asyncio.Future()  # run forever

        asyncio.create_task(server())

    async def handle_client_connection(
        self, websocket: WebSocketServerProtocol, path: str, message_handler
    ):
        """Handle incoming WebSocket connection from client"""
        session_id = str(uuid.uuid4())
        self.active_connections.add(websocket)

        try:
            self.logger.info(f"Client connected: {session_id}")

            # Send welcome message
            await self.send_welcome_message(websocket, session_id)

            # Handle messages
            async for message in websocket:
                await message_handler(websocket, message, session_id)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {session_id}")
        except Exception as e:
            self.logger.error(f"Error handling client connection: {e}")
            await self.send_error_message(websocket, str(e))
        finally:
            self.active_connections.discard(websocket)

    async def send_welcome_message(
        self, websocket: WebSocketServerProtocol, session_id: str
    ):
        """Send welcome message to new client"""
        welcome_data = {
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await self.send_json_message(websocket, welcome_data)

    async def send_json_message(
            self,
            websocket: WebSocketServerProtocol,
            data: dict):
        """Send JSON message to client"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            self.logger.error(f"Error sending JSON message: {e}")

    async def send_error_message(
        self, websocket: WebSocketServerProtocol, error_message: str
    ):
        """Send error message to client"""
        error_data = {
            "type": "error",
            "message": error_message,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await self.send_json_message(websocket, error_data)

    async def broadcast_message(self, data: dict):
        """Broadcast message to all active connections"""
        if not self.active_connections:
            return

        # Create list of tasks for parallel sending
        send_tasks = []
        for (
            connection
        ) in (
            self.active_connections.copy()
        ):  # Copy to avoid modification during iteration
            task = asyncio.create_task(
                self._safe_send_to_connection(
                    connection, data))
            send_tasks.append(task)

        # Wait for all sends to complete
        if send_tasks:
            await asyncio.gather(*send_tasks, return_exceptions=True)

    async def _safe_send_to_connection(
        self, connection: WebSocketServerProtocol, data: dict
    ):
        """Safely send message to a connection, removing if failed"""
        try:
            await self.send_json_message(connection, data)
        except Exception as e:
            self.logger.warning(f"Failed to send to connection, removing: {e}")
            self.active_connections.discard(connection)

    async def broadcast_audio(self, audio_data: bytes):
        """Broadcast audio data to all active connections"""
        if not self.active_connections:
            return

        audio_message = {
            "type": "audio_stream",
            "audio": base64.b64encode(audio_data).decode("utf-8"),
            "timestamp": asyncio.get_event_loop().time(),
        }
        await self.broadcast_message(audio_message)

    async def connect_to_elevenlabs(
            self,
            api_key: str,
            voice_id: str,
            model_id: str = "eleven_multilingual_v2"):
        """Connect to ElevenLabs WebSocket API"""
        try:
            url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
            headers = {"xi-api-key": api_key}

            self.elevenlabs_connection = await websockets.connect(
                url, extra_headers=headers
            )

            # Send initial configuration
            await self._send_elevenlabs_config(api_key)

            # Start listening for audio
            asyncio.create_task(self.listen_to_elevenlabs())

            self.logger.info("Connected to ElevenLabs streaming API")

        except Exception as e:
            self.logger.error(f"Failed to connect to ElevenLabs: {e}")
            await self.handle_elevenlabs_reconnect(api_key, voice_id, model_id)

    async def _send_elevenlabs_config(self, api_key: str):
        """Send initial configuration to ElevenLabs"""
        config = {
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True,
            },
            "xi_api_key": api_key,
        }
        await self.elevenlabs_connection.send(json.dumps(config))

    async def listen_to_elevenlabs(self):
        """Listen for audio data from ElevenLabs"""
        try:
            async for message in self.elevenlabs_connection:
                await self._process_elevenlabs_message(message)

        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("ElevenLabs connection closed")
        except Exception as e:
            self.logger.error(f"Error in ElevenLabs listener: {e}")

    async def _process_elevenlabs_message(self, message):
        """Process message received from ElevenLabs"""
        if isinstance(message, bytes):
            # Audio data
            await self.broadcast_audio(message)
        else:
            # JSON message
            try:
                data = json.loads(message)
                if data.get("audio"):
                    audio_bytes = base64.b64decode(data["audio"])
                    await self.broadcast_audio(audio_bytes)
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid JSON from ElevenLabs: {message}")

    async def handle_elevenlabs_reconnect(
        self, api_key: str, voice_id: str, model_id: str
    ):
        """Handle reconnection to ElevenLabs with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("Max ElevenLabs reconnection attempts reached")
            return

        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))

        self.logger.info(
            f"Reconnecting to ElevenLabs in {delay}s (attempt {self.reconnect_attempts})"
        )
        await asyncio.sleep(delay)

        await self.connect_to_elevenlabs(api_key, voice_id, model_id)

        # Reset counter on successful connection
        self.reconnect_attempts = 0

    async def stream_text_to_elevenlabs(self, text: str):
        """Stream text to ElevenLabs for TTS"""
        if not self.elevenlabs_connection:
            self.logger.warning("ElevenLabs connection not available")
            return

        try:
            # Send text for streaming
            await self.elevenlabs_connection.send(
                json.dumps({"text": text, "try_trigger_generation": True})
            )

        except Exception as e:
            self.logger.error(f"Error streaming text to ElevenLabs: {e}")

    async def close_all_connections(self):
        """Close all active connections"""
        # Close client connections
        close_tasks = []
        for connection in self.active_connections.copy():
            task = asyncio.create_task(connection.close())
            close_tasks.append(task)

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        self.active_connections.clear()

        # Close ElevenLabs connection
        if self.elevenlabs_connection:
            await self.elevenlabs_connection.close()
            self.elevenlabs_connection = None

    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "active_client_connections": len(self.active_connections),
            "elevenlabs_connected": self.elevenlabs_connection is not None,
            "reconnect_attempts": self.reconnect_attempts,
            "server_host": self.host,
            "server_port": self.port,
        }
