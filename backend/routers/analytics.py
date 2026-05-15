"""
Analytics Router - video performance stats and comment collection
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from models.database import get_db, VideoModel, VideoStatsModel
from routers.auth import get_current_user
from services.analytics_service import (
    fetch_instagram_media_stats,
    fetch_instagram_insights,
    fetch_instagram_comments,
    fetch_youtube_stats,
)
from services.token_storage import TokenStorage

router = APIRouter(prefix="/analytics", tags=["Analytics"])
token_storage = TokenStorage()
logger = logging.getLogger(__name__)

IDEA_KEYWORDS = [
    "solltest", "könntest", "wäre cool", "idea", "idee", "würde",
    "vorschlag", "suggestion", "try", "consider", "you should", "how about",
    "warum nicht", "könntet", "mach doch", "nächstes mal",
]


@router.get("/videos")
async def get_videos_with_stats(
    user_id: str = Query(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns all successfully uploaded videos with their cached platform stats."""
    if str(current_user["id"]) != user_id:
        raise HTTPException(403, "Not authorized")

    videos = (
        db.query(VideoModel)
        .filter(VideoModel.user_id == user_id, VideoModel.status.in_(["uploaded", "partial"]))
        .order_by(VideoModel.created_at.desc())
        .all()
    )

    result = []
    for video in videos:
        stats_by_platform: dict = {}
        for stat in db.query(VideoStatsModel).filter(VideoStatsModel.video_id == video.id).all():
            stats_by_platform[stat.platform] = {
                "view_count": stat.view_count,
                "like_count": stat.like_count,
                "comment_count": stat.comment_count,
                "share_count": stat.share_count,
                "fetched_at": stat.fetched_at.isoformat() if stat.fetched_at else None,
            }

        result.append({
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "platforms": video.platforms or [],
            "upload_results": video.upload_results or {},
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "stats": stats_by_platform,
        })

    return {"videos": result}


@router.post("/video/{video_id}/refresh")
async def refresh_video_stats(
    video_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetches fresh stats from all platforms for a specific video and stores them."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")
    if str(video.user_id) != str(current_user["id"]):
        raise HTTPException(403, "Not authorized")

    upload_results = video.upload_results or {}
    user_id = str(current_user["id"])
    refreshed: dict = {}

    # Instagram
    ig_result = upload_results.get("instagram", {})
    ig_media_id = ig_result.get("media_id")
    if ig_media_id and not ig_result.get("mock"):
        ig_creds = token_storage.load_instagram_credentials(user_id)
        if ig_creds:
            media_stats = await fetch_instagram_media_stats(ig_media_id, ig_creds["access_token"])
            insights = await fetch_instagram_insights(ig_media_id, ig_creds["access_token"])
            if media_stats or insights:
                _upsert_stats(db, video_id, user_id, "instagram", ig_media_id, {
                    "view_count": insights.get("plays", insights.get("impressions", 0)),
                    "like_count": media_stats.get("like_count", 0),
                    "comment_count": media_stats.get("comment_count", 0),
                    "share_count": insights.get("shares", 0),
                })
                refreshed["instagram"] = True

    # YouTube
    yt_result = upload_results.get("youtube", {})
    yt_video_id = yt_result.get("video_id")
    if yt_video_id and not yt_result.get("mock"):
        yt_stats = await fetch_youtube_stats(yt_video_id)
        if yt_stats:
            _upsert_stats(db, video_id, user_id, "youtube", yt_video_id, yt_stats)
            refreshed["youtube"] = True

    db.commit()
    return {"status": "success", "refreshed": refreshed}


@router.get("/video/{video_id}/comments")
async def get_video_comments(
    video_id: str,
    platform: str = Query("instagram"),
    filter_type: str = Query("all"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetches comments for a specific video from the given platform.
    filter_type: all | questions | ideas
    """
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")
    if str(video.user_id) != str(current_user["id"]):
        raise HTTPException(403, "Not authorized")

    upload_results = video.upload_results or {}
    user_id = str(current_user["id"])

    if platform == "instagram":
        ig_result = upload_results.get("instagram", {})
        ig_media_id = ig_result.get("media_id")

        if not ig_media_id or ig_result.get("mock"):
            return {"comments": [], "platform": platform, "filter": filter_type, "total": 0, "mock": bool(ig_result.get("mock"))}

        ig_creds = token_storage.load_instagram_credentials(user_id)
        if not ig_creds:
            raise HTTPException(400, "Instagram nicht verbunden")

        comments = await fetch_instagram_comments(ig_media_id, ig_creds["access_token"])
        comments = _apply_filter(comments, filter_type)
        return {
            "comments": comments,
            "platform": platform,
            "filter": filter_type,
            "total": len(comments),
        }

    return {"comments": [], "platform": platform, "filter": filter_type, "total": 0}


def _apply_filter(comments: list, filter_type: str) -> list:
    if filter_type == "questions":
        return [c for c in comments if "?" in c.get("text", "")]
    if filter_type == "ideas":
        return [
            c for c in comments
            if any(kw in c.get("text", "").lower() for kw in IDEA_KEYWORDS)
        ]
    return comments


def _upsert_stats(
    db: Session,
    video_id: str,
    user_id: str,
    platform: str,
    platform_video_id: str,
    stats: dict,
) -> None:
    record = (
        db.query(VideoStatsModel)
        .filter(VideoStatsModel.video_id == video_id, VideoStatsModel.platform == platform)
        .first()
    )
    if record:
        record.view_count = stats.get("view_count", 0)
        record.like_count = stats.get("like_count", 0)
        record.comment_count = stats.get("comment_count", 0)
        record.share_count = stats.get("share_count", 0)
        record.fetched_at = datetime.now()
    else:
        db.add(VideoStatsModel(
            id=str(uuid.uuid4()),
            video_id=video_id,
            user_id=user_id,
            platform=platform,
            platform_video_id=platform_video_id,
            view_count=stats.get("view_count", 0),
            like_count=stats.get("like_count", 0),
            comment_count=stats.get("comment_count", 0),
            share_count=stats.get("share_count", 0),
            fetched_at=datetime.now(),
        ))
