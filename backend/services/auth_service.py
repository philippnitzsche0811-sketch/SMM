"""
Authentication Service
Verwaltet User-Registrierung, Login und Token-Generierung
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service für Authentifizierung und User-Verwaltung"""

    def __init__(self):
        # JWT Settings
        self.SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Aus .env laden
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        # Password Hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # User Storage
        self.users_file = "data/users.json"
        self._ensure_data_directory()
        self._users = self._load_users()

    def _ensure_data_directory(self):
        """Erstellt data/ Verzeichnis falls nicht vorhanden"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as f:
                json.dump({}, f)

    def _load_users(self) -> Dict[str, Any]:
        """Lädt Users aus JSON-Datei"""
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Users: {e}")
            return {}

    def _save_users(self):
        """Speichert Users in JSON-Datei"""
        try:
            with open(self.users_file, "w") as f:
                json.dump(self._users, f, indent=2)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Users: {e}")

    def _hash_password(self, password: str) -> str:
        """Hasht ein Passwort mit bcrypt"""
        # Kürze Passwort auf 72 bytes (bcrypt Limit)
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifiziert ein Passwort gegen den Hash"""
        try:
            # Kürze Passwort auf 72 bytes (bcrypt Limit)
            if len(plain_password.encode('utf-8')) > 72:
                plain_password = plain_password[:72]
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Fehler bei Passwort-Verifikation: {e}")
            return False

    def _generate_user_id(self) -> str:
        """Generiert eine eindeutige User-ID"""
        import uuid
        return f"user_{uuid.uuid4().hex[:12]}"

    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Registriert einen neuen User

        Args:
            email: User Email
            password: Klartext-Passwort

        Returns:
            User-Daten (ohne Passwort)

        Raises:
            ValueError: Wenn Email bereits existiert oder Passwort ungültig
        """
        # Validierung
        if not email or "@" not in email:
            raise ValueError("Ungültige Email-Adresse")

        if not password or len(password) < 6:
            raise ValueError("Passwort muss mindestens 6 Zeichen lang sein")

        if len(password) > 72:
            logger.warning(f"Passwort für {email} wurde auf 72 Zeichen gekürzt")
            password = password[:72]

        # Prüfe ob Email bereits existiert
        email_lower = email.lower()
        for user in self._users.values():
            if user["email"].lower() == email_lower:
                raise ValueError("Email bereits registriert")

        # Erstelle neuen User
        user_id = self._generate_user_id()

        try:
            hashed_password = self._hash_password(password)
        except Exception as e:
            logger.error(f"Hashing-Fehler: {e}")
            raise ValueError("Passwort konnte nicht verschlüsselt werden")

        user_data = {
            "user_id": user_id,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "connected_platforms": []
        }

        self._users[user_id] = user_data
        self._save_users()

        logger.info(f"✅ User registriert: {email} (ID: {user_id})")

        # Gib User ohne Passwort zurück
        return {
            "user_id": user_id,
            "email": email,
            "created_at": user_data["created_at"],
            "connected_platforms": []
        }

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authentifiziert einen User

        Args:
            email: User Email
            password: Klartext-Passwort

        Returns:
            User-Daten (ohne Passwort) wenn erfolgreich, sonst None
        """
        # Kürze Passwort auf 72 bytes (bcrypt Limit)
        if len(password) > 72:
            password = password[:72]

        # Suche User nach Email
        email_lower = email.lower()
        user = None
        for u in self._users.values():
            if u["email"].lower() == email_lower:
                user = u
                break

        if not user:
            logger.warning(f"❌ User nicht gefunden: {email}")
            return None

        # Verifiziere Passwort
        if not self._verify_password(password, user["hashed_password"]):
            logger.warning(f"❌ Falsches Passwort: {email}")
            return None

        logger.info(f"✅ Login erfolgreich: {email}")

        # Gib User ohne Passwort zurück
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "created_at": user["created_at"],
            "connected_platforms": user["connected_platforms"]
        }

    def create_access_token(self, user_id: str, email: str) -> str:
        """
        Erstellt einen JWT Access Token

        Args:
            user_id: User ID
            email: User Email

        Returns:
            JWT Token als String
        """
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire
        }

        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifiziert einen JWT Token

        Args:
            token: JWT Token

        Returns:
            Payload (user_id, email) wenn gültig, sonst None
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None or email is None:
                return None

            return {"user_id": user_id, "email": email}

        except JWTError as e:
            logger.warning(f"Token-Verifikation fehlgeschlagen: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Holt User-Daten anhand der ID

        Args:
            user_id: User ID

        Returns:
            User-Daten (ohne Passwort) wenn gefunden, sonst None
        """
        user = self._users.get(user_id)
        if not user:
            return None

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "created_at": user["created_at"],
            "connected_platforms": user["connected_platforms"]
        }

    def add_connected_platform(self, user_id: str, platform_data: Dict[str, Any]) -> bool:
        """
        Fügt eine verbundene Plattform zum User hinzu

        Args:
            user_id: User ID
            platform_data: Plattform-Daten (platform, account_id, access_token, etc.)

        Returns:
            True wenn erfolgreich, False wenn User nicht gefunden
        """
        user = self._users.get(user_id)
        if not user:
            return False

        # Prüfe ob Plattform bereits verbunden
        for i, platform in enumerate(user["connected_platforms"]):
            if platform["platform"] == platform_data["platform"]:
                # Update existing
                user["connected_platforms"][i] = platform_data
                self._save_users()
                logger.info(f"✅ Plattform aktualisiert: {platform_data['platform']} für {user['email']}")
                return True

        # Füge neue Plattform hinzu
        user["connected_platforms"].append(platform_data)
        self._save_users()
        logger.info(f"✅ Plattform verbunden: {platform_data['platform']} für {user['email']}")
        return True
    def get_all_users_count(self) -> int:
        """Gibt die Anzahl registrierter User zurück"""
        return len(self._users)


# Singleton Instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Gibt die Singleton-Instanz des AuthService zurück"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service



