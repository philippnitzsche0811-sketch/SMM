"""
Encryption Service für Token-Verschlüsselung in PostgreSQL
"""

import os
from sqlalchemy import text
from typing import Optional

class EncryptionService:
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY must be set in environment")
    
    def encrypt(self, plaintext: Optional[str], db_session) -> Optional[bytes]:
        """Verschlüsselt Text mit PostgreSQL pgcrypto"""
        if not plaintext:
            return None
        
        result = db_session.execute(
            text("SELECT encrypt_token(:plaintext, :key)"),
            {"plaintext": plaintext, "key": self.encryption_key}
        ).scalar()
        
        return bytes(result) if result else None
    
    def decrypt(self, encrypted: Optional[bytes], db_session) -> Optional[str]:
        """Entschlüsselt Bytes mit PostgreSQL pgcrypto"""
        if not encrypted:
            return None
        
        result = db_session.execute(
            text("SELECT decrypt_token(:encrypted, :key)"),
            {"encrypted": encrypted, "key": self.encryption_key}
        ).scalar()
        
        return result

# Singleton instance
encryption_service = EncryptionService()

