from fastapi import APIRouter, Request as FastAPIRequest, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging
import requests

from config import settings
from services.instagram_service import instagram_upload_video
from services.user_service import UserService
from services.token_storage import TokenStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Instagram"])

user_service = UserService()
token_storage = TokenStorage()


# ==========================================
# Request Models
# ==========================================

class ConnectRequest(BaseModel):
    user_id: str

class DisconnectRequest(BaseModel):
    user_id: str

class RefreshRequest(BaseModel):
    user_id: str


# ==========================================
# OAuth Endpoints
# ==========================================

@router.post("/connect")
async def connect_instagram(request: ConnectRequest):
    """
    Generiert Instagram OAuth URL fÃ¼r User
    
    Body:
        {
            "user_id": "user_xxx"
        }
    
    Returns:
        OAuth URL zum Weiterleiten des Users
    """
    try:
        logger.info(f"Instagram Auth-URL wird fÃ¼r User {request.user_id} generiert...")
        
        client_id = settings.INSTAGRAM_CLIENT_ID
        
        if not client_id:
            raise HTTPException(400, "Instagram Client ID nicht konfiguriert.")
        
        redirect_uri = f"{settings.BACKEND_URL}/instagram/oauth/callback"
        scopes = "user_profile,user_media"
        
        auth_url = (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&response_type=code"
            f"&state={request.user_id}"
        )
        
        logger.info(f"âœ… Instagram Auth-URL generiert fÃ¼r User {request.user_id}")
        
        return {
            "status": "success",
            "message": "Bitte im Browser authentifizieren",
            "auth_url": auth_url,
            "user_id": request.user_id,
            "platform": "instagram"
        }
        
    except Exception as e:
        logger.error(f"âŒ Instagram Auth-URL Generierung fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"Instagram-Auth fehlgeschlagen: {str(e)}")


@router.get("/oauth/callback")
async def instagram_oauth_callback(request: FastAPIRequest):
    """
    Callback fÃ¼r Instagram OAuth Flow
    
    Query Parameters:
        code: Authorization Code von Instagram
        state: User-ID (wurde im OAuth-Start Ã¼bergeben)
    """
    try:
        code = request.query_params.get("code")
        user_id = request.query_params.get("state")
        error = request.query_params.get("error")
        
        if error:
            logger.error(f"Instagram OAuth Fehler: {error}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message={error}"
            )
        
        if not code or not user_id:
            raise HTTPException(400, "Code oder User-ID fehlt in Callback")
        
        logger.info(f"Instagram OAuth Callback fÃ¼r User {user_id}")
        
        # Exchange code for token
        access_token, ig_user_id = await exchange_instagram_code_for_token(code)
        
        # Get long-lived token
        long_lived_token = await get_long_lived_token(access_token)
        
        # Save credentials
        token_storage.save_instagram_credentials(user_id, long_lived_token, ig_user_id)
        
        user_service.set_platform_credentials(
            user_id=user_id,
            platform="instagram",
            credentials={
                "access_token": long_lived_token,
                "user_id": ig_user_id
            }
        )
        
        logger.info(f"âœ… Instagram erfolgreich verbunden fÃ¼r User {user_id}")
        
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?success=instagram"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"âŒ Instagram OAuth fehlgeschlagen: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message={str(e)}"
        )


async def exchange_instagram_code_for_token(code: str) -> tuple[str, str]:
    """
    Tauscht Authorization Code gegen Access Token
    
    Returns:
        tuple: (access_token, ig_user_id)
    """
    url = "https://api.instagram.com/oauth/access_token"
    redirect_uri = f"{settings.BACKEND_URL}/instagram/oauth/callback"
    
    data = {
        "client_id": settings.INSTAGRAM_CLIENT_ID,
        "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        if "access_token" not in result:
            raise ValueError(f"UngÃ¼ltige Instagram API Response: {result}")
        
        return result["access_token"], str(result["user_id"])
        
    except requests.RequestException as e:
        logger.error(f"Instagram Token Exchange fehlgeschlagen: {str(e)}")
        raise ValueError(f"Token Exchange fehlgeschlagen: {str(e)}")


async def get_long_lived_token(short_lived_token: str) -> str:
    """
    Konvertiert Short-Lived Token in Long-Lived Token (60 Tage)
    """
    url = "https://graph.instagram.com/access_token"
    
    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
        "access_token": short_lived_token
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        return result["access_token"]
        
    except Exception as e:
        logger.warning(f"Long-lived token exchange fehlgeschlagen: {str(e)}")
        return short_lived_token


# ==========================================
# Token Management
# ==========================================

@router.post("/refresh")
async def refresh_instagram_token(request: RefreshRequest):
    """
    Erneuert Instagram Access Token (vor Ablauf)
    
    Body:
        {
            "user_id": "user_xxx"
        }
    """
    try:
        creds = token_storage.load_instagram_credentials(request.user_id)
        
        if not creds or "access_token" not in creds:
            raise HTTPException(404, "Keine Instagram Credentials gefunden")
        
        url = "https://graph.instagram.com/refresh_access_token"
        
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": creds["access_token"]
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        # Save new token
        token_storage.save_instagram_credentials(
            request.user_id,
            result["access_token"],
            creds["user_id"]
        )
        
        logger.info(f"âœ… Instagram Token erneuert fÃ¼r User {request.user_id}")
        
        return {"status": "success", "message": "Token erneuert"}
        
    except Exception as e:
        logger.error(f"âŒ Instagram Token Refresh fehlgeschlagen: {str(e)}")
        raise HTTPException(500, str(e))


@router.post("/disconnect")
async def disconnect_instagram(request: DisconnectRequest):
    """
    Trennt Instagram Verbindung
    
    Body:
        {
            "user_id": "user_xxx"
        }
    """
    try:
        # Delete tokens
        token_storage.delete_instagram_credentials(request.user_id)
        
        # Remove from user service
        user_service.remove_platform_credentials(request.user_id, "instagram")
        
        logger.info(f"âœ… Instagram getrennt fÃ¼r User {request.user_id}")
        
        return {
            "status": "success",
            "message": "Instagram wurde getrennt"
        }
        
    except Exception as e:
        logger.error(f"âŒ Instagram Disconnect fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"Disconnect fehlgeschlagen: {str(e)}")


# ==========================================
# Upload Helper
# ==========================================

async def upload_to_instagram(user_id: str, video_path: str, title: str):
    """
    Hilfsfunktion fÃ¼r Instagram Upload
    
    Returns:
        dict: Upload-Ergebnis
    """
    ig_creds = user_service.get_platform_credentials(user_id, "instagram")
    
    if not ig_creds:
        logger.info(f"Lade Instagram-Token von Disk fÃ¼r User {user_id}")
        ig_creds = token_storage.load_instagram_credentials(user_id)
        
        if ig_creds:
            user_service.set_platform_credentials(user_id, "instagram", ig_creds)
    
    if not ig_creds:
        raise ValueError("Instagram nicht verbunden - User muss sich authentifizieren")
    
    result = instagram_upload_video(
        ig_user_id=ig_creds["user_id"],
        access_token=ig_creds["access_token"],
        video_path=video_path,
        caption=title
    )
    
    logger.info(f"âœ… Instagram Upload erfolgreich fÃ¼r User {user_id}")
    
    return result



