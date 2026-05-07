import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from models.database import UploadGroupModel, GroupVideoModel, VideoModel
from models.video import VideoStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_group(
    db: Session,
    user_id: str,
    name: str,
    platforms: List[str],
    privacy_status: str = "private",
    category: str = "entertainment",
) -> UploadGroupModel:
    group_id = f"grp_{int(datetime.now().timestamp() * 1000)}"
    group = UploadGroupModel(
        id=group_id,
        user_id=user_id,
        name=name,
        platforms=platforms,
        privacy_status=privacy_status,
        category=category,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    logger.info(f"✅ Upload group created: {group_id}")
    return group


def get_group(db: Session, group_id: str) -> Optional[UploadGroupModel]:
    return db.query(UploadGroupModel).filter(UploadGroupModel.id == group_id).first()


def get_user_groups(db: Session, user_id: str) -> List[UploadGroupModel]:
    return (
        db.query(UploadGroupModel)
        .filter(UploadGroupModel.user_id == user_id)
        .order_by(UploadGroupModel.created_at.desc())
        .all()
    )


def get_group_videos(db: Session, group_id: str) -> List[GroupVideoModel]:
    return (
        db.query(GroupVideoModel)
        .filter(GroupVideoModel.group_id == group_id)
        .order_by(GroupVideoModel.position)
        .all()
    )


def add_video_to_group(
    db: Session,
    group_id: str,
    video_id: str,
    ai_context: Optional[str] = None,
) -> GroupVideoModel:
    existing_count = (
        db.query(GroupVideoModel)
        .filter(GroupVideoModel.group_id == group_id)
        .count()
    )
    gv_id = f"gv_{int(datetime.now().timestamp() * 1000)}"
    gv = GroupVideoModel(
        id=gv_id,
        group_id=group_id,
        video_id=video_id,
        position=existing_count,
        status="queued",
        ai_context=ai_context,
    )
    db.add(gv)
    db.commit()
    recompute_group_schedule(db, group_id)
    logger.info(f"✅ Video {video_id} added to group {group_id}")
    return gv


def remove_video_from_group(db: Session, gv_id: str):
    gv = db.query(GroupVideoModel).filter(GroupVideoModel.id == gv_id).first()
    if not gv:
        raise ValueError(f"GroupVideo {gv_id} not found")
    group_id = gv.group_id
    db.delete(gv)
    db.commit()
    recompute_group_schedule(db, group_id)
    logger.info(f"✅ GroupVideo {gv_id} removed")


def pause_group(db: Session, group_id: str):
    group = get_group(db, group_id)
    if group:
        group.status = "paused"
        group.updated_at = datetime.now()
        db.commit()


def resume_group(db: Session, group_id: str):
    group = get_group(db, group_id)
    if group:
        group.status = "active"
        group.updated_at = datetime.now()
        db.commit()
        recompute_group_schedule(db, group_id)


def delete_group(db: Session, group_id: str):
    group = get_group(db, group_id)
    if not group:
        raise ValueError(f"Group {group_id} not found")
    db.delete(group)
    db.commit()
    logger.info(f"🗑️ Group {group_id} deleted")


def update_group(
    db: Session,
    group_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
) -> UploadGroupModel:
    group = get_group(db, group_id)
    if not group:
        raise ValueError(f"Group {group_id} not found")
    if name is not None:
        group.name = name
    if status is not None:
        group.status = status
    group.updated_at = datetime.now()
    db.commit()
    db.refresh(group)
    return group


# ---------------------------------------------------------------------------
# Density scheduling algorithm
# ---------------------------------------------------------------------------

def recompute_group_schedule(db: Session, group_id: str):
    """Assign scheduled_at to all queued GroupVideos using density-aware algorithm."""
    group = get_group(db, group_id)
    if not group or group.status == "paused":
        return

    queued = (
        db.query(GroupVideoModel)
        .filter(
            GroupVideoModel.group_id == group_id,
            GroupVideoModel.status == "queued",
        )
        .order_by(GroupVideoModel.position)
        .all()
    )

    n = len(queued)
    if n == 0:
        return

    slots = _compute_slots(db, group, n)

    for gv, slot_dt in zip(queued, slots):
        gv.scheduled_at = slot_dt
        # Mirror scheduled_at onto the video record so the scheduler can pick it up
        video = db.query(VideoModel).filter(VideoModel.id == gv.video_id).first()
        if video:
            video.scheduled_at = slot_dt
            video.updated_at = datetime.now()

    db.commit()
    logger.info(f"📅 Scheduled {n} videos for group {group_id}")


def _compute_slots(db: Session, group: UploadGroupModel, n: int) -> List[datetime]:
    """Return n datetime slots using density-based rules."""
    from services.optimizer_service import _best_upload_times, _get_user_upload_history

    now = datetime.now(timezone.utc)
    history = _get_user_upload_history(db, group.user_id)
    platforms = group.platforms if isinstance(group.platforms, list) else []
    # Use first platform as primary signal; fall back to 'youtube'
    primary = platforms[0] if platforms else "youtube"

    if n == 1:
        # Strict: next optimal slot
        times = _best_upload_times(primary, group.category, history)
        if times:
            return [datetime.fromisoformat(times[0])]
        return [now + timedelta(hours=2)]

    if n <= 4:
        # Top-5 slots, ≥24h apart
        times = _best_upload_times(primary, group.category, history)
        return _spaced_slots(times, n, min_gap_hours=24, now=now, fallback_interval_hours=24)

    if n <= 9:
        # Top-10 over 2 weeks, ≥18h apart
        times_raw = _best_upload_times(primary, group.category, history)
        # Extend to 2 weeks by repeating weekly
        extended = _extend_times_to_n(times_raw, n + 5, weeks=2, now=now)
        return _spaced_slots(extended, n, min_gap_hours=18, now=now, fallback_interval_hours=20)

    # n ≥ 10: daily uploads at best hour or 15:00 UTC
    best_hour = _best_hour_of_day(history, primary) or 15
    slots: List[datetime] = []
    day = now
    while len(slots) < n:
        day = day + timedelta(days=1)
        slot = day.replace(hour=best_hour, minute=0, second=0, microsecond=0)
        slots.append(slot)
    return slots


def _spaced_slots(
    times: List[str],
    n: int,
    min_gap_hours: int,
    now: datetime,
    fallback_interval_hours: int,
) -> List[datetime]:
    result: List[datetime] = []
    last: Optional[datetime] = None

    for t_str in times:
        if len(result) >= n:
            break
        try:
            dt = datetime.fromisoformat(t_str)
        except ValueError:
            continue
        if dt <= now:
            continue
        if last is None or (dt - last).total_seconds() >= min_gap_hours * 3600:
            result.append(dt)
            last = dt

    # Fill remaining with fallback spacing
    while len(result) < n:
        base = result[-1] if result else now
        next_slot = base + timedelta(hours=fallback_interval_hours)
        result.append(next_slot)

    return result[:n]


def _extend_times_to_n(times: List[str], target: int, weeks: int, now: datetime) -> List[str]:
    """Repeat weekly offsets to cover `weeks` weeks."""
    result = list(times)
    for week in range(1, weeks + 1):
        for t_str in times:
            if len(result) >= target:
                break
            try:
                dt = datetime.fromisoformat(t_str)
                result.append((dt + timedelta(weeks=week)).isoformat())
            except ValueError:
                pass
    return result


def _best_hour_of_day(history: List[dict], platform: str) -> Optional[int]:
    from collections import Counter
    platform_history = [h for h in history if h["platform"] == platform]
    if not platform_history:
        return None
    counter: Counter = Counter(h["hour_of_day"] for h in platform_history)
    return counter.most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Scheduler helpers
# ---------------------------------------------------------------------------

def get_due_group_videos(db: Session) -> List[GroupVideoModel]:
    """All queued group videos whose scheduled_at is in the past."""
    now = datetime.now(timezone.utc)
    return (
        db.query(GroupVideoModel)
        .filter(
            GroupVideoModel.status == "queued",
            GroupVideoModel.scheduled_at <= now,
        )
        .all()
    )


def mark_video_uploading(db: Session, gv_id: str):
    gv = db.query(GroupVideoModel).filter(GroupVideoModel.id == gv_id).first()
    if gv:
        gv.status = "uploading"
        db.commit()


def mark_video_uploaded(db: Session, gv_id: str):
    gv = db.query(GroupVideoModel).filter(GroupVideoModel.id == gv_id).first()
    if gv:
        gv.status = "done"
        gv.uploaded_at = datetime.now()
        db.commit()


def mark_video_failed(db: Session, gv_id: str):
    gv = db.query(GroupVideoModel).filter(GroupVideoModel.id == gv_id).first()
    if gv:
        gv.status = "failed"
        db.commit()
