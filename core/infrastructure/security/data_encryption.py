"""
Advanced Data Encryption System
Provides end-to-end encryption for sensitive child data
"""

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

logger = structlog.get_logger()


class EncryptionLevel(Enum):
    """Encryption levels for different data types"""
    BASIC = "basic"          # Non-sensitive data
    STANDARD = "standard"    # Normal user data
    HIGH = "high"           # Sensitive data
    CRITICAL = "critical"   # Child data, audio, personal info


class DataClassification(Enum):
    """Data classification types"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # Child data


@dataclass
class EncryptedData:
    """Encrypted data container"""
    ciphertext: str
    encryption_level: EncryptionLevel
    algorithm: str
    key_id: str
    iv: Optional[str] = None
    tag: Optional[str] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ciphertext": self.ciphertext,
            "encryption_level": self.encryption_level.value,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "iv": self.iv,
            "tag": self.tag,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedData':
        """Create from dictionary"""
        return cls(
            ciphertext=data["ciphertext"],
            encryption_level=EncryptionLevel(data["encryption_level"]),
            algorithm=data["algorithm"],
            key_id=data["key_id"],
            iv=data.get("iv"),
            tag=data.get("tag"),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata")
        )


class KeyManager:
    """Secure key management system"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or self._generate_master_key()
        self._key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._key_rotation_interval = timedelta(days=30)
    
    def _generate_master_key(self) -> bytes:
        """Generate a secure master key"""
        # In production, this should be retrieved from HSM or key vault
        return Fernet.generate_key()
    
    def generate_data_key(self, key_id: str, level: EncryptionLevel) -> bytes:
        """Generate a data encryption key"""
        # Check cache
        if key_id in self._key_cache:
            key, created_at = self._key_cache[key_id]
            if datetime.utcnow() - created_at < self._key_rotation_interval:
                return key
        
        # Derive key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=key_id.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        
        # Cache key
        self._key_cache[key_id] = (key, datetime.utcnow())
        
        return key
    
    def rotate_keys(self) -> None:
        """Rotate encryption keys"""
        now = datetime.utcnow()
        expired_keys = [
            key_id for key_id, (_, created_at) in self._key_cache.items()
            if now - created_at >= self._key_rotation_interval
        ]
        
        for key_id in expired_keys:
            del self._key_cache[key_id]
        
        logger.info(f"Rotated {len(expired_keys)} encryption keys")


class DataEncryptionService:
    """
    Comprehensive data encryption service for child data protection
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.key_manager = KeyManager()
        self._encryption_algorithms = {
            EncryptionLevel.BASIC: self._encrypt_basic,
            EncryptionLevel.STANDARD: self._encrypt_standard,
            EncryptionLevel.HIGH: self._encrypt_aes_gcm,
            EncryptionLevel.CRITICAL: self._encrypt_aes_gcm_with_rsa
        }
        self._decryption_algorithms = {
            "fernet": self._decrypt_fernet,
            "aes_gcm": self._decrypt_aes_gcm,
            "aes_gcm_rsa": self._decrypt_aes_gcm_with_rsa
        }
        
        # RSA keys for critical data
        self._rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        self._rsa_public_key = self._rsa_private_key.public_key()
    
    async def encrypt(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        level: EncryptionLevel = EncryptionLevel.STANDARD,
        classification: DataClassification = DataClassification.INTERNAL
    ) -> EncryptedData:
        """
        Encrypt data based on sensitivity level
        """
        # Serialize data if needed
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Select encryption method based on level
        encrypt_func = self._encryption_algorithms[level]
        
        # Generate key ID
        key_id = self._generate_key_id(classification)
        
        # Encrypt
        encrypted = await encrypt_func(data, key_id)
        
        # Log encryption event (without sensitive data)
        logger.info(
            "Data encrypted",
            level=level.value,
            classification=classification.value,
            key_id=key_id,
            size=len(data)
        )
        
        return encrypted
    
    async def decrypt(self, encrypted_data: EncryptedData) -> bytes:
        """
        Decrypt data
        """
        # Check expiration
        if encrypted_data.expires_at and datetime.utcnow() > encrypted_data.expires_at:
            raise ValueError("Encrypted data has expired")
        
        # Select decryption method
        decrypt_func = self._decryption_algorithms.get(encrypted_data.algorithm)
        if not decrypt_func:
            raise ValueError(f"Unknown encryption algorithm: {encrypted_data.algorithm}")
        
        # Decrypt
        decrypted = await decrypt_func(encrypted_data)
        
        # Log decryption event
        logger.info(
            "Data decrypted",
            level=encrypted_data.encryption_level.value,
            key_id=encrypted_data.key_id
        )
        
        return decrypted
    
    async def encrypt_child_data(self, child_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt all sensitive fields in child data
        """
        encrypted_fields = {}
        sensitive_fields = [
            "name", "date_of_birth", "audio_recordings", 
            "conversations", "personal_info", "medical_info"
        ]
        
        for field in sensitive_fields:
            if field in child_data:
                encrypted = await self.encrypt(
                    child_data[field],
                    level=EncryptionLevel.CRITICAL,
                    classification=DataClassification.RESTRICTED
                )
                encrypted_fields[f"encrypted_{field}"] = encrypted.to_dict()
        
        # Keep non-sensitive fields
        result = {
            k: v for k, v in child_data.items() 
            if k not in sensitive_fields
        }
        result.update(encrypted_fields)
        
        return result
    
    async def decrypt_child_data(self, encrypted_child_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt all encrypted fields in child data
        """
        decrypted_data = {}
        
        for key, value in encrypted_child_data.items():
            if key.startswith("encrypted_"):
                # Decrypt field
                field_name = key.replace("encrypted_", "")
                encrypted = EncryptedData.from_dict(value)
                decrypted = await self.decrypt(encrypted)
                
                # Parse JSON if needed
                try:
                    decrypted_data[field_name] = json.loads(decrypted.decode('utf-8'))
                except:
                    decrypted_data[field_name] = decrypted.decode('utf-8')
            else:
                decrypted_data[key] = value
        
        return decrypted_data
    
    async def _encrypt_basic(self, data: bytes, key_id: str) -> EncryptedData:
        """Basic encryption using Fernet"""
        key = self.key_manager.generate_data_key(key_id, EncryptionLevel.BASIC)
        f = Fernet(key)
        ciphertext = f.encrypt(data)
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.BASIC,
            algorithm="fernet",
            key_id=key_id
        )
    
    async def _encrypt_standard(self, data: bytes, key_id: str) -> EncryptedData:
        """Standard encryption using Fernet with metadata"""
        key = self.key_manager.generate_data_key(key_id, EncryptionLevel.STANDARD)
        f = Fernet(key)
        ciphertext = f.encrypt(data)
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.STANDARD,
            algorithm="fernet",
            key_id=key_id,
            expires_at=datetime.utcnow() + timedelta(days=90),
            metadata={"version": "1.0"}
        )
    
    async def _encrypt_aes_gcm(self, data: bytes, key_id: str) -> EncryptedData:
        """High security encryption using AES-GCM"""
        key = self.key_manager.generate_data_key(key_id, EncryptionLevel.HIGH)[:32]
        iv = os.urandom(12)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv)
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.HIGH,
            algorithm="aes_gcm",
            key_id=key_id,
            iv=base64.b64encode(iv).decode('utf-8'),
            tag=base64.b64encode(encryptor.tag).decode('utf-8'),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
    
    async def _encrypt_aes_gcm_with_rsa(self, data: bytes, key_id: str) -> EncryptedData:
        """Critical data encryption using AES-GCM with RSA key wrapping"""
        # Generate AES key
        aes_key = os.urandom(32)
        iv = os.urandom(12)
        
        # Encrypt data with AES-GCM
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv)
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Wrap AES key with RSA
        wrapped_key = self._rsa_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.CRITICAL,
            algorithm="aes_gcm_rsa",
            key_id=key_id,
            iv=base64.b64encode(iv).decode('utf-8'),
            tag=base64.b64encode(encryptor.tag).decode('utf-8'),
            expires_at=datetime.utcnow() + timedelta(days=7),
            metadata={
                "wrapped_key": base64.b64encode(wrapped_key).decode('utf-8'),
                "version": "2.0"
            }
        )
    
    async def _decrypt_fernet(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt Fernet encrypted data"""
        key = self.key_manager.generate_data_key(
            encrypted_data.key_id,
            encrypted_data.encryption_level
        )
        f = Fernet(key)
        ciphertext = base64.b64decode(encrypted_data.ciphertext)
        return f.decrypt(ciphertext)
    
    async def _decrypt_aes_gcm(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt AES-GCM encrypted data"""
        key = self.key_manager.generate_data_key(
            encrypted_data.key_id,
            encrypted_data.encryption_level
        )[:32]
        
        iv = base64.b64decode(encrypted_data.iv)
        tag = base64.b64decode(encrypted_data.tag)
        ciphertext = base64.b64decode(encrypted_data.ciphertext)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag)
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _decrypt_aes_gcm_with_rsa(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt AES-GCM with RSA wrapped key"""
        # Unwrap AES key
        wrapped_key = base64.b64decode(encrypted_data.metadata["wrapped_key"])
        aes_key = self._rsa_private_key.decrypt(
            wrapped_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data
        iv = base64.b64decode(encrypted_data.iv)
        tag = base64.b64decode(encrypted_data.tag)
        ciphertext = base64.b64decode(encrypted_data.ciphertext)
        
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, tag)
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _generate_key_id(self, classification: DataClassification) -> str:
        """Generate unique key ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{classification.value}:{timestamp}:{os.urandom(8).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def encrypt_audio(self, audio_data: bytes, child_id: str) -> EncryptedData:
        """Special handling for audio data encryption"""
        # Add metadata for audio
        metadata = {
            "child_id": hashlib.sha256(child_id.encode()).hexdigest()[:8],
            "content_type": "audio",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        encrypted = await self.encrypt(
            audio_data,
            level=EncryptionLevel.CRITICAL,
            classification=DataClassification.RESTRICTED
        )
        
        encrypted.metadata.update(metadata)
        return encrypted
    
    def generate_encryption_report(self) -> Dict[str, Any]:
        """Generate encryption usage report"""
        return {
            "algorithm_support": list(self._encryption_algorithms.keys()),
            "key_rotation_interval": str(self.key_manager._key_rotation_interval),
            "active_keys": len(self.key_manager._key_cache),
            "rsa_key_size": self._rsa_private_key.key_size,
            "timestamp": datetime.utcnow().isoformat()
        } 