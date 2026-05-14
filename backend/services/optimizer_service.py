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
from models.database import AdminTrendDataModel, AiTokenUsageModel, AppConfigModel
from services import youtube_data_service, trend_cache_service

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
    niche: str = "default",
    creator_tone: str = "informative",
) -> dict:
    user_history = _get_user_upload_history(db, user_id)

    suggestions: dict = {}
    all_upload_times: list[str] = []
    trend_refreshed_at: Optional[str] = None

    for platform in platforms:
        platform = platform.lower()
        if platform not in ("youtube", "tiktok", "instagram"):
            continue

        constraints = PLATFORM_CONSTRAINTS.get(platform, {})

        # Load top-performing video history for feedback context
        try:
            from services.video_stats_service import get_top_performing_videos
            top_videos = get_top_performing_videos(db, user_id, platform, n=5)
        except Exception:
            top_videos = []

        # Load live trend + personal performance data
        try:
            trend_data, refreshed_at = await trend_cache_service.get_trend_data(
                db, platform, category
            )
            if refreshed_at and not trend_refreshed_at:
                trend_refreshed_at = refreshed_at.isoformat()
        except Exception as exc:
            logger.warning(f"Trend data load failed ({platform}/{category}): {exc}")
            trend_data = {}

        try:
            user_perf = await trend_cache_service.get_user_performance(db, user_id, platform)
        except Exception as exc:
            logger.warning(f"User perf load failed ({user_id}/{platform}): {exc}")
            user_perf = None

        # Merge manually curated admin data (takes priority — prepended to auto-fetched)
        try:
            admin_row = (
                db.query(AdminTrendDataModel)
                .filter(
                    AdminTrendDataModel.platform == platform,
                    AdminTrendDataModel.category == category,
                )
                .first()
            )
            logger.info(f"🔍 Admin trend lookup ({platform}/{category}): {'found' if admin_row else 'no data'}")
            if admin_row:
                trend_data = _merge_admin_trend(trend_data, admin_row)
                logger.info(f"✅ Admin trend data merged ({platform}/{category}): {len(admin_row.top_tags or [])} tags, {len(admin_row.title_words or [])} words")
        except Exception as exc:
            logger.warning(f"Admin trend data load failed ({platform}/{category}): {exc}")

        # AI optimization: title + description + hashtags in one call
        if _claude and not settings.AI_MOCK_MODE:
            try:
                ai = await _optimize_with_claude(
                    db=db,
                    platform=platform,
                    title_draft=title_draft,
                    description_draft=description_draft,
                    category=category,
                    constraints=constraints,
                    video_duration=video_duration,
                    trend_data=trend_data,
                    user_perf=user_perf,
                    niche=niche,
                    creator_tone=creator_tone,
                    top_videos=top_videos,
                )
                title = ai["title"]
                title_options = ai.get("title_options", [title])
                description = ai["description"]
                tags = ai["hashtags"]
            except Exception as exc:
                logger.error(f"Claude optimization failed for {platform}: {exc}")
                fallback = _template_fallback(platform, title_draft, description_draft, constraints)
                title, description = fallback["title"], fallback["description"]
                title_options = fallback.get("title_options", [title])
                tags = _static_hashtags(platform, category)
        else:
            fallback = _template_fallback(platform, title_draft, description_draft, constraints)
            title, description = fallback["title"], fallback["description"]
            title_options = fallback.get("title_options", [title])
            tags = _static_hashtags(platform, category)

        upload_times = _best_upload_times(platform, category, user_history)
        all_upload_times.extend(upload_times)

        suggestions[platform] = {
            "title": title,
            "title_options": title_options,
            "description": description,
            "tags": tags,
            "upload_times": upload_times,
        }

    return {
        "suggestions": suggestions,
        "best_overall_time": _pick_best_time(all_upload_times),
        "trend_refreshed_at": trend_refreshed_at,
    }


# ---------------------------------------------------------------------------
# Claude AI optimization
# ---------------------------------------------------------------------------

_NICHE_STRATEGY: dict[str, str] = {
    "fitness": "Fitness & Sport — Schmerzpunkt ansprechen (Fett verlieren, Muskeln aufbauen, schneller werden), konkrete Zahlen im Titel (5kg in 4 Wochen), vorher/nachher Framing, Motivation + Disziplin als Trigger.",
    "food": "Food & Rezepte — Gericht prominent nennen, Schwierigkeitsgrad (5 Minuten, einfach, schnell), Emotion (das cremigste, das beste ever), Jahreszeit oder Anlass nutzen.",
    "finance": "Finance & Geld — konkrete Summen nennen (1000€ im Monat, 5% Rendite), Angst vor Verlust oder FOMO nutzen, Expertise signalisieren (Fehler die 99% machen), Clickbait mit Substanz.",
    "gaming": "Gaming — Titel mit Spielname + Event/Patch, emotional (unmöglich, episch, 1 vs 100), Community-Insider-Sprache nutzen, Cliffhanger am Titelende.",
    "tech": "Tech & Gadgets — Produktname früh nennen, Vergleich oder Review-Format (besser als X?, lohnt sich?), konkrete Specs oder Preisnennung, Neuheit betonen.",
    "lifestyle": "Lifestyle — Aspiration und Ästhetik, 'mein', 'meine Routine', 'ein Tag in meinem Leben', Storytelling und Authentizität, Orte und Gefühle.",
    "education": "Education & Lernen — klare Lernversprechen (du lernst X in Y Minuten), Stufenformat (für Anfänger, für Fortgeschrittene), Komplexes einfach erklären, Nützlichkeit direkt im Titel.",
    "comedy": "Comedy & Entertainment — Überraschung und Subversion der Erwartung, übertriebene Aussagen, Selbstironie, Trendbezug oder virales Meme aufgreifen.",
    "beauty": "Beauty & Make-up — Produkt oder Look nennen, Transformation betonen, Dauer (10-Minuten-Make-up), Anlass (Party, Alltag, Hochzeit), Trending Looks referenzieren.",
    "travel": "Travel & Reise — Ort konkret nennen, Überraschungsmoment (das erwartet dich nicht, geheimtipp), Budget (X Euro Urlaub), Itinerary-Format (3 Tage in X).",
    "default": "Allgemeiner Content — starke Emotion oder Neugier im Titel, klarer Nutzen für den Zuschauer, konkrete Zahlen oder Versprechen wo möglich.",
}

_TONE_GUIDE: dict[str, str] = {
    "educational": "Lehrreicher, autoritativer Ton. Erkläre das Warum. Baue Expertise auf. CTA: 'Mehr lernen', 'Alles erklärt in…'",
    "entertainer": "Lebendiger, unterhaltsamer Ton. Humor und Persönlichkeit durchscheinen lassen. CTA: 'Schau dir auch an…', 'Folge für mehr'",
    "inspirational": "Motivierender, emotionaler Ton. Transformation betonen. Zuschauer ermächtigen. CTA: 'Du schaffst das', 'Starte heute'",
    "informative": "Sachlicher, direkter Ton. Fakten first. Klarer Nutzen ohne Blabla. CTA: 'Alle Details in der Beschreibung', 'Link unten'",
}

_PLATFORM_FORMAT: dict[str, str] = {
    "youtube": """YOUTUBE-SPEZIFISCHE REGELN (STRIKT EINHALTEN):
- Titel: Hauptkeyword in den ersten 40 Zeichen, klar und suchoptimiert. Keine Clickbait ohne Substanz.
- Beschreibung: 150-400 Wörter. Erste 2 Zeilen entscheidend (erscheinen vor "mehr anzeigen"). Struktur:
  Zeile 1-2: Kurze Zusammenfassung mit Haupt-Keywords
  [Leerzeile]
  Ausführlichere Erklärung des Inhalts (2-3 Absätze)
  [Leerzeile]
  Timestamps wenn sinnvoll: 00:00 Intro, 01:30 Hauptteil...
  [Leerzeile]
  Links / Social Media / CTAs
  [Leerzeile]
  #Hashtag1 #Hashtag2 #Hashtag3 (3-5 am Ende der Beschreibung)
- Hashtags: 8-15 Tags, Mix aus Broad (Millionen Suchen) + Mid (100k-1M) + Nischen-Tags. KEIN #-Zeichen im Array.
- Ziel: SEO-Ranking + hohe CTR durch Thumbnail+Titel Combo.""",

    "tiktok": """TIKTOK-SPEZIFISCHE REGELN (STRIKT EINHALTEN):
- Titel/Caption: Max 150 Zeichen für optimale Darstellung. Kurz, direkt, mit Hook in den ersten 5 Wörtern.
  Emojis strategisch einsetzen (1-3 pro Caption, am Satzende oder als Aufzählung).
  Caption = das erste was Nutzer nach dem Video lesen — muss Neugier oder Engagement erzeugen.
- Beschreibung: IDENTISCH mit dem Titel/Caption Feld — bei TikTok gibt es nur die Caption.
  Kein langer Fließtext. Hashtags direkt in der Caption oder darunter.
- Hashtags: Genau 3-5 Tags. Formel: 1 Mega-Tag (>10M Views), 1-2 Mid-Tags (1M-10M), 1-2 Nischen-Tags.
  Direkt nach der Caption, ohne Leerzeile.
- Titeloptionen: Alle 3 unter 150 Zeichen. Mindestens eine Option mit Emoji. Eine mit Frage-Hook. Eine mit Zahlen.
- Ziel: Watch-Time + Shares + Kommentare (FYP-Algorithmus).""",

    "instagram": """INSTAGRAM-SPEZIFISCHE REGELN (STRIKT EINHALTEN):
- Titel: Wird als erster Satz der Caption genutzt. Kurz und packend (unter 125 Zeichen, erscheint vor "mehr").
  Starke erste Zeile = mehr "mehr anzeigen" Klicks = besseres Engagement-Signal.
- Beschreibung/Caption: 150-300 Wörter. Storytelling-Struktur:
  Zeile 1: Hook-Satz (unter 125 Zeichen — wird vor "mehr" angezeigt)
  [Leerzeile]
  Story oder Mehrwert (3-5 kurze Absätze, luftig formatiert)
  [Leerzeile]
  Soft CTA (kein harter Link-Push — "speichern falls hilfreich", "markiere jemanden dem das hilft")
  [Leerzeile]
  .
  .
  .
  #Hashtag1 #Hashtag2 ... (Hashtags am Ende oder im ersten Kommentar, 15-20 Stück)
- Hashtags: 15-20 Tags. Formel: 5 Große (>500k Posts), 7-8 Mid (50k-500k), 5 Nischen (<50k). KEIN #-Zeichen im Array.
- Ziel: Saves + Shares (Reels-Algorithmus), Entdeckung über Hashtags.""",
}


async def _optimize_with_claude(
    db: Session,
    platform: str,
    title_draft: str,
    description_draft: str,
    category: str,
    constraints: dict,
    video_duration: Optional[int],
    trend_data: dict,
    user_perf: Optional[dict],
    niche: str = "default",
    creator_tone: str = "informative",
    top_videos: list | None = None,
) -> dict:
    title_limit = constraints.get("title_max_chars", 100)
    desc_limit = constraints.get("description_max_chars", 2000)
    tags_max = constraints.get("tags_max_count", 20)

    duration_line = f"Videolänge: {video_duration} Sekunden." if video_duration else ""

    # Build real-data block from trend + personal performance
    real_data_lines: list[str] = []
    if trend_data:
        top_tags = trend_data.get("top_tags", [])
        patterns = trend_data.get("title_patterns", {})
        if top_tags:
            real_data_lines.append(f"Trending-Tags ({platform.upper()}): {', '.join(top_tags[:12])}")
        if patterns.get("common_words"):
            real_data_lines.append(f"Häufige Titelwörter aktuell: {', '.join(patterns['common_words'][:10])}")
        if patterns.get("common_starters"):
            starters = '", "'.join(patterns["common_starters"][:4])
            real_data_lines.append(f'Häufige Titel-Starter: "{starters}"')
        if patterns.get("avg_length"):
            real_data_lines.append(f"Ø Titellänge Top-Videos: {patterns['avg_length']} Zeichen")

    if user_perf:
        user_tags = [t["tag"] for t in (user_perf.get("top_tags") or [])[:8]]
        user_hours = [str(h["hour"]) + ":00" for h in (user_perf.get("best_hours") or [])[:4]]
        if user_tags:
            real_data_lines.append(f"Deine best-performing eigenen Tags: {', '.join(user_tags)}")
        if user_hours:
            real_data_lines.append(f"Deine besten Upload-Zeiten (UTC): {', '.join(user_hours)}")

    if trend_data.get("_admin_notes"):
        real_data_lines.append(f"Admin-Beobachtungen: {trend_data['_admin_notes']}")

    # Top-performing videos feedback loop
    if top_videos:
        for i, v in enumerate(top_videos[:3], 1):
            views = v.get("view_count", 0)
            title = v.get("title", "")
            tags = v.get("tags") or []
            if title and views > 0:
                tag_preview = ", ".join(tags[:5]) if tags else "—"
                real_data_lines.append(
                    f"Dein Top-{i} Video ({views:,} Views): Titel='{title}' | Tags: {tag_preview}"
                )

    live_data_block = ""
    if real_data_lines:
        live_data_block = (
            "\n=== LIVE PLATFORM DATA ===\n"
            + "\n".join(f"- {line}" for line in real_data_lines)
            + "\nNutze diese Daten konkret — verwende die trending Tags und Titelstruktur.\n"
            "=== ENDE ===\n"
        )

    niche_strategy = _NICHE_STRATEGY.get(niche, _NICHE_STRATEGY["default"])
    tone_guide = _TONE_GUIDE.get(creator_tone, _TONE_GUIDE["informative"])
    platform_format = _PLATFORM_FORMAT.get(platform, "")

    user_prompt = f"""Du erstellst plattform-native Video-Metadaten für {platform.upper()}.

=== CREATOR PROFIL ===
Nische: {niche.upper()} — {niche_strategy}
Ton: {creator_tone.upper()} — {tone_guide}
Kategorie: {category}
{duration_line}

=== PLATTFORM-FORMAT REGELN ===
{platform_format}

=== LIMITS ===
Titel-Limit: {title_limit} Zeichen (alle 3 Varianten müssen eingehalten werden)
Beschreibungs-Limit: {desc_limit} Zeichen
Max. Hashtags: {tags_max}
{live_data_block}
=== ORIGINAL-KONTEXT ===
Titel-Entwurf: {title_draft}
Beschreibung/Kontext: {description_draft}

=== AUFGABE ===
Erstelle 3 Titel-Varianten nach diesen Strategien:
1. HOOK — startet mit einer Emotion, überraschenden Aussage oder Schmerzpunkt. Kein generischer Einstieg.
2. SEO — Haupt-Keyword in den ersten Wörtern, klar und suchoptimiert. Für {platform.upper()} Suchalgorithmus.
3. CURIOSITY — erzeugt Neugier oder FOMO. Lässt eine Frage offen oder deutet Überraschendes an.

Antworte NUR mit dieser JSON-Struktur (kein Markdown, keine Erklärungen):
{{
  "title": "die stärkste der drei Varianten für {platform.upper()}",
  "title_options": [
    "HOOK-Variante (Emotion/Schmerzpunkt)",
    "SEO-Variante (Keyword-optimiert)",
    "CURIOSITY-Variante (Neugier/FOMO)"
  ],
  "description": "plattform-native Beschreibung nach den obigen FORMAT REGELN",
  "hashtags": ["tag1", "tag2"]
}}

Kritisch: Beschreibung und Hashtags müssen sich je nach Plattform DEUTLICH unterscheiden.
Sprache des Originals beibehalten (deutsch oder englisch)."""

    response = await _claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=(
            f"Du bist ein spezialisierter Content-Stratege für {platform.upper()} mit Fokus auf die Nische '{niche}'. "
            f"Du kennst die plattform-spezifischen Algorithmen, Formate und Creator-Strategien für {platform.upper()} genau. "
            "Deine Metadaten sind platform-native — nicht copy-paste zwischen Plattformen. "
            "Antworte ausschließlich mit validem JSON – kein Markdown, keine Erklärungen."
        ),
        messages=[{"role": "user", "content": user_prompt}],
    )

    try:
        import uuid as _uuid
        db.add(AiTokenUsageModel(
            id=str(_uuid.uuid4()),
            model=response.model,
            platform=platform,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        ))
        db.commit()
    except Exception as _e:
        logger.warning(f"Token usage tracking failed: {_e}")

    raw = response.content[0].text.strip()
    # Strip markdown code fences if model wrapped response despite instructions
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        if raw.endswith("```"):
            raw = raw.rsplit("\n```", 1)[0]
        raw = raw.strip()
    if not raw:
        raise ValueError("Claude returned empty response")
    result = json.loads(raw)

    raw_options = result.get("title_options", [])
    title_options = [str(t)[:title_limit] for t in raw_options][:3]
    best_title = str(result.get("title", title_draft))[:title_limit]
    if not title_options:
        title_options = [best_title]

    return {
        "title": best_title,
        "title_options": title_options,
        "description": str(result.get("description", description_draft))[:desc_limit],
        "hashtags": [str(t) for t in result.get("hashtags", [])][:tags_max],
    }


# ---------------------------------------------------------------------------
# Template fallback (no AI / AI_MOCK_MODE)
# ---------------------------------------------------------------------------

import re as _re


def _clean_title(raw: str) -> str:
    cleaned = _re.sub(r"[_-]+", " ", raw).strip()
    cleaned = _re.sub(r"\s+", " ", cleaned)
    return cleaned.title()


def _title_variants(title: str, platform: str, title_limit: int) -> list[str]:
    base = _clean_title(title)
    if platform == "youtube":
        variants = [base, base + " (Full Video)", "How To: " + base]
    elif platform == "tiktok":
        variants = [base, base + " \U0001F525", "POV: " + base.lower()]
    elif platform == "instagram":
        variants = [base, base + " ✨", "My " + base.lower() + " experience"]
    else:
        variants = [base, base + " | Full Video", "Watch: " + base]
    return [v[:title_limit] for v in variants]


def _template_fallback(
    platform: str,
    title_draft: str,
    description_draft: str,
    constraints: dict,
) -> dict:
    title_limit = constraints.get("title_max_chars", 100)
    desc_limit = constraints.get("description_max_chars", 2000)

    title = _clean_title(title_draft.strip())[:title_limit]
    context = description_draft.strip()
    has_context = bool(context) and context.lower() != title_draft.strip().lower()

    if platform == "youtube":
        base = context if has_context else title
        desc = base + "\n\nLike & subscribe for more content like this."
        desc = desc[:desc_limit]
    elif platform == "tiktok":
        desc = context[:200] if has_context else (title + " \U0001F525")
    elif platform == "instagram":
        base_desc = context if has_context else title
        if len(base_desc) > 125:
            cut = base_desc[:125].rsplit(" ", 1)[0]
            desc = cut + "\n\n" + base_desc[len(cut):].strip()
        else:
            desc = base_desc
        desc = desc[:desc_limit]
    else:
        desc = (context if has_context else title)[:desc_limit]

    return {
        "title": title,
        "title_options": _title_variants(title_draft, platform, title_limit),
        "description": desc,
    }


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

def _merge_admin_trend(trend_data: dict, admin_row) -> dict:
    """Merge admin-curated data into auto-fetched trend_data. Admin entries take priority."""
    merged = dict(trend_data)

    # top_tags: admin first, then auto-fetched — deduplicated
    if admin_row.top_tags:
        existing = merged.get("top_tags") or []
        seen: set = set()
        combined = []
        for t in (list(admin_row.top_tags) + list(existing)):
            if t not in seen:
                seen.add(t)
                combined.append(t)
        merged["top_tags"] = combined

    # title_patterns sub-dict
    patterns = dict(merged.get("title_patterns") or {})

    if admin_row.title_words:
        existing_words = patterns.get("common_words") or []
        seen = set()
        combined = []
        for w in (list(admin_row.title_words) + list(existing_words)):
            if w not in seen:
                seen.add(w)
                combined.append(w)
        patterns["common_words"] = combined

    if admin_row.title_starters:
        existing_starters = patterns.get("common_starters") or []
        seen = set()
        combined = []
        for s in (list(admin_row.title_starters) + list(existing_starters)):
            if s not in seen:
                seen.add(s)
                combined.append(s)
        patterns["common_starters"] = combined

    merged["title_patterns"] = patterns

    if admin_row.notes:
        merged["_admin_notes"] = admin_row.notes

    return merged


async def get_trending_hashtags(platform: str, category: str) -> list[str]:
    if platform == "youtube":
        tags = await youtube_data_service.get_trending_tags(category)
        if tags:
            return tags
    return _static_hashtags(platform, category)


def get_best_times_for_user(db: Session, user_id: str, platform: str) -> list[str]:
    history = _get_user_upload_history(db, user_id)
    return _best_upload_times(platform=platform, category="default", user_history=history)
