from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime
from pathlib import Path

from services.user_service import UserService
from services.token_storage import TokenStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["User Management"])

user_service = UserService()
token_storage = TokenStorage()

@router.get("/{user_id}/status")
async def get_user_status(user_id: str):
    """
    PrÃ¼ft welche Plattformen ein User verbunden hat
    Returns connected platforms with metadata
    """
    
    connected_platforms = []
    
    # YouTube
    if (user_service.get_platform_credentials(user_id, "youtube") or 
        token_storage.load_youtube_credentials(user_id)):
        
        # Get token file timestamp for connected_at
        token_path = Path("tokens") / f"{user_id}_youtube_token.json"
        connected_at = None
        if token_path.exists():
            timestamp = token_path.stat().st_mtime
            connected_at = datetime.fromtimestamp(timestamp).isoformat()
        
        connected_platforms.append({
            "platform": "youtube",
            "connected_at": connected_at,
            "account_id": "N/A"  # Could be extracted from token later
        })
    
    # TikTok
    if (user_service.get_platform_credentials(user_id, "tiktok") or 
        token_storage.load_tiktok_credentials(user_id)):
        
        token_path = Path("tokens") / f"{user_id}_tiktok_token.json"
        connected_at = None
        if token_path.exists():
            timestamp = token_path.stat().st_mtime
            connected_at = datetime.fromtimestamp(timestamp).isoformat()
        
        connected_platforms.append({
            "platform": "tiktok",
            "connected_at": connected_at,
            "account_id": "N/A"
        })
    
    # Instagram
    if (user_service.get_platform_credentials(user_id, "instagram") or 
        token_storage.load_instagram_credentials(user_id)):
        
        token_path = Path("tokens") / f"{user_id}_instagram_token.json"
        connected_at = None
        if token_path.exists():
            timestamp = token_path.stat().st_mtime
            connected_at = datetime.fromtimestamp(timestamp).isoformat()
        
        connected_platforms.append({
            "platform": "instagram",
            "connected_at": connected_at,
            "account_id": "N/A"
        })
    
    logger.info(f"âœ… User {user_id} hat {len(connected_platforms)} Plattform(en) verbunden")
    
    return {
        "user_id": user_id,
        "exists": len(connected_platforms) > 0,
        "connected_platforms": connected_platforms
    }

@router.delete("/{user_id}/disconnect/{platform}")
async def disconnect_platform(user_id: str, platform: str):
    """Trennt eine Plattform von einem User"""
    try:
        # Aus Memory entfernen
        try:
            user_service.remove_platform_credentials(user_id, platform)
        except ValueError:
            pass
        
        # Von Disk lÃ¶schen
        if platform == "youtube":
            token_storage.delete_youtube_credentials(user_id)
        elif platform == "tiktok":
            token_path = token_storage._get_token_path(user_id, "tiktok")
            if token_path.exists():
                token_path.unlink()
        elif platform == "instagram":
            token_path = token_storage._get_token_path(user_id, "instagram")
            if token_path.exists():
                token_path.unlink()
        
        logger.info(f"âœ… Plattform {platform} von User {user_id} getrennt")
        return {
            "status": "success",
            "message": f"{platform} wurde getrennt"
        }
    except Exception as e:
        logger.error(f"âŒ Fehler beim Trennen von {platform}: {str(e)}")
        raise HTTPException(500, f"Fehler beim Trennen: {str(e)}")

