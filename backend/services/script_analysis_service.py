import logging
import json
from config import settings

logger = logging.getLogger(__name__)

try:
    from anthropic import AsyncAnthropic
    _claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
except ImportError:
    _claude = None
    logger.warning("anthropic not installed — script analysis will use mock mode")

try:
    import openai as _openai_module
except ImportError:
    _openai_module = None

MOCK_RESULT = {
    "hook_score": 4,
    "hook_feedback": "Strong opening — you address the viewer's pain point right away. Consider adding a specific number or surprising stat in the first 3 seconds to boost retention even further.",
    "structure_feedback": "Good flow from problem to solution. The middle section could be tighter — aim to cut 20% and show more, tell less.",
    "tips": [
        "Lead with your most surprising fact or result — don't build up to it.",
        "Add visible on-screen text in the first 2 seconds for viewers watching without sound.",
        "Close with a specific CTA (e.g. 'Comment what you tried') instead of a generic 'follow me' — it drives 3× more engagement.",
    ],
}


async def analyze_text(text: str, idea_title: str, platforms: list[str]) -> dict:
    if settings.AI_MOCK_MODE or not _claude:
        logger.info("[MOCK] Script text analysis (AI_MOCK_MODE or no Claude key)")
        return MOCK_RESULT

    platform_ctx = ", ".join(p.capitalize() for p in platforms) if platforms else "social media"
    prompt = f"""You are an expert video content strategist. A creator is planning a short-form or long-form video for {platform_ctx}.

Idea title: "{idea_title}"

Script / notes:
{text}

Analyze this script and return a JSON object with EXACTLY these fields:
- hook_score: integer 1-5 (1 = very weak hook, 5 = excellent hook)
- hook_feedback: string, 1-2 sentences about the opening hook quality and one concrete improvement suggestion
- structure_feedback: string, 1-2 sentences about the overall content structure
- tips: array of exactly 3 short, specific, actionable improvement suggestions

Return only valid JSON. No markdown, no explanation outside JSON."""

    try:
        response = await _claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Script text analysis failed: {e}")
        return MOCK_RESULT


async def analyze_audio(file_bytes: bytes, filename: str, idea_title: str, platforms: list[str]) -> dict:
    if settings.AI_MOCK_MODE or not _openai_module or not settings.OPENAI_API_KEY:
        logger.info("[MOCK] Script audio analysis (AI_MOCK_MODE or no OpenAI key)")
        return MOCK_RESULT

    try:
        import io
        client = _openai_module.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        buf = io.BytesIO(file_bytes)
        buf.name = filename
        transcription = await client.audio.transcriptions.create(model="whisper-1", file=buf)
        transcript = transcription.text
        logger.info(f"Whisper transcription: {len(transcript)} chars for '{filename}'")
        return await analyze_text(transcript, idea_title, platforms)
    except Exception as e:
        logger.error(f"Audio transcription/analysis failed: {e}")
        return MOCK_RESULT
