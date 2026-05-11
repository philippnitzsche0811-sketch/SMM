from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
import logging

from services.file_service import FileService
from services.video_service import VideoService
from models.database import get_db, VideoModel
from models.video import Video, VideoStatus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Upload"])

file_service = FileService()
video_service = VideoService()


# ================================================================================
# Request Models
# ================================================================================

class DeleteVideoRequest(BaseModel):
    user_id: str


class UpdateVideoRequest(BaseModel):
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    privacy_status: Optional[str] = None


class SimpleUploadFinalizeRequest(BaseModel):
    user_id: str
    title: str
    description: str = ""
    tags: List[str] = []
    platforms: List[str]
    privacy_status: str = "private"
    schedule_type: str = "now"       # "now" | "datetime" | "group"
    scheduled_at: Optional[str] = None
    group_id: Optional[str] = None


# ================================================================================
# Upload
# ================================================================================

@router.post("/upload_video")
async def upload_video(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    privacy_status: str = Form("private"),
    platforms: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"📤 Video-Upload Request von User {user_id}")

        content_type = video.content_type or ""
        filename = video.filename or ""

        is_video = (
            content_type.startswith("video/") or
            any(filename.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"])
        )

        if not is_video:
            raise HTTPException(
                status_code=400,
                detail=f"Hochgeladene Datei ist kein Video (Type: {content_type})"
            )

        platform_list = [p.strip().lower() for p in platforms.split(",") if p.strip()]
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]

        # Temp-Datei speichern
        temp_video_path = await file_service.save_temp_file(video)
        logger.info(f"💾 Temp file saved: {temp_video_path}")

        # Video in DB anlegen – file_path wird mitgespeichert
        video_record = video_service.create_video(
            db=db,
            user_id=user_id,
            title=title,
            description=description,
            tags=tags_list,
            platforms=platform_list,
            privacy_status=privacy_status,
            file_path=temp_video_path
        )

        # Background Upload starten
        background_tasks.add_task(
            video_service.process_video_upload,
            video_record.id,
            temp_video_path
        )

        logger.info(f"✅ Video {video_record.id} erstellt - Background Upload gestartet")

        return {
            "video_id": video_record.id,
            "status": video_record.status,
            "message": "Upload gestartet",
            "platforms": video_record.platforms,
            "created_at": video_record.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Video-Upload fehlgeschlagen: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload fehlgeschlagen: {str(e)}")


# ================================================================================
# Video Status & Info
# ================================================================================

@router.get("/video/{video_id}")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    try:
        video = video_service.get_video(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail=f"Video {video_id} nicht gefunden")

        return {
            "video_id": video.id,
            "status": video.status,
            "title": video.title,
            "description": video.description,
            "platforms": video.platforms,
            "tags": video.tags,
            "privacy_status": video.privacy_status,
            "upload_results": video.upload_results or {},
            "errors": video.errors,
            "created_at": video.created_at.isoformat(),
            "updated_at": video.updated_at.isoformat() if video.updated_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Videos {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Videos: {str(e)}")


@router.get("/videos/user/{user_id}")
async def get_user_videos(user_id: str, db: Session = Depends(get_db)):
    try:
        videos = video_service.get_user_videos(db, user_id)

        return {
            "user_id": user_id,
            "total": len(videos),
            "videos": [
                {
                    "video_id": v.id,
                    "title": v.title,
                    "description": v.description,
                    "status": v.status,
                    "platforms": v.platforms,
                    "tags": v.tags,
                    "privacy_status": v.privacy_status,
                    "upload_results": v.upload_results or {},
                    "errors": v.errors,
                    "created_at": v.created_at.isoformat(),
                    "updated_at": v.updated_at.isoformat() if v.updated_at else None
                }
                for v in videos
            ]
        }

    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Videos für User {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Videos: {str(e)}")


# ================================================================================
# Update
# ================================================================================

@router.patch("/video/{video_id}")
async def update_video(
    video_id: str,
    request: UpdateVideoRequest,
    db: Session = Depends(get_db)
):
    try:
        video = video_service.get_video(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail=f"Video {video_id} nicht gefunden")

        if video.user_id != request.user_id:
            raise HTTPException(status_code=403, detail="Nicht autorisiert")

        updated = False

        if request.title:
            video.title = request.title
            updated = True
        if request.description is not None:
            video.description = request.description
            updated = True
        if request.tags:
            video.tags = [t.strip() for t in request.tags.split(",")]
            updated = True
        if request.privacy_status:
            video.privacy_status = request.privacy_status
            updated = True

        if updated:
            video.updated_at = datetime.now()
            db.commit()
            db.refresh(video)

        return {
            "success": True,
            "message": "Video aktualisiert" if updated else "Keine Änderungen",
            "video": {
                "video_id": video.id,
                "title": video.title,
                "description": video.description,
                "tags": video.tags,
                "privacy_status": video.privacy_status,
                "updated_at": video.updated_at.isoformat() if video.updated_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update fehlgeschlagen für Video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update fehlgeschlagen: {str(e)}")


# ================================================================================
# Delete (lokal + Plattformen)
# ================================================================================

@router.post("/simple")
async def simple_upload(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    platforms: str = Form(...),
    privacy_status: str = Form("private"),
    schedule_type: str = Form("now"),
    scheduled_at: str = Form(""),
    group_id: str = Form(""),
    upload_mode: str = Form("simple"),
    db: Session = Depends(get_db),
):
    content_type = video.content_type or ""
    filename = video.filename or ""
    is_video = content_type.startswith("video/") or any(
        filename.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    )
    if not is_video:
        raise HTTPException(status_code=400, detail="File is not a video")

    platform_list = [p.strip().lower() for p in platforms.split(",") if p.strip()]
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    temp_path = await file_service.save_temp_file(video)

    scheduled_dt = None
    if scheduled_at:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
            if scheduled_dt.tzinfo is not None:
                scheduled_dt = scheduled_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_at format")

    video_record = video_service.create_video(
        db=db,
        user_id=user_id,
        title=title,
        description=description,
        tags=tags_list,
        platforms=platform_list,
        privacy_status=privacy_status,
        file_path=temp_path,
    )
    db_video = db.query(VideoModel).filter(VideoModel.id == video_record.id).first()
    if db_video:
        db_video.upload_mode = upload_mode
        db_video.scheduled_at = scheduled_dt
        db.commit()

    if schedule_type == "now":
        background_tasks.add_task(
            video_service.process_video_upload,
            video_record.id,
            temp_path,
        )
        return {"video_id": video_record.id, "status": "uploading", "schedule_type": "now"}

    if schedule_type == "datetime" and scheduled_dt:
        return {
            "video_id": video_record.id,
            "status": "scheduled",
            "scheduled_at": scheduled_dt.isoformat(),
        }

    if schedule_type == "group" and group_id:
        from services.upload_group_service import add_video_to_group
        gv = add_video_to_group(db, group_id=group_id, video_id=video_record.id)
        return {
            "video_id": video_record.id,
            "group_video_id": gv.id,
            "status": "queued",
            "scheduled_at": gv.scheduled_at.isoformat() if gv.scheduled_at else None,
        }

    raise HTTPException(status_code=400, detail="Invalid schedule_type or missing parameters")


@router.post("/finalize/{video_id}")
async def finalize_upload(
    video_id: str,
    request: SimpleUploadFinalizeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    video.title = request.title
    video.description = request.description
    video.tags = request.tags
    video.platforms = request.platforms
    video.privacy_status = request.privacy_status
    video.updated_at = datetime.now()
    db.commit()

    if request.schedule_type == "now":
        background_tasks.add_task(
            video_service.process_video_upload,
            video_id,
            video.file_path,
        )
        return {"video_id": video_id, "status": "uploading"}

    if request.schedule_type == "datetime" and request.scheduled_at:
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_at)
            if scheduled_dt.tzinfo is not None:
                scheduled_dt = scheduled_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_at format")
        video.scheduled_at = scheduled_dt
        db.commit()
        return {"video_id": video_id, "status": "scheduled", "scheduled_at": scheduled_dt.isoformat()}

    if request.schedule_type == "group" and request.group_id:
        from services.upload_group_service import add_video_to_group
        gv = add_video_to_group(db, group_id=request.group_id, video_id=video_id)
        return {
            "video_id": video_id,
            "group_video_id": gv.id,
            "status": "queued",
            "scheduled_at": gv.scheduled_at.isoformat() if gv.scheduled_at else None,
        }

    raise HTTPException(status_code=400, detail="Invalid schedule_type")


@router.delete("/video/{video_id}")
async def delete_video(
    video_id: str,
    request: DeleteVideoRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"🗑️ Delete Request: video_id={video_id}, user_id={request.user_id}")

        video = video_service.get_video(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail=f"Video {video_id} nicht gefunden")

        if video.user_id != request.user_id:
            raise HTTPException(status_code=403, detail="Nicht autorisiert")

        video_title = video.title
        platforms = video.platforms or []
        upload_results = video.upload_results or {}

        # Plattform-Löschung (Best Effort)
        for platform in platforms:
            platform_video_id = (upload_results.get(platform) or {}).get("video_id")
            if not platform_video_id:
                logger.info(f"ℹ️ Keine Plattform-Video-ID für {platform} – überspringe")
                continue
            try:
                if platform == "youtube":
                    from routers.youtube import delete_from_youtube
                    await delete_from_youtube(request.user_id, platform_video_id)
                elif platform == "tiktok":
                    from routers.tiktok import delete_from_tiktok
                    await delete_from_tiktok(request.user_id, platform_video_id)
                elif platform == "instagram":
                    from routers.instagram import delete_from_instagram
                    await delete_from_instagram(request.user_id, platform_video_id)
                logger.info(f"✅ Video von {platform} gelöscht")
            except Exception as e:
                logger.warning(f"⚠️ Platform-Delete fehlgeschlagen ({platform}): {str(e)}")

        # Lokale Datei löschen (falls noch vorhanden)
        if video.file_path:
            file_service.delete_file(video.file_path)

        # Aus DB löschen
        video_service.delete_video(db, video_id)

        return {
            "success": True,
            "message": f"Video '{video_title}' wurde gelöscht",
            "video_id": video_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete fehlgeschlagen für Video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Löschen fehlgeschlagen: {str(e)}")
