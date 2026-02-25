"""
Migration: Verschlüsselt bestehende Tokens in der Datenbank
"""

from sqlalchemy import create_engine, text
from services.encryption_service import encryption_service
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate_encrypt_tokens():
    with engine.connect() as conn:
        # Hole alle unverschlüsselten Tokens
        result = conn.execute(text("""
            SELECT id, access_token, refresh_token 
            FROM platform_connections 
            WHERE access_token IS NOT NULL
        """))
        
        for row in result:
            encrypted_access = encryption_service.encrypt(row.access_token)
            encrypted_refresh = encryption_service.encrypt(row.refresh_token) if row.refresh_token else None
            
            # Update mit verschlüsselten Werten
            conn.execute(text("""
                UPDATE platform_connections 
                SET access_token = :access, refresh_token = :refresh
                WHERE id = :id
            """), {
                "access": encrypted_access,
                "refresh": encrypted_refresh,
                "id": row.id
            })
        
        conn.commit()
        print(f"✅ Migrated {result.rowcount} token records to encrypted format")

if __name__ == "__main__":
    migrate_encrypt_tokens()
