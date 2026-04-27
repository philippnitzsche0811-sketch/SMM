# Implement a New Feature

You are helping implement a new feature in the SMM platform (FastAPI + Vue 3).

## Steps

1. **Clarify scope** — before writing any code, confirm:
   - What does the feature do from the user's perspective?
   - Which platforms does it affect (YouTube, TikTok, Instagram, or all)?
   - Is there a backend API change needed, or frontend only?

2. **Plan before coding** — list the files that will change and why. Show the user the plan and get confirmation before implementing.

3. **Backend first** — if an API endpoint is needed:
   - Add service logic in `backend/services/`
   - Add/extend router in `backend/routers/`
   - Register in `backend/main.py` if it's a new router
   - Add any new DB columns to the model

4. **Frontend second** — update or create:
   - Types in `frontend/src/types/`
   - API call in `frontend/src/services/api.ts`
   - Composable in `frontend/src/composables/` if logic is complex
   - Component/view in the appropriate folder

5. **Check for env variables** — if the feature needs new API keys or settings, add them to `.env.example` and `backend/config.py`

6. **Never implement half-finished code** — if a feature is large, split it into clear steps and complete each one fully.

## Current planned features (context)
- TikTok external data (trending hashtags, best upload times)
- AI title/description/hashtag generation (OpenAI, mockable)
- Upload time optimizer
- Complete Instagram Reels pipeline
