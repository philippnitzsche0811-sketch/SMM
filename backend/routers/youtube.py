from fastapi import APIRouter, UploadFile, File, Form, Request as FastAPIRequest, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging
import json

from services.youtube_service import get_youtube_auth_url, authenticate_youtube_with_code, upload_video_to_youtube
from config import settings
from services.user_service import UserService
from services.file_service import FileService
from services.token_storage import TokenStorage
from models.database import get_db
from google.oauth2.credentials import Credentials
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["YouTube"])

user_service = UserService()
file_service = FileService()
token_storage = TokenStorage()


@router.post("/connect")
async def connect_youtube(
    user_id: str = Form(...),
    client_secrets_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Generates YouTube OAuth URL for user."""
    if str(current_user["id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        logger.info(f"YouTube Connect Request for user: {user_id}")
        logger.info(f"File: {client_secrets_file.filename}")
        logger.info(f"Content-Type: {client_secrets_file.content_type}")

        if not client_secrets_file.filename.endswith('.json'):
            raise HTTPException(400, "Client Secrets must be a JSON file (.json)")

        temp_path = await file_service.save_temp_file(
            client_secrets_file,
            f"{user_id}_client_secret.json"
        )

        logger.info(f"Temp file saved: {temp_path}")

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                client_secrets = json.load(f)

            if 'web' not in client_secrets and 'installed' not in client_secrets:
                raise ValueError("Invalid client_secrets.json structure")

        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON file")
        except ValueError as e:
            raise HTTPException(400, str(e))

        token_storage._save_credentials(
            user_id=user_id,
            platform="youtube_temp",
            data={
                "access_token": temp_path,
                "refresh_token": None,
            }
        )

        auth_url = get_youtube_auth_url(temp_path, user_id)

        logger.info(f"YouTube Auth-URL generated for user {user_id}")

        return {
            "status": "success",
            "message": "Please authenticate in browser",
            "auth_url": auth_url,
            "user_id": user_id,
            "platform": "youtube"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube Auth-URL generation failed: {str(e)}")
        raise HTTPException(500, f"YouTube auth failed: {str(e)}")


@router.get("/oauth_callback")
@router.get("/oauth/callback")
async def youtube_oauth_callback(request: FastAPIRequest, db: Session = Depends(get_db)):
    """Callback for YouTube OAuth flow."""
    logger.info("=" * 50)
    logger.info("YOUTUBE OAUTH CALLBACK STARTED")
    logger.info("=" * 50)

    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        logger.info(f"Query params - code: {bool(code)}, state: {state}, error: {error}")

        if error:
            logger.error(f"YouTube OAuth error: {error}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message={error}"
            )

        if not code or not state:
            logger.error("Missing parameters!")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message=missing_parameters"
            )

        user_id = state
        logger.info(f"User ID: {user_id}")

        temp_creds = token_storage._load_credentials(user_id, "youtube_temp")
        client_secrets_path = temp_creds.get("access_token") if temp_creds else None
        logger.info(f"Client secrets path: {client_secrets_path}")

        if not client_secrets_path:
            logger.error("Client secrets not found!")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message=secrets_not_found"
            )

        logger.info("Starting authentication...")

        credentials = authenticate_youtube_with_code(client_secrets_path, code, user_id)

        logger.info("Credentials obtained!")

        token_storage.save_youtube_credentials(user_id, credentials)
        user_service.set_platform_credentials(
            user_id=user_id,
            platform="youtube",
            credentials=credentials
        )

        logger.info("Credentials saved to file")

        from models.database import PlatformConnection
        import secrets as secret_gen
        from datetime import datetime

        logger.info("Saving to database...")

        existing_platform = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == "youtube"
        ).first()

        if existing_platform:
            logger.info(f"Updating existing YouTube connection")
            existing_platform.connected = True
            existing_platform.access_token = credentials.token
            existing_platform.refresh_token = credentials.refresh_token
            existing_platform.token_expiry = credentials.expiry
            existing_platform.updated_at = datetime.now()
        else:
            logger.info(f"Creating new YouTube connection")
            new_platform = PlatformConnection(
                id=f"plat_{secret_gen.token_hex(8)}",
                user_id=user_id,
                platform="youtube",
                connected=True,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(new_platform)

        db.commit()
        logger.info("Database commit successful!")

        file_service.delete_file(client_secrets_path)
        token_storage._delete_credentials(user_id, "youtube_temp")

        logger.info(f"Cleanup completed")
        logger.info(f"YouTube successfully connected for user {user_id}")
        logger.info("=" * 50)
        logger.info("REDIRECTING TO FRONTEND")
        logger.info("=" * 50)

        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?success=youtube",
            status_code=302
        )

    except Exception as e:
        logger.error(f"YouTube OAuth failed: {str(e)}", exc_info=True)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message={str(e)}",
            status_code=302
        )


def upload_to_youtube(user_id: str, video_path: str, title: str,
                      description: str, tags_list: list, privacy_status: str):
    """Helper for YouTube upload."""
    logger.info(f"Looking for YouTube credentials for user: {user_id}")

    youtube_creds = user_service.get_platform_credentials(user_id, "youtube")
    logger.info(f"Memory: {'found' if youtube_creds else 'not found'}")

    if not youtube_creds:
        logger.info(f"Loading YouTube token from disk for user {user_id}")
        youtube_creds = token_storage.load_youtube_credentials(user_id)
        logger.info(f"Disk: {'found' if youtube_creds else 'not found'}")

        if youtube_creds:
            user_service.set_platform_credentials(user_id, "youtube", youtube_creds)
            logger.info("Credentials cached in memory")

    if not youtube_creds:
        logger.error(f"No YouTube credentials found for user {user_id}!")
        logger.error(f"Token file: {token_storage._get_token_path(user_id, 'youtube')}")
        raise ValueError("User not authenticated")

    if isinstance(youtube_creds, dict):
        logger.info("Converting dict to Credentials object")
        credentials = Credentials(
            token=youtube_creds.get("token"),
            refresh_token=youtube_creds.get("refresh_token"),
            token_uri=youtube_creds.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=youtube_creds.get("client_id"),
            client_secret=youtube_creds.get("client_secret"),
            scopes=youtube_creds.get("scopes", ["https://www.googleapis.com/auth/youtube.upload"])
        )
    else:
        credentials = youtube_creds

    logger.info(f"Starting YouTube upload, credentials type: {type(credentials)}")

    result = upload_video_to_youtube(
        credentials=credentials,
        video_path=video_path,
        title=title,
        description=description,
        tags=tags_list,
        privacy_status=privacy_status
    )

    logger.info(f"YouTube upload successful for user {user_id}")
    return result
