# backend/routers/optimizer.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session

from models.database import get_db
from routers.auth import get_current_user
from services.optimizer_service import (
    generate_suggestions,
    get_trending_hashtags,
    get_best_times_for_user,
)

router = APIRouter(prefix="/api/optimizer", tags=["optimizer"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class SuggestRequest(BaseModel):
    user_id: str
    title_draft: str = Field(default="", max_length=500)
    description_draft: str = Field(default="", max_length=10000)
    category: str = Field(default="default", max_length=100)
    platforms: list[str] = Field(default_factory=list)
    video_duration: Optional[int] = Field(default=None, ge=0)


class PlatformSuggestion(BaseModel):
    title: str
    title_options: Optional[List[str]] = None
    description: str
    tags: list[str]
    upload_times: list[str]


class SuggestResponse(BaseModel):
    suggestions: dict[str, PlatformSuggestion]
    best_overall_time: str
    trend_refreshed_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/suggest", response_model=SuggestResponse)
async def suggest(
    body: SuggestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if str(current_user["id"]) != str(body.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to optimize for this user.")

    if not body.platforms:
        raise HTTPException(status_code=400, detail="At least one platform must be specified.")

    return await generate_suggestions(
        db=db,
        user_id=body.user_id,
        title_draft=body.title_draft,
        description_draft=body.description_draft,
        category=body.category,
        platforms=body.platforms,
        video_duration=body.video_duration,
    )


@router.get("/trending-hashtags")
async def trending_hashtags(
    platform: str = Query(..., description="youtube | tiktok | instagram"),
    category: str = Query(default="default"),
    current_user: dict = Depends(get_current_user),
) -> dict:
    platform = platform.lower()
    if platform not in ("youtube", "tiktok", "instagram"):
        raise HTTPException(status_code=400, detail="Invalid platform.")

    tags = await get_trending_hashtags(platform=platform, category=category)
    return {"platform": platform, "category": category, "hashtags": tags}


@router.get("/best-times")
async def best_times(
    user_id: str = Query(...),
    platform: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if str(current_user["id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized.")

    platform = platform.lower()
    if platform not in ("youtube", "tiktok", "instagram"):
        raise HTTPException(status_code=400, detail="Invalid platform.")

    times = get_best_times_for_user(db=db, user_id=user_id, platform=platform)
    return {"user_id": user_id, "platform": platform, "best_times": times}
