"""
YouTube Upload Service
"""
import logging
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from config import settings

logger = logging.getLogger(__name__)

# OAuth Scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_youtube_auth_url(client_secrets_path: str, user_id: str):
    """
    Generiert YouTube OAuth URL
    """
    # âœ… Ã„NDERE HIER - Redirect zu /youtube/oauth_callback
    redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/youtube/oauth_callback"

    
    logger.info(f"ðŸ”— Redirect URI: {redirect_uri}")
    
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
        redirect_uri=redirect_uri,
        state=user_id  # State ist bereits "user_517b3b295a111f54"
    )
    
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    logger.info(f"ðŸ”— YouTube Auth-URL generiert fÃ¼r User {user_id}")
    
    return auth_url



def authenticate_youtube_with_code(client_secrets_path: str, code: str, user_id: str):
    """
    Tauscht OAuth Code gegen Credentials
    """
    try:
        # âœ… WICHTIG: Gleiche Redirect URI wie bei get_youtube_auth_url!
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/youtube/oauth_callback"
        
        logger.info(f"ðŸ” Authentifiziere YouTube fÃ¼r User {user_id}")
        logger.info(f"ðŸ”— Redirect URI: {redirect_uri}")
        
        flow = Flow.from_client_secrets_file(
            client_secrets_path,
            scopes=["https://www.googleapis.com/auth/youtube.upload"],
            redirect_uri=redirect_uri  # âœ… Muss identisch sein!
        )
        
        # Token holen
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        logger.info(f"âœ… YouTube-Credentials erfolgreich erhalten fÃ¼r User {user_id}")
        
        return credentials
        
    except Exception as e:
        logger.error(f"âŒ YouTube-Authentifizierung fehlgeschlagen: {str(e)}")
        raise



def build_youtube_service(credentials: Credentials):
    """
    Erstellt YouTube Service aus Credentials
    
    Args:
        credentials: Google OAuth2 Credentials
        
    Returns:
        YouTube API Service
    """
    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        logger.info("âœ… YouTube Service erstellt")
        return youtube
    except Exception as e:
        logger.error(f"âŒ Fehler beim Erstellen des YouTube Service: {str(e)}")
        raise


def upload_video_to_youtube(
    credentials: Credentials,
    video_path: str,
    title: str,
    description: str = "",
    tags: list = None,
    privacy_status: str = "private"
) -> dict:
    """
    LÃ¤dt ein Video auf YouTube hoch
    
    Args:
        credentials: Google OAuth2 Credentials (nicht YouTube Service!)
        video_path: Pfad zur Video-Datei
        title: Video-Titel
        description: Video-Beschreibung
        tags: Liste von Tags
        privacy_status: Privacy Status (public/private/unlisted)
        
    Returns:
        Upload-Ergebnis mit Video-ID
    """
    try:
        logger.info(f"ðŸ“¤ YouTube-Upload startet: {title}")
        
        # YouTube Service aus Credentials erstellen
        youtube = build_youtube_service(credentials)
        
        # Request Body erstellen
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Media Upload vorbereiten
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )
        
        # Upload durchfÃ¼hren
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        video_id = response.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        logger.info(f"âœ… YouTube-Upload erfolgreich: {video_url}")
        
        return {
            'video_id': video_id,
            'url': video_url,
            'title': title,
            'privacy_status': privacy_status
        }
        
    except Exception as e:
        logger.error(f"âŒ YouTube-Upload fehlgeschlagen: {str(e)}")
        raise
