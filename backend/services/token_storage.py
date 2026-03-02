import json
import logging
import os
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models.database import SessionLocal, PlatformConnection

logger = logging.getLogger(__name__)


class TokenStorage:
    """Token-Speicherung in PostgreSQL (platform_connections Tabelle)"""

    def _get_db(self) -> Session:
        return SessionLocal()

    # ==========================================
    # Generische Hilfsmethoden
    # ==========================================

    def _save_credentials(self, user_id: str, platform: str, data: dict,
                          username: str = None, channel_id: str = None):
        """Speichert oder aktualisiert Credentials in der DB"""
        db = self._get_db()
        try:
            existing = db.query(PlatformConnection).filter(
                PlatformConnection.user_id == user_id,
                PlatformConnection.platform == platform
            ).first()

            if existing:
                existing.access_token = data.get("access_token")
                existing.refresh_token = data.get("refresh_token")
                existing.connected = True
                existing.updated_at = datetime.now()
                if username:
                    existing.username = username
                if channel_id:
                    existing.channel_id = channel_id
                logger.info(f"🔄 {platform} Credentials aktualisiert (User: {user_id})")
            else:
                connection = PlatformConnection(
                    id=f"plat_{secrets.token_hex(8)}",
                    user_id=user_id,
                    platform=platform,
                    connected=True,
                    access_token=data.get("access_token"),
                    refresh_token=data.get("refresh_token"),
                    username=username,
                    channel_id=channel_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(connection)
                logger.info(f"✅ {platform} Credentials gespeichert (User: {user_id})")

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Fehler beim Speichern von {platform} Credentials: {str(e)}")
            raise
        finally:
            db.close()

    def _load_credentials(self, user_id: str, platform: str) -> Optional[dict]:
        """Lädt Credentials aus der DB"""
        db = self._get_db()
        try:
            connection = db.query(PlatformConnection).filter(
                PlatformConnection.user_id == user_id,
                PlatformConnection.platform == platform,
                PlatformConnection.connected == True
            ).first()

            if not connection:
                logger.warning(f"⚠️ {platform} Token nicht gefunden (User: {user_id})")
                return None

            return {
                "access_token": connection.access_token,
                "refresh_token": connection.refresh_token,
                "username": connection.username,
                "channel_id": connection.channel_id,
                "platform": platform,
            }
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden von {platform} Credentials: {str(e)}")
            return None
        finally:
            db.close()

    def _delete_credentials(self, user_id: str, platform: str):
        """Löscht Credentials aus der DB"""
        db = self._get_db()
        try:
            connection = db.query(PlatformConnection).filter(
                PlatformConnection.user_id == user_id,
                PlatformConnection.platform == platform
            ).first()

            if connection:
                db.delete(connection)
                db.commit()
                logger.info(f"🗑️ {platform} Credentials gelöscht (User: {user_id})")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Fehler beim Löschen von {platform} Credentials: {str(e)}")
            raise
        finally:
            db.close()

    # ==========================================
    # TikTok
    # ==========================================

    def save_tiktok_credentials(self, user_id: str, access_token: str,
                                 open_id: str, refresh_token: str = None):
        self._save_credentials(
            user_id=user_id,
            platform="tiktok",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token or "",
            },
            channel_id=open_id
        )

    def load_tiktok_credentials(self, user_id: str) -> Optional[dict]:
        creds = self._load_credentials(user_id, "tiktok")
        if creds:
            creds["open_id"] = creds.get("channel_id", "")
        return creds

    def delete_tiktok_credentials(self, user_id: str):
        self._delete_credentials(user_id, "tiktok")

    # ==========================================
    # Instagram
    # ==========================================

    def save_instagram_credentials(self, user_id: str, access_token: str,
                                    ig_user_id: str, username: str = None):
        self._save_credentials(
            user_id=user_id,
            platform="instagram",
            data={
                "access_token": access_token,
                "refresh_token": None,
            },
            username=username,
            channel_id=ig_user_id
        )

    def load_instagram_credentials(self, user_id: str) -> Optional[dict]:
        creds = self._load_credentials(user_id, "instagram")
        if creds:
            creds["user_id"] = creds.get("channel_id", "")
        return creds

    def delete_instagram_credentials(self, user_id: str):
        self._delete_credentials(user_id, "instagram")

    # ==========================================
    # YouTube
    # ==========================================

    def save_youtube_credentials(self, user_id: str, credentials,
                                  channel_title: str = None, channel_id: str = None):
        """credentials = Google OAuth Credentials Objekt"""
        self._save_credentials(
            user_id=user_id,
            platform="youtube",
            data={
                "access_token": json.dumps({
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "scopes": list(credentials.scopes) if credentials.scopes else [],
                }),
                "refresh_token": credentials.refresh_token,
            },
            username=channel_title,
            channel_id=channel_id
        )

    def load_youtube_credentials(self, user_id: str) -> Optional[dict]:
        creds = self._load_credentials(user_id, "youtube")
        if not creds:
            return None
        try:
            # access_token enthält den kompletten JSON-String
            token_data = json.loads(creds["access_token"])
            return token_data
        except (json.JSONDecodeError, TypeError):
            return creds

    def delete_youtube_credentials(self, user_id: str):
        self._delete_credentials(user_id, "youtube")

    # ==========================================
    # Rückwärtskompatibilität (alte Datei-Tokens migrieren)
    # ==========================================

    def migrate_file_tokens(self, user_id: str):
        """Migriert alte Datei-Tokens in die DB (einmalig)"""
        token_dir = Path(os.getenv("TOKEN_DIR", "./tokens"))

        for platform in ["tiktok", "instagram", "youtube"]:
            token_file = token_dir / f"{platform}_{user_id}.json"
            if token_file.exists():
                try:
                    with open(token_file, "r") as f:
                        data = json.load(f)

                    existing = self._load_credentials(user_id, platform)
                    if not existing:
                        self._save_credentials(
                            user_id=user_id,
                            platform=platform,
                            data=data,
                            username=data.get("username"),
                            channel_id=data.get("open_id") or data.get("user_id") or data.get("channel_id")
                        )
                        logger.info(f"✅ {platform} Token migriert für User {user_id}")

                    token_file.unlink()
                except Exception as e:
                    logger.warning(f"⚠️ Migration fehlgeschlagen ({platform}): {str(e)}")
