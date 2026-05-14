from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from models.database import get_db, VideoModel
from models.video import VideoStatus
from services.video_service import VideoService
from services.video_analysis_service import analyze_video_frames, analyze_hook, get_analysis
from services.file_service import FileService
from services.upload_group_service import add_video_to_group, get_group

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Smart Upload"])
file_service = FileService()


# ── Request schemas ──────────────────────────────────────────────────────────

class ScheduleSmartRequest(BaseModel):
    user_id: str
    platforms: List[str]
    privacy_status: str = "private"
    schedule_type: str = "now"  # "now" | "datetime" | "group"
    scheduled_at: Optional[str] = None
    group_id: Optional[str] = None
    ai_context: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def start_analysis(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_db),
):
    content_type = video.content_type or ""
    filename = video.filename or ""
    is_video = content_type.startswith("video/") or any(
        filename.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    )
    if not is_video:
        raise HTTPException(status_code=400, detail="File is not a video")

    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    temp_path = await file_service.save_temp_file(video)

    video_record = VideoService.create_video(
        db=db,
        user_id=user_id,
        title=title,
        description=description,
        tags=tags_list,
        platforms=[],  # platforms chosen after analysis
        privacy_status="private",
        file_path=temp_path,
    )
    # Mark upload_mode on the record
    db_video = db.query(VideoModel).filter(VideoModel.id == video_record.id).first()
    if db_video:
        db_video.upload_mode = "smart"
        db.commit()

    background_tasks.add_task(
        _run_analysis_background,
        video_record.id,
        user_id,
        temp_path,
        db,
    )

    return {
        "video_id": video_record.id,
        "status": "analyzing",
        "message": "Analysis started — poll /analysis/{video_id}",
    }


@router.get("/analysis/{video_id}")
async def get_analysis_status(video_id: str, db: Session = Depends(get_db)):
    analysis = get_analysis(db, video_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "video_id": video_id,
        "status": analysis.status,
        "frames_extracted": analysis.frames_extracted,
        "result": analysis.analysis_result if analysis.status == "done" else None,
        "hook_result": analysis.hook_result if analysis.status == "done" else None,
    }


@router.post("/schedule/{video_id}")
async def schedule_smart_upload(
    video_id: str,
    request: ScheduleSmartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update platforms, privacy, and user-edited metadata
    video.platforms = request.platforms
    video.privacy_status = request.privacy_status
    if request.title is not None:
        video.title = request.title
    if request.description is not None:
        video.description = request.description
    if request.tags is not None:
        video.tags = request.tags
    db.commit()

    if request.schedule_type == "now":
        background_tasks.add_task(
            VideoService.process_video_upload,
            video_id,
            video.file_path,
        )
        return {"status": "uploading", "message": "Upload started"}

    if request.schedule_type == "datetime":
        if not request.scheduled_at:
            raise HTTPException(status_code=400, detail="scheduled_at required for datetime schedule")
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_at format")
        video.scheduled_at = scheduled_dt
        video.status = VideoStatus.PENDING.value
        db.commit()
        return {"status": "scheduled", "scheduled_at": scheduled_dt.isoformat()}

    if request.schedule_type == "group":
        if not request.group_id:
            raise HTTPException(status_code=400, detail="group_id required")
        group = get_group(db, request.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        gv = add_video_to_group(db, request.group_id, video_id, ai_context=request.ai_context)
        return {
            "status": "queued",
            "group_video_id": gv.id,
            "scheduled_at": gv.scheduled_at.isoformat() if gv.scheduled_at else None,
        }

    raise HTTPException(status_code=400, detail="Invalid schedule_type")


# ── Background task ──────────────────────────────────────────────────────────

async def _run_analysis_background(video_id: str, user_id: str, video_path: str, request_db=None):
    from models.database import SessionLocal, UserModel
    db = SessionLocal()
    try:
        # Fetch user niche for hook context
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        niche = getattr(user, "niche", None) or "default"

        # Run full analysis and hook analysis concurrently
        import asyncio
        await asyncio.gather(
            analyze_video_frames(db, user_id, video_id, video_path),
            analyze_hook(db, user_id, video_id, video_path, niche=niche),
            return_exceptions=True,
        )
        logger.info(f"✅ Analysis + hook analysis complete for video {video_id}")
    except Exception as exc:
        logger.error(f"❌ Background analysis failed for {video_id}: {exc}")
    finally:
        db.close()
