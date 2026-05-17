"""
Analytics Service - fetches performance stats and comments from social media platforms
"""
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.instagram.com/v21.0"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


async def fetch_instagram_media_stats(media_id: str, access_token: str) -> dict:
    """Fetches basic stats for an Instagram media item (likes, comments_count, permalink)."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{GRAPH_BASE}/{media_id}",
                params={
                    "fields": "like_count,comments_count,timestamp,media_type,permalink,thumbnail_url",
                    "access_token": access_token,
                }
            )
            if resp.status_code != 200:
                logger.warning(f"Instagram media stats {resp.status_code}: {resp.text[:200]}")
                return {}
            data = resp.json()
            return {
                "like_count": data.get("like_count", 0),
                "comment_count": data.get("comments_count", 0),
                "media_type": data.get("media_type", ""),
                "permalink": data.get("permalink", ""),
                "thumbnail_url": data.get("thumbnail_url", ""),
                "timestamp": data.get("timestamp", ""),
            }
    except Exception as e:
        logger.error(f"Instagram media stats error: {e}")
        return {}


async def fetch_instagram_insights(media_id: str, access_token: str) -> dict:
    """Fetches insights for an Instagram Reel (plays, reach, shares, saves)."""
    # Reel metrics
    metrics_sets = [
        "plays,reach,shares,saved,total_interactions",
        "impressions,reach,shares,saved",
    ]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for metrics in metrics_sets:
                resp = await client.get(
                    f"{GRAPH_BASE}/{media_id}/insights",
                    params={"metric": metrics, "access_token": access_token}
                )
                if resp.status_code == 200:
                    result = {}
                    for item in resp.json().get("data", []):
                        name = item.get("name")
                        # insights return values as list or direct value
                        values = item.get("values")
                        if values:
                            result[name] = values[-1].get("value", 0)
                        else:
                            result[name] = item.get("value", 0)
                    return result
            return {}
    except Exception as e:
        logger.error(f"Instagram insights error: {e}")
        return {}


async def fetch_instagram_comments(media_id: str, access_token: str, limit: int = 50) -> list:
    """Fetches comments for an Instagram media item."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{GRAPH_BASE}/{media_id}/comments",
                params={
                    "fields": "id,text,username,timestamp,like_count",
                    "limit": limit,
                    "access_token": access_token,
                }
            )
            if resp.status_code != 200:
                logger.warning(f"Instagram comments {resp.status_code}: {resp.text[:200]}")
                return []
            return resp.json().get("data", [])
    except Exception as e:
        logger.error(f"Instagram comments error: {e}")
        return []


async def reply_to_instagram_comment(comment_id: str, message: str, access_token: str) -> dict:
    """Posts a reply to an Instagram comment."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{GRAPH_BASE}/{comment_id}/replies",
                data={"message": message, "access_token": access_token},
            )
            if resp.status_code != 200:
                error_msg = resp.json().get("error", {}).get("message", "Reply fehlgeschlagen")
                raise ValueError(error_msg)
            return resp.json()
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Instagram reply error: {e}")
        raise ValueError(str(e))


async def fetch_youtube_stats(video_id: str) -> dict:
    """Fetches YouTube video statistics using the Data API."""
    if not settings.YOUTUBE_DATA_API_KEY:
        return {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={"id": video_id, "part": "statistics", "key": settings.YOUTUBE_DATA_API_KEY}
            )
            if resp.status_code != 200:
                return {}
            items = resp.json().get("items", [])
            if not items:
                return {}
            s = items[0].get("statistics", {})
            return {
                "view_count": int(s.get("viewCount", 0)),
                "like_count": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0)),
            }
    except Exception as e:
        logger.error(f"YouTube stats error: {e}")
        return {}
