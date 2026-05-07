from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import get_db, GroupVideoModel, VideoModel
from services.upload_group_service import (
    add_video_to_group,
    create_group,
    delete_group,
    get_group,
    get_group_videos,
    get_user_groups,
    pause_group,
    remove_video_from_group,
    resume_group,
    update_group,
)
from services.video_service import VideoService
from services.file_service import FileService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Upload Groups"])
file_service = FileService()


# ── Request schemas ──────────────────────────────────────────────────────────

class CreateGroupRequest(BaseModel):
    user_id: str
    name: str
    platforms: List[str]
    privacy_status: str = "private"
    category: str = "entertainment"


class PatchGroupRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    status: Optional[str] = None  # "active" | "paused"


class DeleteGroupRequest(BaseModel):
    user_id: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _serialize_group(group, db: Session) -> dict:
    videos = get_group_videos(db, group.id)
    next_upload = None
    queued = [v for v in videos if v.status == "queued" and v.scheduled_at]
    if queued:
        next_upload = min(v.scheduled_at for v in queued).isoformat()

    return {
        "id": group.id,
        "name": group.name,
        "platforms": group.platforms,
        "privacy_status": group.privacy_status,
        "category": group.category,
        "status": group.status,
        "video_count": len(videos),
        "next_upload": next_upload,
        "created_at": group.created_at.isoformat(),
        "updated_at": group.updated_at.isoformat() if group.updated_at else None,
    }


def _serialize_group_video(gv: GroupVideoModel, db: Session) -> dict:
    video = db.query(VideoModel).filter(VideoModel.id == gv.video_id).first()
    return {
        "id": gv.id,
        "video_id": gv.video_id,
        "position": gv.position,
        "status": gv.status,
        "scheduled_at": gv.scheduled_at.isoformat() if gv.scheduled_at else None,
        "uploaded_at": gv.uploaded_at.isoformat() if gv.uploaded_at else None,
        "ai_context": gv.ai_context,
        "title": video.title if video else None,
        "created_at": gv.created_at.isoformat(),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/")
async def create_upload_group(request: CreateGroupRequest, db: Session = Depends(get_db)):
    group = create_group(
        db,
        user_id=request.user_id,
        name=request.name,
        platforms=request.platforms,
        privacy_status=request.privacy_status,
        category=request.category,
    )
    return _serialize_group(group, db)


@router.get("/")
async def list_upload_groups(user_id: str, db: Session = Depends(get_db)):
    groups = get_user_groups(db, user_id)
    return {"groups": [_serialize_group(g, db) for g in groups]}


@router.get("/{group_id}")
async def get_upload_group(group_id: str, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    videos = get_group_videos(db, group_id)
    return {
        **_serialize_group(group, db),
        "videos": [_serialize_group_video(v, db) for v in videos],
    }


@router.post("/{group_id}/videos")
async def add_video(
    group_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    ai_context: str = Form(""),
    db: Session = Depends(get_db),
):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    content_type = video.content_type or ""
    filename = video.filename or ""
    is_video = content_type.startswith("video/") or any(
        filename.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    )
    if not is_video:
        raise HTTPException(status_code=400, detail="File is not a video")

    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    temp_path = await file_service.save_temp_file(video)

    video_record = VideoService.create_video_for_group(
        db=db,
        user_id=user_id,
        title=title,
        description=description,
        tags=tags_list,
        platforms=group.platforms,
        privacy_status=group.privacy_status,
        file_path=temp_path,
    )

    gv = add_video_to_group(db, group_id=group_id, video_id=video_record.id, ai_context=ai_context or None)

    return {
        "group_video_id": gv.id,
        "video_id": video_record.id,
        "scheduled_at": gv.scheduled_at.isoformat() if gv.scheduled_at else None,
        "status": gv.status,
    }


@router.delete("/{group_id}/videos/{gv_id}")
async def remove_video(group_id: str, gv_id: str, user_id: str, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        remove_video_from_group(db, gv_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"success": True}


@router.patch("/{group_id}")
async def patch_group(group_id: str, request: PatchGroupRequest, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if request.status == "paused":
        pause_group(db, group_id)
    elif request.status == "active":
        resume_group(db, group_id)

    updated = update_group(db, group_id, name=request.name)
    return _serialize_group(updated, db)


@router.delete("/{group_id}")
async def delete_upload_group(group_id: str, request: DeleteGroupRequest, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        delete_group(db, group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"success": True}


@router.get("/{group_id}/schedule-preview")
async def schedule_preview(group_id: str, db: Session = Depends(get_db)):
    from services.upload_group_service import get_group_videos
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    videos = get_group_videos(db, group_id)
    return {
        "group_id": group_id,
        "slots": [
            {
                "video_id": v.video_id,
                "position": v.position,
                "scheduled_at": v.scheduled_at.isoformat() if v.scheduled_at else None,
                "status": v.status,
            }
            for v in videos
        ],
    }
