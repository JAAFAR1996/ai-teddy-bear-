"""
Audio Recorder for AI Teddy Bear UI
Professional audio recording with multiple backend support
"""

import numpy as np
import wave
import io
from datetime import datetime

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

import structlog

logger = structlog.get_logger()


class AudioRecorder:
    """Professional audio recorder with multiple backend support"""
    
    def __init__(self, config):
        self.config = config
        self.audio_stream = None
        self.pyaudio_instance = None
        self._setup_audio_system()
    
    def _setup_audio_system(self):
        """Initialize audio recording system"""
        try:
            if PYAUDIO_AVAILABLE:
                self.pyaudio_instance = pyaudio.PyAudio()
                logger.info("PyAudio initialized successfully")
            elif SOUNDDEVICE_AVAILABLE:
                logger.info("Using SoundDevice for audio")
            else:
                raise Exception("No audio library available")
        except Exception as e:
            logger.error("Failed to initialize audio system", error=str(e))
            raise
    
    def start_recording(self, device_id=None):
        """Start audio recording"""
        try:
            self.config.is_recording = True
            self.config.audio_data = []
            self.config.recording_start_time = datetime.now()
            
            if SOUNDDEVICE_AVAILABLE:
                self._start_sounddevice_recording(device_id)
            elif PYAUDIO_AVAILABLE:
                self._start_pyaudio_recording()
            else:
                raise Exception("No audio library available")
            
            logger.info("Audio recording started", 
                       sample_rate=self.config.sample_rate,
                       channels=self.config.channels)
        except Exception as e:
            logger.error("Failed to start recording", error=str(e))
            self.config.is_recording = False
            raise
    
    def _start_sounddevice_recording(self, device_id):
        """Start recording using SoundDevice"""
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning("SoundDevice status", status=status)
            
            if self.config.is_recording:
                audio_chunk = (indata[:, 0] * 32767).astype(np.int16)
                self.config.audio_data.append(audio_chunk.tobytes())
                
                # Calculate volume level
                volume = np.sqrt(np.mean(audio_chunk**2))
                self.config.volume_level = min(100, (volume / 1000) * 100)
        
        self.audio_stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            callback=audio_callback,
            device=device_id,
            blocksize=self.config.chunk_size
        )
        self.audio_stream.start()
    
    def _start_pyaudio_recording(self):
        """Start recording using PyAudio"""
        def audio_callback(in_data, frame_count, time_info, status):
            if self.config.is_recording:
                self.config.audio_data.append(in_data)
                
                audio_chunk = np.frombuffer(in_data, dtype=np.int16)
                volume = np.sqrt(np.mean(audio_chunk**2))
                self.config.volume_level = min(100, (volume / 1000) * 100)
                
            return (in_data, pyaudio.paContinue)
        
        self.audio_stream = self.pyaudio_instance.open(
            format=self.config.audio_format,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=self.config.chunk_size,
            stream_callback=audio_callback
        )
        self.audio_stream.start_stream()
    
    def stop_recording(self):
        """Stop audio recording"""
        try:
            self.config.is_recording = False
            
            if self.audio_stream:
                if hasattr(self.audio_stream, 'stop'):
                    self.audio_stream.stop()
                    self.audio_stream.close()
                else:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                self.audio_stream = None
            
            logger.info("Audio recording stopped")
        except Exception as e:
            logger.error("Error stopping recording", error=str(e))
            raise
    
    def get_recorded_audio(self) -> bytes:
        """Get recorded audio as WAV data"""
        if not self.config.audio_data:
            return b''
        
        audio_bytes = b''.join(self.config.audio_data)
        return self._create_wav_data(audio_bytes)
    
    def _create_wav_data(self, audio_bytes: bytes) -> bytes:
        """Create WAV file data from raw audio"""
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(audio_bytes)
        
        return wav_buffer.getvalue()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.config.is_recording:
            self.stop_recording()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None 