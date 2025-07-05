"""
🔐 Audio Encryption System - AES-256-GCM End-to-End Encryption
===============================================================

Advanced audio encryption for AI Teddy Bear with:
- AES-256-GCM encryption for audio streams
- Key management and rotation
- Secure key exchange
- Audio integrity verification
- Performance optimization for real-time audio

Author: Jaafar Adeeb - Security Lead
"""

import base64
import hashlib
import os
import secrets
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = structlog.get_logger(__name__)


@dataclass
class AudioEncryptionContext:
    """Context for audio encryption operations"""

    session_id: str
    device_id: str
    user_id: str
    encryption_key: bytes
    nonce_counter: int = 0
    created_at: datetime = None
    expires_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)


@dataclass
class EncryptedAudioPacket:
    """Encrypted audio data packet"""

    session_id: str
    sequence_number: int
    encrypted_data: bytes
    nonce: bytes
    tag: bytes
    timestamp: datetime
    checksum: str


class AudioEncryptionManager:
    """Advanced audio encryption manager with AES-256-GCM"""

    def __init__(self):
        self.active_sessions: Dict[str, AudioEncryptionContext] = {}
        self.master_key = self._generate_master_key()
        self.session_keys: Dict[str, bytes] = {}

        # Performance optimization
        self.cipher_cache: Dict[bytes, AESGCM] = {}
        self.max_cache_size = 100

        # Security parameters
        self.key_rotation_interval = timedelta(hours=24)
        self.max_session_duration = timedelta(hours=48)
        self.nonce_size = 12  # 96 bits for GCM
        self.key_size = 32  # 256 bits for AES

    def _generate_master_key(self) -> bytes:
        """Generate or load master encryption key"""

        # In production, this would be loaded from secure storage (Vault)
        master_key_path = os.getenv(
            "AUDIO_MASTER_KEY_PATH",
            "/tmp/.audio_master_key")

        try:
            if os.path.exists(master_key_path):
                with open(master_key_path, "rb") as f:
                    master_key = f.read()
                logger.info("Master key loaded from storage")
            else:
                master_key = secrets.token_bytes(32)  # 256-bit key
                with open(master_key_path, "wb") as f:
                    f.write(master_key)
                os.chmod(master_key_path, 0o600)  # Restrict permissions
                logger.info("New master key generated and stored")

            return master_key

        except Exception as e:
            logger.error("Failed to load/generate master key", error=str(e))
            # Fallback to in-memory key (less secure)
            return secrets.token_bytes(32)

    async def create_encryption_session(
            self, device_id: str, user_id: str) -> str:
        """Create new encryption session for audio communication"""

        session_id = f"audio_sess_{secrets.token_hex(16)}"

        # Derive session key from master key
        session_key = self._derive_session_key(session_id, device_id, user_id)

        # Create encryption context
        context = AudioEncryptionContext(
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
            encryption_key=session_key,
        )

        self.active_sessions[session_id] = context
        self.session_keys[session_id] = session_key

        logger.info(
            "Audio encryption session created",
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
        )

        return session_id

    def _derive_session_key(
        self, session_id: str, device_id: str, user_id: str
    ) -> bytes:
        """Derive session-specific encryption key"""

        # Create key derivation info
        info = f"{session_id}:{device_id}:{user_id}".encode("utf-8")

        # Use HKDF for key derivation
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=None,  # Could add salt for additional security
            info=info,
            backend=default_backend(),
        )

        return hkdf.derive(self.master_key)

    async def encrypt_audio_data(
        self, session_id: str, audio_data: bytes, sequence_number: int = 0
    ) -> EncryptedAudioPacket:
        """Encrypt audio data using AES-256-GCM"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        context = self.active_sessions[session_id]

        # Check if session is still valid
        if datetime.utcnow() > context.expires_at:
            raise ValueError(f"Session expired: {session_id}")

        # Generate unique nonce for this packet
        nonce = self._generate_nonce(context)

        # Get or create cipher instance
        cipher = self._get_cipher(context.encryption_key)

        try:
            # Encrypt audio data
            encrypted_data = cipher.encrypt(nonce, audio_data, None)

            # Split encrypted data and authentication tag
            # GCM automatically appends the tag to the ciphertext
            ciphertext = encrypted_data[:-16]  # All except last 16 bytes
            tag = encrypted_data[-16:]  # Last 16 bytes are the tag

            # Create checksum for integrity verification
            checksum = self._calculate_checksum(audio_data, nonce, tag)

            # Create encrypted packet
            packet = EncryptedAudioPacket(
                session_id=session_id,
                sequence_number=sequence_number,
                encrypted_data=ciphertext,
                nonce=nonce,
                tag=tag,
                timestamp=datetime.utcnow(),
                checksum=checksum,
            )

            # Update nonce counter
            context.nonce_counter += 1

            logger.debug(
                "Audio data encrypted",
                session_id=session_id,
                data_size=len(audio_data),
                encrypted_size=len(ciphertext),
            )

            return packet

        except Exception as e:
            logger.error(
                "Audio encryption failed",
                session_id=session_id,
                error=str(e))
            raise

    async def decrypt_audio_data(self, packet: EncryptedAudioPacket) -> bytes:
        """Decrypt audio data using AES-256-GCM"""

        session_id = packet.session_id

        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        context = self.active_sessions[session_id]

        # Get cipher instance
        cipher = self._get_cipher(context.encryption_key)

        try:
            # Reconstruct full encrypted data (ciphertext + tag)
            encrypted_data = packet.encrypted_data + packet.tag

            # Decrypt audio data
            decrypted_data = cipher.decrypt(packet.nonce, encrypted_data, None)

            # Verify checksum for integrity
            expected_checksum = self._calculate_checksum(
                decrypted_data, packet.nonce, packet.tag
            )

            if packet.checksum != expected_checksum:
                raise ValueError("Audio data integrity check failed")

            logger.debug(
                "Audio data decrypted",
                session_id=session_id,
                decrypted_size=len(decrypted_data),
            )

            return decrypted_data

        except Exception as e:
            logger.error(
                "Audio decryption failed",
                session_id=session_id,
                error=str(e))
            raise

    def _generate_nonce(self, context: AudioEncryptionContext) -> bytes:
        """Generate unique nonce for GCM encryption"""

        # Create nonce from session ID, counter, and timestamp
        # This ensures uniqueness even in high-frequency scenarios
        timestamp = int(
            datetime.utcnow().timestamp() *
            1000000)  # microseconds

        # Combine session info, counter, and timestamp
        nonce_data = struct.pack(">Q", timestamp) + struct.pack(
            ">I", context.nonce_counter
        )

        # Hash to get exactly 12 bytes for GCM
        nonce_hash = hashlib.sha256(
            nonce_data + context.session_id.encode()).digest()

        return nonce_hash[: self.nonce_size]

    def _get_cipher(self, key: bytes) -> AESGCM:
        """Get cached cipher instance or create new one"""

        if key in self.cipher_cache:
            return self.cipher_cache[key]

        # Create new cipher
        cipher = AESGCM(key)

        # Cache management
        if len(self.cipher_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cipher_cache))
            del self.cipher_cache[oldest_key]

        self.cipher_cache[key] = cipher
        return cipher

    def _calculate_checksum(
            self,
            data: bytes,
            nonce: bytes,
            tag: bytes) -> str:
        """Calculate checksum for integrity verification"""

        # Combine all components for checksum
        combined = data + nonce + tag

        # Use SHA-256 for checksum
        checksum_hash = hashlib.sha256(combined).digest()

        # Return as hex string
        return checksum_hash.hex()

    async def rotate_session_key(self, session_id: str) -> bool:
        """Rotate encryption key for a session"""

        if session_id not in self.active_sessions:
            return False

        context = self.active_sessions[session_id]

        # Generate new session key
        new_key = self._derive_session_key(
            f"{session_id}_rotated_{int(datetime.utcnow().timestamp())}",
            context.device_id,
            context.user_id,
        )

        # Update context
        context.encryption_key = new_key
        context.nonce_counter = 0  # Reset counter
        context.created_at = datetime.utcnow()
        context.expires_at = context.created_at + timedelta(hours=24)

        # Update session keys
        self.session_keys[session_id] = new_key

        # Clear cipher cache for old key
        if context.encryption_key in self.cipher_cache:
            del self.cipher_cache[context.encryption_key]

        logger.info("Session key rotated", session_id=session_id)
        return True

    async def close_session(self, session_id: str) -> bool:
        """Close encryption session and cleanup"""

        if session_id not in self.active_sessions:
            return False

        context = self.active_sessions[session_id]

        # Clear cipher cache
        if context.encryption_key in self.cipher_cache:
            del self.cipher_cache[context.encryption_key]

        # Remove session data
        del self.active_sessions[session_id]
        if session_id in self.session_keys:
            del self.session_keys[session_id]

        logger.info("Encryption session closed", session_id=session_id)
        return True

    async def get_session_info(
            self, session_id: str) -> Optional[Dict[str, any]]:
        """Get information about encryption session"""

        if session_id not in self.active_sessions:
            return None

        context = self.active_sessions[session_id]

        return {
            "session_id": context.session_id,
            "device_id": context.device_id,
            "user_id": context.user_id,
            "created_at": context.created_at.isoformat(),
            "expires_at": context.expires_at.isoformat(),
            "nonce_counter": context.nonce_counter,
            "is_expired": datetime.utcnow() > context.expires_at,
        }

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""

        now = datetime.utcnow()
        expired_sessions = []

        for session_id, context in self.active_sessions.items():
            if now > context.expires_at:
                expired_sessions.append(session_id)

        # Close expired sessions
        for session_id in expired_sessions:
            await self.close_session(session_id)

        logger.info("Expired sessions cleaned up", count=len(expired_sessions))
        return len(expired_sessions)

    async def encrypt_audio_stream(
        self, session_id: str, audio_chunks: List[bytes]
    ) -> List[EncryptedAudioPacket]:
        """Encrypt multiple audio chunks as a stream"""

        encrypted_packets = []

        for i, chunk in enumerate(audio_chunks):
            packet = await self.encrypt_audio_data(session_id, chunk, i)
            encrypted_packets.append(packet)

        logger.info(
            "Audio stream encrypted",
            session_id=session_id,
            chunks=len(audio_chunks))

        return encrypted_packets

    async def decrypt_audio_stream(
            self, packets: List[EncryptedAudioPacket]) -> bytes:
        """Decrypt multiple audio packets back to stream"""

        # Sort packets by sequence number
        sorted_packets = sorted(packets, key=lambda p: p.sequence_number)

        decrypted_chunks = []

        for packet in sorted_packets:
            chunk = await self.decrypt_audio_data(packet)
            decrypted_chunks.append(chunk)

        # Combine all chunks
        full_audio = b"".join(decrypted_chunks)

        logger.info(
            "Audio stream decrypted",
            packets=len(packets),
            total_size=len(full_audio))

        return full_audio

    def serialize_packet(self, packet: EncryptedAudioPacket) -> str:
        """Serialize encrypted packet for transmission"""

        packet_data = {
            "session_id": packet.session_id,
            "sequence_number": packet.sequence_number,
            "encrypted_data": base64.b64encode(packet.encrypted_data).decode(),
            "nonce": base64.b64encode(packet.nonce).decode(),
            "tag": base64.b64encode(packet.tag).decode(),
            "timestamp": packet.timestamp.isoformat(),
            "checksum": packet.checksum,
        }

        import json

        return json.dumps(packet_data)

    def deserialize_packet(self, packet_json: str) -> EncryptedAudioPacket:
        """Deserialize packet from JSON"""

        import json

        packet_data = json.loads(packet_json)

        return EncryptedAudioPacket(
            session_id=packet_data["session_id"],
            sequence_number=packet_data["sequence_number"],
            encrypted_data=base64.b64decode(packet_data["encrypted_data"]),
            nonce=base64.b64decode(packet_data["nonce"]),
            tag=base64.b64decode(packet_data["tag"]),
            timestamp=datetime.fromisoformat(packet_data["timestamp"]),
            checksum=packet_data["checksum"],
        )


# Global audio encryption manager
_audio_encryption_manager: Optional[AudioEncryptionManager] = None


def get_audio_encryption_manager() -> AudioEncryptionManager:
    """Get global audio encryption manager instance"""
    global _audio_encryption_manager
    if _audio_encryption_manager is None:
        _audio_encryption_manager = AudioEncryptionManager()
    return _audio_encryption_manager


# Convenience functions


async def encrypt_child_audio(
        device_id: str,
        user_id: str,
        audio_data: bytes) -> str:
    """Encrypt audio data from child device"""
    manager = get_audio_encryption_manager()

    # Create or get existing session
    session_id = await manager.create_encryption_session(device_id, user_id)

    # Encrypt audio
    packet = await manager.encrypt_audio_data(session_id, audio_data)

    # Return serialized packet
    return manager.serialize_packet(packet)


async def decrypt_child_audio(encrypted_packet_json: str) -> bytes:
    """Decrypt audio data for processing"""
    manager = get_audio_encryption_manager()

    # Deserialize packet
    packet = manager.deserialize_packet(encrypted_packet_json)

    # Decrypt audio
    return await manager.decrypt_audio_data(packet)
