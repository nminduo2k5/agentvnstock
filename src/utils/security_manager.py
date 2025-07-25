# src/utils/security_manager.py
"""
Security Manager for API Keys and Sensitive Data
Quản lý bảo mật cho API keys và dữ liệu nhạy cảm
"""

import os
import base64
import hashlib
from typing import Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Quản lý bảo mật cho API keys và dữ liệu nhạy cảm"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.getenv("MASTER_KEY", "default_key_change_in_production")
        self._fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Tạo Fernet cipher từ master key"""
        try:
            # Derive key from master key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'duong_ai_trading_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to create cipher: {e}")
            # Fallback to simple key
            key = base64.urlsafe_b64encode(hashlib.sha256(self.master_key.encode()).digest())
            return Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Mã hóa API key"""
        try:
            if not api_key:
                return ""
            encrypted = self._fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return api_key  # Fallback to plain text in case of error
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Giải mã API key"""
        try:
            if not encrypted_key:
                return ""
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_key  # Fallback to assume it's plain text
    
    def validate_api_key(self, api_key: str, key_type: str = "gemini") -> bool:
        """Validate API key format"""
        if not api_key:
            return False
        
        validation_rules = {
            "gemini": lambda k: k.startswith("AIza") and len(k) > 30,
            "serper": lambda k: len(k) > 20 and k.replace("-", "").replace("_", "").isalnum(),
            "openai": lambda k: k.startswith("sk-") and len(k) > 40
        }
        
        validator = validation_rules.get(key_type, lambda k: len(k) > 10)
        return validator(api_key)
    
    def mask_api_key(self, api_key: str) -> str:
        """Mask API key for logging"""
        if not api_key or len(api_key) < 8:
            return "***"
        return f"{api_key[:4]}...{api_key[-4:]}"

# Singleton instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get singleton security manager"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager