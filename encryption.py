import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

class AESEncryption:
    def __init__(self, password: Optional[str] = None):
        """Initialize AES encryption with password or generate new key"""
        if password:
            self.key = self._derive_key_from_password(password.encode())
        else:
            self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key_from_password(self, password: bytes) -> bytes:
        """Derive encryption key from password"""
        salt = b'stable_salt_for_demo'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES"""
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES"""
        return self.fernet.decrypt(encrypted_data)
    
    def get_key(self) -> bytes:
        """Get the encryption key"""
        return self.key

class MatrixEncryption:
    def __init__(self, password: str = "matrix_crypto_2024"):
        """Initialize matrix encryption system"""
        self.aes = AESEncryption(password)
    
    def encrypt_packet_payload(self, payload: bytes) -> bytes:
        """Encrypt packet payload"""
        return self.aes.encrypt(payload)
    
    def decrypt_packet_payload(self, encrypted_payload: bytes) -> bytes:
        """Decrypt packet payload"""
        return self.aes.decrypt(encrypted_payload)
    
    def get_encryption_info(self) -> dict:
        """Get information about encryption setup"""
        return {
            'algorithm': 'AES-128',
            'key_derivation': 'PBKDF2-SHA256',
            'iterations': 100000
        }