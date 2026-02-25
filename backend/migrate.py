# migrate.py
from models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Add username column
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR;"))
        conn.commit()
        print("✅ username Spalte hinzugefügt")
    except Exception as e:
        print(f"⚠️  username existiert bereits oder Fehler: {e}")
    
    # Create platform_connections table
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS platform_connections (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                platform VARCHAR NOT NULL,
                connected BOOLEAN DEFAULT TRUE,
                access_token TEXT,
                refresh_token TEXT,
                token_expiry TIMESTAMP,
                username VARCHAR,
                channel_id VARCHAR,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_platform_user ON platform_connections(user_id);"))
        conn.commit()
        print("✅ platform_connections Tabelle erstellt")
    except Exception as e:
        print(f"⚠️  Tabelle existiert bereits oder Fehler: {e}")

print("✅ Migration abgeschlossen!")
