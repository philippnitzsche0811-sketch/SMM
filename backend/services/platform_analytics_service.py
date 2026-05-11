"""
Fetches personal performance data from TikTok and Instagram using the
user's stored OAuth tokens. Returns top-performing tags and best upload hours.
"""
import logging
import re
from collections import defaultdict
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_HASHTAG_RE = re.compile(r"#(\w+)")


# ---------------------------------------------------------------------------
# TikTok
# ---------------------------------------------------------------------------

async def get_tiktok_performance(access_token: str) -> dict:
    """
    Fetch the user's TikTok videos via the standard Creator API and compute
    top-performing hashtags + best upload hours from view counts.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(
                "https://open.tiktokapis.com/v2/video/list/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                json={
                    "max_count": 20,
                    "fields": ["id", "title", "create_time", "view_count", "like_count", "share_count"],
                },
            )
            if resp.status_code != 200:
                logger.warning(f"TikTok video/list returned {resp.status_code}")
                return {}
            data = resp.json()
    except Exception as exc:
        logger.error(f"TikTok performance fetch failed: {exc}")
        return {}

    videos = data.get("data", {}).get("videos", [])
    tag_views: dict[str, list[int]] = defaultdict(list)
    hour_views: dict[int, list[int]] = defaultdict(list)

    for v in videos:
        views = int(v.get("view_count", 0))
        caption = v.get("title", "")
        create_time = v.get("create_time", 0)

        for tag in _HASHTAG_RE.findall(caption.lower()):
            tag_views[tag].append(views)

        if create_time:
            import datetime
            hour = datetime.datetime.utcfromtimestamp(create_time).hour
            hour_views[hour].append(views)

    top_tags = _top_tags(tag_views, n=12)
    best_hours = _best_hours(hour_views, n=5)
    return {"top_tags": top_tags, "best_hours": best_hours}


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------

async def get_instagram_performance(access_token: str, ig_user_id: str) -> dict:
    """
    Fetch the user's recent Instagram media via the Graph API and compute
    top-performing hashtags + best upload hours from engagement (likes + comments).
    """
    if not ig_user_id:
        return {}
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                f"https://graph.instagram.com/v21.0/{ig_user_id}/media",
                params={
                    "fields": "id,like_count,comments_count,caption,timestamp,media_type",
                    "access_token": access_token,
                    "limit": "30",
                },
            )
            if resp.status_code != 200:
                logger.warning(f"Instagram media returned {resp.status_code}: {resp.text[:200]}")
                return {}
            data = resp.json()
    except Exception as exc:
        logger.error(f"Instagram performance fetch failed: {exc}")
        return {}

    items = data.get("data", [])
    tag_engagement: dict[str, list[int]] = defaultdict(list)
    hour_engagement: dict[int, list[int]] = defaultdict(list)

    for item in items:
        likes = int(item.get("like_count", 0))
        comments = int(item.get("comments_count", 0))
        engagement = likes + comments * 3  # comments weighted higher
        caption = item.get("caption", "") or ""
        timestamp = item.get("timestamp", "")

        for tag in _HASHTAG_RE.findall(caption.lower()):
            tag_engagement[tag].append(engagement)

        if timestamp and len(timestamp) >= 13:
            try:
                hour = int(timestamp[11:13])
                hour_engagement[hour].append(engagement)
            except (ValueError, IndexError):
                pass

    top_tags = _top_tags(tag_engagement, n=15)
    best_hours = _best_hours(hour_engagement, n=5)
    return {"top_tags": top_tags, "best_hours": best_hours}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _top_tags(tag_map: dict[str, list[int]], n: int) -> list[dict]:
    result = [
        {"tag": tag, "avg_views": round(sum(v) / len(v))}
        for tag, v in tag_map.items() if v
    ]
    return sorted(result, key=lambda x: x["avg_views"], reverse=True)[:n]


def _best_hours(hour_map: dict[int, list[int]], n: int) -> list[dict]:
    result = [
        {"hour": h, "avg_engagement": round(sum(v) / len(v))}
        for h, v in hour_map.items() if v
    ]
    return sorted(result, key=lambda x: x["avg_engagement"], reverse=True)[:n]
