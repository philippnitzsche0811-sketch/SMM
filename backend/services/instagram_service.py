"""
Instagram Upload Service (Reels via Facebook Graph API)
"""
import requests
import logging
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


def instagram_upload_video(
    ig_user_id: str,
    access_token: str,
    video_path: str,
    caption: str = "",
    share_to_feed: bool = True
) -> dict:
    """
    Lädt ein Video als Instagram Reel hoch
    
    Args:
        ig_user_id: Instagram Business Account ID
        access_token: Facebook Access Token
        video_path: Pfad zur Video-Datei
        caption: Reel-Caption (max 2200 Zeichen)
        share_to_feed: Ob das Reel auch im Feed erscheinen soll
    
    Returns:
        dict: Upload-Response
    """
    try:
        # Validierung
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
        
        if len(caption) > 2200:
            logger.warning("⚠️ Instagram Caption zu lang, wird gekürzt")
            caption = caption[:2197] + "..."
        
        logger.info(f"📤 Instagram Reel-Upload startet...")
        
        # Schritt 1: Container erstellen
        container_id = _create_reel_container(
            ig_user_id=ig_user_id,
            access_token=access_token,
            video_path=video_path,
            caption=caption,
            share_to_feed=share_to_feed
        )
        
        logger.info(f"✅ Container erstellt (ID: {container_id})")
        
        # Schritt 2: Auf Verarbeitung warten
        _wait_for_container_ready(ig_user_id, access_token, container_id)
        
        # Schritt 3: Container veröffentlichen
        media_id = _publish_reel_container(
            ig_user_id=ig_user_id,
            access_token=access_token,
            creation_id=container_id
        )
        
        logger.info(f"✅ Instagram Reel veröffentlicht! Media-ID: {media_id}")
        
        return {
            "media_id": media_id,
            "container_id": container_id,
            "status": "published",
            "message": "Reel erfolgreich veröffentlicht"
        }
        
    except requests.RequestException as e:
        logger.error(f"❌ Instagram API Fehler: {e}")
        raise Exception(f"Instagram Upload fehlgeschlagen: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Instagram Upload fehlgeschlagen: {e}")
        raise


def _create_reel_container(
    ig_user_id: str,
    access_token: str,
    video_path: str,
    caption: str,
    share_to_feed: bool
) -> str:
    """
    Erstellt einen Reel-Container und lädt das Video hoch
    
    Returns:
        str: Container-ID
    """
    url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
    
    with open(video_path, "rb") as video_file:
        files = {
            "video_file": video_file
        }
        
        data = {
            "media_type": "REELS",
            "caption": caption,
            "share_to_feed": str(share_to_feed).lower(),
            "access_token": access_token
        }
        
        response = requests.post(url, data=data, files=files, timeout=300)
        response.raise_for_status()
    
    result = response.json()
    
    if "id" not in result:
        raise ValueError(f"Ungültige Instagram API Response: {result}")
    
    return result["id"]


def _wait_for_container_ready(
    ig_user_id: str,
    access_token: str,
    container_id: str,
    max_wait_time: int = 300
) -> bool:
    """
    Wartet bis der Container fertig verarbeitet ist
    
    Args:
        ig_user_id: Instagram User ID
        access_token: Access Token
        container_id: Container-ID
        max_wait_time: Maximale Wartezeit in Sekunden
    
    Returns:
        bool: True wenn bereit
    """
    url = f"https://graph.facebook.com/v18.0/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": access_token
    }
    
    start_time = time.time()
    
    logger.info("⏳ Warte auf Container-Verarbeitung...")
    
    while True:
        # Timeout check
        if time.time() - start_time > max_wait_time:
            raise TimeoutError("Container-Verarbeitung dauert zu lange")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            status = result.get("status_code")
            
            if status == "FINISHED":
                logger.info("✅ Container ist bereit")
                return True
            elif status == "ERROR":
                raise Exception("Container-Verarbeitung fehlgeschlagen")
            
            # Warte 5 Sekunden vor nächster Abfrage
            time.sleep(5)
            
        except requests.RequestException as e:
            logger.warning(f"⚠️ Status-Abfrage fehlgeschlagen: {e}")
            time.sleep(5)


def _publish_reel_container(
    ig_user_id: str,
    access_token: str,
    creation_id: str
) -> str:
    """
    Veröffentlicht den Reel-Container
    
    Returns:
        str: Media-ID
    """
    url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
    
    data = {
        "creation_id": creation_id,
        "access_token": access_token
    }
    
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    
    if "id" not in result:
        raise ValueError(f"Ungültige Publish-Response: {result}")
    
    return result["id"]


def get_media_insights(
    media_id: str,
    access_token: str
) -> dict:
    """
    Holt Insights/Statistiken für ein veröffentlichtes Reel
    
    Args:
        media_id: Instagram Media ID
        access_token: Access Token
    
    Returns:
        dict: Insights-Daten
    """
    url = f"https://graph.facebook.com/v18.0/{media_id}/insights"
    
    params = {
        "metric": "plays,likes,comments,shares,saved",
        "access_token": access_token
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"❌ Insights-Abfrage fehlgeschlagen: {e}")
        raise