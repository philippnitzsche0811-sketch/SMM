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
            "Analyze these video frames and return ONLY valid JSON with this exact structure:\n"
            "{\n"
            '  "overall_score": <1-10 int>,\n'
            '  "summary": "<2-3 sentence overview of what is shown in the video>",\n'
            '  "pacing_suggestions": ["<actionable suggestion>", ...],\n'
            '  "content_quality": ["<observation>", ...],\n'
            '  "cut_suggestions": ["<suggestion>", ...],\n'
            '  "sound_recommendations": ["<recommendation>", ...],\n'
            '  "metadata_suggestions": {\n'
            '    "title_options": [\n'
            '      "<HOOK: starts with emotion or surprising statement>",\n'
            '      "<SEO: main keyword early, clear, optimized for search>",\n'
            '      "<CURIOSITY: creates intrigue or FOMO>"\n'
            '    ],\n'
            '    "description": "<SEO-optimized description based on visual content, 150-300 chars>",\n'
            '    "hashtags": ["<tag1>", "<tag2>", ...]\n'
            '  }\n'
            "}\n\n"
            "The metadata_suggestions must be based on what you ACTUALLY SEE in the frames, "
            "not generic placeholders."
        ),
    })

    response = await _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=(
            "You are a professional video editor AND viral content strategist. "
            "Analyze video frames: give actionable editing feedback AND generate "
            "high-CTR metadata (titles, description, hashtags) based on the visual content. "
            "Respond ONLY with valid JSON — no markdown, no explanation."
        ),
        messages=[{"role": "user", "content": content}],
    )

    raw = response.content[0].text
    result = json.loads(raw)
    meta = result.get("metadata_suggestions", {})
    return {
        "overall_score": int(result.get("overall_score", 7)),
        "summary": str(result.get("summary", "")),
        "pacing_suggestions": list(result.get("pacing_suggestions", [])),
        "content_quality": list(result.get("content_quality", [])),
        "cut_suggestions": list(result.get("cut_suggestions", [])),
        "sound_recommendations": list(result.get("sound_recommendations", [])),
        "metadata_suggestions": {
            "title_options": [str(t) for t in meta.get("title_options", [])][:3],
            "description": str(meta.get("description", "")),
            "hashtags": [str(h) for h in meta.get("hashtags", [])][:20],
        },
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
        "metadata_suggestions": {
            "title_options": [
                "I Tried This and It Changed Everything (You Need to See This)",
                "Complete Guide: How to Get Results Fast in 2025",
                "Nobody Talks About This Method — Here's Why It Works",
            ],
            "description": (
                "In this video we walk through the complete process step by step. "
                "Whether you're a beginner or experienced, this breakdown has something for everyone. "
                "Watch until the end for the key insight most people miss."
            ),
            "hashtags": [
                "tutorial", "howto", "tips", "viral", "trending",
                "guide", "learn", "content", "socialmedia", "growth",
            ],
        },
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


# ---------------------------------------------------------------------------
# Hook Analysis (first 5 seconds — visual + audio)
# ---------------------------------------------------------------------------

async def analyze_hook(
    db: Session,
    user_id: str,
    video_id: str,
    video_path: str,
    niche: str = "default",
) -> dict:
    """Analyze the first 5 seconds (hook) of a video for both visual and audio effectiveness."""
    analysis = _get_or_create_analysis(db, video_id, user_id)

    if settings.AI_MOCK_MODE:
        result = _mock_hook_response()
        _save_hook_result(db, analysis, result)
        logger.info(f"[HOOK] Mock analysis saved for {video_id}")
        return result

    try:
        # 1. Visual: 4 frames from first 5 seconds
        loop = asyncio.get_event_loop()
        frames_b64 = await loop.run_in_executor(None, _extract_hook_frames_sync, video_path)
        logger.info(f"[HOOK] {len(frames_b64)} frames extracted from first 5s ({video_id})")

        # 2. Audio: volume stats via FFmpeg volumedetect
        audio_stats = await loop.run_in_executor(None, _get_audio_stats, video_path)
        logger.info(f"[HOOK] Audio stats: {audio_stats} ({video_id})")

        # 3. Audio: Whisper transcription of first 5 seconds
        transcript = await _transcribe_hook_audio(video_path)
        logger.info(f"[HOOK] Transcript: '{transcript[:60]}...' ({video_id})" if transcript else f"[HOOK] No transcript ({video_id})")

        # 4. Admin hook examples for niche context
        hook_examples = _get_hook_examples(db, niche)

        # 5. Claude Sonnet hook analysis
        result = await _call_claude_hook_analysis(
            frames_b64=frames_b64,
            audio_stats=audio_stats,
            transcript=transcript,
            hook_examples=hook_examples,
            niche=niche,
        )
        _save_hook_result(db, analysis, result)
        logger.info(f"[HOOK] Analysis done — score={result.get('hook_score')}/10 ({video_id})")
        return result

    except Exception as exc:
        logger.error(f"[HOOK] Analysis failed for {video_id}: {exc}")
        fallback = _mock_hook_response()
        _save_hook_result(db, analysis, fallback)
        return fallback


def _extract_hook_frames_sync(video_path: str) -> List[str]:
    """Extract 4 frames from the first 5 seconds of the video."""
    frames_b64: List[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_pattern = os.path.join(tmp_dir, "hook_%02d.jpg")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-t", "5",
            "-vf", "fps=1",
            "-vframes", "4",
            "-q:v", "3",
            out_pattern,
            "-y", "-loglevel", "error",
        ]
        try:
            subprocess.run(cmd, check=True, timeout=30)
        except Exception as exc:
            logger.warning(f"[HOOK] Frame extraction failed: {exc}")
            return []

        for fname in sorted(os.listdir(tmp_dir)):
            if fname.endswith(".jpg"):
                fpath = os.path.join(tmp_dir, fname)
                with open(fpath, "rb") as f:
                    frames_b64.append(base64.standard_b64encode(f.read()).decode())

    return frames_b64[:4]


def _get_audio_stats(video_path: str) -> dict:
    """Run FFmpeg volumedetect on the first 5 seconds and return loudness stats."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-t", "5",
                "-af", "volumedetect",
                "-f", "null", "-",
            ],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stderr
        mean_vol = _parse_ffmpeg_float(output, "mean_volume")
        max_vol = _parse_ffmpeg_float(output, "max_volume")
        has_audio = mean_vol is not None and mean_vol > -70

        energy = "none"
        if has_audio:
            if mean_vol is not None:
                if mean_vol > -20:
                    energy = "high"
                elif mean_vol > -35:
                    energy = "medium"
                else:
                    energy = "low"

        return {
            "has_audio": has_audio,
            "mean_volume": mean_vol,
            "max_volume": max_vol,
            "energy": energy,
        }
    except Exception as exc:
        logger.debug(f"[HOOK] Audio stats failed: {exc}")
        return {"has_audio": False, "mean_volume": None, "max_volume": None, "energy": "unknown"}


def _parse_ffmpeg_float(text: str, key: str) -> Optional[float]:
    import re
    match = re.search(rf"{key}:\s*([-\d.]+)\s*dB", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


async def _transcribe_hook_audio(video_path: str) -> str:
    """Extract first 5s of audio and transcribe with OpenAI Whisper. Returns '' on failure."""
    if not settings.OPENAI_API_KEY:
        return ""
    try:
        import openai
        loop = asyncio.get_event_loop()

        # Extract 5s audio as mp3 in a temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_audio = tmp.name

        cmd = [
            "ffmpeg", "-i", video_path,
            "-t", "5",
            "-acodec", "libmp3lame", "-ab", "64k",
            "-ar", "16000", "-ac", "1",
            tmp_audio,
            "-y", "-loglevel", "error",
        ]
        try:
            await loop.run_in_executor(None, lambda: subprocess.run(cmd, check=True, timeout=20))
        except Exception as exc:
            logger.debug(f"[HOOK] Audio extraction for Whisper failed: {exc}")
            return ""

        # Transcribe
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        with open(tmp_audio, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )

        os.unlink(tmp_audio)
        return str(transcript).strip()[:300]  # cap at 300 chars

    except Exception as exc:
        logger.debug(f"[HOOK] Whisper transcription failed: {exc}")
        try:
            os.unlink(tmp_audio)
        except Exception:
            pass
        return ""


def _get_hook_examples(db: Session, niche: str) -> list:
    """Load admin-curated hook examples for the given niche."""
    from models.database import HookExampleModel
    try:
        rows = (
            db.query(HookExampleModel)
            .filter(HookExampleModel.niche.in_([niche, "default"]))
            .order_by(HookExampleModel.score.desc())
            .limit(5)
            .all()
        )
        return [
            {
                "platform": r.platform,
                "hook_type": r.hook_type or "combo",
                "description": r.description or "",
                "what_worked": r.what_worked or "",
                "score": r.score,
            }
            for r in rows
        ]
    except Exception:
        return []


async def _call_claude_hook_analysis(
    frames_b64: List[str],
    audio_stats: dict,
    transcript: str,
    hook_examples: list,
    niche: str,
) -> dict:
    if not _claude:
        return _mock_hook_response()

    content = []
    for i, b64 in enumerate(frames_b64):
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
        })
        content.append({"type": "text", "text": f"Hook frame {i + 1} of {len(frames_b64)} (second {i + 1})"})

    # Build audio context block
    audio_lines = []
    if audio_stats.get("has_audio"):
        audio_lines.append(f"Audio energy: {audio_stats['energy'].upper()}")
        if audio_stats.get("mean_volume") is not None:
            audio_lines.append(f"Mean volume: {audio_stats['mean_volume']:.1f} dB")
    else:
        audio_lines.append("Audio: NONE detected (silent or no audio track)")
    if transcript:
        audio_lines.append(f"Spoken words (Whisper): \"{transcript}\"")
    else:
        audio_lines.append("Speech transcript: none detected")

    # Build examples block
    examples_lines = []
    if hook_examples:
        examples_lines.append(f"Successful {niche} hook examples (for reference):")
        for ex in hook_examples:
            examples_lines.append(
                f"  • [{ex['hook_type']}] {ex['description']} — What worked: {ex['what_worked']}"
            )

    prompt_parts = [
        f"=== AUDIO DATA (first 5 seconds) ===",
        *audio_lines,
        "",
        f"=== NICHE CONTEXT ===",
        f"Creator niche: {niche}",
        "",
    ]
    if examples_lines:
        prompt_parts += examples_lines + [""]

    prompt_parts += [
        "=== YOUR TASK ===",
        "Analyze the HOOK (first 5 seconds) shown in these frames combined with the audio data above.",
        "A great hook must: (1) grab attention in <1s, (2) make viewer want to watch on, (3) signal what the video is about.",
        "",
        "Return ONLY valid JSON — no markdown, no explanation:",
        "{",
        '  "hook_score": <1-10 int — 1=terrible, 5=average, 8=strong, 10=viral-ready>,',
        '  "hook_type": "<verbal|visual|text_overlay|music|combo>",',
        '  "audio_energy": "<none|low|medium|high>",',
        '  "audio_transcript": "<first spoken words or empty string>",',
        '  "strengths": ["<what is working well>", ...],',
        '  "weaknesses": ["<specific problem>", ...],',
        '  "improvements": ["<concrete actionable fix>", ...]',
        "}",
        "",
        "Improvements must be SPECIFIC and ACTIONABLE — not 'improve your hook' but 'add text overlay in second 1 with a number or question'.",
        f"Respond in the same language as the transcript (or German if no transcript).",
    ]

    content.append({"type": "text", "text": "\n".join(prompt_parts)})

    response = await _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=(
            f"Du bist ein Hook-Spezialist für Social Media Videos in der Nische '{niche}'. "
            "Du kennst die Algorithmen von TikTok, YouTube Shorts und Instagram Reels genau. "
            "Antworte ausschließlich mit validem JSON — kein Markdown, keine Erklärungen."
        ),
        messages=[{"role": "user", "content": content}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        if raw.endswith("```"):
            raw = raw.rsplit("\n```", 1)[0]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return _mock_hook_response()

    return {
        "hook_score":       int(result.get("hook_score", 6)),
        "hook_type":        str(result.get("hook_type", "combo")),
        "audio_energy":     str(result.get("audio_energy", audio_stats.get("energy", "unknown"))),
        "audio_transcript": str(result.get("audio_transcript", transcript))[:300],
        "strengths":        [str(s) for s in result.get("strengths", [])][:5],
        "weaknesses":       [str(w) for w in result.get("weaknesses", [])][:5],
        "improvements":     [str(i) for i in result.get("improvements", [])][:5],
    }


def _mock_hook_response() -> dict:
    return {
        "hook_score": 6,
        "hook_type": "visual",
        "audio_energy": "medium",
        "audio_transcript": "",
        "strengths": [
            "Gesicht ist in Sekunde 1 sichtbar — schafft Vertrauen",
            "Gute Belichtung im Hook-Frame",
        ],
        "weaknesses": [
            "Kein Text-Overlay in den ersten 2 Sekunden",
            "Kein sofortiger Sprechbeginn — 1-2 Sekunden Stille am Anfang",
        ],
        "improvements": [
            "Füge in Sekunde 1 einen Text ein wie '90% machen das falsch' oder eine Zahl",
            "Starte sofort zu sprechen — keine Stille in Sekunde 0–1",
            "Nutze einen Trending Sound vom Start an für höhere Reichweite",
        ],
    }


def _save_hook_result(db: Session, analysis: VideoAnalysisModel, result: dict) -> None:
    analysis.hook_result = result
    analysis.updated_at = datetime.now()
    db.commit()
