import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import settings
from models.database import init_db,SessionLocal, UserModel
from routers import youtube, tiktok, instagram, upload, user, static_pages, auth
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta



# Logging Setup
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
# FastAPI App
app = FastAPI(
    title="Social Media Upload Manager",
    version="1.0.0",
    description="Multi-Platform Video Upload Manager",
    redirect_slashes=False
)

os.makedirs(settings.TEMP_DIR, exist_ok=True)
app.mount("/api/videos/temp", StaticFiles(directory=settings.TEMP_DIR), name="temp_videos")

# CORS Middleware - dynamisch aus ENV
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",  # Development fallback
    "http://localhost:3000",  # Production port
]

# Nur in Development: Wildcard erlauben
if settings.DEBUG:
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Starting application in {settings.ENVIRONMENT} mode...")
    try:
        init_db()
        logger.info("✅ Database tables initialized")
        scheduler.start()
        logger.info("✅ Scheduler gestartet")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(youtube.router, prefix="/api/youtube")
app.include_router(tiktok.router, prefix="/api/tiktok")
app.include_router(instagram.router, prefix="/api/instagram")
app.include_router(upload.router, prefix="/api/upload")
app.include_router(user.router, prefix="/api/user")
app.include_router(static_pages.router)

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Social Media Upload Manager",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

# Root
@app.get("/")
async def root():
    return {
        "message": "Social Media Upload Manager API",
        "docs": "/docs",
        "health": "/health",
        "environment": settings.ENVIRONMENT
    }
@scheduler.scheduled_job("interval", hours=1)
def cleanup_unverified_accounts():
    db = SessionLocal()
    try:
        cutoff = datetime.now() - timedelta(hours=2)
        deleted = db.query(UserModel).filter(
            UserModel.is_verified == False,
            UserModel.created_at < cutoff
        ).delete()
        db.commit()
        if deleted:
            logger.info(f"🗑️ {deleted} unverifizierte Accounts gelöscht")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Cleanup fehlgeschlagen: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # Nur in Development
    )


