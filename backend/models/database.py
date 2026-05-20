# models/database.py
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON, Text, ForeignKey, Integer
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
    niche = Column(String, nullable=True)          # fitness | food | finance | gaming | tech | lifestyle | education | comedy | beauty | travel | default
    creator_tone = Column(String, nullable=True)   # educational | entertainer | inspirational | informative
    plan = Column(String, default="free", nullable=False, server_default="free")  # free | pro
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
    file_path = Column(String, nullable=True)
    upload_results = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    platform_metadata = Column(JSON, nullable=True)  # {youtube: {title, description, tags, privacy_status}, ...}
    scheduled_at = Column(DateTime, nullable=True)
    upload_mode = Column(String, nullable=True)  # "simple" | "smart" | "group"
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


class UploadGroupModel(Base):
    __tablename__ = "upload_groups"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    platforms = Column(JSON, nullable=False)
    privacy_status = Column(String, default="private")
    category = Column(String, default="entertainment")
    status = Column(String, default="active")  # active | paused | completed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class GroupVideoModel(Base):
    __tablename__ = "group_videos"

    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("upload_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, default=0)
    scheduled_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    status = Column(String, default="queued")  # queued | uploading | done | failed
    ai_context = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class VideoAnalysisModel(Base):
    __tablename__ = "video_analyses"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(String, nullable=False, index=True)
    frames_extracted = Column(Integer, default=0)
    analysis_result = Column(JSON, nullable=True)
    hook_result = Column(JSON, nullable=True)   # Hook-specific analysis (first 5s)
    status = Column(String, default="pending")  # pending | processing | done | failed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


class HookExampleModel(Base):
    __tablename__ = "hook_examples"

    id = Column(String, primary_key=True, index=True)
    platform = Column(String, nullable=False, index=True)  # youtube|tiktok|instagram
    niche = Column(String, nullable=False, index=True)     # fitness|gaming|default|...
    hook_type = Column(String, nullable=True)              # verbal|visual|text|music|combo
    description = Column(Text, nullable=True)              # "Video über Gewichtsverlust..."
    what_worked = Column(Text, nullable=True)              # "Zahlen im ersten Satz + Gesicht"
    score = Column(Integer, nullable=True)                 # 1-10
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class TrendCacheModel(Base):
    __tablename__ = "trend_cache"

    id = Column(String, primary_key=True, index=True)
    platform = Column(String, nullable=False, index=True)   # youtube / tiktok / instagram
    category = Column(String, nullable=False, index=True)   # gaming, default, …
    data = Column(JSON, nullable=True)                       # {top_tags, title_patterns, sample_titles}
    refreshed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)


class UserPerformanceCacheModel(Base):
    __tablename__ = "user_performance_cache"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String, nullable=False)               # youtube / tiktok / instagram
    top_tags = Column(JSON, nullable=True)                  # [{tag, score}]
    best_hours = Column(JSON, nullable=True)                # [{hour, avg_engagement}]
    best_days = Column(JSON, nullable=True)                 # [{dow, avg_engagement}]
    updated_at = Column(DateTime, nullable=True)


class AiTokenUsageModel(Base):
    __tablename__ = "ai_token_usage"

    id            = Column(String, primary_key=True, index=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    model         = Column(String, nullable=False)
    platform      = Column(String, nullable=True)   # youtube|tiktok|instagram
    input_tokens  = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)


class AppConfigModel(Base):
    __tablename__ = "app_config"

    key        = Column(String, primary_key=True)
    value      = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminTrendDataModel(Base):
    __tablename__ = "admin_trend_data"

    id             = Column(String, primary_key=True, index=True)
    platform       = Column(String, nullable=False, index=True)   # youtube|tiktok|instagram
    category       = Column(String, nullable=False, index=True)   # gaming|education|default|...
    top_tags       = Column(JSON, nullable=True)                  # list[str]
    title_words    = Column(JSON, nullable=True)                  # list[str]
    title_starters = Column(JSON, nullable=True)                  # list[str]
    notes          = Column(Text, nullable=True)
    updated_at     = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ContentIdeaModel(Base):
    __tablename__ = "content_ideas"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    concept = Column(Text, nullable=True)
    target_platforms = Column(JSON, nullable=True)   # ["tiktok", "instagram"]
    target_date = Column(DateTime, nullable=True)
    status = Column(String, default="idea")          # idea | planning | ready
    tags = Column(JSON, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)     # {titles: [], hashtags: []}
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


class VideoStatsModel(Base):
    __tablename__ = "video_stats"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String, nullable=False)          # youtube | tiktok | instagram
    platform_video_id = Column(String, nullable=True)  # YouTube video_id, TikTok publish_id, ...
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


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
