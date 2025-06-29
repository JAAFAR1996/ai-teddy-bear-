from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from datetime import datetime
import jwt
import base64
import logging

logger = logging.getLogger(__name__)
active_sessions = {}

def register_websocket_handlers(socketio):
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect', namespace='/ws')
    def handle_connect():
        """Handle WebSocket connection"""
        try:
            # Validate connection token
            token = request.args.get('token')
            if not token:
                disconnect()
                return False
            
            # Mock token validation - replace with actual JWT decode
            session_id = f"session_{request.sid}"
            child_id = "child_default"
            
            # Join room based on session
            join_room(session_id)
            
            # Store session info
            session_data = {
                'session_id': session_id,
                'child_id': child_id,
                'connected_at': datetime.utcnow(),
                'client_id': request.sid
            }
            active_sessions[session_id] = session_data
            
            # Send connection confirmation
            emit('connected', {
                'session_id': session_id,
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"WebSocket connected: session={session_id}, client={request.sid}")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            disconnect()
            return False

    @socketio.on('audio_stream', namespace='/ws')
    def handle_audio_stream(data):
        """Handle real-time audio streaming"""
        try:
            session_id = data.get('session_id')
            audio_chunk = data.get('audio_chunk')  # Base64 encoded audio
            chunk_index = data.get('chunk_index')
            
            if session_id not in active_sessions:
                emit('error', {'message': 'Invalid session'})
                return
            
            # Mock audio processing
            emit('chunk_processed', {
                'chunk_index': chunk_index,
                'status': 'processed',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Mock transcription response
            if chunk_index % 5 == 0:  # Every 5th chunk
                emit('transcription', {
                    'text': 'مرحبا، كيف حالك؟',
                    'confidence': 0.95,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Mock AI response
            if chunk_index % 10 == 0:  # Every 10th chunk
                emit('ai_response', {
                    'text': 'أهلاً بك! أنا بخير، شكراً لك',
                    'emotion': 'happy',
                    'audio_url': '/audio/response.mp3',
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Audio stream error: {e}")
            emit('error', {'message': 'Audio processing failed'})

    @socketio.on('disconnect', namespace='/ws')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        try:
            # Find and clean up session
            for session_id, session_data in list(active_sessions.items()):
                if session_data.get('client_id') == request.sid:
                    # Remove from active sessions
                    del active_sessions[session_id]
                    
                    # Leave room
                    leave_room(session_id)
                    
                    logger.info(f"WebSocket disconnected: session={session_id}, client={request.sid}")
                    break
                    
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

    return socketio