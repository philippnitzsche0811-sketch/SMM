# backend/routers/admin.py
"""
Admin-only endpoints for manually entering trend research data.
Guard: current_user["email"] must match settings.ADMIN_EMAIL.
"""
import re
import uuid
import logging
from collections import Counter
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from sqlalchemy import func
from models.database import AdminTrendDataModel, HookExampleModel, AiTokenUsageModel, AppConfigModel, get_db
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

_VALID_PLATFORMS = {"youtube", "tiktok", "instagram"}


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if not settings.ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access not configured")
    if current_user.get("email") != settings.ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AdminTrendDataIn(BaseModel):
    platform: str
    category: str
    top_tags: Optional[list[str]] = None
    title_words: Optional[list[str]] = None
    title_starters: Optional[list[str]] = None
    notes: Optional[str] = None


class AdminTrendDataOut(BaseModel):
    id: str
    platform: str
    category: str
    top_tags: Optional[list[str]]
    title_words: Optional[list[str]]
    title_starters: Optional[list[str]]
    notes: Optional[str]
    updated_at: Optional[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/trend-data", response_model=AdminTrendDataOut)
async def upsert_trend_data(
    body: AdminTrendDataIn,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    if body.platform not in _VALID_PLATFORMS:
        raise HTTPException(400, f"platform must be one of {_VALID_PLATFORMS}")

    row = (
        db.query(AdminTrendDataModel)
        .filter(
            AdminTrendDataModel.platform == body.platform,
            AdminTrendDataModel.category == body.category,
        )
        .first()
    )
    now = datetime.utcnow()

    if row:
        row.top_tags       = body.top_tags
        row.title_words    = body.title_words
        row.title_starters = body.title_starters
        row.notes          = body.notes
        row.updated_at     = now
    else:
        row = AdminTrendDataModel(
            id=str(uuid.uuid4()),
            platform=body.platform,
            category=body.category,
            top_tags=body.top_tags,
            title_words=body.title_words,
            title_starters=body.title_starters,
            notes=body.notes,
            updated_at=now,
        )
        db.add(row)

    try:
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to upsert admin trend data: {exc}")
        raise HTTPException(500, "Failed to save")

    return _to_out(row)


@router.get("/trend-data", response_model=list[AdminTrendDataOut])
async def list_trend_data(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    rows = (
        db.query(AdminTrendDataModel)
        .order_by(AdminTrendDataModel.updated_at.desc())
        .all()
    )
    return [_to_out(r) for r in rows]


@router.delete("/trend-data/{entry_id}", status_code=204)
async def delete_trend_data(
    entry_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.query(AdminTrendDataModel).filter(AdminTrendDataModel.id == entry_id).first()
    if not row:
        raise HTTPException(404, "Entry not found")
    db.delete(row)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, "Failed to delete")


class ParseRawRequest(BaseModel):
    raw_text: str
    platform: str = "youtube"
    category: str = "default"


_STOPWORDS = {
    "the","a","an","in","on","of","to","for","is","are","with","and","or",
    "how","your","my","this","that","you","i","it","at","by","from","as",
    "be","was","have","has","not","what","why","when","can","we","do","did",
    "will","all","get","more","about","new","best","so","but","if","then",
    "just","like","make","use","one","our","its","out","up","no","now","here",
    "ich","das","die","der","ein","eine","und","oder","ist","sind","mit","für",
    "auf","von","zu","in","bei","nach","wie","was","wir","du","er","sie","es",
    "nicht","auch","noch","nur","schon","dann","wenn","aber","damit","weil",
}

_HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
_WORD_RE    = re.compile(r"\b[a-zA-ZäöüÄÖÜß]{3,}\b")


@router.post("/parse-raw")
async def parse_raw_text(
    body: ParseRawRequest,
    _: dict = Depends(require_admin),
):
    """
    Extract top_tags, title_words, and title_starters from pasted raw text
    (TikTok Creative Center output, Instagram captions, YouTube title lists, etc.)
    No AI call — pure regex + frequency analysis.
    """
    text = body.raw_text

    # 1. Hashtags via regex
    raw_tags = _HASHTAG_RE.findall(text)
    seen: set = set()
    top_tags: list[str] = []
    for t in raw_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            top_tags.append(tl)
    top_tags = top_tags[:25]

    # 2. Title words — frequency count on lines that look like titles (≥ 15 chars)
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) >= 15]
    word_counter: Counter = Counter()
    for line in lines:
        for word in _WORD_RE.findall(line.lower()):
            if word not in _STOPWORDS and word not in seen:  # skip if already a hashtag
                word_counter[word] += 1
    title_words = [w for w, _ in word_counter.most_common(15)]

    # 3. Title starters — first 2–3 words of title-like lines, deduplicated
    starter_seen: set = set()
    title_starters: list[str] = []
    for line in lines:
        words = _WORD_RE.findall(line)
        if len(words) >= 2:
            starter = " ".join(words[:3])
            starter_lower = starter.lower()
            if starter_lower not in starter_seen:
                starter_seen.add(starter_lower)
                title_starters.append(starter)
        if len(title_starters) >= 8:
            break

    return {
        "top_tags":       top_tags,
        "title_words":    title_words,
        "title_starters": title_starters,
    }


# ---------------------------------------------------------------------------
# Hook Examples CRUD
# ---------------------------------------------------------------------------

class HookExampleIn(BaseModel):
    platform: str
    niche: str
    hook_type: Optional[str] = None
    description: Optional[str] = None
    what_worked: Optional[str] = None
    score: Optional[int] = None
    source_url: Optional[str] = None


@router.post("/hook-examples", status_code=201)
async def create_hook_example(
    body: HookExampleIn,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    if body.platform not in _VALID_PLATFORMS:
        raise HTTPException(400, f"platform must be one of {_VALID_PLATFORMS}")

    row = HookExampleModel(
        id=str(uuid.uuid4()),
        platform=body.platform,
        niche=body.niche,
        hook_type=body.hook_type,
        description=body.description,
        what_worked=body.what_worked,
        score=body.score,
        source_url=body.source_url,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, "Failed to save hook example")
    return _hook_to_out(row)


@router.get("/hook-examples")
async def list_hook_examples(
    platform: Optional[str] = None,
    niche: Optional[str] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = db.query(HookExampleModel)
    if platform:
        q = q.filter(HookExampleModel.platform == platform)
    if niche:
        q = q.filter(HookExampleModel.niche == niche)
    rows = q.order_by(HookExampleModel.created_at.desc()).all()
    return [_hook_to_out(r) for r in rows]


@router.patch("/hook-examples/{example_id}")
async def update_hook_example(
    example_id: str,
    body: HookExampleIn,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.query(HookExampleModel).filter(HookExampleModel.id == example_id).first()
    if not row:
        raise HTTPException(404, "Hook example not found")
    for field in ("platform", "niche", "hook_type", "description", "what_worked", "score", "source_url"):
        val = getattr(body, field, None)
        if val is not None:
            setattr(row, field, val)
    try:
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, "Failed to update")
    return _hook_to_out(row)


@router.delete("/hook-examples/{example_id}", status_code=204)
async def delete_hook_example(
    example_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.query(HookExampleModel).filter(HookExampleModel.id == example_id).first()
    if not row:
        raise HTTPException(404, "Hook example not found")
    db.delete(row)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Failed to delete")


def _hook_to_out(row: HookExampleModel) -> dict:
    return {
        "id":          row.id,
        "platform":    row.platform,
        "niche":       row.niche,
        "hook_type":   row.hook_type,
        "description": row.description,
        "what_worked": row.what_worked,
        "score":       row.score,
        "source_url":  row.source_url,
        "created_at":  row.created_at.isoformat() if row.created_at else None,
    }


# ---------------------------------------------------------------------------
# Token usage tracking
# ---------------------------------------------------------------------------

_INPUT_PRICE_PER_M  = 0.80   # USD per 1M input tokens  (Haiku estimate)
_OUTPUT_PRICE_PER_M = 4.00   # USD per 1M output tokens (Haiku estimate)


@router.get("/token-usage")
async def get_token_usage(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    from datetime import timezone
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _agg(query_result):
        inp = query_result.input_tokens or 0
        out = query_result.output_tokens or 0
        calls = query_result.calls or 0
        cost = round((inp / 1_000_000 * _INPUT_PRICE_PER_M) + (out / 1_000_000 * _OUTPUT_PRICE_PER_M), 4)
        return {"input_tokens": inp, "output_tokens": out, "total_tokens": inp + out, "calls": calls, "estimated_cost_usd": cost}

    total_row = db.query(
        func.coalesce(func.sum(AiTokenUsageModel.input_tokens), 0).label("input_tokens"),
        func.coalesce(func.sum(AiTokenUsageModel.output_tokens), 0).label("output_tokens"),
        func.count(AiTokenUsageModel.id).label("calls"),
    ).one()

    month_row = db.query(
        func.coalesce(func.sum(AiTokenUsageModel.input_tokens), 0).label("input_tokens"),
        func.coalesce(func.sum(AiTokenUsageModel.output_tokens), 0).label("output_tokens"),
        func.count(AiTokenUsageModel.id).label("calls"),
    ).filter(AiTokenUsageModel.timestamp >= month_start).one()

    budget_row = db.query(AppConfigModel).filter(AppConfigModel.key == "monthly_token_budget").first()
    budget = int(budget_row.value) if (budget_row and budget_row.value) else None

    return {
        "all_time": _agg(total_row),
        "this_month": _agg(month_row),
        "monthly_budget_tokens": budget,
        "month_label": now.strftime("%B %Y"),
    }


class TokenBudgetIn(BaseModel):
    budget: Optional[int] = None


@router.put("/token-budget", status_code=204)
async def set_token_budget(
    body: TokenBudgetIn,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.query(AppConfigModel).filter(AppConfigModel.key == "monthly_token_budget").first()
    value = str(body.budget) if body.budget is not None else None
    if row:
        row.value = value
        row.updated_at = datetime.utcnow()
    else:
        row = AppConfigModel(key="monthly_token_budget", value=value)
        db.add(row)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, "Failed to save budget")


def _to_out(row: AdminTrendDataModel) -> dict:
    return {
        "id":             row.id,
        "platform":       row.platform,
        "category":       row.category,
        "top_tags":       row.top_tags,
        "title_words":    row.title_words,
        "title_starters": row.title_starters,
        "notes":          row.notes,
        "updated_at":     row.updated_at.isoformat() if row.updated_at else None,
    }
