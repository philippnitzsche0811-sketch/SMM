from fastapi import APIRouter, Request as FastAPIRequest, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging
import requests
import hashlib
import base64
import secrets

from config import settings
from services.tiktok_service import tiktok_upload_video
from utils.utils import build_tiktok_caption
from services.user_service import UserService
from services.token_storage import TokenStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["TikTok"])

user_service = UserService()
token_storage = TokenStorage()

# Store code_verifier temporarily (in production use Redis/Database)
pkce_storage = {}


# ==========================================
# PKCE Helper Functions
# ==========================================

def generate_code_verifier() -> str:
    """Generiert einen zufÃ¤lligen Code Verifier fÃ¼r PKCE"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')


def generate_code_challenge(code_verifier: str) -> str:
    """Generiert Code Challenge aus Code Verifier"""
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


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
async def connect_tiktok(request: ConnectRequest):
    """
    Generiert TikTok OAuth URL mit PKCE
    
    Body:
        {
            "user_id": "user_xxx"
        }
    
    Returns:
        OAuth URL zum Weiterleiten des Users
    """
    try:
        logger.info(f"TikTok Auth-URL wird fÃ¼r User {request.user_id} generiert...")
        
        client_key = settings.TIKTOK_CLIENT_KEY
        
        if not client_key:
            raise HTTPException(400, "TikTok Client Key nicht konfiguriert.")
        
        # Generate PKCE codes
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        
        # Store code_verifier temporarily (mapped to user_id)
        pkce_storage[request.user_id] = code_verifier
        
        redirect_uri = f"{settings.BACKEND_URL}/tiktok/oauth/callback"
        scopes = "user.info.basic,video.upload,video.publish"
        
        auth_url = (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={client_key}"
            f"&scope={scopes}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&state={request.user_id}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )
        
        logger.info(f"âœ… TikTok Auth-URL mit PKCE generiert fÃ¼r User {request.user_id}")
        
        return {
            "status": "success",
            "message": "Bitte im Browser authentifizieren",
            "auth_url": auth_url,
            "user_id": request.user_id,
            "platform": "tiktok"
        }
        
    except Exception as e:
        logger.error(f"âŒ TikTok Auth-URL Generierung fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"TikTok-Auth fehlgeschlagen: {str(e)}")


@router.get("/oauth/callback")
async def tiktok_oauth_callback(request: FastAPIRequest):
    """
    Callback fÃ¼r TikTok OAuth Flow
    
    Query Parameters:
        code: Authorization Code von TikTok
        state: User-ID (wurde im OAuth-Start Ã¼bergeben)
    """
    try:
        code = request.query_params.get("code")
        user_id = request.query_params.get("state")
        error = request.query_params.get("error")
        error_description = request.query_params.get("error_description")
        
        if error:
            logger.error(f"TikTok OAuth Fehler: {error} - {error_description}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=tiktok&message={error_description or error}"
            )
        
        if not code or not user_id:
            raise HTTPException(400, "Code oder User-ID fehlt in Callback")
        
        # Retrieve code_verifier
        code_verifier = pkce_storage.get(user_id)
        if not code_verifier:
            raise HTTPException(400, "Code Verifier nicht gefunden - Session abgelaufen")
        
        logger.info(f"TikTok OAuth Callback fÃ¼r User {user_id}")
        
        # Exchange code for token (with code_verifier)
        access_token, open_id, refresh_token = await exchange_code_for_token(code, code_verifier)
        
        # Save credentials
        token_storage.save_tiktok_credentials(user_id, access_token, open_id, refresh_token)
        
        user_service.set_platform_credentials(
            user_id=user_id,
            platform="tiktok",
            credentials={
                "access_token": access_token,
                "open_id": open_id,
                "refresh_token": refresh_token
            }
        )
        
        # Clean up PKCE storage
        pkce_storage.pop(user_id, None)
        
        logger.info(f"âœ… TikTok erfolgreich verbunden fÃ¼r User {user_id}")
        
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?success=tiktok"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"âŒ TikTok OAuth fehlgeschlagen: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?error=tiktok&message={str(e)}"
        )


async def exchange_code_for_token(code: str, code_verifier: str) -> tuple[str, str, str]:
    """
    Tauscht Authorization Code gegen Access Token (mit PKCE)
    
    Returns:
        tuple: (access_token, open_id, refresh_token)
    """
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "client_secret": settings.TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{settings.BACKEND_URL}/tiktok/oauth/callback",
        "code_verifier": code_verifier  # âœ… PKCE code_verifier
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    
    try:
        logger.info(f"ðŸ”„ Token Exchange Request: {url}")
        
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        
        logger.info(f"ðŸ“¥ Token Exchange Response Status: {resp.status_code}")
        logger.info(f"ðŸ“¥ Token Exchange Response: {resp.text}")
        
        resp.raise_for_status()
        result = resp.json()
        
        if "access_token" not in result:
            raise ValueError(f"UngÃ¼ltige TikTok API Response: {result}")
        
        access_token = result["access_token"]
        open_id = result["open_id"]
        refresh_token = result.get("refresh_token", "")
        
        return access_token, open_id, refresh_token
        
    except requests.RequestException as e:
        logger.error(f"âŒ TikTok Token Exchange fehlgeschlagen: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"âŒ Response Body: {e.response.text}")
        raise ValueError(f"Token Exchange fehlgeschlagen: {str(e)}")


# ==========================================
# Token Management
# ==========================================

@router.post("/refresh")
async def refresh_tiktok_token(request: RefreshRequest):
    """
    Erneuert TikTok Access Token
    
    Body:
        {
            "user_id": "user_xxx"
        }
    """
    try:
        creds = token_storage.load_tiktok_credentials(request.user_id)
        
        if not creds or "refresh_token" not in creds:
            raise HTTPException(404, "Keine TikTok Credentials gefunden")
        
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        
        data = {
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": creds["refresh_token"]
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        # Save new tokens
        token_storage.save_tiktok_credentials(
            request.user_id,
            result["access_token"],
            creds["open_id"],
            result.get("refresh_token", creds["refresh_token"])
        )
        
        logger.info(f"âœ… TikTok Token erneuert fÃ¼r User {request.user_id}")
        
        return {"status": "success", "message": "Token erneuert"}
        
    except Exception as e:
        logger.error(f"âŒ TikTok Token Refresh fehlgeschlagen: {str(e)}")
        raise HTTPException(500, str(e))


@router.post("/disconnect")
async def disconnect_tiktok(request: DisconnectRequest):
    """
    Trennt TikTok Verbindung
    
    Body:
        {
            "user_id": "user_xxx"
        }
    """
    try:
        # Delete tokens
        token_storage.delete_tiktok_credentials(request.user_id)
        
        # Remove from user service
        user_service.remove_platform_credentials(request.user_id, "tiktok")
        
        # Clean up PKCE storage
        pkce_storage.pop(request.user_id, None)
        
        logger.info(f"âœ… TikTok getrennt fÃ¼r User {request.user_id}")
        
        return {
            "status": "success",
            "message": "TikTok wurde getrennt"
        }
        
    except Exception as e:
        logger.error(f"âŒ TikTok Disconnect fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"Disconnect fehlgeschlagen: {str(e)}")


# ==========================================
# Upload Helper
# ==========================================

async def upload_to_tiktok(user_id: str, video_path: str, title: str,
                           description: str, tags_list: list):
    """
    Hilfsfunktion fÃ¼r TikTok Upload
    
    Returns:
        dict: Upload-Ergebnis
    """
    tiktok_creds = user_service.get_platform_credentials(user_id, "tiktok")
    
    if not tiktok_creds:
        logger.info(f"Lade TikTok-Token von Disk fÃ¼r User {user_id}")
        tiktok_creds = token_storage.load_tiktok_credentials(user_id)
        
        if tiktok_creds:
            user_service.set_platform_credentials(user_id, "tiktok", tiktok_creds)
    
    if not tiktok_creds:
        raise ValueError("TikTok nicht verbunden - User muss sich authentifizieren")
    
    caption = build_tiktok_caption(title, description, tags_list)
    
    result = tiktok_upload_video(
        access_token=tiktok_creds["access_token"],
        open_id=tiktok_creds["open_id"],
        video_path=video_path,
        caption=caption
    )
    
    logger.info(f"âœ… TikTok Upload erfolgreich fÃ¼r User {user_id}")
    
    return result



