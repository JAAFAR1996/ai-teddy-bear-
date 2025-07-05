#!/usr/bin/env python3
"""
🏗️ Streaming Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

# Original imports
import asyncio
import json
import logging
import uuid
from asyncio.log import logger
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import websockets


class AudioBuffer:
    """Thread-safe audio buffer for real-time streaming"""

    def __init__(self, max_size: int = 8192, chunk_size: int = 1024):
        self.buffer = deque(maxlen=max_size)
        self._lock = asyncio.Lock()
        self.chunk_size = chunk_size
        self.total_bytes = 0
        self.dropped_bytes = 0

    async def write(self, data: bytes) -> None:
        """Write audio data to buffer"""
        async with self._lock:
            if len(self.buffer) == self.buffer.maxlen:
                dropped = self.buffer.popleft()
                self.dropped_bytes += len(dropped)
            self.buffer.append(data)
            self.total_bytes += len(data)

    async def read(self, size: Optional[int] = None) -> bytes:
        """Read audio data from buffer"""
        async with self._lock:
            if not self.buffer:
                return b""

            size = size or self.chunk_size
            result = b""

            while self.buffer and len(result) < size:
                chunk = self.buffer.popleft()
                if len(result) + len(chunk) <= size:
                    result += chunk
                else:
                    needed = size - len(result)
                    result += chunk[:needed]
                    self.buffer.appendleft(chunk[needed:])
                    break

            return result

    async def clear(self) -> None:
        """Clear the buffer"""
        async with self._lock:
            self.buffer.clear()

    @property
    async def size(self) -> int:
        """Get current buffer size in bytes"""
        async with self._lock:
            return sum(len(chunk) for chunk in self.buffer)



class StreamingService:
    def __init__(self, config=None, stt_service=None, conversation_repo=None):
        self._is_active = True

        self.connections = {}
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # ElevenLabs API configuration
        self.elevenlabs_api_key = self.config.api_keys.ELEVENLABS_API_KEY
        self.default_voice = self.config.speech.voice_name
        self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)

        # WebSocket configuration
        self.ws_host = self.config.server.FLASK_HOST
        self.ws_port = self.config.server.WEBSOCKET_PORT
        self.elevenlabs_ws_url = "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_multilingual_v2"

        # Audio configuration
        self.sample_rate = self.config.voice_settings.VOICE_SAMPLE_RATE
        self.chunk_size = 1024   # غيّرها إذا عندك خيار في الإعدادات
        self.buffer_size = 8192  # غيّرها إذا عندك خيار في الإعدادات

        # Connection management
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.elevenlabs_connection: Optional[WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0

        # Audio buffers
        self.input_buffer = AudioBuffer(self.buffer_size, self.chunk_size)
        self.output_buffer = AudioBuffer(self.buffer_size, self.chunk_size)

        # Services
        self.stt_service = stt_service
        self.llm_factory = LLMServiceFactory(self.config)
        self.moderation_service = ModerationService(self.config)
        if conversation_repo is None:
            raise ValueError(
                "conversation_repo is required for StreamingService")
        self.parent_dashboard = ParentDashboardService(
            self.config, conversation_repo)

        # Session management
        self.session_manager = SessionManager()

        # Stream state
        self.is_streaming = False
        self.stream_task: Optional[asyncio.Task] = None

    @property
    def is_streaming(self) -> Any:
        """Check if service is streaming"""
        return getattr(self, '_is_streaming', False)

    @is_streaming.setter
    def is_streaming(self, value) -> Any:
        self._is_streaming = value

    async def start(self):
        logger.info(f"[START] id={id(self)}, is_active(before)={self._is_active}")

        self.logger.info("Start method called!")
        try:
            # Initialize streaming components
            self._is_active = True
            logger.info(f"[START] id={id(self)}, is_active(after)={self._is_active}")
            self.is_streaming = True
            self.logger.info("Streaming service started")
        except Exception as e:
            self.logger.error(f"Failed to start streaming service: {e}")
            self._is_active = False

    def is_active(self) -> bool:
        """Check if service is active"""
        return self._is_active

    def health_check(self) -> dict:
        logger.info(f"[HEALTH] id={id(self)}, is_active={self._is_active}")
        """Perform health check"""
        return {
            "healthy": self._is_active,
            "status": "active" if self._is_active else "inactive",
            "details": {
                "websocket_connected": hasattr(self, 'elevenlabs_connection') and self.elevenlabs_connection is not None,
                "audio_stream_active": self.is_streaming
            }
        }

    async def stop(self):
        """Stop the streaming service"""
        try:
            self._is_active = False
            self.is_streaming = False

            # Cancel stream task
            if self.stream_task:
                self.stream_task.cancel()

            # Close WebSocket connections
            for connection in self.active_connections:
                await connection.close()

            # Close ElevenLabs connection
            if self.elevenlabs_connection:
                await self.elevenlabs_connection.close()

            self.logger.info("StreamingService stopped")

        except Exception as e:
            self.logger.error(f"Error stopping StreamingService: {e}")

    async def start_websocket_server(self):
        """Start WebSocket server for client connections"""
        async def server():
            async with websockets.serve(
                self.handle_client_connection,
                self.ws_host,
                self.ws_port
            ):
                self.logger.info(
                    f"WebSocket server started on {self.ws_host}:{self.ws_port}")
                await asyncio.Future()  # run forever

        asyncio.create_task(server())

    async def handle_client_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connection from client"""
        session_id = str(uuid.uuid4())
        self.active_connections.add(websocket)

        try:
            self.logger.info(f"Client connected: {session_id}")

            # Send welcome message
            await websocket.send(json.dumps({
                "type": "connection",
                "status": "connected",
                "session_id": session_id
            }))

            # Handle messages
            async for message in websocket:
                await self.process_client_message(websocket, message, session_id)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {session_id}")

        finally:
            self.active_connections.discard(websocket)
            self.session_manager.end_session(session_id)

    async def process_client_message(self, websocket: WebSocketServerProtocol, message: str, session_id: str):
        """Process message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            logger.info(f"[TEST] Received message type: {message_type}")

            if message_type == 'ping':
                # Handle ping test
                await websocket.send(json.dumps({
                    "type": "pong",
                    "message": "WebSocket connection working!"
                }))
                logger.info("[TEST] Sent pong response")

            elif message_type == 'audio':
                # Handle audio data
                audio_data = base64.b64decode(data['audio'])
                await self.process_audio_input(audio_data, session_id, websocket)

            elif message_type == 'text':
                # Handle text input
                text = data.get('text', '')
                await self.process_text_input(text, session_id, websocket)

            elif message_type == 'control':
                # Handle control commands
                command = data.get('command')
                await self.handle_control_command(command, session_id, websocket)

        except Exception as e:
            self.logger.error(f"Error processing client message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def connect_to_elevenlabs(self):
        """Connect to ElevenLabs WebSocket API"""
        try:
            voice_id = await self.get_voice_id(self.default_voice)
            url = self.elevenlabs_ws_url.format(voice_id=voice_id)

            headers = {
                "xi-api-key": self.elevenlabs_api_key,
            }

            self.elevenlabs_connection = await websockets.connect(url, extra_headers=headers)

            # Send initial configuration
            await self.elevenlabs_connection.send(json.dumps({
                "text": " ",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.0,
                    "use_speaker_boost": True
                },
                "xi_api_key": self.elevenlabs_api_key,
            }))

            # Start listening for audio
            asyncio.create_task(self.listen_to_elevenlabs())

            self.logger.info("Connected to ElevenLabs streaming API")

        except Exception as e:
            self.logger.error(f"Failed to connect to ElevenLabs: {e}")
            await self.handle_elevenlabs_reconnect()

    async def listen_to_elevenlabs(self):
        """Listen for audio data from ElevenLabs"""
        try:
            async for message in self.elevenlabs_connection:
                if isinstance(message, bytes):
                    # Audio data
                    await self.output_buffer.write(message)
                    await self.broadcast_audio(message)
                else:
                    # JSON message
                    data = json.loads(message)
                    if data.get('audio'):
                        audio_bytes = base64.b64decode(data['audio'])
                        await self.output_buffer.write(audio_bytes)
                        await self.broadcast_audio(audio_bytes)

        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("ElevenLabs connection closed")
            await self.handle_elevenlabs_reconnect()

        except Exception as e:
            self.logger.error(f"Error in ElevenLabs listener: {e}")
            await self.handle_elevenlabs_reconnect()

    async def handle_elevenlabs_reconnect(self):
        """Handle reconnection to ElevenLabs with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return

        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))

        self.logger.info(
            f"Reconnecting to ElevenLabs in {delay}s (attempt {self.reconnect_attempts})")
        await asyncio.sleep(delay)

        await self.connect_to_elevenlabs()

        # Reset counter on successful connection
        self.reconnect_attempts = 0

    async def stream_text_to_speech(self, text: str):
        """Stream text to ElevenLabs for TTS"""
        if not self.elevenlabs_connection:
            await self.connect_to_elevenlabs()

        try:
            # Send text for streaming
            await self.elevenlabs_connection.send(json.dumps({
                "text": text,
                "try_trigger_generation": True
            }))

        except Exception as e:
            self.logger.error(f"Error streaming text to speech: {e}")
            await self.handle_elevenlabs_reconnect()

    async def process_audio_input(self, audio_data: bytes, session_id: str, websocket: Optional[WebSocketServerProtocol] = None):
        """Process incoming audio data"""
        logger.debug("[DEBUG] دخل process_audio_input")
        try:
            # Set processing state
            state_manager.set_processing(True)

            # Add to input buffer
            await self.input_buffer.write(audio_data)
            # Process with STT when buffer has enough data
            buffer_size = await self.input_buffer.size
            logger.info()
                f"[DEBUG] بعد إضافة الصوت: buffer_size={buffer_size}, chunk_size={self.chunk_size}")
            if buffer_size >= self.chunk_size:
                audio_chunk = await self.input_buffer.read(buffer_size)
                logger.info()
                    f"[DEBUG] buffer_size={buffer_size}, chunk_size={self.chunk_size}, audio_chunk len={len(audio_chunk)}")

                # Convert to text
                if self.stt_service:
                    logger.debug("[DEBUG] قبل استدعاء stt_service.transcribe")
                    text = await self.stt_service.transcribe(audio_chunk)
                    logger.info()
                        f"[DEBUG] بعد استدعاء stt_service.transcribe: {text}")
                    if text:
                        await self.process_text_input(text, session_id, websocket)

            # Clear processing state
            state_manager.set_processing(False)

        except Exception as e:
            self.logger.error(f"Error processing audio input: {e}")

    async def process_text_input(self, text: str, session_id: str, websocket=None):
        """Process text input and generate response"""
        logger.debug(f"[DEBUG] دخل process_text_input: text={text}")
        try:
            # Get LLM response
            response = await self.get_llm_response(text, session_id)
            logger.debug(f"[DEBUG] الرد من LLM: {response}")

            # تحويل النص إلى صوت
            audio_bytes = None
            audio_format = "wav"

            # Define availability flags for TTS providers
            try:
            except ImportError:

            try:
            except ImportError:

            # محاولة استخدام ElevenLabs
            if self.elevenlabs_api_key and ELEVENLABS_AVAILABLE:
                try:
                    logger.debug("[DEBUG] استخدام ElevenLabs لتحويل النص...")

                    audio_bytes = await asyncio.to_thread(
                        generate,
                        text=response,
                        voice=self.default_voice or "Rachel",
                        model="eleven_multilingual_v2",
                        api_key=self.elevenlabs_api_key
                    )
                    audio_format = "mp3"  # ElevenLabs يرجع MP3
                    logger.info()
                        f"[DEBUG] نجح ElevenLabs - حجم الصوت: {len(audio_bytes)}")

                except Exception as e:
    logger.error(f"Error: {e}")f"[DEBUG] فشل ElevenLabs: {e}")
                    audio_bytes = None

            # استخدام gTTS كبديل
            if audio_bytes is None and GTTS_AVAILABLE:
                try:

                    logger.debug("[DEBUG] استخدام gTTS كبديل...")
                    tts = gTTS(text=response, lang='ar')
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    audio_bytes = audio_buffer.read()
                    audio_format = "mp3"
                    logger.debug(f"[DEBUG] نجح gTTS - حجم الصوت: {len(audio_bytes)}")

                except Exception as e:
    logger.error(f"Error: {e}")f"[DEBUG] فشل gTTS: {e}")

            # إرسال الرد
            if audio_bytes and websocket:
                response_data = {
                    "type": "audio",
                    # حقل 'audio' وليس 'audio_data'
                    "audio": base64.b64encode(audio_bytes).decode("utf-8"),
                    "format": audio_format,
                    "text": text,  # النص الأصلي من المستخدم
                    "response": response,  # رد الذكاء الاصطناعي
                    "timestamp": datetime.now().isoformat()
                }

                logger.info()
                    f"[DEBUG] إرسال رد بحجم: {len(response_data['audio'])} حرف")
                await websocket.send(json.dumps(response_data))
                logger.debug("[DEBUG] ✅ تم إرسال الرد بنجاح!")

            elif not audio_bytes:
                logger.error("[DEBUG] ❌ فشل توليد الصوت!")
                if websocket:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "عذراً، فشل تحويل النص إلى صوت. حاول مرة أخرى."
                    }))
            else:
                logger.error("[DEBUG] ❌ لا يوجد websocket للإرسال!")

        except Exception as e:
            self.logger.error(f"Error processing text input: {e}")
            traceback.print_exc()

            if websocket:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"خطأ في معالجة النص: {str(e)}"
                }))

    async def get_voice_id(self, voice_name: str) -> str:
        """Get voice ID from voice name"""
        try:
            voices = await asyncio.to_thread(self.elevenlabs_client.voices.get_all)
            for voice in voices.voices:
                if voice.name.lower() == voice_name.lower():
                    return voice.voice_id

            # Default voice if not found
            return voices.voices[0].voice_id if voices.voices else None

        except Exception as e:
            self.logger.error(f"Error getting voice ID: {e}")
            raise

    async def tts_elevenlabs(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs"""
        try:

            audio = await asyncio.to_thread(
                generate,
                text=text,
                voice=self.default_voice,
                model="eleven_multilingual_v2"
            )
            return audio
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            return b""

    # باقي الـ methods من الكود الأصلي (get_llm_response, etc.)
    async def get_llm_response(self, text: str, session_id: str = None, retry_count: int = 0) -> str:
        """Get response from LLM for the given text"""
        # الكود الموجود سابقاً
        try:
            # Check content moderation if enabled
            if self.moderation_service:
                moderation_result = await self.moderation_service.check_content(text)
                if not moderation_result['allowed']:
                    self.logger.warning(
                        f"Content moderation blocked message: {moderation_result['reason']}")
                    return "عذراً، لا يمكنني الإجابة على هذا السؤال. هل يمكنك طرح سؤال آخر؟"

            # تحديد المزود
            provider = LLMProvider.OPENAI

            # بناء السياق
            history = []
            session = self.session_manager.get_session(session_id)
            if session:
                for msg in self.session_manager.session_history.get(session_id, [])[-5:]:
                    if msg['type'] == 'user_audio':
                        history.append(
                            Message(role='user', content=msg['content']))
                    elif msg['type'] == 'assistant':
                        history.append(
                            Message(role='assistant', content=msg['content']))

            history.append(Message(role='user', content=text))
            history.insert(0, Message(
                role='system', content="أنت مساعد ذكي ودود للأطفال. أجب باختصار وبلغة عربية سهلة."))

            conversation = Conversation(messages=history)

            # استدعاء المصنع
            llm_response = await self.llm_factory.generate_response(
                conversation,
                provider=provider,
                max_tokens=150,
                temperature=0.7
            )

            # Check response moderation
            if self.moderation_service:
                moderation_result = await self.moderation_service.check_content(llm_response)
                if not moderation_result['allowed']:
                    self.logger.warning(
                        f"LLM response blocked by moderation: {moderation_result['reason']}")
                    return "عذراً، لا يمكنني الإجابة على هذا السؤال بشكل مناسب. هل يمكنك طرح سؤال آخر؟"

            # Log to session
            if session_id:
                self.session_manager.add_message(
                    session_id, "assistant", llm_response)

                # Log to parent dashboard
                if self.parent_dashboard:
                    user_id = self.session_manager.get_session(
                        session_id).get('user_id')
                    if user_id:
                        await self.parent_dashboard.log_interaction(
                            user_id=user_id,
                            child_message=text,
                            assistant_message=llm_response,
                            timestamp=datetime.now()
                        )

            return llm_response

        except Exception as e:
            self.logger.error(f"LLM response error: {e}")

            # Retry logic
            if retry_count < 2:
                # ... الكود الموجود للـ retry
                pass

            return "عذراً، لم أستطع فهم ما تقول. هل يمكنك إعادة المحاولة؟"

    async def get_streaming_status(self, session_id: str) -> dict:
        """Get streaming status from repository with input validation"""
        if not isinstance(session_id, str) or not session_id:
            self.logger.error("Invalid session_id for get_streaming_status")
            return {"status": "error", "reason": "Invalid session_id"}
        if hasattr(self, 'streaming_repository'):
            return await self.streaming_repository.get_status(session_id)
        self.logger.error("streaming_repository not configured")
        return {"status": "error", "reason": "Repository not configured"}