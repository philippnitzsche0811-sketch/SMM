# backend/services/optimizer_service.py

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from data.optimizer_config import (
    PLATFORM_PEAK_TIMES,
    PLATFORM_CONSTRAINTS,
    HASHTAG_SEEDS,
)

logger = logging.getLogger(__name__)

# Optional OpenAI import – graceful fallback if not installed/configured
try:
    from openai import AsyncOpenAI
    _openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
except ImportError:
    _openai_client = None
    logger.warning("OpenAI package not installed – using template-based suggestions only.")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def generate_suggestions(
    db: AsyncSession,
    user_id: int,
    title_draft: str,
    description_draft: str,
    category: str,
    platforms: list[str],
    video_duration: Optional[int] = None,
) -> dict:
    """
    Main optimizer function.
    Returns platform-specific suggestions and the best overall upload time.
    """
    # 1. Fetch user's historical upload data
    user_history = await _get_user_upload_history(db, user_id)

    # 2. Build suggestions per platform
    suggestions = {}
    all_upload_times: list[str] = []

    for platform in platforms:
        platform = platform.lower()
        if platform not in ["youtube", "tiktok", "instagram"]:
            continue

        constraints = PLATFORM_CONSTRAINTS.get(platform, {})

        # Text optimization via AI or template
        text_data = await _optimize_text(
            platform=platform,
            title_draft=title_draft,
            description_draft=description_draft,
            category=category,
            constraints=constraints,
            video_duration=video_duration,
        )

        # Hashtag suggestions
        tags = _get_hashtags(platform=platform, category=category)

        # Best upload times (personal + general)
        upload_times = _calculate_best_times(
            platform=platform,
            category=category,
            user_history=user_history,
        )
        all_upload_times.extend(upload_times)

        suggestions[platform] = {
            "title": text_data["title"],
            "description": text_data["description"],
            "tags": tags,
            "upload_times": upload_times,
        }

    # 3. Determine single best overall time
    best_overall_time = _pick_best_overall_time(all_upload_times)

    return {
        "suggestions": suggestions,
        "best_overall_time": best_overall_time,
    }


# ---------------------------------------------------------------------------
# Text Optimization
# ---------------------------------------------------------------------------

async def _optimize_text(
    platform: str,
    title_draft: str,
    description_draft: str,
    category: str,
    constraints: dict,
    video_duration: Optional[int],
) -> dict:
    """Try GPT-4o first, fall back to template-based optimization."""
    if _openai_client:
        try:
            return await _optimize_text_with_ai(
                platform, title_draft, description_draft, category, constraints, video_duration
            )
        except Exception as e:
            logger.error(f"OpenAI optimization failed, using fallback: {e}")

    return _optimize_text_template(platform, title_draft, description_draft, constraints)


async def _optimize_text_with_ai(
    platform: str,
    title_draft: str,
    description_draft: str,
    category: str,
    constraints: dict,
    video_duration: Optional[int],
) -> dict:
    """Use GPT-4o to generate optimized title and description."""
    title_limit = constraints.get("title_max_chars", 100)
    desc_limit = constraints.get("description_max_chars", 2000)
    desc_note = constraints.get("description_note", "")

    duration_info = f"Video duration: {video_duration} seconds." if video_duration else ""

    system_prompt = (
        "You are an expert social media content optimizer. "
        "Your task is to optimize video titles and descriptions for maximum reach and engagement. "
        "Always respond with valid JSON only – no markdown, no explanation."
    )

    user_prompt = f"""
Optimize the following video metadata for {platform.upper()}.

Category: {category}
{duration_info}
Platform note: {desc_note}
Title limit: {title_limit} characters
Description limit: {desc_limit} characters

Original title: {title_draft}
Original description: {description_draft}

Return ONLY this JSON structure:
{{
  "title": "optimized title here (max {title_limit} chars)",
  "description": "optimized description here (max {desc_limit} chars)"
}}

Requirements:
- Title: compelling, keyword-rich, platform-appropriate, within character limit
- Description: natural keyword integration, platform-specific formatting
- Keep the core message/topic from the originals
- Write in the same language as the original content
"""

    response = await _openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    # Enforce character limits as safety net
    title = result.get("title", title_draft)[:title_limit]
    description = result.get("description", description_draft)[:desc_limit]

    return {"title": title, "description": description}


def _optimize_text_template(
    platform: str,
    title_draft: str,
    description_draft: str,
    constraints: dict,
) -> dict:
    """
    Template-based fallback: enforces limits and adds platform-specific formatting.
    No AI dependency required.
    """
    title_limit = constraints.get("title_max_chars", 100)
    desc_limit = constraints.get("description_max_chars", 2000)

    title = title_draft.strip()[:title_limit]
    description = description_draft.strip()

    if platform == "youtube":
        if len(description) < 100:
            description += "\n\n👇 Subscribe for more content!"
        description = description[:desc_limit]

    elif platform == "tiktok":
        # TikTok: short caption, hashtags inline
        description = description[:200]  # Keep it short for TikTok

    elif platform == "instagram":
        # Instagram: ensure first 125 chars are the hook
        if len(description) > 125:
            first_line = description[:125].rsplit(" ", 1)[0]
            rest = description[len(first_line):].strip()
            description = f"{first_line}\n\n{rest}"
        description = description[:desc_limit]

    return {"title": title, "description": description}


# ---------------------------------------------------------------------------
# Hashtag Generation
# ---------------------------------------------------------------------------

def _get_hashtags(platform: str, category: str) -> list[str]:
    """Return relevant hashtags for platform + category combination."""
    platform_seeds = HASHTAG_SEEDS.get(platform, {})
    category_lower = category.lower()

    # Try exact match, then fuzzy match, then default
    tags = platform_seeds.get(category_lower)
    if not tags:
        for key in platform_seeds:
            if key in category_lower or category_lower in key:
                tags = platform_seeds[key]
                break
    if not tags:
        tags = platform_seeds.get("default", [])

    return tags[:20]  # Respect max tag counts


# ---------------------------------------------------------------------------
# Upload Time Calculation
# ---------------------------------------------------------------------------

def _calculate_best_times(
    platform: str,
    category: str,
    user_history: list[dict],
) -> list[str]:
    """
    Combine personal upload history with general peak times.
    Returns up to 5 ISO 8601 datetime strings (next 7 days).
    """
    now = datetime.now(timezone.utc)
    scored_slots: dict[tuple[int, int], float] = {}  # (day_of_week, hour) -> score

    # Score general peak times
    platform_peaks = PLATFORM_PEAK_TIMES.get(platform, {})
    category_peaks = platform_peaks.get(category.lower(), platform_peaks.get("default", []))

    for slot in category_peaks:
        day = slot["day"]
        for hour in slot["hours"]:
            key = (day, hour)
            scored_slots[key] = scored_slots.get(key, 0) + 1.0

    # Boost with personal history (if available)
    if user_history:
        platform_history = [h for h in user_history if h["platform"] == platform]
        if platform_history:
            personal_counter = Counter(
                (h["day_of_week"], h["hour_of_day"]) for h in platform_history
                if h["status"] in ("uploaded", "processing")
            )
            max_count = max(personal_counter.values()) if personal_counter else 1
            for (day, hour), count in personal_counter.items():
                key = (day, hour)
                # Personal data weighted 1.5x normalized
                scored_slots[key] = scored_slots.get(key, 0) + (count / max_count) * 1.5

    # Sort by score, then convert to actual upcoming datetimes
    sorted_slots = sorted(scored_slots.items(), key=lambda x: x[1], reverse=True)

    result_times: list[str] = []
    seen_dates: set = set()

    for (target_dow, target_hour), _ in sorted_slots:
        if len(result_times) >= 5:
            break

        # Find the next occurrence of this day/hour in the next 7 days
        for days_ahead in range(8):
            candidate = now + timedelta(days=days_ahead)
            if candidate.weekday() == target_dow:
                dt = candidate.replace(
                    hour=target_hour, minute=0, second=0, microsecond=0
                )
                if dt > now:
                    date_key = dt.strftime("%Y-%m-%d")
                    if date_key not in seen_dates:
                        result_times.append(dt.isoformat())
                        seen_dates.add(date_key)
                        break

    return sorted(result_times)


def _pick_best_overall_time(all_times: list[str]) -> str:
    """Pick the single best upload time across all platforms."""
    if not all_times:
        # Fallback: next Friday at 15:00 UTC
        now = datetime.now(timezone.utc)
        days_until_friday = (4 - now.weekday()) % 7 or 7
        return (now + timedelta(days=days_until_friday)).replace(
            hour=15, minute=0, second=0, microsecond=0
        ).isoformat()

    # Most frequently suggested time wins
    time_counts = Counter(all_times)
    return time_counts.most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

async def _get_user_upload_history(db: AsyncSession, user_id: int) -> list[dict]:
    """Load user's upload history from videos table + performance table."""
    try:
        # Check upload_performance table first (populated by this service)
        result = await db.execute(
            text("""
                SELECT platform, day_of_week, hour_of_day, status
                FROM upload_performance
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT 100
            """),
            {"user_id": user_id},
        )
        rows = result.fetchall()

        if rows:
            return [
                {"platform": r.platform, "day_of_week": r.day_of_week,
                 "hour_of_day": r.hour_of_day, "status": r.status}
                for r in rows
            ]

        # Fallback: derive from videos table created_at
        result = await db.execute(
            text("""
                SELECT platforms, status, created_at
                FROM videos
                WHERE user_id = :user_id AND created_at IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 50
            """),
            {"user_id": user_id},
        )
        rows = result.fetchall()
        history = []
        for r in rows:
            if r.created_at and r.platforms:
                for platform in r.platforms:
                    history.append({
                        "platform": platform.lower(),
                        "day_of_week": r.created_at.weekday(),
                        "hour_of_day": r.created_at.hour,
                        "status": r.status,
                    })
        return history

    except Exception as e:
        logger.error(f"Error fetching upload history for user {user_id}: {e}")
        return []


async def get_trending_hashtags(platform: str, category: str) -> list[str]:
    """Public function for the trending-hashtags endpoint."""
    return _get_hashtags(platform=platform, category=category)


async def get_best_times_for_user(
    db: AsyncSession, user_id: int, platform: str
) -> list[str]:
    """Public function for the best-times endpoint."""
    user_history = await _get_user_upload_history(db, user_id)
    return _calculate_best_times(
        platform=platform,
        category="default",
        user_history=user_history,
    )
