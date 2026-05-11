# backend/services/youtube_data_service.py

import logging
import re
from collections import Counter
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

# YouTube Data API v3 category IDs
_CATEGORY_ID_MAP: dict[str, str] = {
    "gaming": "20",
    "education": "27",
    "music": "10",
    "entertainment": "24",
    "lifestyle": "22",
    "tech": "28",
    "food": "26",
    "sports": "17",
}

_YOUTUBE_VIDEOS_URL  = "https://www.googleapis.com/youtube/v3/videos"
_YOUTUBE_SEARCH_URL  = "https://www.googleapis.com/youtube/v3/search"
_STOPWORDS = {"the","a","an","in","on","of","to","for","is","are","with","and","or","how","your","my","this","that","you","i","it","at","by","from","as","be","was","have","has","not","what","why","when","can","we","do","did","will","all","get","more","about","new","best"}


async def get_trending_tags(category: str) -> list[str]:
    """
    Fetch trending video tags from YouTube Data API v3 for the given category.
    Returns up to 20 aggregated tags sorted by frequency.
    Falls back to empty list if the API key is missing or the call fails.
    """
    if not settings.YOUTUBE_DATA_API_KEY:
        logger.warning("YOUTUBE_DATA_API_KEY not set – skipping trending tags fetch")
        return []

    params: dict = {
        "part": "snippet",
        "chart": "mostPopular",
        "regionCode": "DE",
        "maxResults": "25",
        "key": settings.YOUTUBE_DATA_API_KEY,
    }
    category_id = _CATEGORY_ID_MAP.get(category.lower())
    if category_id:
        params["videoCategoryId"] = category_id

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(_YOUTUBE_VIDEOS_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.error(f"YouTube Data API request failed: {exc}")
        return []

    tag_counter: Counter = Counter()
    for item in data.get("items", []):
        for tag in item.get("snippet", {}).get("tags", []):
            tag_counter[tag.lower().strip()] += 1

    return [tag for tag, _ in tag_counter.most_common(20)]


async def get_trending_analysis(category: str) -> dict:
    """
    Extended trending analysis for a category.
    Returns top_tags, title_patterns (word freq, avg length, common starters), and sample_titles.
    """
    if not settings.YOUTUBE_DATA_API_KEY:
        return {}

    params: dict = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "DE",
        "maxResults": "50",
        "key": settings.YOUTUBE_DATA_API_KEY,
    }
    category_id = _CATEGORY_ID_MAP.get(category.lower())
    if category_id:
        params["videoCategoryId"] = category_id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(_YOUTUBE_VIDEOS_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.error(f"YouTube trending analysis failed: {exc}")
        return {}

    tag_counter: Counter = Counter()
    word_counter: Counter = Counter()
    starter_counter: Counter = Counter()
    titles: list[str] = []
    title_lengths: list[int] = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        title = snippet.get("title", "")
        if title:
            titles.append(title)
            title_lengths.append(len(title))
            words = re.findall(r"\b[a-zA-ZäöüÄÖÜß]{3,}\b", title.lower())
            for w in words:
                if w not in _STOPWORDS:
                    word_counter[w] += 1
            if len(words) >= 2:
                starter = " ".join(words[:2])
                starter_counter[starter] += 1
        for tag in snippet.get("tags", []):
            tag_counter[tag.lower().strip()] += 1

    return {
        "top_tags": [t for t, _ in tag_counter.most_common(20)],
        "title_patterns": {
            "avg_length": round(sum(title_lengths) / len(title_lengths)) if title_lengths else 0,
            "common_words": [w for w, _ in word_counter.most_common(12)],
            "common_starters": [s for s, _ in starter_counter.most_common(6)],
        },
        "sample_titles": titles[:8],
    }


async def get_channel_performance(access_token: str) -> dict:
    """
    Fetch the user's own YouTube channel videos and compute top-performing tags
    and best upload hours based on view counts.
    Requires a user OAuth access token with youtube.readonly scope.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            # Step 1: get up to 50 of the user's video IDs
            search_resp = await client.get(
                _YOUTUBE_SEARCH_URL,
                params={"part": "id", "forMine": "true", "type": "video", "maxResults": "50"},
                headers=headers,
            )
            if search_resp.status_code != 200:
                return {}
            search_data = search_resp.json()
            video_ids = [
                item["id"]["videoId"]
                for item in search_data.get("items", [])
                if item.get("id", {}).get("videoId")
            ]
            if not video_ids:
                return {}

            # Step 2: fetch statistics + snippet for those videos
            stats_resp = await client.get(
                _YOUTUBE_VIDEOS_URL,
                params={
                    "part": "statistics,snippet",
                    "id": ",".join(video_ids),
                    "maxResults": "50",
                },
                headers=headers,
            )
            if stats_resp.status_code != 200:
                return {}
            stats_data = stats_resp.json()
    except Exception as exc:
        logger.error(f"YouTube channel performance fetch failed: {exc}")
        return {}

    tag_views: dict[str, list[int]] = {}
    hour_views: dict[int, list[int]] = {}

    for item in stats_data.get("items", []):
        views = int(item.get("statistics", {}).get("viewCount", 0))
        published = item.get("snippet", {}).get("publishedAt", "")
        tags = item.get("snippet", {}).get("tags", [])

        for tag in tags:
            tag_views.setdefault(tag.lower(), []).append(views)

        if published:
            try:
                hour = int(published[11:13])
                hour_views.setdefault(hour, []).append(views)
            except (ValueError, IndexError):
                pass

    top_tags = sorted(
        [{"tag": t, "avg_views": round(sum(v) / len(v))} for t, v in tag_views.items() if v],
        key=lambda x: x["avg_views"], reverse=True,
    )[:15]

    best_hours = sorted(
        [{"hour": h, "avg_views": round(sum(v) / len(v))} for h, v in hour_views.items() if v],
        key=lambda x: x["avg_views"], reverse=True,
    )[:5]

    return {"top_tags": top_tags, "best_hours": best_hours}
