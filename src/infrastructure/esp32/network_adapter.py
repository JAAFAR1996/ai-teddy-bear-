"""Network adapter for ESP32 teddy bear simulator."""

import structlog
from typing import Dict, Any, Optional
import requests
import threading
import time
import json
from datetime import datetime

logger = structlog.get_logger(__name__)


class NetworkAdapter:
    """Low-level network adapter for ESP32 simulation."""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        self.is_connected = False
        self.connection_timeout = 10
        self.request_timeout = 30
        self.retry_attempts = 3
        self.last_response_time = None
        
        # Connection pool settings
        self.session.headers.update({
            'User-Agent': 'ESP32-TeddyBear-Simulator/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        logger.info(f" Network adapter initialized for {server_url}")
    
    def test_connection(self) -> bool:
        """Test connection to server."""
        try:
            start_time = time.time()
            
            # Try to reach the server
            response = self.session.get(
                f"{self.server_url}/health", 
                timeout=self.connection_timeout
            )
            
            end_time = time.time()
            self.last_response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f" Connection test passed ({self.last_response_time:.1f}ms)")
                return True
            else:
                logger.warning(f" Server returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectException:
            logger.warning(" Cannot connect to server (using mock mode)")
            # In simulation, we'll continue with mock responses
            self.is_connected = False
            self.last_response_time = 100.0  # Mock response time
            return True  # Allow simulation to continue
            
        except requests.exceptions.Timeout:
            logger.error(" Connection timeout")
            return False
            
        except Exception as e:
            logger.error(f" Connection test failed: {e}")
            return False
    
    def send_post_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send POST request to server."""
        try:
            url = f"{self.server_url}{endpoint}"
            
            # Add timestamp to request
            data['timestamp'] = datetime.now().isoformat()
            data['client_type'] = 'ESP32_Simulator'
            
            logger.debug(f" POST {endpoint}: {data.get('type', 'unknown')}")
            
            start_time = time.time()
            
            if self.is_connected:
                # Real request
                response = self.session.post(
                    url,
                    json=data,
                    timeout=self.request_timeout
                )
                
                end_time = time.time()
                self.last_response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f" Response: {result.get('type', 'unknown')}")
                    return result
                else:
                    logger.error(f" Server error: {response.status_code}")
                    return None
            else:
                # Mock response for simulation
                mock_response = self._generate_mock_response(endpoint, data)
                time.sleep(0.1)  # Simulate network delay
                self.last_response_time = 100.0
                logger.debug(f" Mock response: {mock_response.get('type', 'unknown')}")
                return mock_response
                
        except requests.exceptions.Timeout:
            logger.error(f" Request timeout for {endpoint}")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.warning(f" Connection error for {endpoint}, using mock response")
            return self._generate_mock_response(endpoint, data)
            
        except Exception as e:
            logger.error(f" Request failed: {e}")
            return None
    
    def send_get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Send GET request to server."""
        try:
            url = f"{self.server_url}{endpoint}"
            
            logger.debug(f" GET {endpoint}")
            
            start_time = time.time()
            
            if self.is_connected:
                # Real request
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.request_timeout
                )
                
                end_time = time.time()
                self.last_response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f" Response received")
                    return result
                else:
                    logger.error(f" Server error: {response.status_code}")
                    return None
            else:
                # Mock response
                mock_response = self._generate_mock_get_response(endpoint, params)
                time.sleep(0.05)  # Simulate network delay
                self.last_response_time = 50.0
                return mock_response
                
        except Exception as e:
            logger.error(f" GET request failed: {e}")
            return None
    
    def send_websocket_message(self, message: Dict[str, Any]) -> bool:
        """Send WebSocket message (simulated)."""
        try:
            # In a real implementation, this would use websockets library
            logger.debug(f" WebSocket message: {message.get('type', 'unknown')}")
            
            # Simulate WebSocket send
            time.sleep(0.01)  # Very fast for WebSocket
            self.last_response_time = 10.0
            
            return True
            
        except Exception as e:
            logger.error(f" WebSocket send failed: {e}")
            return False
    
    def upload_audio(self, audio_data: bytes, metadata: Dict[str, Any]) -> Optional[str]:
        """Upload audio data to server."""
        try:
            endpoint = "/api/audio/upload"
            
            # Prepare multipart form data
            files = {
                'audio': ('audio.wav', audio_data, 'audio/wav'),
                'metadata': (None, json.dumps(metadata), 'application/json')
            }
            
            logger.info(f" Uploading {len(audio_data)} bytes of audio")
            
            start_time = time.time()
            
            if self.is_connected:
                response = self.session.post(
                    f"{self.server_url}{endpoint}",
                    files=files,
                    timeout=self.request_timeout * 2  # Longer timeout for uploads
                )
                
                end_time = time.time()
                self.last_response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    audio_id = result.get('audio_id')
                    logger.info(f" Audio uploaded: {audio_id}")
                    return audio_id
                else:
                    logger.error(f" Upload failed: {response.status_code}")
                    return None
            else:
                # Mock upload
                time.sleep(0.5)  # Simulate upload time
                mock_id = f"audio_{int(time.time())}"
                logger.info(f" Mock audio uploaded: {mock_id}")
                return mock_id
                
        except Exception as e:
            logger.error(f" Audio upload failed: {e}")
            return None
    
    def download_audio(self, audio_url: str) -> Optional[bytes]:
        """Download audio from URL."""
        try:
            logger.info(f" Downloading audio: {audio_url}")
            
            start_time = time.time()
            
            if self.is_connected and audio_url.startswith('http'):
                response = self.session.get(audio_url, timeout=self.request_timeout)
                
                end_time = time.time()
                self.last_response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    logger.info(f" Downloaded {len(response.content)} bytes")
                    return response.content
                else:
                    logger.error(f" Download failed: {response.status_code}")
                    return None
            else:
                # Mock download
                time.sleep(0.3)
                mock_audio = b'mock_audio_response' * 500
                logger.info(f" Mock downloaded {len(mock_audio)} bytes")
                return mock_audio
                
        except Exception as e:
            logger.error(f" Audio download failed: {e}")
            return None
    
    def send_heartbeat(self, device_info: Dict[str, Any]) -> bool:
        """Send heartbeat to server."""
        try:
            heartbeat_data = {
                'type': 'heartbeat',
                'device_info': device_info,
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.send_post_request('/api/device/heartbeat', heartbeat_data)
            return response is not None
            
        except Exception as e:
            logger.error(f" Heartbeat failed: {e}")
            return False
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get network adapter status."""
        return {
            "server_url": self.server_url,
            "is_connected": self.is_connected,
            "last_response_time_ms": self.last_response_time,
            "connection_timeout": self.connection_timeout,
            "request_timeout": self.request_timeout,
            "retry_attempts": self.retry_attempts
        }
    
    def _generate_mock_response(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response for testing."""
        request_type = data.get('type', 'unknown')
        
        if endpoint == '/api/device/register':
            return {
                'type': 'registration_response',
                'status': 'success',
                'device_id': data.get('device_id'),
                'session_id': f"session_{int(time.time())}",
                'message': 'Device registered successfully'
            }
        
        elif endpoint == '/api/conversation' or request_type == 'conversation':
            return {
                'type': 'ai_response',
                'text': 'مرحبا! كيف يمكنني مساعدتك اليوم',
                'audio_url': None,
                'emotion': 'happy',
                'confidence': 0.95
            }
        
        elif request_type == 'heartbeat':
            return {
                'type': 'heartbeat_response',
                'status': 'ok',
                'server_time': datetime.now().isoformat()
            }
        
        else:
            return {
                'type': 'generic_response',
                'status': 'received',
                'message': 'Mock response',
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_mock_get_response(self, endpoint: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock GET response."""
        if endpoint == '/health':
            return {
                'status': 'healthy',
                'server': 'ESP32-TeddyBear-Server',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        
        elif endpoint.startswith('/api/child/'):
            return {
                'child_id': params.get('child_id', 'mock_child'),
                'name': 'Test Child',
                'age': 7,
                'total_conversations': 25,
                'last_seen': datetime.now().isoformat()
            }
        
        else:
            return {
                'status': 'ok',
                'data': None,
                'timestamp': datetime.now().isoformat()
            }
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'session'):
            self.session.close()
