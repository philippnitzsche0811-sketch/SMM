from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    UPLOADED = "uploaded"
    PARTIAL = "partial"
    FAILED = "failed"


class Video(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    tags: List[str] = []
    platforms: List[str] = []
    privacy_status: str = "private"
    status: VideoStatus = VideoStatus.PENDING
    created_at: datetime
    updated_at: Optional[datetime] = None
    upload_results: Dict[str, dict] = {}
    errors: Optional[Dict[str, str]] = None
    
    # ✅ Pydantic v2 Config
    model_config = ConfigDict(from_attributes=True)

