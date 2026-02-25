import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import VideoModel
from models.video import VideoStatus
from services.file_service import FileService
from routers.youtube import upload_to_youtube
from routers.tiktok import upload_to_tiktok
from routers.instagram import upload_to_instagram

logger = logging.getLogger(__name__)
file_service = FileService()


class VideoService:
    
    @staticmethod
    def create_video(
        db: Session,
        user_id: str,
        title: str,
        description: str,
        tags: List[str],
        platforms: List[str],
        privacy_status: str
    ) -> VideoModel:
        """Erstellt ein neues Video in der Datenbank"""
        video_id = f"video_{int(datetime.now().timestamp() * 1000)}"
        
        db_video = VideoModel(
            id=video_id,
            user_id=user_id,
            title=title,
            description=description,
            tags=tags,
            platforms=platforms,
            privacy_status=privacy_status,
            status=VideoStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        
        logger.info(f"✅ Video erstellt: {video_id}")
        return db_video
    
    @staticmethod
    def get_video(db: Session, video_id: str) -> Optional[VideoModel]:
        """Holt ein Video aus der Datenbank"""
        return db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    @staticmethod
    def get_user_videos(db: Session, user_id: str) -> List[VideoModel]:
        """Holt alle Videos eines Users"""
        return db.query(VideoModel).filter(
            VideoModel.user_id == user_id
        ).order_by(VideoModel.created_at.desc()).all()
    
    @staticmethod
    def update_status(db: Session, video_id: str, status: VideoStatus):
        """Updated den Video-Status"""
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if video:
            video.status = status.value
            video.updated_at = datetime.now()
            db.commit()
            logger.info(f"📝 Video {video_id} - Status: {status}")
    
    @staticmethod
    def add_upload_result(db: Session, video_id: str, platform: str, result: dict):
        """Fügt Upload-Ergebnis hinzu"""
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if video:
            if not video.upload_results:
                video.upload_results = {}
            video.upload_results[platform] = result
            db.commit()
    
    @staticmethod
    def add_upload_error(db: Session, video_id: str, platform: str, error: str):
        """Fügt Upload-Fehler hinzu"""
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if video:
            if not video.errors:
                video.errors = {}
            video.errors[platform] = error
            db.commit()
    
    @staticmethod
    def delete_video(db: Session, video_id: str):
        """Löscht ein Video"""
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if video:
            db.delete(video)
            db.commit()
            logger.info(f"🗑️ Video {video_id} gelöscht")
        else:
            raise ValueError(f"Video {video_id} nicht gefunden")
    
    @staticmethod
    async def process_video_upload(video_id: str, temp_file_path: str):
        """
        Background Task: Führt den Upload auf alle Plattformen durch
        """
        # Neue DB Session für Background Task
        from models.database import SessionLocal
        db = SessionLocal()
        
        try:
            video = VideoService.get_video(db, video_id)
            
            if not video:
                logger.error(f"❌ Video {video_id} nicht gefunden")
                return
            
            # Status: Processing
            VideoService.update_status(db, video_id, VideoStatus.PROCESSING)
            
            successful = []
            failed = []
            
            # YouTube Upload
            if "youtube" in video.platforms:
                try:
                    logger.info(f"📤 Uploading to YouTube: {video_id}")
                    result = upload_to_youtube(
                        video.user_id,
                        temp_file_path,
                        video.title,
                        video.description or "",
                        video.tags or [],
                        video.privacy_status
                    )
                    VideoService.add_upload_result(db, video_id, "youtube", result)
                    successful.append("youtube")
                    logger.info(f"✅ YouTube Upload erfolgreich: {video_id}")
                except Exception as e:
                    logger.error(f"❌ YouTube Upload fehlgeschlagen: {str(e)}")
                    VideoService.add_upload_error(db, video_id, "youtube", str(e))
                    failed.append("youtube")
            
            # TikTok Upload
            if "tiktok" in video.platforms:
                try:
                    logger.info(f"📤 Uploading to TikTok: {video_id}")
                    result = upload_to_tiktok(
                        video.user_id,
                        temp_file_path,
                        video.title,
                        video.description or "",
                        video.tags or []
                    )
                    VideoService.add_upload_result(db, video_id, "tiktok", result)
                    successful.append("tiktok")
                    logger.info(f"✅ TikTok Upload erfolgreich: {video_id}")
                except Exception as e:
                    logger.error(f"❌ TikTok Upload fehlgeschlagen: {str(e)}")
                    VideoService.add_upload_error(db, video_id, "tiktok", str(e))
                    failed.append("tiktok")
            
            # Instagram Upload
            if "instagram" in video.platforms:
                try:
                    logger.info(f"📤 Uploading to Instagram: {video_id}")
                    result = upload_to_instagram(
                        video.user_id,
                        temp_file_path,
                        video.title
                    )
                    VideoService.add_upload_result(db, video_id, "instagram", result)
                    successful.append("instagram")
                    logger.info(f"✅ Instagram Upload erfolgreich: {video_id}")
                except Exception as e:
                    logger.error(f"❌ Instagram Upload fehlgeschlagen: {str(e)}")
                    VideoService.add_upload_error(db, video_id, "instagram", str(e))
                    failed.append("instagram")
            
            # Final Status
            if len(failed) == 0:
                VideoService.update_status(db, video_id, VideoStatus.UPLOADED)
            elif len(successful) > 0:
                VideoService.update_status(db, video_id, VideoStatus.PARTIAL)
            else:
                VideoService.update_status(db, video_id, VideoStatus.FAILED)
            
            logger.info(f"✅ Upload abgeschlossen: {video_id} - Erfolgreich: {successful}, Fehlgeschlagen: {failed}")
            
        except Exception as e:
            logger.error(f"❌ Video Processing fehlgeschlagen: {str(e)}")
            try:
                VideoService.update_status(db, video_id, VideoStatus.FAILED)
            except:
                pass
        
        finally:
            # Cleanup
            db.close()
            
            # Delete temp file
            try:
                file_service.delete_file(temp_file_path)
                logger.info(f"🗑️ Temp file deleted: {temp_file_path}")
            except Exception as e:
                logger.error(f"❌ Fehler beim Löschen der Temp-Datei: {str(e)}")
