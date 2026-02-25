import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import settings
from models.database import init_db
from routers import youtube, tiktok, instagram, upload, user, static_pages, auth

# Logging Setup
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Social Media Upload Manager",
    version="1.0.0",
    description="Multi-Platform Video Upload Manager"
)

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
    logger.info(f"ðŸš€ Starting application in {settings.ENVIRONMENT} mode...")
    try:
        init_db()
        logger.info("âœ… Database tables initialized")
    except Exception as e:
        logger.error(f"âŒ Database initialization failed: {e}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # Nur in Development
    )


