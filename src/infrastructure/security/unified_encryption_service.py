"""
Unified Encryption Service
Combines all encryption functionality in one comprehensive service
"""

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
    nonce: Optional[str] = None
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
            "nonce": self.nonce,
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
            nonce=data.get("nonce"),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata")
        )


class UnifiedEncryptionService:
    """
    Unified encryption service combining all encryption functionality
    """
    
    def __init__(self, master_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.master_key = master_key or os.environ.get('MASTER_ENCRYPTION_KEY', Fernet.generate_key().decode())
        
        # Initialize key derivation
        self._init_key_derivation()
        
        # Initialize RSA keys for critical data
        self._init_rsa_keys()
        
        # Key cache for performance
        self._key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._key_rotation_interval = timedelta(days=30)
    
    def _init_key_derivation(self):
        """Initialize key derivation function"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ai-teddy-bear-2025",
            iterations=100000,
        )
        self.derived_key = kdf.derive(self.master_key.encode())
        self.aesgcm = AESGCM(self.derived_key)
    
    def _init_rsa_keys(self):
        """Initialize RSA keys for critical encryption"""
        self._rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        self._rsa_public_key = self._rsa_private_key.public_key()
    
    # Simple encryption methods (backward compatible)
    def encrypt_simple(self, data: str) -> Tuple[str, str]:
        """Simple encrypt method for backward compatibility"""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        return (base64.b64encode(ciphertext).decode(), base64.b64encode(nonce).decode())
    
    def decrypt_simple(self, ciphertext: str, nonce: str) -> str:
        """Simple decrypt method for backward compatibility"""
        ciphertext_bytes = base64.b64decode(ciphertext)
        nonce_bytes = base64.b64decode(nonce)
        plaintext = self.aesgcm.decrypt(nonce_bytes, ciphertext_bytes, None)
        return plaintext.decode()
    
    # Advanced encryption methods
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
        
        # Generate key ID
        key_id = self._generate_key_id(classification)
        
        # Select encryption method based on level
        if level == EncryptionLevel.BASIC:
            return await self._encrypt_basic(data, key_id)
        elif level == EncryptionLevel.STANDARD:
            return await self._encrypt_standard(data, key_id)
        elif level == EncryptionLevel.HIGH:
            return await self._encrypt_aes_gcm(data, key_id)
        else:  # CRITICAL
            return await self._encrypt_aes_gcm_with_rsa(data, key_id)
    
    async def decrypt(self, encrypted_data: EncryptedData) -> bytes:
        """
        Decrypt data
        """
        # Check expiration
        if encrypted_data.expires_at and datetime.utcnow() > encrypted_data.expires_at:
            raise ValueError("Encrypted data has expired")
        
        # Select decryption method
        if encrypted_data.algorithm == "fernet":
            return await self._decrypt_fernet(encrypted_data)
        elif encrypted_data.algorithm == "aes_gcm":
            return await self._decrypt_aes_gcm(encrypted_data)
        elif encrypted_data.algorithm == "aes_gcm_rsa":
            return await self._decrypt_aes_gcm_with_rsa(encrypted_data)
        else:
            raise ValueError(f"Unknown encryption algorithm: {encrypted_data.algorithm}")
    
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
                except json.JSONDecodeError:
                    decrypted_data[field_name] = decrypted.decode('utf-8')
            else:
                decrypted_data[key] = value
        
        return decrypted_data
    
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
    
    # Private encryption methods
    async def _encrypt_basic(self, data: bytes, key_id: str) -> EncryptedData:
        """Basic encryption using Fernet"""
        key = self._generate_data_key(key_id, EncryptionLevel.BASIC)
        f = Fernet(key)
        ciphertext = f.encrypt(data)
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.BASIC,
            algorithm="fernet",
            key_id=key_id
        )
    
    async def _encrypt_standard(self, data: bytes, key_id: str) -> EncryptedData:
        """Standard encryption using AES-GCM"""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        
        return EncryptedData(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            encryption_level=EncryptionLevel.STANDARD,
            algorithm="aes_gcm",
            key_id=key_id,
            nonce=base64.b64encode(nonce).decode('utf-8'),
            expires_at=datetime.utcnow() + timedelta(days=90)
        )
    
    async def _encrypt_aes_gcm(self, data: bytes, key_id: str) -> EncryptedData:
        """High security encryption using AES-GCM"""
        key = self._generate_data_key(key_id, EncryptionLevel.HIGH)[:32]
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
    
    # Private decryption methods
    async def _decrypt_fernet(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt Fernet encrypted data"""
        key = self._generate_data_key(
            encrypted_data.key_id,
            encrypted_data.encryption_level
        )
        f = Fernet(key)
        ciphertext = base64.b64decode(encrypted_data.ciphertext)
        return f.decrypt(ciphertext)
    
    async def _decrypt_aes_gcm(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt AES-GCM encrypted data"""
        if encrypted_data.nonce:
            # Simple AES-GCM (standard level)
            ciphertext_bytes = base64.b64decode(encrypted_data.ciphertext)
            nonce_bytes = base64.b64decode(encrypted_data.nonce)
            return self.aesgcm.decrypt(nonce_bytes, ciphertext_bytes, None)
        else:
            # Advanced AES-GCM with custom key
            key = self._generate_data_key(
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
    
    # Helper methods
    def _generate_data_key(self, key_id: str, level: EncryptionLevel) -> bytes:
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
            salt=f"{key_id}:{level.value}".encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        
        # Cache key
        self._key_cache[key_id] = (key, datetime.utcnow())
        
        return key
    
    def _generate_key_id(self, classification: DataClassification) -> str:
        """Generate unique key ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{classification.value}:{timestamp}:{os.urandom(8).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
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
    
    def generate_encryption_report(self) -> Dict[str, Any]:
        """Generate encryption usage report"""
        return {
            "encryption_levels": [level.value for level in EncryptionLevel],
            "key_rotation_interval": str(self._key_rotation_interval),
            "active_keys": len(self._key_cache),
            "rsa_key_size": self._rsa_private_key.key_size,
            "supported_algorithms": ["fernet", "aes_gcm", "aes_gcm_rsa"],
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance for backward compatibility
_default_service = None

def get_encryption_service(master_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> UnifiedEncryptionService:
    """Get or create encryption service instance"""
    global _default_service
    if _default_service is None:
        _default_service = UnifiedEncryptionService(master_key, config)
    return _default_service


# Backward compatibility aliases
EncryptionService = UnifiedEncryptionService
DataEncryptionService = UnifiedEncryptionService 