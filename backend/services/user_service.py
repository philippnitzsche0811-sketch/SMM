"""
User Service für Verwaltung von User-Credentials
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class UserService:
    """
    Verwaltet User-Daten und Platform-Credentials
    """
    
    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._temp_data: Dict[str, Dict[str, Any]] = {}
        logger.info("UserService initialisiert")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Gibt User-Daten zurück"""
        return self._users.get(user_id)
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle User zurück"""
        return self._users
    
    def set_platform_credentials(
        self, 
        user_id: str, 
        platform: str, 
        credentials: Any
    ):
        """
        Speichert Platform-Credentials für einen User
        
        Args:
            user_id: User-ID
            platform: Platform-Name (youtube, tiktok, instagram)
            credentials: Credentials (kann Service-Objekt oder Dict sein)
        """
        if user_id not in self._users:
            self._users[user_id] = {}
        
        self._users[user_id][platform] = credentials
        logger.info(f"✅ Credentials für {platform} gespeichert (User: {user_id})")
    
    def get_platform_credentials(
        self, 
        user_id: str, 
        platform: str
    ) -> Optional[Any]:
        """
        Gibt Platform-Credentials für einen User zurück
        
        Args:
            user_id: User-ID
            platform: Platform-Name
            
        Returns:
            Credentials oder None wenn nicht vorhanden
        """
        user_data = self._users.get(user_id)
        if not user_data:
            logger.warning(f"User {user_id} nicht gefunden")
            return None
        
        credentials = user_data.get(platform)
        if not credentials:
            logger.warning(f"Keine {platform}-Credentials für User {user_id}")
            return None
        
        return credentials
    
    def remove_platform_credentials(self, user_id: str, platform: str):
        """
        Entfernt Platform-Credentials für einen User
        
        Args:
            user_id: User-ID
            platform: Platform-Name
            
        Raises:
            ValueError: Wenn User oder Platform nicht existiert
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} nicht gefunden")
        
        if platform not in self._users[user_id]:
            raise ValueError(f"Platform {platform} nicht verbunden")
        
        del self._users[user_id][platform]
        logger.info(f"🗑️ {platform}-Credentials entfernt (User: {user_id})")
        
        # User komplett löschen wenn keine Platforms mehr
        if not self._users[user_id]:
            del self._users[user_id]
            logger.info(f"🗑️ User {user_id} komplett entfernt (keine Platforms)")
    
    def set_temp_data(self, user_id: str, key: str, value: Any):
        """
        Speichert temporäre Daten für einen User (z.B. während OAuth)
        
        Args:
            user_id: User-ID
            key: Daten-Key
            value: Daten-Value
        """
        if user_id not in self._temp_data:
            self._temp_data[user_id] = {}
        
        self._temp_data[user_id][key] = value
        logger.debug(f"Temp-Daten gespeichert: {user_id}/{key}")
    
    def get_temp_data(self, user_id: str, key: str) -> Optional[Any]:
        """
        Gibt temporäre Daten für einen User zurück
        
        Args:
            user_id: User-ID
            key: Daten-Key
            
        Returns:
            Daten-Value oder None
        """
        user_temp = self._temp_data.get(user_id)
        if not user_temp:
            return None
        
        return user_temp.get(key)
    
    def remove_temp_data(self, user_id: str, key: str):
        """
        Entfernt temporäre Daten für einen User
        
        Args:
            user_id: User-ID
            key: Daten-Key
        """
        if user_id in self._temp_data and key in self._temp_data[user_id]:
            del self._temp_data[user_id][key]
            logger.debug(f"Temp-Daten entfernt: {user_id}/{key}")
            
            # User aus temp_data entfernen wenn leer
            if not self._temp_data[user_id]:
                del self._temp_data[user_id]
    
    def clear_all_temp_data(self, user_id: str):
        """
        Löscht alle temporären Daten für einen User
        
        Args:
            user_id: User-ID
        """
        if user_id in self._temp_data:
            del self._temp_data[user_id]
            logger.info(f"🗑️ Alle Temp-Daten entfernt (User: {user_id})")