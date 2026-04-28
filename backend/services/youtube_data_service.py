# backend/services/youtube_data_service.py

import logging
from collections import Counter

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

_YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


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
