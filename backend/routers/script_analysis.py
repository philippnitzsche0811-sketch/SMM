from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from models.database import get_db, UserModel
from services import script_analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Script Analysis"])

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB


def _require_pro(user_id: str, db: Session):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or user.plan != "pro":
        raise HTTPException(status_code=403, detail="Pro plan required for script analysis")


class TextAnalysisRequest(BaseModel):
    user_id: str
    idea_title: str
    text: str
    platforms: Optional[List[str]] = []


@router.post("/text")
async def analyze_script_text(body: TextAnalysisRequest, db: Session = Depends(get_db)):
    _require_pro(body.user_id, db)
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    result = await script_analysis_service.analyze_text(body.text, body.idea_title, body.platforms or [])
    return result


@router.post("/audio")
async def analyze_script_audio(
    user_id: str = Form(...),
    idea_title: str = Form(...),
    platforms: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _require_pro(user_id, db)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum 25 MB.")
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
    result = await script_analysis_service.analyze_audio(
        file_bytes, file.filename or "audio.mp3", idea_title, platform_list
    )
    return result
