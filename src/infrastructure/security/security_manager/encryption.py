"""
Enterprise-grade encryption service.
"""
import secrets
from typing import Dict, Optional, Tuple, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AdvancedEncryption:
    """
    Provides strong symmetric (AES-GCM via Fernet) and asymmetric (RSA-OAEP)
    encryption, including hybrid encryption for large data.
    """

    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        self._key_cache: Dict[str, bytes] = {}

        # Generate a default RSA key pair for asymmetric operations
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt_symmetric(self, data: Union[str, bytes], key_id: Optional[str] = None) -> bytes:
        """Encrypts data using a symmetric key (Fernet)."""
        data_bytes = data.encode("utf-8") if isinstance(data, str) else data
        fernet_instance = Fernet(self._key_cache.get(key_id, self.master_key))
        return fernet_instance.encrypt(data_bytes)

    def decrypt_symmetric(self, encrypted_data: bytes, key_id: Optional[str] = None) -> bytes:
        """Decrypts data using a symmetric key."""
        fernet_instance = Fernet(self._key_cache.get(key_id, self.master_key))
        return fernet_instance.decrypt(encrypted_data)

    def encrypt_asymmetric(self, data: Union[str, bytes]) -> bytes:
        """Encrypts data using the RSA public key (OAEP padding)."""
        data_bytes = data.encode("utf-8") if isinstance(data, str) else data

        # RSA-OAEP with SHA-256 can encrypt data up to (key_size_in_bytes - 2*hash_output_size - 2)
        # For a 4096-bit key (512 bytes) and SHA-256 (32 bytes), this is 512 - 64 - 2 = 446 bytes.
        if len(data_bytes) > 446:
            return self._encrypt_hybrid(data_bytes)

        return self.public_key.encrypt(
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_asymmetric(self, encrypted_data: bytes) -> bytes:
        """Decrypts data using the RSA private key."""
        # A simple check to see if the data might be hybrid encrypted
        if len(encrypted_data) > 512:
            return self._decrypt_hybrid(encrypted_data)

        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _encrypt_hybrid(self, data: bytes) -> bytes:
        """Encrypts large data using a hybrid RSA + AES-CBC approach."""
        aes_key = secrets.token_bytes(32)  # 256-bit AES key
        iv = secrets.token_bytes(16)   # 128-bit IV for CBC

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()

        # PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        encrypted_content = encryptor.update(
            padded_data) + encryptor.finalize()

        encrypted_aes_key = self.public_key.encrypt(
            aes_key, padding.OAEP(mgf=padding.MGF1(
                algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        return encrypted_aes_key + iv + encrypted_content

    def _decrypt_hybrid(self, hybrid_encrypted_data: bytes) -> bytes:
        """Decrypts large data encrypted with the hybrid scheme."""
        rsa_key_size_bytes = self.private_key.key_size // 8
        encrypted_aes_key = hybrid_encrypted_data[:rsa_key_size_bytes]
        iv = hybrid_encrypted_data[rsa_key_size_bytes:rsa_key_size_bytes + 16]
        encrypted_content = hybrid_encrypted_data[rsa_key_size_bytes + 16:]

        aes_key = self.private_key.decrypt(
            encrypted_aes_key, padding.OAEP(mgf=padding.MGF1(
                algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(
            encrypted_content) + decryptor.finalize()

        # Unpad
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generates a new RSA key pair and returns them in PEM format."""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return private_pem, public_pem

    def derive_key(self, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """Derives a secure encryption key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return kdf.derive(password.encode("utf-8"))
