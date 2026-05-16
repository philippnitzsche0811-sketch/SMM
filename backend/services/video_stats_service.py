# backend/services/video_stats_service.py
"""
Fetches per-video performance stats from YouTube / TikTok / Instagram
after upload and stores them in video_stats table.
Used by APScheduler to build a feedback loop for the AI optimizer.
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.database import VideoStatsModel, VideoModel

logger = logging.getLogger(__name__)


async def collect_stats_for_uploaded_videos(db: Session) -> None:
    """Find uploaded videos without stats older than 20h and fetch their platform stats."""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=20)

    # Videos uploaded at least 20h ago with no stats entry yet
    rows = db.execute(
        text("""
            SELECT v.id AS video_id, v.user_id, v.platforms, v.upload_results
            FROM videos v
            WHERE v.status = 'uploaded'
              AND v.created_at <= :cutoff
              AND NOT EXISTS (
                  SELECT 1 FROM video_stats s WHERE s.video_id = v.id
              )
            ORDER BY v.created_at DESC
            LIMIT 50
        """),
        {"cutoff": cutoff},
    ).fetchall()

    for row in rows:
        video_id = row.video_id
        user_id = row.user_id
        platforms = row.platforms or []
        upload_results = row.upload_results or {}

        for platform in platforms:
            platform = platform.lower()
            result = upload_results.get(platform, {})
            if not result:
                continue

            platform_video_id = (
                result.get("video_id")      # YouTube
                or result.get("publish_id") # TikTok
                or result.get("media_id")   # Instagram
            )

            try:
                stats = await _fetch_stats(db, user_id, platform, platform_video_id, result)
                if stats:
                    _save_stats(db, video_id, user_id, platform, platform_video_id, stats)
            except Exception as exc:
                logger.warning(f"Stats fetch failed ({video_id}/{platform}): {exc}")


async def _fetch_stats(
    db: Session,
    user_id: str,
    platform: str,
    platform_video_id: str | None,
    upload_result: dict,
) -> dict | None:
    from models.database import PlatformConnection
    from services.encryption_service import decrypt_token

    conn = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == user_id,
        PlatformConnection.platform == platform,
        PlatformConnection.connected == True,
    ).first()

    if not conn or not conn.access_token:
        return None

    try:
        access_token = decrypt_token(conn.access_token)
    except Exception:
        access_token = conn.access_token

    if platform == "youtube":
        return await _youtube_stats(access_token, platform_video_id)
    elif platform == "tiktok":
        return await _tiktok_stats(access_token, platform_video_id)
    elif platform == "instagram":
        return await _instagram_stats(access_token, platform_video_id)
    return None


async def _youtube_stats(access_token: str, video_id: str | None) -> dict | None:
    if not video_id:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics",
                    "id": video_id,
                    "access_token": access_token,
                },
            )
            if resp.status_code != 200:
                return None
            items = resp.json().get("items", [])
            if not items:
                return None
            stats = items[0].get("statistics", {})
            return {
                "view_count":    int(stats.get("viewCount", 0)),
                "like_count":    int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "share_count":   0,
            }
    except Exception as exc:
        logger.debug(f"YouTube stats fetch error: {exc}")
        return None


async def _tiktok_stats(access_token: str, publish_id: str | None) -> dict | None:
    if not publish_id:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://open.tiktokapis.com/v2/video/list/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                json={
                    "max_count": 20,
                    "fields": ["id", "view_count", "like_count", "comment_count", "share_count"],
                },
            )
            if resp.status_code != 200:
                return None
            videos = resp.json().get("data", {}).get("videos", [])
            for v in videos:
                if str(v.get("id")) == str(publish_id):
                    return {
                        "view_count":    int(v.get("view_count", 0)),
                        "like_count":    int(v.get("like_count", 0)),
                        "comment_count": int(v.get("comment_count", 0)),
                        "share_count":   int(v.get("share_count", 0)),
                    }
    except Exception as exc:
        logger.debug(f"TikTok stats fetch error: {exc}")
    return None


async def _instagram_stats(access_token: str, media_id: str | None) -> dict | None:
    if not media_id:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://graph.instagram.com/v21.0/{media_id}",
                params={
                    "fields": "like_count,comments_count",
                    "access_token": access_token,
                },
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            return {
                "view_count":    0,
                "like_count":    int(data.get("like_count", 0)),
                "comment_count": int(data.get("comments_count", 0)),
                "share_count":   0,
            }
    except Exception as exc:
        logger.debug(f"Instagram stats fetch error: {exc}")
    return None


def _save_stats(
    db: Session,
    video_id: str,
    user_id: str,
    platform: str,
    platform_video_id: str | None,
    stats: dict,
) -> None:
    now = datetime.now(timezone.utc)
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
        fetched_at=now,
    ))
    try:
        db.commit()
        logger.info(f"✅ Stats saved: {video_id}/{platform} views={stats.get('view_count', 0)}")
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to save stats ({video_id}/{platform}): {exc}")


def get_top_performing_videos(db: Session, user_id: str, platform: str, n: int = 5) -> list[dict]:
    """Return the top n videos by view count for a user+platform with their titles."""
    rows = db.execute(
        text("""
            SELECT s.view_count, s.like_count, v.title, v.tags, v.created_at
            FROM video_stats s
            JOIN videos v ON v.id = s.video_id
            WHERE s.user_id = :uid AND s.platform = :platform AND s.view_count > 0
            ORDER BY s.view_count DESC
            LIMIT :n
        """),
        {"uid": user_id, "platform": platform, "n": n},
    ).fetchall()

    return [
        {
            "title": r.title,
            "tags": r.tags or [],
            "view_count": r.view_count,
            "like_count": r.like_count,
        }
        for r in rows
    ]
