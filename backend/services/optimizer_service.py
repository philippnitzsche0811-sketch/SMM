# backend/services/optimizer_service.py

import json
import logging
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from data.optimizer_config import (
    PLATFORM_PEAK_TIMES,
    PLATFORM_CONSTRAINTS,
    HASHTAG_SEEDS,
)
from services import youtube_data_service

logger = logging.getLogger(__name__)

try:
    from anthropic import AsyncAnthropic
    _claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
except ImportError:
    _claude = None
    logger.warning("anthropic package not installed – using template-based suggestions only.")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def generate_suggestions(
    db: Session,
    user_id: str,
    title_draft: str,
    description_draft: str,
    category: str,
    platforms: list[str],
    video_duration: Optional[int] = None,
) -> dict:
    user_history = _get_user_upload_history(db, user_id)

    suggestions: dict = {}
    all_upload_times: list[str] = []

    for platform in platforms:
        platform = platform.lower()
        if platform not in ("youtube", "tiktok", "instagram"):
            continue

        constraints = PLATFORM_CONSTRAINTS.get(platform, {})

        # External trending tags (YouTube only – others use Claude knowledge)
        trending_tags: list[str] = []
        if platform == "youtube":
            trending_tags = await youtube_data_service.get_trending_tags(category)

        # AI optimization: title + description + hashtags in one call
        if _claude and not settings.AI_MOCK_MODE:
            try:
                ai = await _optimize_with_claude(
                    platform=platform,
                    title_draft=title_draft,
                    description_draft=description_draft,
                    category=category,
                    constraints=constraints,
                    video_duration=video_duration,
                    trending_tags=trending_tags,
                )
                title = ai["title"]
                description = ai["description"]
                tags = ai["hashtags"]
            except Exception as exc:
                logger.error(f"Claude optimization failed for {platform}: {exc}")
                fallback = _template_fallback(platform, title_draft, description_draft, constraints)
                title, description = fallback["title"], fallback["description"]
                tags = _static_hashtags(platform, category)
        else:
            fallback = _template_fallback(platform, title_draft, description_draft, constraints)
            title, description = fallback["title"], fallback["description"]
            tags = _static_hashtags(platform, category)

        upload_times = _best_upload_times(platform, category, user_history)
        all_upload_times.extend(upload_times)

        suggestions[platform] = {
            "title": title,
            "description": description,
            "tags": tags,
            "upload_times": upload_times,
        }

    return {
        "suggestions": suggestions,
        "best_overall_time": _pick_best_time(all_upload_times),
    }


# ---------------------------------------------------------------------------
# Claude AI optimization
# ---------------------------------------------------------------------------

async def _optimize_with_claude(
    platform: str,
    title_draft: str,
    description_draft: str,
    category: str,
    constraints: dict,
    video_duration: Optional[int],
    trending_tags: list[str],
) -> dict:
    title_limit = constraints.get("title_max_chars", 100)
    desc_limit = constraints.get("description_max_chars", 2000)
    desc_note = constraints.get("description_note", "")
    tags_max = constraints.get("tags_max_count", 20)

    duration_line = f"Videolänge: {video_duration} Sekunden." if video_duration else ""
    trending_line = (
        f"Aktuell trending auf {platform.upper()}: {', '.join(trending_tags[:12])}"
        if trending_tags else ""
    )

    user_prompt = f"""Optimiere die folgenden Video-Metadaten für {platform.upper()}.

Kategorie: {category}
{duration_line}
Plattform-Hinweis: {desc_note}
Titel-Limit: {title_limit} Zeichen
Beschreibungs-Limit: {desc_limit} Zeichen
Max. Hashtags: {tags_max}
{trending_line}

Originaler Titel: {title_draft}
Originale Beschreibung: {description_draft}

Antworte NUR mit dieser JSON-Struktur:
{{
  "title": "optimierter Titel",
  "description": "optimierte Beschreibung",
  "hashtags": ["hashtag1", "hashtag2"]
}}

Anforderungen:
- Titel: überzeugend, keyword-reich, innerhalb des Zeichenlimits
- Beschreibung: natürliche Keywords, plattformgerechte Formatierung, innerhalb des Zeichenlimits
- Hashtags: {tags_max} relevante Tags ohne #-Zeichen, Mix aus trending und nischenspezifisch
- Sprache des Originals beibehalten (deutsch oder englisch)
- Kernbotschaft des Originals erhalten"""

    response = await _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "Du bist ein Experte für Social-Media-Content-Optimierung. "
            "Optimiere Video-Metadaten für maximale Reichweite und Engagement. "
            "Antworte ausschließlich mit validem JSON – kein Markdown, keine Erklärungen."
        ),
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text
    result = json.loads(raw)

    return {
        "title": str(result.get("title", title_draft))[:title_limit],
        "description": str(result.get("description", description_draft))[:desc_limit],
        "hashtags": [str(t) for t in result.get("hashtags", [])][:tags_max],
    }


# ---------------------------------------------------------------------------
# Template fallback (no AI)
# ---------------------------------------------------------------------------

def _template_fallback(
    platform: str,
    title_draft: str,
    description_draft: str,
    constraints: dict,
) -> dict:
    title = title_draft.strip()[:constraints.get("title_max_chars", 100)]
    desc = description_draft.strip()
    desc_limit = constraints.get("description_max_chars", 2000)

    if platform == "youtube":
        if len(desc) < 100:
            desc += "\n\n👇 Abonniere für mehr Content!"
        desc = desc[:desc_limit]
    elif platform == "tiktok":
        desc = desc[:200]
    elif platform == "instagram":
        if len(desc) > 125:
            cut = desc[:125].rsplit(" ", 1)[0]
            desc = f"{cut}\n\n{desc[len(cut):].strip()}"
        desc = desc[:desc_limit]

    return {"title": title, "description": desc}


# ---------------------------------------------------------------------------
# Static hashtag seeds (fallback)
# ---------------------------------------------------------------------------

def _static_hashtags(platform: str, category: str) -> list[str]:
    seeds = HASHTAG_SEEDS.get(platform, {})
    cat = category.lower()
    tags = seeds.get(cat)
    if not tags:
        for key in seeds:
            if key in cat or cat in key:
                tags = seeds[key]
                break
    if not tags:
        tags = seeds.get("default", [])
    return tags[:20]


# ---------------------------------------------------------------------------
# Upload time calculation
# ---------------------------------------------------------------------------

def _best_upload_times(
    platform: str,
    category: str,
    user_history: list[dict],
) -> list[str]:
    now = datetime.now(timezone.utc)
    scored: dict[tuple[int, int], float] = {}

    # General peak times as base score
    peaks = PLATFORM_PEAK_TIMES.get(platform, {})
    slots = peaks.get(category.lower(), peaks.get("default", []))
    for slot in slots:
        for hour in slot["hours"]:
            key = (slot["day"], hour)
            scored[key] = scored.get(key, 0) + 1.0

    # Personal history boosts score (1.5× weight, normalized)
    platform_history = [h for h in user_history if h["platform"] == platform]
    if platform_history:
        counter: Counter = Counter(
            (h["day_of_week"], h["hour_of_day"])
            for h in platform_history
            if h["status"] in ("uploaded", "processing")
        )
        max_count = max(counter.values()) if counter else 1
        for (d, h), count in counter.items():
            scored[(d, h)] = scored.get((d, h), 0) + (count / max_count) * 1.5

    sorted_slots = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    result: list[str] = []
    seen_dates: set = set()

    for (target_dow, target_hour), _ in sorted_slots:
        if len(result) >= 5:
            break
        for days_ahead in range(8):
            candidate = now + timedelta(days=days_ahead)
            if candidate.weekday() == target_dow:
                dt = candidate.replace(hour=target_hour, minute=0, second=0, microsecond=0)
                if dt > now:
                    date_key = dt.strftime("%Y-%m-%d")
                    if date_key not in seen_dates:
                        result.append(dt.isoformat())
                        seen_dates.add(date_key)
                        break

    return sorted(result)


def _pick_best_time(all_times: list[str]) -> str:
    if not all_times:
        now = datetime.now(timezone.utc)
        days_until_friday = (4 - now.weekday()) % 7 or 7
        return (now + timedelta(days=days_until_friday)).replace(
            hour=15, minute=0, second=0, microsecond=0
        ).isoformat()
    return Counter(all_times).most_common(1)[0][0]


# ---------------------------------------------------------------------------
# DB helpers (sync)
# ---------------------------------------------------------------------------

def _get_user_upload_history(db: Session, user_id: str) -> list[dict]:
    try:
        rows = db.execute(
            text("""
                SELECT platform, day_of_week, hour_of_day, status
                FROM upload_performance
                WHERE user_id = :uid
                ORDER BY uploaded_at DESC
                LIMIT 100
            """),
            {"uid": user_id},
        ).fetchall()

        if rows:
            return [
                {"platform": r.platform, "day_of_week": r.day_of_week,
                 "hour_of_day": r.hour_of_day, "status": r.status}
                for r in rows
            ]

        # Fallback: derive timing from videos table
        rows = db.execute(
            text("""
                SELECT platforms, status, created_at
                FROM videos
                WHERE user_id = :uid AND created_at IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 50
            """),
            {"uid": user_id},
        ).fetchall()

        history: list[dict] = []
        for r in rows:
            if r.created_at and r.platforms:
                for p in (r.platforms if isinstance(r.platforms, list) else []):
                    history.append({
                        "platform": p.lower(),
                        "day_of_week": r.created_at.weekday(),
                        "hour_of_day": r.created_at.hour,
                        "status": r.status,
                    })
        return history

    except Exception as exc:
        logger.error(f"Error fetching upload history for user {user_id}: {exc}")
        try:
            db.rollback()
        except Exception:
            pass
        return []


# ---------------------------------------------------------------------------
# Public helpers for standalone endpoints
# ---------------------------------------------------------------------------

async def get_trending_hashtags(platform: str, category: str) -> list[str]:
    if platform == "youtube":
        tags = await youtube_data_service.get_trending_tags(category)
        if tags:
            return tags
    return _static_hashtags(platform, category)


def get_best_times_for_user(db: Session, user_id: str, platform: str) -> list[str]:
    history = _get_user_upload_history(db, user_id)
    return _best_upload_times(platform=platform, category="default", user_history=history)
