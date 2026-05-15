import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import settings
from models.database import init_db, SessionLocal, UserModel, engine
from routers import youtube, tiktok, instagram, upload, user, static_pages, auth
from routers.upload_groups import router as upload_groups_router
from routers.smart_upload import router as smart_upload_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from routers.optimizer import router as optimizer_router
from routers.admin import router as admin_router
from routers.ideas import router as ideas_router
from routers.analytics import router as analytics_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, headers_enabled=True)



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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return PlainTextResponse("User-agent: *\nAllow: /\n")


@app.api_route("/api/videos/temp/{filename}", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_temp_video(filename: str, request: Request):
    safe_name = os.path.basename(filename)
    file_path = os.path.join(settings.TEMP_DIR, safe_name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # HEAD: nur Headers zurückgeben (kein Body) – für Instagram/Meta-Crawler
    if request.method == "HEAD":
        file_size = os.path.getsize(file_path)
        return Response(
            headers={
                "content-type": "video/mp4",
                "content-length": str(file_size),
                "accept-ranges": "bytes",
                "cache-control": "public, max-age=3600",
                "access-control-allow-origin": "*",
            }
        )

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )

# CORS Middleware - dynamisch aus ENV
allowed_origins = [
    settings.FRONTEND_URL,
    "https://app.decodu-smm.com",
    "https://decodu-smm.com",
    "http://localhost:5173",
    "http://localhost:3000",
]

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
        try:
            init_db()
        except IntegrityError:
            # Multiple uvicorn workers race to create tables — the winner already did it
            logger.warning("⚠️ init_db: table creation race ignored (another worker created it)")
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
app.include_router(optimizer_router)
app.include_router(upload_groups_router, prefix="/api/upload-groups")
app.include_router(smart_upload_router, prefix="/api/smart-upload")
app.include_router(admin_router)
app.include_router(ideas_router, prefix="/api/ideas")
app.include_router(analytics_router, prefix="/api")
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
@scheduler.scheduled_job("interval", minutes=5)
async def process_scheduled_videos_job():
    """Upload videos that have a scheduled_at in the past and are still pending."""
    from models.database import VideoModel
    from services.video_service import VideoService
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC, matches DB column
        due = (
            db.query(VideoModel)
            .filter(
                VideoModel.status == "pending",
                VideoModel.scheduled_at != None,
                VideoModel.scheduled_at <= now,
                VideoModel.file_path != None,
            )
            .all()
        )
        for v in due:
            logger.info(f"⏰ Scheduled upload: {v.id}")
            await VideoService.process_scheduled_video(v.id, v.file_path)
    except Exception as e:
        logger.error(f"❌ process_scheduled_videos_job failed: {e}")
    finally:
        db.close()


@scheduler.scheduled_job("interval", minutes=30)
async def process_upload_groups_job():
    """Process due group videos."""
    from services.upload_group_service import get_due_group_videos, mark_video_uploading, mark_video_uploaded, mark_video_failed
    from services.video_service import VideoService
    from models.database import VideoModel
    db = SessionLocal()
    try:
        due = get_due_group_videos(db)
        for gv in due:
            video = db.query(VideoModel).filter(VideoModel.id == gv.video_id).first()
            if not video or not video.file_path:
                logger.warning(f"⚠️ Group video {gv.id} has no file_path – skipping")
                mark_video_failed(db, gv.id)
                continue
            logger.info(f"⏰ Group upload: video={gv.video_id} group={gv.group_id}")
            mark_video_uploading(db, gv.id)
            try:
                await VideoService.process_scheduled_video(gv.video_id, video.file_path)
                mark_video_uploaded(db, gv.id)
            except Exception as e:
                logger.error(f"❌ Group video {gv.id} upload failed: {e}")
                mark_video_failed(db, gv.id)
    except Exception as e:
        logger.error(f"❌ process_upload_groups_job failed: {e}")
    finally:
        db.close()


@scheduler.scheduled_job("interval", hours=12)
async def collect_video_stats_job():
    """Fetch per-video stats from platforms for videos uploaded 20+ hours ago."""
    from services.video_stats_service import collect_stats_for_uploaded_videos
    db = SessionLocal()
    try:
        await collect_stats_for_uploaded_videos(db)
    except Exception as e:
        logger.error(f"❌ collect_video_stats_job failed: {e}")
    finally:
        db.close()


@scheduler.scheduled_job("interval", hours=6)
async def refresh_global_trends_job():
    """Refresh YouTube trending-analysis cache for all known categories."""
    from services import trend_cache_service
    categories = ["default", "gaming", "education", "music", "entertainment",
                  "lifestyle", "tech", "food", "sports"]
    db = SessionLocal()
    try:
        for cat in categories:
            await trend_cache_service.update_global_trend_cache(db, "youtube", cat)
        logger.info(f"✅ Global trend cache refreshed ({len(categories)} categories)")
    except Exception as e:
        logger.error(f"❌ refresh_global_trends_job failed: {e}")
    finally:
        db.close()


@scheduler.scheduled_job("cron", hour=3, minute=0)
async def refresh_user_performance_job():
    """Nightly refresh of per-user performance cache for all connected platforms."""
    from models.database import PlatformConnection
    from services import trend_cache_service
    db = SessionLocal()
    try:
        user_ids = (
            db.query(PlatformConnection.user_id)
            .filter(PlatformConnection.connected == True)
            .distinct()
            .all()
        )
        user_ids = [row[0] for row in user_ids]
        for uid in user_ids:
            await trend_cache_service.update_user_performance(db, uid)
        logger.info(f"✅ User performance cache refreshed ({len(user_ids)} users)")
    except Exception as e:
        logger.error(f"❌ refresh_user_performance_job failed: {e}")
    finally:
        db.close()


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


