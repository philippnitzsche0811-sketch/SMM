# utils/auth.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
import logging
from config import settings  # ✅ Importiere settings

logger = logging.getLogger(__name__)

SECRET_KEY = settings.JWT_SECRET  # ✅ JWT_SECRET, nicht JWT_SECRET_KEY!
ALGORITHM = settings.JWT_ALGORITHM  # ✅ Nutze auch den Algorithm aus config

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Erstellt JWT Access Token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    logger.info(f"🔐 Creating token with data: {to_encode}")
    logger.info(f"🔑 Using SECRET_KEY: {SECRET_KEY[:10]}...")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"✅ Token created: {encoded_jwt[:30]}...")
    
    return encoded_jwt


def decode_access_token(token: str):
    """
    Dekodiert und validiert JWT Token
    """
    try:
        logger.info(f"🔓 Decoding token: {token[:30]}...")
        logger.info(f"🔑 Using SECRET_KEY: {SECRET_KEY[:10]}...")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        logger.info(f"✅ Token decoded successfully: {payload}")
        
        return payload
    except JWTError as e:
        logger.error(f"❌ JWT decode failed: {str(e)}")
        raise HTTPException(401, f"Invalid token: {str(e)}")



