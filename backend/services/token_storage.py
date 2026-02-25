import json
import logging
import os
from pathlib import Path
from datetime import datetime  # âœ… Hier hinzufÃ¼gen
from config import settings

logger = logging.getLogger(__name__)


class TokenStorage:
    """Service fÃ¼r Token-Speicherung auf Disk"""
    
    def __init__(self):
        self.token_dir = Path(os.getenv("TOKEN_DIR", "./tokens"))
        self.token_dir.mkdir(exist_ok=True, parents=True)
    
    # ==========================================
    # TikTok
    # ==========================================
    
    def save_tiktok_credentials(self, user_id: str, access_token: str, open_id: str, refresh_token: str = None):
        """
        Speichert TikTok Credentials
        
        Args:
            user_id: User ID
            access_token: TikTok Access Token
            open_id: TikTok Open ID
            refresh_token: TikTok Refresh Token (optional)
        """
        token_file = self.token_dir / f"tiktok_{user_id}.json"
        
        credentials = {
            "access_token": access_token,
            "open_id": open_id,
            "refresh_token": refresh_token or "",
            "platform": "tiktok",
            "created_at": datetime.now().isoformat()
        }
        
        with open(token_file, "w") as f:
            json.dump(credentials, f, indent=2)
        
        logger.info(f"ðŸ’¾ TikTok Token gespeichert fÃ¼r User {user_id}")
    
    def load_tiktok_credentials(self, user_id: str):
        """LÃ¤dt TikTok Credentials"""
        token_file = self.token_dir / f"tiktok_{user_id}.json"
        
        if not token_file.exists():
            logger.warning(f"âš ï¸  TikTok Token nicht gefunden fÃ¼r User {user_id}")
            return None
        
        try:
            with open(token_file, "r") as f:
                credentials = json.load(f)
            
            logger.info(f"âœ… TikTok Token geladen fÃ¼r User {user_id}")
            return credentials
        except Exception as e:
            logger.error(f"âŒ Fehler beim Laden von TikTok Token: {str(e)}")
            return None
    
    def delete_tiktok_credentials(self, user_id: str):
        """LÃ¶scht TikTok Credentials"""
        token_file = self.token_dir / f"tiktok_{user_id}.json"
        if token_file.exists():
            token_file.unlink()
            logger.info(f"ðŸ—‘ï¸  TikTok Token gelÃ¶scht fÃ¼r User {user_id}")
    
    # ==========================================
    # Instagram
    # ==========================================
    
    def save_instagram_credentials(self, user_id: str, access_token: str, ig_user_id: str):
        """
        Speichert Instagram Credentials
        
        Args:
            user_id: User ID
            access_token: Instagram Access Token
            ig_user_id: Instagram User ID
        """
        token_file = self.token_dir / f"instagram_{user_id}.json"
        
        credentials = {
            "access_token": access_token,
            "user_id": ig_user_id,
            "platform": "instagram",
            "created_at": datetime.now().isoformat()
        }
        
        with open(token_file, "w") as f:
            json.dump(credentials, f, indent=2)
        
        logger.info(f"ðŸ’¾ Instagram Token gespeichert fÃ¼r User {user_id}")
    
    def load_instagram_credentials(self, user_id: str):
        """LÃ¤dt Instagram Credentials"""
        token_file = self.token_dir / f"instagram_{user_id}.json"
        
        if not token_file.exists():
            logger.warning(f"âš ï¸  Instagram Token nicht gefunden fÃ¼r User {user_id}")
            return None
        
        try:
            with open(token_file, "r") as f:
                credentials = json.load(f)
            
            logger.info(f"âœ… Instagram Token geladen fÃ¼r User {user_id}")
            return credentials
        except Exception as e:
            logger.error(f"âŒ Fehler beim Laden von Instagram Token: {str(e)}")
            return None
    
    def delete_instagram_credentials(self, user_id: str):
        """LÃ¶scht Instagram Credentials"""
        token_file = self.token_dir / f"instagram_{user_id}.json"
        if token_file.exists():
            token_file.unlink()
            logger.info(f"ðŸ—‘ï¸  Instagram Token gelÃ¶scht fÃ¼r User {user_id}")
    
    # ==========================================
    # YouTube
    # ==========================================
    
    def save_youtube_credentials(self, user_id: str, credentials):
        """
        Speichert YouTube Credentials
        
        Args:
            user_id: User ID
            credentials: YouTube Credentials Objekt (aus google.oauth2)
        """
        token_file = self.token_dir / f"youtube_{user_id}.json"
        
        # Convert credentials to dict
        creds_dict = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "platform": "youtube",
            "created_at": datetime.now().isoformat()
        }
        
        with open(token_file, "w") as f:
            json.dump(creds_dict, f, indent=2)
        
        logger.info(f"ðŸ’¾ YouTube Token gespeichert fÃ¼r User {user_id}")
    
    def load_youtube_credentials(self, user_id: str):
        """LÃ¤dt YouTube Credentials"""
        token_file = self.token_dir / f"youtube_{user_id}.json"
        
        if not token_file.exists():
            logger.warning(f"âš ï¸  YouTube Token nicht gefunden fÃ¼r User {user_id}")
            return None
        
        try:
            with open(token_file, "r") as f:
                credentials = json.load(f)
            
            logger.info(f"âœ… YouTube Token geladen fÃ¼r User {user_id}")
            return credentials
        except Exception as e:
            logger.error(f"âŒ Fehler beim Laden von YouTube Token: {str(e)}")
            return None
    
    def delete_youtube_credentials(self, user_id: str):
        """LÃ¶scht YouTube Credentials"""
        token_file = self.token_dir / f"youtube_{user_id}.json"
        if token_file.exists():
            token_file.unlink()
            logger.info(f"ðŸ—‘ï¸  YouTube Token gelÃ¶scht fÃ¼r User {user_id}")




