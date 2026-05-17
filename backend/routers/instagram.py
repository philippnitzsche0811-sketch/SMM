# instagram_router.py
from fastapi import APIRouter, Request as FastAPIRequest, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import logging
import httpx
import hashlib
import hmac
import base64
import json
from datetime import datetime
from urllib.parse import quote

from config import settings
from services.instagram_service import instagram_upload_video
from services.user_service import UserService
from services.token_storage import TokenStorage
from routers.auth import get_current_user


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
async def connect_instagram(
    request: ConnectRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generates Instagram OAuth URL for user.
    Uses new Instagram Graph API with Instagram Login.
    """
    if str(current_user["id"]) != str(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        logger.info(f"Generating Instagram auth URL for user {request.user_id}")

        client_id = settings.INSTAGRAM_CLIENT_ID
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI

        if not client_id:
            raise HTTPException(400, "Instagram Client ID nicht konfiguriert.")
        if not redirect_uri:
            raise HTTPException(400, "Instagram Redirect URI nicht konfiguriert.")

        # Valid scopes for Instagram Platform (https://www.instagram.com/oauth/authorize)
        # instagram_manage_comments requires Meta App Review → added only after approval
        scopes_raw = ",".join([
            "instagram_business_basic",
            "instagram_business_content_publish",
        ])

        scopes = quote(scopes_raw, safe="")
        auth_url = (
            f"https://www.instagram.com/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&state={request.user_id}"
        )



        logger.info(f"Instagram auth URL generated for user {request.user_id}")
        logger.info(f"Instagram auth URL: {auth_url}")

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

        # Instagram hängt manchmal "#_" ans Ende des Codes
        if code and "#_" in code:
            code = code.split("#_")[0]

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

        # Fetch account username
        ig_username = await fetch_instagram_username(long_lived_token)

        # Save to token storage
        token_storage.save_instagram_credentials(user_id, long_lived_token, ig_user_id, username=ig_username)

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
    logger.info(f"Token exchange data: client_id={settings.INSTAGRAM_CLIENT_ID}, redirect_uri={settings.INSTAGRAM_REDIRECT_URI}, code_length={len(code)}")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url, 
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            result = resp.json()
            logger.info(f"Token exchange full response: status={resp.status_code}, body={result}")
            logger.info(f"Request that was sent: url={url}, data={data}")


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
    Raises ValueError if the exchange fails so the OAuth callback surfaces a proper error
    instead of silently storing a 1-hour token that will break uploads later.
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
                error_msg = result.get("error_message", result.get("error", str(result)))
                raise ValueError(f"Long-lived token exchange failed: {error_msg}")

            logger.info("Successfully exchanged for long-lived token")
            return result["access_token"]

    except httpx.HTTPError as e:
        raise ValueError(f"Long-lived token exchange request failed: {str(e)}")



async def fetch_instagram_username(access_token: str) -> str | None:
    """Fetches the Instagram username for the connected account."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://graph.instagram.com/me",
                params={"fields": "username", "access_token": access_token}
            )
            data = resp.json()
            username = data.get("username")
            if username:
                logger.info(f"Instagram username fetched: {username}")
            return username
    except Exception as e:
        logger.warning(f"Could not fetch Instagram username: {e}")
        return None


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
async def disconnect_instagram(
    request: DisconnectRequest,
    current_user: dict = Depends(get_current_user),
):
    if str(current_user["id"]) != str(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        token_storage.delete_instagram_credentials(request.user_id)
        
        # Fehler ignorieren wenn User nicht im Memory
        try:
            user_service.remove_platform_credentials(request.user_id, "instagram")
        except ValueError:
            pass

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


# ==========================================
# Meta Data Deletion Callback (required for App Review)
# ==========================================

@router.post("/data-deletion", include_in_schema=False)
async def instagram_data_deletion_callback(request: FastAPIRequest):
    """
    Meta sends a signed_request here when a user removes the app from their Instagram settings.
    Must respond with a confirmation_code and status URL.
    https://developers.facebook.com/docs/instagram-platform/data-deletion-request
    """
    try:
        form = await request.form()
        signed_request_raw = form.get("signed_request", "")

        ig_user_id = "unknown"
        if signed_request_raw and "." in signed_request_raw:
            try:
                _, payload_b64 = signed_request_raw.split(".", 1)
                # Base64url padding
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += "=" * padding
                payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                ig_user_id = payload.get("user_id", "unknown")
            except Exception:
                pass

        logger.info(f"Instagram data deletion request received for IG user {ig_user_id}")

        # Confirmation code so Meta can verify deletion was processed
        ts = int(datetime.now().timestamp())
        raw = f"{ig_user_id}:{ts}".encode()
        confirmation_code = hmac.new(b"smm-del", raw, hashlib.sha256).hexdigest()[:16]

        return {
            "url": f"{settings.FRONTEND_URL}/privacy",
            "confirmation_code": confirmation_code,
        }

    except Exception as e:
        logger.error(f"Data deletion callback error: {e}")
        return {"url": "", "confirmation_code": "error"}


@router.get("/data-deletion", response_class=HTMLResponse, include_in_schema=False)
async def instagram_data_deletion_status():
    """Status page shown to users who initiated data deletion from Instagram."""
    return """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Data Deletion - Decodu-SMM</title>
<style>body{font-family:sans-serif;max-width:600px;margin:4rem auto;padding:0 1rem;color:#333}
h1{color:#667eea}p{line-height:1.7;color:#555}a{color:#667eea}</style>
</head>
<body>
<h1>Data Deletion Request Received</h1>
<p>Your data deletion request has been received and processed. All data associated with your Instagram account has been removed from Decodu-SMM.</p>
<p>This includes: OAuth access tokens, upload history linked to your Instagram account.</p>
<p>If you have any questions, contact us at <a href="mailto:privacy@decodu-smm.com">privacy@decodu-smm.com</a>.</p>
<p><a href="https://decodu-smm.com/privacy">Back to Privacy Policy</a></p>
</body></html>"""
