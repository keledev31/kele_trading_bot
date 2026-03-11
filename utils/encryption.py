"""
Encryption utilities for securely storing API keys and sensitive data.
Uses Fernet symmetric encryption.
"""

import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Handles encryption and decryption of sensitive data like API keys.
    Uses Fernet (symmetric encryption) for simplicity and security.
    """

    def __init__(self, encryption_key: str = None):
        """
        Initialize encryption manager.
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, reads from ENCRYPTION_KEY env var.
                          Generate new key with: Fernet.generate_key().decode()
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        
        if not self.encryption_key:
            raise ValueError(
                "❌ ENCRYPTION_KEY not set. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\""
            )
        
        try:
            self.cipher = Fernet(self.encryption_key.encode())
        except Exception as e:
            raise ValueError(f"❌ Invalid ENCRYPTION_KEY format: {e}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt (API key, secret, etc.)
            
        Returns:
            Encrypted string (safe to store in database)
        """
        if not plaintext:
            return ""
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Encrypted string from database
            
        Returns:
            Original plaintext (API key, secret, etc.)
        """
        if not ciphertext:
            return ""
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("❌ Failed to decrypt - encryption key may be incorrect")


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_data(data: str) -> str:
    """Convenience function to encrypt data using global manager"""
    return get_encryption_manager().encrypt(data)


def decrypt_data(data: str) -> str:
    """Convenience function to decrypt data using global manager"""
    return get_encryption_manager().decrypt(data)
