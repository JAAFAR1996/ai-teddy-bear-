from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from typing import Tuple

class EncryptionService:
    """Military-grade encryption for child data"""
    
    def __init__(self, master_key: str):
        # Derive encryption key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai-teddy-bear-2025',
            iterations=100000,
        )
        self.key = kdf.derive(master_key.encode())
        self.aesgcm = AESGCM(self.key)
        
    def encrypt(self, data: str) -> Tuple[str, str]:
        """Encrypt data and return (ciphertext, nonce)"""
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        
        return (
            base64.b64encode(ciphertext).decode(),
            base64.b64encode(nonce).decode()
        )
        
    def decrypt(self, ciphertext: str, nonce: str) -> str:
        """Decrypt data"""
        ciphertext_bytes = base64.b64decode(ciphertext)
        nonce_bytes = base64.b64decode(nonce)
        
        plaintext = self.aesgcm.decrypt(nonce_bytes, ciphertext_bytes, None)
        return plaintext.decode()