"""
TikTok Upload Service
"""
import requests
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TIKTOK_API_BASE = "https://open.tiktokapis.com"


def tiktok_upload_video(
    access_token: str,
    open_id: str,
    video_path: str,
    caption: str = "",
    privacy_level: str = "SELF_ONLY"  # SELF_ONLY, MUTUAL_FOLLOW_FRIENDS, PUBLIC_TO_EVERYONE
) -> dict:
    """
    Lädt ein Video auf TikTok hoch
    
    Args:
        access_token: TikTok Access Token
        open_id: TikTok Open ID des Users
        video_path: Pfad zur Video-Datei
        caption: Video-Caption (max 2200 Zeichen)
        privacy_level: Privacy-Einstellung
    
    Returns:
        dict: Upload-Response
    """
    try:
        # Validierung
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
        
        filesize = Path(video_path).stat().st_size
        
        # Caption kürzen falls nötig
        if len(caption) > 2200:
            logger.warning("⚠️ TikTok Caption zu lang, wird gekürzt")
            caption = caption[:2197] + "..."
        
        logger.info(f"📤 TikTok-Upload startet (Größe: {filesize} bytes)")
        
        # Schritt 1: Upload initialisieren
        init_response = _initialize_upload(
            access_token=access_token,
            caption=caption,
            privacy_level=privacy_level,
            filesize=filesize
        )
        
        upload_url = init_response["data"]["upload_url"]
        publish_id = init_response["data"]["publish_id"]
        
        logger.info(f"✅ Upload initialisiert (publish_id: {publish_id})")
        
        # Schritt 2: Video hochladen
        _upload_video_file(upload_url, video_path, filesize)
        
        logger.info("✅ TikTok-Upload erfolgreich!")
        
        return {
            "publish_id": publish_id,
            "status": "uploaded",
            "message": "Video wird von TikTok verarbeitet"
        }
        
    except requests.RequestException as e:
        logger.error(f"❌ TikTok API Fehler: {e}")
        raise Exception(f"TikTok Upload fehlgeschlagen: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ TikTok Upload fehlgeschlagen: {e}")
        raise


def _initialize_upload(
    access_token: str,
    caption: str,
    privacy_level: str,
    filesize: int
) -> dict:
    """
    Initialisiert den TikTok Upload
    
    Returns:
        dict: Init-Response mit upload_url und publish_id
    """
    url = f"{TIKTOK_API_BASE}/v2/post/publish/inbox/video/init/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # Für kleine Videos: Single-Chunk Upload
    chunk_size = filesize
    total_chunks = 1
    
    data = {
        "post_info": {
            "title": caption,
            "description": caption,
            "privacy_level": privacy_level,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": filesize,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunks
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    
    if "data" not in result:
        raise ValueError(f"Ungültige TikTok API Response: {result}")
    
    return result


def _upload_video_file(upload_url: str, video_path: str, filesize: int):
    """
    Lädt die Video-Datei zum TikTok Server hoch
    """
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    
    headers = {
        "Content-Type": "video/mp4",
        "Content-Length": str(len(video_bytes)),
        "Content-Range": f"bytes 0-{len(video_bytes)-1}/{len(video_bytes)}"
    }
    
    response = requests.put(
        upload_url,
        data=video_bytes,
        headers=headers,
        timeout=300  # 5 Minuten Timeout für große Dateien
    )
    response.raise_for_status()
    
    logger.info(f"📤 Video hochgeladen ({filesize} bytes)")


def get_upload_status(access_token: str, publish_id: str) -> dict:
    """
    Prüft den Status eines TikTok-Uploads
    
    Args:
        access_token: TikTok Access Token
        publish_id: Publish ID vom Upload
    
    Returns:
        dict: Status-Informationen
    """
    url = f"{TIKTOK_API_BASE}/v2/post/publish/status/fetch/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    data = {"publish_id": publish_id}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"❌ Status-Abfrage fehlgeschlagen: {e}")
        raise