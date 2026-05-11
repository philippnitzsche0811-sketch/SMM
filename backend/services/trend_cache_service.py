# backend/services/trend_cache_service.py
"""
Manages TrendCache (global, 6h TTL) and UserPerformanceCache (per-user, 24h TTL).
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from models.database import TrendCacheModel, UserPerformanceCacheModel, PlatformConnection

logger = logging.getLogger(__name__)

_TREND_TTL_HOURS = 6
_PERF_TTL_HOURS = 24


# ---------------------------------------------------------------------------
# Global trend data (YouTube via API key; TikTok/Instagram global n/a)
# ---------------------------------------------------------------------------

async def get_trend_data(
    db: Session, platform: str, category: str
) -> tuple[dict, Optional[datetime]]:
    """Return (trend_data, refreshed_at). Fetches live if stale or missing."""
    from services import youtube_data_service  # lazy import avoids circular deps

    row = (
        db.query(TrendCacheModel)
        .filter(TrendCacheModel.platform == platform, TrendCacheModel.category == category)
        .first()
    )
    now = datetime.now(timezone.utc)

    if row and row.expires_at and row.data:
        exp = row.expires_at.replace(tzinfo=timezone.utc) if row.expires_at.tzinfo is None else row.expires_at
        if exp > now:
            return row.data, row.refreshed_at

    # Cache miss or stale — fetch live
    fresh = await _fetch_global_trend(platform, category, youtube_data_service)
    if not fresh:
        # Return stale data rather than nothing
        return (row.data or {}, row.refreshed_at) if row else ({}, None)

    refreshed_at = _upsert_trend_cache(db, platform, category, fresh)
    return fresh, refreshed_at


async def update_global_trend_cache(
    db: Session, platform: str, category: str
) -> None:
    from services import youtube_data_service
    fresh = await _fetch_global_trend(platform, category, youtube_data_service)
    if fresh:
        _upsert_trend_cache(db, platform, category, fresh)


async def _fetch_global_trend(platform: str, category: str, youtube_data_service) -> dict:
    if platform == "youtube":
        try:
            return await youtube_data_service.get_trending_analysis(category)
        except Exception as exc:
            logger.error(f"Global trend fetch failed ({platform}/{category}): {exc}")
    return {}


def _upsert_trend_cache(
    db: Session, platform: str, category: str, data: dict
) -> datetime:
    now = datetime.now(timezone.utc)
    row = (
        db.query(TrendCacheModel)
        .filter(TrendCacheModel.platform == platform, TrendCacheModel.category == category)
        .first()
    )
    if row:
        row.data = data
        row.refreshed_at = now
        row.expires_at = now + timedelta(hours=_TREND_TTL_HOURS)
    else:
        db.add(TrendCacheModel(
            id=str(uuid.uuid4()),
            platform=platform,
            category=category,
            data=data,
            refreshed_at=now,
            expires_at=now + timedelta(hours=_TREND_TTL_HOURS),
        ))
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to save trend cache ({platform}/{category}): {exc}")
    return now


# ---------------------------------------------------------------------------
# Per-user performance data
# ---------------------------------------------------------------------------

async def get_user_performance(
    db: Session, user_id: str, platform: str
) -> Optional[dict]:
    """Return cached performance dict, or None if stale/missing."""
    row = (
        db.query(UserPerformanceCacheModel)
        .filter(
            UserPerformanceCacheModel.user_id == user_id,
            UserPerformanceCacheModel.platform == platform,
        )
        .first()
    )
    if not row:
        return None
    if row.updated_at:
        now = datetime.now(timezone.utc)
        upd = row.updated_at.replace(tzinfo=timezone.utc) if row.updated_at.tzinfo is None else row.updated_at
        if (now - upd).total_seconds() > _PERF_TTL_HOURS * 3600:
            return None
    return {
        "top_tags": row.top_tags or [],
        "best_hours": row.best_hours or [],
        "best_days": row.best_days or [],
    }


async def update_user_performance(db: Session, user_id: str) -> None:
    """Fetch performance data for all connected platforms and write to cache."""
    from services import youtube_data_service, platform_analytics_service

    connections = (
        db.query(PlatformConnection)
        .filter(
            PlatformConnection.user_id == user_id,
            PlatformConnection.connected == True,
        )
        .all()
    )

    for conn in connections:
        platform = conn.platform.lower()
        if platform not in ("youtube", "tiktok", "instagram"):
            continue

        raw_token = conn.access_token
        if not raw_token:
            continue

        try:
            try:
                from services.encryption_service import decrypt_token
                access_token = decrypt_token(raw_token)
            except Exception:
                access_token = raw_token

            perf: dict = {}
            if platform == "youtube":
                perf = await youtube_data_service.get_channel_performance(access_token)
            elif platform == "tiktok":
                perf = await platform_analytics_service.get_tiktok_performance(access_token)
            elif platform == "instagram":
                ig_user_id = conn.channel_id or ""
                perf = await platform_analytics_service.get_instagram_performance(
                    access_token, ig_user_id
                )

            if perf:
                _upsert_user_perf(db, user_id, platform, perf)

        except Exception as exc:
            logger.error(f"User perf update failed ({user_id}/{platform}): {exc}")


def _upsert_user_perf(
    db: Session, user_id: str, platform: str, perf: dict
) -> None:
    now = datetime.now(timezone.utc)
    row = (
        db.query(UserPerformanceCacheModel)
        .filter(
            UserPerformanceCacheModel.user_id == user_id,
            UserPerformanceCacheModel.platform == platform,
        )
        .first()
    )
    if row:
        row.top_tags = perf.get("top_tags", [])
        row.best_hours = perf.get("best_hours", [])
        row.best_days = perf.get("best_days", [])
        row.updated_at = now
    else:
        db.add(UserPerformanceCacheModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            platform=platform,
            top_tags=perf.get("top_tags", []),
            best_hours=perf.get("best_hours", []),
            best_days=perf.get("best_days", []),
            updated_at=now,
        ))
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to save user perf cache ({user_id}/{platform}): {exc}")
