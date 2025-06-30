"""
🔐 Audio Security - AES-256-GCM Encryption
===========================================

Author: Jaafar Adeeb - Security Lead
"""

import os
import secrets
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

logger = structlog.get_logger(__name__)


@dataclass
class AudioSession:
    """Audio encryption session"""
    session_id: str
    device_id: str
    user_id: str
    encryption_key: bytes
    created_at: datetime
    expires_at: datetime


class AudioEncryptionManager:
    """Audio encryption with AES-256-GCM"""
    
    def __init__(self):
        self.active_sessions: Dict[str, AudioSession] = {}
        self.master_key = self._get_master_key()
    
    def _get_master_key(self) -> bytes:
        """Get or generate master key"""
        # In production, load from Vault
        return secrets.token_bytes(32)  # 256-bit key
    
    async def create_session(self, device_id: str, user_id: str) -> str:
        """Create new encryption session"""
        
        session_id = f"audio_{secrets.token_hex(16)}"
        
        # Derive session key
        session_key = self._derive_key(session_id, device_id, user_id)
        
        session = AudioSession(
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
            encryption_key=session_key,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.active_sessions[session_id] = session
        
        logger.info("Audio session created", 
                   session_id=session_id,
                   device_id=device_id)
        
        return session_id
    
    def _derive_key(self, session_id: str, device_id: str, user_id: str) -> bytes:
        """Derive session-specific key"""
        
        # Simple key derivation (in production, use HKDF)
        data = f"{session_id}:{device_id}:{user_id}".encode()
        key_material = hashlib.pbkdf2_hmac('sha256', data, self.master_key, 100000)
        return key_material[:32]  # 256-bit key
    
    async def encrypt_audio(self, session_id: str, audio_data: bytes) -> Dict[str, str]:
        """Encrypt audio data"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session = self.active_sessions[session_id]
        
        # Check expiration
        if datetime.utcnow() > session.expires_at:
            raise ValueError("Session expired")
        
        # Generate nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        # Encrypt with AES-GCM
        cipher = AESGCM(session.encryption_key)
        encrypted_data = cipher.encrypt(nonce, audio_data, None)
        
        logger.debug("Audio encrypted", 
                    session_id=session_id,
                    size=len(audio_data))
        
        return {
            'session_id': session_id,
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def decrypt_audio(self, encrypted_packet: Dict[str, str]) -> bytes:
        """Decrypt audio data"""
        
        session_id = encrypted_packet['session_id']
        
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session = self.active_sessions[session_id]
        
        # Decrypt data
        encrypted_data = base64.b64decode(encrypted_packet['encrypted_data'])
        nonce = base64.b64decode(encrypted_packet['nonce'])
        
        cipher = AESGCM(session.encryption_key)
        decrypted_data = cipher.decrypt(nonce, encrypted_data, None)
        
        logger.debug("Audio decrypted", 
                    session_id=session_id,
                    size=len(decrypted_data))
        
        return decrypted_data
    
    async def close_session(self, session_id: str) -> bool:
        """Close encryption session"""
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info("Audio session closed", session_id=session_id)
            return True
        
        return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        
        now = datetime.utcnow()
        expired = []
        
        for session_id, session in self.active_sessions.items():
            if now > session.expires_at:
                expired.append(session_id)
        
        for session_id in expired:
            await self.close_session(session_id)
        
        return len(expired)


# Global instance
_audio_manager: Optional[AudioEncryptionManager] = None


def get_audio_encryption_manager() -> AudioEncryptionManager:
    """Get global audio encryption manager"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioEncryptionManager()
    return _audio_manager


# Convenience functions

async def encrypt_child_audio(device_id: str, user_id: str, audio_data: bytes) -> Dict[str, str]:
    """Encrypt audio from child device"""
    manager = get_audio_encryption_manager()
    
    # Create or reuse session
    session_id = await manager.create_session(device_id, user_id)
    
    return await manager.encrypt_audio(session_id, audio_data)


async def decrypt_child_audio(encrypted_packet: Dict[str, str]) -> bytes:
    """Decrypt child audio data"""
    manager = get_audio_encryption_manager()
    return await manager.decrypt_audio(encrypted_packet) 