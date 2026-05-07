# Implement a New Feature

You are helping implement a new feature in the SMM platform (FastAPI + Vue 3).

## Steps

1. **Clarify scope** — before writing any code, confirm:
   - What does the feature do from the user's perspective?
   - Which platforms are affected (YouTube, TikTok, Instagram, all)?
   - Backend API change needed, or frontend only?

2. **Read before writing** — use Explore/Grep to find relevant files. Never guess file paths.

3. **Plan before coding** — list all files that will change and why. Show the plan and get confirmation.

4. **Backend first** — if an API endpoint is needed:
   - Add service logic in `backend/services/`
   - Add/extend router in `backend/routers/`
   - Register router in `backend/main.py` if new
   - Add new settings to `backend/config.py` AND `.env.example`
   - If feature calls external API: add `if settings.UPLOAD_MOCK_MODE:` branch with log output

5. **Frontend second:**
   - Types in `frontend/src/types/`
   - API call in `frontend/src/services/api.ts`
   - Composable in `frontend/src/composables/` if logic is complex
   - Component/view in appropriate folder

6. **Test locally:**
   - Start: `docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d`
   - Backend auto-reloads; only rebuild frontend if template/build changes
   - Check http://localhost:8001/docs for API
   - Check http://localhost:8080 for frontend
   - Check logs: `docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f backend`
   - Confirm `[MOCK]` lines appear for upload features

## Mock mode pattern (for features calling external APIs)

```python
# In the service function, at the top:
if settings.UPLOAD_MOCK_MODE:
    logger.info("=" * 60)
    logger.info("[MOCK] FeatureName simuliert (UPLOAD_MOCK_MODE=true)")
    logger.info(f"[MOCK] Relevant param: {param}")
    logger.info("[MOCK] ✅ Erfolgreich (kein echter API-Call)")
    logger.info("=" * 60)
    return {"status": "ok", "mock": True, ...}
```

## Current planned features (context)
- TikTok external data (trending hashtags, best upload times)
- AI title/description/hashtag generation (OpenAI, mockable)
- Upload time optimizer
- Complete Instagram Reels pipeline
- Security hardening (rate limiting, input validation)
