import asyncio
import base64
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from config import settings
from models.database import VideoAnalysisModel

logger = logging.getLogger(__name__)

try:
    from anthropic import AsyncAnthropic
    _claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
except ImportError:
    _claude = None
    logger.warning("anthropic package not installed – video analysis unavailable.")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_video_frames(
    db: Session,
    user_id: str,
    video_id: str,
    video_path: str,
) -> dict:
    analysis = _get_or_create_analysis(db, video_id, user_id)
    if analysis.status == "done":
        return analysis.analysis_result or {}

    _set_status(db, analysis, "processing")

    try:
        if settings.AI_MOCK_MODE:
            result = _mock_analysis_response()
            _save_result(db, analysis, result, frames_extracted=0)
            return result

        frames_b64 = await _extract_frames_b64(video_path, num_frames=6)
        _set_frames_extracted(db, analysis, len(frames_b64))

        if not frames_b64:
            raise RuntimeError("Could not extract any frames from video")

        result = await _call_claude_vision(frames_b64)
        _save_result(db, analysis, result, frames_extracted=len(frames_b64))
        return result

    except Exception as exc:
        logger.error(f"❌ Video analysis failed for {video_id}: {exc}")
        _set_status(db, analysis, "failed")
        raise


def get_analysis(db: Session, video_id: str) -> Optional[VideoAnalysisModel]:
    return db.query(VideoAnalysisModel).filter(VideoAnalysisModel.video_id == video_id).first()


# ---------------------------------------------------------------------------
# Frame extraction
# ---------------------------------------------------------------------------

async def _extract_frames_b64(video_path: str, num_frames: int = 6) -> List[str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_frames_sync, video_path, num_frames)


def _extract_frames_sync(video_path: str, num_frames: int) -> List[str]:
    frames_b64: List[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_pattern = os.path.join(tmp_dir, "frame_%02d.jpg")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"select=not(mod(n\\,{max(1, _estimate_interval(video_path, num_frames))}))",
            "-vframes", str(num_frames),
            "-q:v", "3",
            "-f", "image2",
            out_pattern,
            "-y", "-loglevel", "error",
        ]
        try:
            subprocess.run(cmd, check=True, timeout=60)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: time-based extraction
            cmd2 = [
                "ffmpeg", "-i", video_path,
                "-vf", f"fps=1/{max(1, _get_duration(video_path) // num_frames)}",
                "-vframes", str(num_frames),
                out_pattern,
                "-y", "-loglevel", "error",
            ]
            try:
                subprocess.run(cmd2, check=True, timeout=60)
            except Exception as e:
                logger.error(f"Frame extraction failed: {e}")
                return []

        for fname in sorted(os.listdir(tmp_dir)):
            if fname.endswith(".jpg"):
                fpath = os.path.join(tmp_dir, fname)
                with open(fpath, "rb") as f:
                    frames_b64.append(base64.standard_b64encode(f.read()).decode())

    return frames_b64[:num_frames]


def _get_duration(video_path: str) -> int:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, text=True, timeout=10,
        )
        return int(float(result.stdout.strip()))
    except Exception:
        return 60


def _estimate_interval(video_path: str, num_frames: int) -> int:
    duration = _get_duration(video_path)
    fps = 30  # safe default
    total_frames = duration * fps
    return max(1, total_frames // num_frames)


# ---------------------------------------------------------------------------
# Claude Vision call
# ---------------------------------------------------------------------------

async def _call_claude_vision(frames_b64: List[str]) -> dict:
    if not _claude:
        return _mock_analysis_response()

    content = []
    for i, b64 in enumerate(frames_b64):
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
        })
        content.append({"type": "text", "text": f"Frame {i + 1} of {len(frames_b64)}"})

    content.append({
        "type": "text",
        "text": (
            "Analyze these video frames and return ONLY valid JSON with this structure:\n"
            '{"overall_score": <1-10 int>, "summary": "<2-3 sentence overview>", '
            '"pacing_suggestions": ["<suggestion>", ...], '
            '"content_quality": ["<observation>", ...], '
            '"cut_suggestions": ["<suggestion>", ...], '
            '"sound_recommendations": ["<recommendation>", ...]}'
        ),
    })

    response = await _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are a professional video editor and social media content strategist. "
            "Analyze video frames and give actionable feedback to improve engagement. "
            "Respond ONLY with valid JSON — no markdown, no explanation."
        ),
        messages=[{"role": "user", "content": content}],
    )

    raw = response.content[0].text
    result = json.loads(raw)
    return {
        "overall_score": int(result.get("overall_score", 7)),
        "summary": str(result.get("summary", "")),
        "pacing_suggestions": list(result.get("pacing_suggestions", [])),
        "content_quality": list(result.get("content_quality", [])),
        "cut_suggestions": list(result.get("cut_suggestions", [])),
        "sound_recommendations": list(result.get("sound_recommendations", [])),
    }


# ---------------------------------------------------------------------------
# Mock
# ---------------------------------------------------------------------------

def _mock_analysis_response() -> dict:
    return {
        "overall_score": 8,
        "summary": (
            "The video has strong visual composition with good lighting throughout. "
            "The pacing is generally engaging but could benefit from tighter cuts in the middle section. "
            "Overall this is solid content ready for social media with minor improvements."
        ),
        "pacing_suggestions": [
            "Consider cutting the intro to under 3 seconds to capture attention faster",
            "The middle section around the 40-60% mark could be tightened by 20-30%",
            "End with a strong visual hook to encourage rewatches",
        ],
        "content_quality": [
            "Lighting is consistent and well-balanced throughout",
            "Subject framing follows the rule of thirds effectively",
            "Good color contrast makes the content visually appealing",
        ],
        "cut_suggestions": [
            "Add a jump cut at 0:12 to remove the slow transition",
            "Consider a match cut when switching locations",
            "The outro could use a zoom-out effect for closure",
        ],
        "sound_recommendations": [
            "Add background music at 15-20% volume to increase engagement",
            "Consider adding sound effects to emphasize key moments",
            "Normalize audio levels to avoid volume spikes",
        ],
    }


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_or_create_analysis(db: Session, video_id: str, user_id: str) -> VideoAnalysisModel:
    existing = db.query(VideoAnalysisModel).filter(VideoAnalysisModel.video_id == video_id).first()
    if existing:
        return existing
    analysis_id = f"analysis_{int(datetime.now().timestamp() * 1000)}"
    analysis = VideoAnalysisModel(
        id=analysis_id,
        video_id=video_id,
        user_id=user_id,
        status="pending",
        created_at=datetime.now(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def _set_status(db: Session, analysis: VideoAnalysisModel, status: str):
    analysis.status = status
    analysis.updated_at = datetime.now()
    db.commit()


def _set_frames_extracted(db: Session, analysis: VideoAnalysisModel, count: int):
    analysis.frames_extracted = count
    db.commit()


def _save_result(db: Session, analysis: VideoAnalysisModel, result: dict, frames_extracted: int):
    analysis.analysis_result = result
    analysis.frames_extracted = frames_extracted
    analysis.status = "done"
    analysis.updated_at = datetime.now()
    db.commit()
