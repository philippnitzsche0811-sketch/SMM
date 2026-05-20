from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import secrets
import logging

from models.database import get_db, ContentIdeaModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Content Ideas"])

VALID_STATUSES = {"idea", "planning", "ready"}


# ── Request Models ──────────────────────────────────────────────────────────

class IdeaCreateRequest(BaseModel):
    user_id: str
    title: str
    concept: Optional[str] = None
    target_platforms: Optional[List[str]] = []
    target_date: Optional[str] = None
    status: Optional[str] = "idea"
    tags: Optional[List[str]] = []


class IdeaUpdateRequest(BaseModel):
    user_id: str
    title: Optional[str] = None
    concept: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    target_date: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    ai_suggestions: Optional[dict] = None


# ── Helpers ─────────────────────────────────────────────────────────────────

def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is not None:
            from datetime import timezone
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat für target_date")


def _idea_to_dict(idea: ContentIdeaModel) -> dict:
    return {
        "id": idea.id,
        "user_id": idea.user_id,
        "title": idea.title,
        "concept": idea.concept,
        "target_platforms": idea.target_platforms or [],
        "target_date": idea.target_date.isoformat() if idea.target_date else None,
        "status": idea.status,
        "tags": idea.tags or [],
        "ai_suggestions": idea.ai_suggestions or {},
        "created_at": idea.created_at.isoformat() if idea.created_at else None,
        "updated_at": idea.updated_at.isoformat() if idea.updated_at else None,
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/")
async def list_ideas(user_id: str, db: Session = Depends(get_db)):
    ideas = (
        db.query(ContentIdeaModel)
        .filter(ContentIdeaModel.user_id == user_id)
        .order_by(ContentIdeaModel.created_at.desc())
        .all()
    )
    return [_idea_to_dict(i) for i in ideas]


@router.post("/")
async def create_idea(body: IdeaCreateRequest, db: Session = Depends(get_db)):
    if body.status and body.status not in VALID_STATUSES:
        raise HTTPException(400, f"Status muss einer von {VALID_STATUSES} sein")

    idea = ContentIdeaModel(
        id=f"idea_{secrets.token_hex(8)}",
        user_id=body.user_id,
        title=body.title,
        concept=body.concept,
        target_platforms=body.target_platforms,
        target_date=_parse_date(body.target_date),
        status=body.status or "idea",
        tags=body.tags,
        created_at=datetime.now(),
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    logger.info(f"✅ Idee erstellt: {idea.id} für User {idea.user_id}")
    return _idea_to_dict(idea)


@router.patch("/{idea_id}")
async def update_idea(idea_id: str, body: IdeaUpdateRequest, db: Session = Depends(get_db)):
    idea = db.query(ContentIdeaModel).filter(ContentIdeaModel.id == idea_id).first()
    if not idea:
        raise HTTPException(404, "Idee nicht gefunden")
    if idea.user_id != body.user_id:
        raise HTTPException(403, "Nicht autorisiert")
    if body.status and body.status not in VALID_STATUSES:
        raise HTTPException(400, f"Status muss einer von {VALID_STATUSES} sein")

    if body.title is not None:
        idea.title = body.title
    if body.concept is not None:
        idea.concept = body.concept
    if body.target_platforms is not None:
        idea.target_platforms = body.target_platforms
    if body.target_date is not None:
        idea.target_date = _parse_date(body.target_date)
    if body.status is not None:
        idea.status = body.status
    if body.tags is not None:
        idea.tags = body.tags
    if body.ai_suggestions is not None:
        idea.ai_suggestions = body.ai_suggestions

    idea.updated_at = datetime.now()
    db.commit()
    db.refresh(idea)
    return _idea_to_dict(idea)


@router.delete("/{idea_id}")
async def delete_idea(idea_id: str, user_id: str, db: Session = Depends(get_db)):
    idea = db.query(ContentIdeaModel).filter(ContentIdeaModel.id == idea_id).first()
    if not idea:
        raise HTTPException(404, "Idee nicht gefunden")
    if idea.user_id != user_id:
        raise HTTPException(403, "Nicht autorisiert")
    db.delete(idea)
    db.commit()
    return {"success": True}
