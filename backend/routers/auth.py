from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import bcrypt
import logging
from utils.auth import create_access_token, decode_access_token  # ✅ NUR diese beiden
from models.database import UserModel, get_db
from services.email_service import EmailService
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

email_service = EmailService()


# ==========================================
# Request Models
# ==========================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# ==========================================
# Helper Functions
# ==========================================

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_verification_token() -> str:
    """Generate secure verification token"""
    return secrets.token_urlsafe(32)



@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Ändert das Passwort des aktuellen Users
    """
    try:
        # Get current user from token
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(401, "Invalid token")
        
        # Get user
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(404, "User not found")
        
        # Verify current password
        if not verify_password(request.current_password, user.hashed_password):
            raise HTTPException(401, "Aktuelles Passwort ist falsch")
        
        # Validate new password
        if len(request.new_password) < 8:
            raise HTTPException(400, "Neues Passwort muss mindestens 8 Zeichen lang sein")
        
        # Update password
        user.hashed_password = hash_password(request.new_password)
        user.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"✅ Passwort geändert für User: {user.email}")
        
        return {
            "status": "success",
            "message": "Passwort erfolgreich geändert"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Change password failed: {str(e)}")
        raise HTTPException(500, "Passwort konnte nicht geändert werden")

# ==========================================
# Registration & Verification
# ==========================================

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registriert neuen User und sendet Verification Email
    """
    try:
        # Check if email already exists
        existing_user = db.query(UserModel).filter(UserModel.email == request.email).first()
        if existing_user:
            raise HTTPException(400, "Email bereits registriert")
        
        # Validate password
        if len(request.password) < 8:
            raise HTTPException(400, "Passwort muss mindestens 8 Zeichen lang sein")
        
        # Generate user ID and tokens
        user_id = f"user_{secrets.token_hex(8)}"
        verification_token = generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
        
        # Create user
        new_user = UserModel(
            id=user_id,
            email=request.email,
            hashed_password=hash_password(request.password),
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_expires,
            created_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        
        # Send verification email
        email_sent = email_service.send_verification_email(request.email, verification_token)
        
        if not email_sent:
            logger.warning(f"⚠️  Verification Email konnte nicht gesendet werden an {request.email}")
        
        logger.info(f"✅ User registriert: {request.email}")
        
        return {
            "status": "success",
            "message": "Registrierung erfolgreich. Bitte überprüfe deine Emails.",
            "user_id": user_id,
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registrierung fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"Registrierung fehlgeschlagen: {str(e)}")


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verifiziert Email mit Token
    """
    try:
        # Find user by token
        user = db.query(UserModel).filter(
            UserModel.verification_token == request.token
        ).first()
        
        if not user:
            raise HTTPException(400, "Ungültiger Verification Token")
        
        # Check if already verified
        if user.is_verified:
            raise HTTPException(400, "Email bereits verifiziert")
        
        # Check if token expired
        if user.verification_token_expires < datetime.now():
            raise HTTPException(400, "Verification Token abgelaufen")
        
        # Verify user
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        user.updated_at = datetime.now()
        
        db.commit()
        
        # Send welcome email
        email_service.send_welcome_email(user.email, user.email.split('@')[0])
        
        logger.info(f"✅ Email verifiziert: {user.email}")
        
        return {
            "status": "success",
            "message": "Email erfolgreich verifiziert! Du kannst dich jetzt anmelden.",
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Email Verification fehlgeschlagen: {str(e)}")
        raise HTTPException(500, f"Verification fehlgeschlagen: {str(e)}")


@router.post("/resend-verification")
async def resend_verification(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Sendet Verification Email erneut
    """
    try:
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        
        if not user:
            # Don't reveal if email exists
            return {
                "status": "success",
                "message": "Falls die Email existiert, wurde eine Verification Email gesendet."
            }
        
        if user.is_verified:
            raise HTTPException(400, "Email bereits verifiziert")
        
        # Generate new token
        verification_token = generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
        
        user.verification_token = verification_token
        user.verification_token_expires = verification_expires
        user.updated_at = datetime.now()
        
        db.commit()
        
        # Send email
        email_service.send_verification_email(user.email, verification_token)
        
        logger.info(f"✅ Verification Email erneut gesendet: {user.email}")
        
        return {
            "status": "success",
            "message": "Verification Email wurde erneut gesendet."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resend Verification fehlgeschlagen: {str(e)}")
        raise HTTPException(500, "Fehler beim Senden der Email")


# ==========================================
# Login
# ==========================================

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login mit Email + Password
    """
    try:
        # ✅ Find user (DIESER CODE FEHLTE!)
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        
        if not user:
            raise HTTPException(401, "Ungültige Email oder Passwort")
        
        # ✅ Check password (DIESER CODE FEHLTE!)
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(401, "Ungültige Email oder Passwort")
        
        # ✅ Check if verified (DIESER CODE FEHLTE!)
        if not user.is_verified:
            raise HTTPException(403, "Bitte verifiziere zuerst deine Email-Adresse")
        
        # ✅ CREATE JWT TOKEN (DIESER CODE FEHLTE!)
        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id
            },
            expires_delta=timedelta(days=settings.JWT_EXPIRE_DAYS)
        )
        
        # ✅ Get connected platforms
        connected_platforms = []
        try:
            from models.database import PlatformConnection
            
            platforms = db.query(PlatformConnection).filter(
                PlatformConnection.user_id == user.id,
                PlatformConnection.connected == True
            ).all()
            
            connected_platforms = [
                {
                    "platform": p.platform,
                    "username": p.username if hasattr(p, 'username') else None,
                    "channelId": p.channel_id if hasattr(p, 'channel_id') else None,
                    "connectedAt": p.created_at.isoformat() if p.created_at else None
                }
                for p in platforms
            ]
        except ImportError:
            logger.warning("PlatformConnection Model nicht gefunden")
        
        logger.info(f"✅ User eingeloggt: {user.email}")
        
        # ✅ RETURN TOKEN mit connected_platforms
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username if hasattr(user, 'username') else None,
                "is_verified": user.is_verified,
                "connected_platforms": connected_platforms
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login fehlgeschlagen: {str(e)}")
        raise HTTPException(500, "Login fehlgeschlagen")



# ==========================================
# Password Reset
# ==========================================

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Sendet Password Reset Email
    """
    try:
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        
        if not user:
            # Don't reveal if email exists
            return {
                "status": "success",
                "message": "Falls die Email existiert, wurde ein Reset Link gesendet."
            }
        
        # Generate reset token
        reset_token = generate_verification_token()
        reset_expires = datetime.now() + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)
        
        user.reset_token = reset_token
        user.reset_token_expires = reset_expires
        user.updated_at = datetime.now()
        
        db.commit()
        
        # Send reset email
        email_service.send_password_reset_email(user.email, reset_token)
        
        logger.info(f"✅ Password Reset Email gesendet: {user.email}")
        
        return {
            "status": "success",
            "message": "Falls die Email existiert, wurde ein Reset Link gesendet."
        }
        
    except Exception as e:
        logger.error(f"❌ Forgot Password fehlgeschlagen: {str(e)}")
        raise HTTPException(500, "Fehler beim Senden der Email")


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Setzt neues Passwort mit Reset Token
    """
    try:
        # Find user by token
        user = db.query(UserModel).filter(
            UserModel.reset_token == request.token
        ).first()
        
        if not user:
            raise HTTPException(400, "Ungültiger Reset Token")
        
        # Check if token expired
        if user.reset_token_expires < datetime.now():
            raise HTTPException(400, "Reset Token abgelaufen")
        
        # Validate new password
        if len(request.new_password) < 8:
            raise HTTPException(400, "Passwort muss mindestens 8 Zeichen lang sein")
        
        # Update password
        user.hashed_password = hash_password(request.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"✅ Passwort zurückgesetzt: {user.email}")
        
        return {
            "status": "success",
            "message": "Passwort erfolgreich zurückgesetzt. Du kannst dich jetzt anmelden."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Reset Password fehlgeschlagen: {str(e)}")
        raise HTTPException(500, "Passwort Reset fehlgeschlagen")

@router.get("/me")
async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Gibt aktuellen User zurück (mit verbundenen Plattformen)
    """
    try:
        logger.info(f"📥 /auth/me called with Authorization: {authorization[:50]}...")
        
        # Extract token from "Bearer <token>"
        if not authorization.startswith("Bearer "):
            logger.error("❌ Authorization header does not start with 'Bearer '")
            raise HTTPException(401, "Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        logger.info(f"🔑 Token extracted: {token[:30]}...")
        
        # Decode token
        payload = decode_access_token(token)
        logger.info(f"✅ Token decoded: {payload}")
        
        user_id = payload.get("user_id")
        
        if not user_id:
            logger.error("❌ No user_id in token payload")
            raise HTTPException(401, "Invalid token")
        
        logger.info(f"👤 User ID from token: {user_id}")
        
        # Get user from DB
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            logger.error(f"❌ User not found in DB: {user_id}")
            raise HTTPException(404, "User not found")
        
        logger.info(f"✅ User found: {user.email}")
        
        # Get connected platforms
        connected_platforms = []
        try:
            from models.database import PlatformConnection
            
            platforms = db.query(PlatformConnection).filter(
                PlatformConnection.user_id == user_id,
                PlatformConnection.connected == True
            ).all()
            
            logger.info(f"📊 Found {len(platforms)} connected platforms")
            
            connected_platforms = [
                {
                    "platform": p.platform,
                    "username": p.username if hasattr(p, 'username') else None,
                    "channelId": p.channel_id if hasattr(p, 'channel_id') else None,
                    "connectedAt": p.created_at.isoformat() if p.created_at else None
                }
                for p in platforms
            ]
        except ImportError:
            logger.warning("⚠️ PlatformConnection Model nicht gefunden")
        except Exception as e:
            logger.error(f"❌ Error getting platforms: {e}")
        
        logger.info(f"✅ Returning user data with {len(connected_platforms)} platforms")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username if hasattr(user, 'username') else None,
            "is_verified": user.is_verified,
            "connected_platforms": connected_platforms,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at and hasattr(user, 'updated_at') else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get current user failed: {str(e)}", exc_info=True)
        raise HTTPException(401, "Invalid or expired token")
