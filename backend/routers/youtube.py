from fastapi import APIRouter, UploadFile, File, Form, Request as FastAPIRequest, HTTPException, Depends  # âœ… FÃ¼ge Depends hinzu
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session  # âœ… NEU: Import Session
import logging
import json

from services.youtube_service import get_youtube_auth_url, authenticate_youtube_with_code, upload_video_to_youtube
from config import settings
from services.user_service import UserService
from services.file_service import FileService
from services.token_storage import TokenStorage
from models.database import get_db  # âœ… NEU: Import get_db
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["YouTube"])

user_service = UserService()
file_service = FileService()
token_storage = TokenStorage()


@router.post("/connect")
async def connect_youtube(
    user_id: str = Form(...),
    client_secrets_file: UploadFile = File(...)
):
    """
    Generiert YouTube OAuth URL fÃ¼r User
    """
    try:
        logger.info(f"ðŸ“¥ YouTube Connect Request fÃ¼r User: {user_id}")
        logger.info(f"ðŸ“„ Dateiname: {client_secrets_file.filename}")
        logger.info(f"ðŸ“¦ Content-Type: {client_secrets_file.content_type}")
        
        # Validate file extension
        if not client_secrets_file.filename.endswith('.json'):
            raise HTTPException(400, "Client Secrets muss eine JSON-Datei sein (.json)")
        
        # Save temp file
        temp_path = await file_service.save_temp_file(
            client_secrets_file, 
            f"{user_id}_client_secret.json"
        )
        
        logger.info(f"ðŸ’¾ Temp-Datei gespeichert: {temp_path}")
        
        # Validate JSON content
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                client_secrets = json.load(f)
            
            # Check if valid Google OAuth structure
            if 'web' not in client_secrets and 'installed' not in client_secrets:
                raise ValueError("UngÃ¼ltige client_secrets.json Struktur")
                
        except json.JSONDecodeError:
            raise HTTPException(400, "UngÃ¼ltige JSON-Datei - Bitte prÃ¼fe das Format")
        except ValueError as e:
            raise HTTPException(400, str(e))
        
        # Store temp path for callback
        user_service.set_temp_data(user_id, "youtube_client_secrets", temp_path)
        
        # Generate OAuth URL
        auth_url = get_youtube_auth_url(temp_path, user_id)
        
        logger.info(f"âœ… YouTube Auth-URL generiert fÃ¼r User {user_id}")
        
        return {
            "status": "success",
            "message": "Bitte im Browser authentifizieren",
            "auth_url": auth_url,
            "user_id": user_id,
            "platform": "youtube"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"âŒ YouTube Auth-URL Generierung fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"YouTube-Auth fehlgeschlagen: {str(e)}")


@router.get("/oauth_callback")
@router.get("/oauth/callback")
async def youtube_oauth_callback(request: FastAPIRequest, db: Session = Depends(get_db)):
    """
    Callback fÃ¼r YouTube OAuth Flow
    """
    logger.info("=" * 50)
    logger.info("ðŸŽ¯ YOUTUBE OAUTH CALLBACK STARTED")
    logger.info("=" * 50)
    
    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")
        
        logger.info(f"ðŸ“¥ Query params - code: {bool(code)}, state: {state}, error: {error}")
        
        if error:
            logger.error(f"YouTube OAuth Fehler: {error}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message={error}"
            )
        
        if not code or not state:
            logger.error(f"âŒ Missing parameters!")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message=missing_parameters"
            )
        
        # âœ… State IST bereits die vollstÃ¤ndige User ID!
        user_id = state  # State ist "user_517b3b295a111f54"
        logger.info(f"ðŸ‘¤ User ID: {user_id}")

        
        # Load client secrets
        client_secrets_path = user_service.get_temp_data(user_id, "youtube_client_secrets")
        logger.info(f"ðŸ“„ Client secrets path: {client_secrets_path}")
        
        if not client_secrets_path:
            logger.error("âŒ Client secrets not found!")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message=secrets_not_found"
            )
        
        logger.info("ðŸ” Starting authentication...")
        
        # Authenticate and get credentials
        credentials = authenticate_youtube_with_code(client_secrets_path, code, user_id)
        
        logger.info("âœ… Credentials obtained!")
        
        # Save credentials to file
        token_storage.save_youtube_credentials(user_id, credentials)
        user_service.set_platform_credentials(
            user_id=user_id,
            platform="youtube",
            credentials=credentials
        )
        
        logger.info("ðŸ’¾ Credentials saved to file")
        
        # âœ… Speichere in der Datenbank!
        from models.database import PlatformConnection
        import secrets as secret_gen
        from datetime import datetime
        
        logger.info("ðŸ’¾ Saving to database...")
        
        # Check if platform connection already exists
        existing_platform = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.platform == "youtube"
        ).first()
        
        if existing_platform:
            logger.info(f"ðŸ“ Updating existing YouTube connection")
            existing_platform.connected = True
            existing_platform.access_token = credentials.token
            existing_platform.refresh_token = credentials.refresh_token
            existing_platform.token_expiry = credentials.expiry
            existing_platform.updated_at = datetime.now()
        else:
            logger.info(f"âœ¨ Creating new YouTube connection")
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
        logger.info(f"âœ… Database commit successful!")
        
        # Cleanup
        file_service.delete_file(client_secrets_path)
        user_service.remove_temp_data(user_id, "youtube_client_secrets")
        
        logger.info(f"ðŸ§¹ Cleanup completed")
        logger.info(f"âœ… YouTube erfolgreich verbunden fÃ¼r User {user_id}")
        logger.info("=" * 50)
        logger.info("ðŸŽ‰ REDIRECTING TO FRONTEND")
        logger.info("=" * 50)
        
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?success=youtube",
            status_code=302  # âœ… Explizit 302 statt 307
        )
        
    except Exception as e:
        logger.error(f"âŒ YouTube OAuth fehlgeschlagen: {str(e)}", exc_info=True)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/platforms?error=youtube&message={str(e)}",
            status_code=302
        )





def upload_to_youtube(user_id: str, video_path: str, title: str, 
                     description: str, tags_list: list, privacy_status: str):
    """
    Hilfsfunktion für YouTube Upload
    
    Returns:
        dict: Upload-Ergebnis
    """
    logger.info(f"🔍 Suche YouTube Credentials für User: {user_id}")
    
    # Erst im Memory suchen
    youtube_creds = user_service.get_platform_credentials(user_id, "youtube")
    logger.info(f"Memory: {'✅ gefunden' if youtube_creds else '❌ nicht gefunden'}")
    
    # Falls nicht im Memory, von Disk laden
    if not youtube_creds:
        logger.info(f"💾 Lade YouTube-Token von Disk für User {user_id}")
        youtube_creds = token_storage.load_youtube_credentials(user_id)
        logger.info(f"Disk: {'✅ gefunden' if youtube_creds else '❌ nicht gefunden'}")
        
        if youtube_creds:
            user_service.set_platform_credentials(user_id, "youtube", youtube_creds)
            logger.info("✅ Credentials in Memory gecacht")
    
    if not youtube_creds:
        logger.error(f"❌ FEHLER: Keine YouTube Credentials für User {user_id} gefunden!")
        logger.error(f"Token-Datei: {token_storage._get_token_path(user_id, 'youtube')}")
        raise ValueError("User nicht authentifiziert")
    
    # ✅ Konvertiere dict zu Credentials Objekt (Import ist jetzt oben)
    if isinstance(youtube_creds, dict):
        logger.info("🔄 Konvertiere dict zu Credentials Objekt")
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
    
    logger.info(f"🚀 Starte YouTube Upload mit Credentials-Typ: {type(credentials)}")
    
    result = upload_video_to_youtube(
        credentials=credentials,
        video_path=video_path,
        title=title,
        description=description,
        tags=tags_list,
        privacy_status=privacy_status
    )
    
    logger.info(f"✅ YouTube Upload erfolgreich für User {user_id}")
    return result

