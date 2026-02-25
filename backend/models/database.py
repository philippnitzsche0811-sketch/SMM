# models/database.py
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL - NUTZT APPLICATION USER!
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://socialhub_app:changeme_app@localhost:5433/socialhub_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models bleiben gleich...
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class VideoModel(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    platforms = Column(JSON, nullable=False)
    privacy_status = Column(String, default="private")
    status = Column(String, default="pending")
    upload_results = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)

class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String, nullable=False)
    connected = Column(Boolean, default=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    username = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def get_db():
    """Dependency für FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Erstellt alle Tabellen"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def drop_db():
    """Löscht alle Tabellen"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Database tables dropped")

if __name__ == "__main__":
    init_db()
