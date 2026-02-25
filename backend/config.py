import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # URLs
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", 30))
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL")
    FROM_NAME: str = os.getenv("FROM_NAME", "SocialHub")
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", 24))
    PASSWORD_RESET_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_EXPIRE_HOURS", 1))

    
    # OAuth
    YOUTUBE_ENABLED: bool = os.getenv("YOUTUBE_ENABLED", "true").lower() == "true"
    TIKTOK_CLIENT_KEY: str = os.getenv("TIKTOK_CLIENT_KEY", "")
    TIKTOK_CLIENT_SECRET: str = os.getenv("TIKTOK_CLIENT_SECRET", "")
    INSTAGRAM_CLIENT_ID: str = os.getenv("INSTAGRAM_CLIENT_ID", "")
    INSTAGRAM_CLIENT_SECRET: str = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
    
    # Files
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/app/temp")
    TOKEN_DIR: str = os.getenv("TOKEN_DIR", "/app/tokens")
    DATA_DIR: str = os.getenv("DATA_DIR", "/app/data")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 500))
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    AI_MOCK_MODE: bool = os.getenv("AI_MOCK_MODE", "false").lower() == "true"
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY")
    
    # Environment
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()

