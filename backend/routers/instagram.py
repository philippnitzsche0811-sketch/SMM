# instagram_router.py
from fastapi import APIRouter, Request as FastAPIRequest, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging
import httpx
from urllib.parse import quote

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
    Generates Instagram OAuth URL for user.
    Uses new Instagram Graph API with Instagram Login.
    """
    try:
        logger.info(f"Generating Instagram auth URL for user {request.user_id}")

        client_id = settings.INSTAGRAM_CLIENT_ID
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI

        if not client_id:
            raise HTTPException(400, "Instagram Client ID nicht konfiguriert.")
        if not redirect_uri:
            raise HTTPException(400, "Instagram Redirect URI nicht konfiguriert.")

        scopes_raw = ",".join([
            "instagram_business_basic",
            "instagram_business_content_publish",
            "instagram_business_manage_comments",
            "instagram_business_manage_messages",
            "instagram_business_manage_insights"
        ])

        scopes = quote(scopes_raw, safe="")

        auth_url = (
            f"https://www.instagram.com/oauth/authorize"
            f"?force_reauth=true"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&state={request.user_id}"
        )

        logger.info(f"Instagram auth URL generated for user {request.user_id}")

        return {
            "status": "success",
            "message": "Bitte im Browser authentifizieren",
            "auth_url": auth_url,
            "user_id": request.user_id,
            "platform": "instagram"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram auth URL generation failed: {str(e)}")
        raise HTTPException(500, f"Instagram-Auth fehlgeschlagen: {str(e)}")


@router.get("/callback")
async def instagram_oauth_callback(request: FastAPIRequest):
    """
    Callback for Instagram OAuth Flow.
    Instagram redirects here after user authorization.
    """
    try:
        code = request.query_params.get("code")
        user_id = request.query_params.get("state")
        error = request.query_params.get("error")
        error_reason = request.query_params.get("error_reason", "")

        if error:
            logger.error(f"Instagram OAuth error: {error} - {error_reason}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message={error_reason or error}"
            )

        if not code:
            logger.error("Instagram callback: missing code")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message=missing_code"
            )

        if not user_id:
            logger.error("Instagram callback: missing state/user_id")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message=missing_state"
            )

        logger.info(f"Instagram OAuth callback for user {user_id}")

        # Exchange code for short-lived token
        access_token, ig_user_id = await exchange_instagram_code_for_token(code)

        # Convert to long-lived token (60 days)
        long_lived_token = await get_long_lived_token(access_token)

        # Save to token storage
        token_storage.save_instagram_credentials(user_id, long_lived_token, ig_user_id)

        # Save to user service
        user_service.set_platform_credentials(
            user_id=user_id,
            platform="instagram",
            credentials={
                "access_token": long_lived_token,
                "user_id": ig_user_id
            }
        )

        logger.info(f"Instagram successfully connected for user {user_id}")

        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?success=instagram"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram OAuth failed: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?error=instagram&message={str(e)}"
        )


async def exchange_instagram_code_for_token(code: str) -> tuple[str, str]:
    """
    Exchanges authorization code for short-lived access token.
    Uses new Instagram Graph API endpoint.

    Returns:
        tuple: (access_token, ig_user_id)
    """
    url = "https://api.instagram.com/oauth/access_token"

    data = {
        "client_id": settings.INSTAGRAM_CLIENT_ID,
        "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "code": code
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, data=data)
            result = resp.json()

            logger.debug(f"Instagram token exchange response: {result}")

            if "access_token" not in result:
                error_msg = result.get("error_message", result.get("error", str(result)))
                raise ValueError(f"Token exchange failed: {error_msg}")

            return result["access_token"], str(result["user_id"])

    except httpx.RequestError as e:
        logger.error(f"Instagram token exchange request failed: {str(e)}")
        raise ValueError(f"Token Exchange fehlgeschlagen: {str(e)}")


async def get_long_lived_token(short_lived_token: str) -> str:
    """
    Converts short-lived token to long-lived token (valid 60 days).
    """
    url = "https://graph.instagram.com/access_token"

    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
        "access_token": short_lived_token
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            result = resp.json()

            if "access_token" not in result:
                logger.warning(f"Long-lived token exchange failed, using short-lived: {result}")
                return short_lived_token

            logger.info("Successfully exchanged for long-lived token")
            return result["access_token"]

    except Exception as e:
        logger.warning(f"Long-lived token exchange failed: {str(e)}, using short-lived token")
        return short_lived_token


# ==========================================
# Token Management
# ==========================================

@router.post("/refresh")
async def refresh_instagram_token(request: RefreshRequest):
    """
    Refreshes Instagram long-lived access token (before expiry).
    Long-lived tokens are valid 60 days and can be refreshed when > 24h old.
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

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            result = resp.json()

            if "access_token" not in result:
                raise ValueError(f"Token refresh failed: {result}")

        token_storage.save_instagram_credentials(
            request.user_id,
            result["access_token"],
            creds["user_id"]
        )

        logger.info(f"Instagram token refreshed for user {request.user_id}")
        return {"status": "success", "message": "Token erfolgreich erneuert"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram token refresh failed: {str(e)}")
        raise HTTPException(500, str(e))


@router.post("/disconnect")
async def disconnect_instagram(request: DisconnectRequest):
    """
    Disconnects Instagram account for user.
    """
    try:
        token_storage.delete_instagram_credentials(request.user_id)
        user_service.remove_platform_credentials(request.user_id, "instagram")

        logger.info(f"Instagram disconnected for user {request.user_id}")

        return {
            "status": "success",
            "message": "Instagram wurde erfolgreich getrennt"
        }

    except Exception as e:
        logger.error(f"Instagram disconnect failed: {str(e)}")
        raise HTTPException(500, f"Disconnect fehlgeschlagen: {str(e)}")


# ==========================================
# Upload Helper
# ==========================================

async def upload_to_instagram(user_id: str, video_path: str, title: str):
    """
    Helper function for Instagram video upload.

    Returns:
        dict: Upload result
    """
    ig_creds = user_service.get_platform_credentials(user_id, "instagram")

    if not ig_creds:
        logger.info(f"Loading Instagram token from disk for user {user_id}")
        ig_creds = token_storage.load_instagram_credentials(user_id)

        if ig_creds:
            user_service.set_platform_credentials(user_id, "instagram", ig_creds)

    if not ig_creds:
        raise ValueError("Instagram nicht verbunden – bitte zuerst authentifizieren")

    result = instagram_upload_video(
        ig_user_id=ig_creds["user_id"],
        access_token=ig_creds["access_token"],
        video_path=video_path,
        caption=title
    )

    logger.info(f"Instagram upload successful for user {user_id}")
    return result




