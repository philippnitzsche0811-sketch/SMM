from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging

from services.file_service import FileService
from services.video_service import VideoService
from models.database import get_db
from models.video import Video

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


# ================================================================================
# Upload Routes
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
    """
    Lädt ein Video auf eine oder mehrere Plattformen hoch (asynchron)
    
    Args:
        user_id: User ID
        video: Video-Datei
        title: Video-Titel
        description: Video-Beschreibung
        tags: Komma-getrennte Tags
        privacy_status: Privacy Status (private/public/unlisted)
        platforms: Komma-getrennte Plattformen (youtube,tiktok,instagram)
    
    Returns:
        Video Upload Response mit video_id und status
    """
    try:
        logger.info(f"📤 Video-Upload Request von User {user_id}")
        
        # Validate video file
        content_type = video.content_type or ""
        filename = video.filename or ""
        
        is_video = (
            content_type.startswith('video/') or
            any(filename.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm'])
        )
        
        if not is_video:
            raise HTTPException(
                status_code=400, 
                detail=f"Hochgeladene Datei ist kein Video (Type: {content_type})"
            )
        
        # Parse parameters
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        tags_list = [t.strip() for t in tags.split(",")] if tags else []
        
        logger.info(f"🎯 Platforms: {platform_list}, Tags: {tags_list}")
        
        # Save temp file
        temp_video_path = await file_service.save_temp_file(video)
        logger.info(f"💾 Temp file saved: {temp_video_path}")
        
        # Create video record in database
        video_record = video_service.create_video(
            db=db,
            user_id=user_id,
            title=title,
            description=description,
            tags=tags_list,
            platforms=platform_list,
            privacy_status=privacy_status
        )
        
        # Start background upload task
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
        raise HTTPException(
            status_code=500, 
            detail=f"Upload fehlgeschlagen: {str(e)}"
        )


# ================================================================================
# Video Status & Info Routes
# ================================================================================

@router.get("/video/{video_id}")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    """
    Prüft den Status eines Video-Uploads
    
    Args:
        video_id: Video ID
    
    Returns:
        Video Status mit upload_results und errors
    """
    try:
        video = video_service.get_video(db, video_id)
        
        if not video:
            raise HTTPException(
                status_code=404, 
                detail=f"Video {video_id} nicht gefunden"
            )
        
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
        raise HTTPException(
            status_code=500, 
            detail=f"Fehler beim Abrufen des Videos: {str(e)}"
        )


@router.get("/videos/user/{user_id}")
async def get_user_videos(user_id: str, db: Session = Depends(get_db)):
    """
    Holt alle Videos eines Users aus der Datenbank
    
    Args:
        user_id: User ID
    
    Returns:
        Liste aller Videos des Users
    """
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
        raise HTTPException(
            status_code=500, 
            detail=f"Fehler beim Abrufen der Videos: {str(e)}"
        )


# ================================================================================
# Video Management Routes (Update/Delete)
# ================================================================================

@router.patch("/video/{video_id}")
async def update_video(
    video_id: str,
    request: UpdateVideoRequest,
    db: Session = Depends(get_db)
):
    """
    Aktualisiert Video-Metadaten
    
    Body:
    ```json
    {
        "user_id": "user_xxx",
        "title": "Neuer Titel",
        "description": "Neue Beschreibung",
        "tags": "tag1,tag2,tag3",
        "privacy_status": "public"
    }
    ```
    """
    try:
        video = video_service.get_video(db, video_id)
        
        if not video:
            raise HTTPException(
                status_code=404, 
                detail=f"Video {video_id} nicht gefunden"
            )
        
        # Check authorization
        if video.user_id != request.user_id:
            logger.warning(
                f"⚠️ User {request.user_id} versucht Video von {video.user_id} zu ändern"
            )
            raise HTTPException(
                status_code=403, 
                detail="Nicht autorisiert - Video gehört einem anderen User"
            )
        
        # Update fields if provided
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
            logger.info(f"✅ Video {video_id} aktualisiert von User {request.user_id}")
        else:
            logger.info(f"ℹ️ Keine Änderungen für Video {video_id}")
        
        return {
            "success": True,
            "message": "Video aktualisiert" if updated else "Keine Änderungen",
            "video": {
                "video_id": video.id,
                "title": video.title,
                "description": video.description,
                "tags": video.tags,
                "privacy_status": video.privacy_status,
                "updated_at": video.updated_at.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update fehlgeschlagen für Video {video_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Update fehlgeschlagen: {str(e)}"
        )


@router.delete("/video/{video_id}")
async def delete_video(
    video_id: str,
    request: DeleteVideoRequest,
    db: Session = Depends(get_db)
):
    """
    Löscht ein Video
    
    Body:
    ```json
    {
        "user_id": "user_xxx"
    }
    ```
    """
    try:
        logger.info(f"🗑️ Delete Request: video_id={video_id}, user_id={request.user_id}")
        
        video = video_service.get_video(db, video_id)
        
        if not video:
            raise HTTPException(
                status_code=404, 
                detail=f"Video {video_id} nicht gefunden"
            )
        
        # Check if user owns the video
        if video.user_id != request.user_id:
            logger.warning(
                f"⚠️ User {request.user_id} versucht Video von {video.user_id} zu löschen"
            )
            raise HTTPException(
                status_code=403, 
                detail="Nicht autorisiert - Video gehört einem anderen User"
            )
        
        video_title = video.title
        
        # Delete from database
        video_service.delete_video(db, video_id)
        
        logger.info(f"✅ Video {video_id} von User {request.user_id} gelöscht")
        
        return {
            "success": True,
            "message": f"Video '{video_title}' wurde gelöscht",
            "video_id": video_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete fehlgeschlagen für Video {video_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Löschen fehlgeschlagen: {str(e)}"
        )
