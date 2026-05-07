# SMM – Social Media Management Platform

## What this app does
Central hub for uploading videos to YouTube, TikTok, and Instagram from one interface.
Users connect their accounts via OAuth, then upload once and the app posts to all selected platforms.

> **Roadmap & geplante Features** → [`ROADMAP.md`](./ROADMAP.md)
> Neue Features nach einer Planungssession dort eintragen. Format: `[ ]` geplant · `[~]` in Arbeit · `[x]` fertig.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, APScheduler |
| Frontend | Vue 3, TypeScript, PrimeVue 3, Pinia |
| Database | PostgreSQL 15 |
| Auth | JWT (30-day tokens) + OAuth2 per platform |
| Infrastructure | Docker Compose (3 services: postgres, backend, frontend) |
| Deployment | Synology NAS — push to git, server pulls and restarts |
| AI / Optimizer | OpenAI API (mockable via `AI_MOCK_MODE=true` in .env) |

---

## Local Development

### Ports (local)
| Service | URL | Notes |
|---|---|---|
| Frontend | http://localhost:8080 | Vue 3 app |
| Backend API | http://localhost:8001 | FastAPI, auto-reload |
| Backend Docs | http://localhost:8001/docs | Swagger UI |
| PostgreSQL | localhost:5433 | direct DB access |

Port 8000 is taken on this machine — local backend runs on **8001**.

### Start / Stop

```powershell
# Start
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d

# Stop
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml down

# Rebuild frontend (after code change — backend auto-reloads)
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml build --no-cache frontend

# Rebuild backend (only when requirements.txt or Dockerfile changes)
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml build --no-cache backend

# Logs
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f backend
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f frontend
```

### Mock Modes (both auto-enabled in local)

| Variable | Default local | Effect |
|---|---|---|
| `UPLOAD_MOCK_MODE=true` | ✅ enabled | Simulates TikTok/Instagram/YouTube uploads — no real API calls, detailed `[MOCK]` log output |
| `AI_MOCK_MODE=true` | ✅ enabled | Simulates OpenAI responses — no tokens consumed |

**UPLOAD_MOCK_MODE log output** (look for this in backend logs):
```
============================================================
[MOCK] TikTok Upload simuliert (UPLOAD_MOCK_MODE=true)
[MOCK] Caption: Mein Video...
[MOCK] Datei:   video.mp4 (12,345,678 bytes)
[MOCK] Privacy: SELF_ONLY
[MOCK] ✅ TikTok Upload erfolgreich (kein echter API-Call)
============================================================
```

### What can be tested locally
- ✅ Auth (register, login, email verify, password reset)
- ✅ Video upload UI (file → metadata → platforms wizard)
- ✅ Platform connection UI (OAuth flows — but redirect must point to correct URL)
- ✅ Upload flow end-to-end (with mock — logs show what would happen)
- ✅ AI content generation (mocked)
- ✅ Dashboard, video history
- ❌ Real TikTok/Instagram/YouTube upload (needs server with public URL for OAuth callback)
- ❌ Email delivery (needs SMTP configured; use real .env values)

### Deploy to Synology
```powershell
./deploy-synology.ps1
```
Server uses `docker compose` (space, not hyphen) — old `docker-compose` binary not installed there.

---

## Project Structure

```
SMM/
├── backend/
│   ├── main.py              ← FastAPI app, router registration, APScheduler
│   ├── config.py            ← All settings from .env (Settings class)
│   ├── models/
│   │   ├── database.py      ← SQLAlchemy init, SessionLocal, all models
│   │   ├── user.py          ← User model fields
│   │   └── video.py         ← VideoStatus enum
│   ├── routers/
│   │   ├── auth.py          ← /api/auth/*
│   │   ├── upload.py        ← /api/upload/* — main upload endpoint
│   │   ├── youtube.py       ← /api/youtube/*
│   │   ├── tiktok.py        ← /api/tiktok/*
│   │   ├── instagram.py     ← /api/instagram/*
│   │   └── user.py          ← /api/user/*
│   ├── services/
│   │   ├── video_service.py    ← Core upload orchestration (process_video_upload)
│   │   ├── tiktok_service.py   ← TikTok v2 API + UPLOAD_MOCK_MODE
│   │   ├── youtube_service.py  ← YouTube Data API + UPLOAD_MOCK_MODE
│   │   ├── instagram_service.py ← Instagram Graph API + UPLOAD_MOCK_MODE
│   │   ├── auth_service.py
│   │   ├── encryption_service.py ← OAuth token encryption at rest
│   │   ├── email_service.py
│   │   ├── file_service.py
│   │   └── user_service.py
│   └── utils/
│       ├── auth.py          ← JWT helpers
│       └── utils.py
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── UploadView.vue      ← 3-step wizard: file → metadata → platforms
│       │   ├── ConnectView.vue     ← Platform OAuth connect
│       │   └── DashboardView.vue
│       ├── components/
│       │   ├── upload/             ← DragDropZone, VideoMetaForm, PlatformSelector
│       │   └── connect/            ← InstagramConnect, TikTokConnect, YouTubeConnect
│       ├── stores/
│       │   ├── authStore.ts        ← JWT + user state
│       │   └── platformStore.ts    ← Connected platform state
│       ├── composables/
│       │   ├── useUpload.ts        ← Upload logic
│       │   └── useAuth.ts
│       └── services/
│           └── api.ts              ← All API calls (Axios)
├── docker-compose.yml
├── docker-compose.local.yml    ← Local overrides: ports, mock modes, volume mounts
├── docker-compose.prod.yml
└── deploy-synology.ps1
```

---

## Key API Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/verify-email
POST   /api/auth/forgot-password
POST   /api/auth/reset-password
POST   /api/auth/change-password
GET    /api/auth/me
PATCH  /api/auth/me
DELETE /api/auth/me

POST   /api/upload/upload_video    ← main upload (multipart/form-data)
GET    /api/upload/video/{id}
GET    /api/upload/videos/user/{userId}
PATCH  /api/upload/video/{id}
DELETE /api/upload/video/{id}

GET    /api/youtube/connect
GET    /api/tiktok/oauth/callback
GET    /api/instagram/callback

GET    /api/user/{id}
GET    /health
```

Swagger UI (local): http://localhost:8001/docs

---

## Upload Flow (video_service.py)

```
POST /api/upload/upload_video
  → save file to temp dir
  → create VideoModel (status=PENDING)
  → start BackgroundTask: process_video_upload()
    → for each platform in video.platforms:
        → call upload_to_{platform}() from router
          → router calls {platform}_service.{platform}_upload_video()
            → if UPLOAD_MOCK_MODE: log [MOCK] details and return fake result
            → else: real API call
        → save result/error to video.upload_results / video.errors
    → set final status: UPLOADED / PARTIAL / FAILED
```

---

## Coding Conventions

- **Backend**: snake_case, async where I/O involved, each platform has `{platform}_service.py`
- **Frontend**: Vue Composition API (`<script setup>`), TypeScript, Pinia for state, PrimeVue components
- **New settings**: always add to `backend/config.py` AND `.env.example`
- **New endpoints**: always register router in `backend/main.py`
- **No new dependencies** without checking existing ones first
- **Never commit** `.env`, `.env.production`, or credentials

---

## Agent Workflow

### Implementing a new feature
1. Read the relevant service + router files first
2. Plan: list files that change, confirm with user
3. Backend first (service → router → main.py → config.py + .env.example)
4. Frontend second (types → api.ts → composable → component/view)
5. Check mock mode: if feature involves external API, add `if settings.UPLOAD_MOCK_MODE:` branch
6. Test locally: rebuild if needed, check http://localhost:8001/docs for API, check logs

### Subagent patterns
- Use **Explore** agent for: "where is X defined", "which files reference Y"
- Use **Plan** agent before large features (3+ files changing)
- Read actual files before suggesting changes — never guess

### Finding things fast
- Platform upload logic: `backend/services/{platform}_service.py`
- API routes: `backend/routers/{platform}.py`
- Frontend API calls: `frontend/src/services/api.ts`
- Global state: `frontend/src/stores/`
- DB models: `backend/models/database.py`

---

## Current State

| Feature | Status |
|---|---|
| Auth (register, login, email verify) | Working |
| YouTube upload | Working (6/day limit for unverified apps) |
| TikTok upload | Working (needs connected account on server) |
| Instagram upload | Working (needs connected account on server) |
| Upload mock mode | Working — UPLOAD_MOCK_MODE=true in local |
| Upload wizard (frontend) | Working (3-step: file → metadata → platforms) |
| Token encryption | Working (encryption_service.py) |
| Scheduled cleanup | Working (unverified accounts removed after 2h) |
| AI content generation | Partial (needs OpenAI key or AI_MOCK_MODE=true) |

---

## Planned Features (priority order)

1. **TikTok external data** — trending hashtags, best posting times, creator analytics
2. **AI title/description/hashtag generator** — OpenAI, uses video metadata + platform context
3. **Upload time optimizer** — platform data + personal upload history
4. **Security hardening** — rate limiting, input validation audit, token refresh flows

---

## TikTok API Notes

- Base URL: `https://open.tiktokapis.com`
- Upload: v2 API, FILE_UPLOAD method, single-chunk for small files
- Privacy levels: `SELF_ONLY` | `MUTUAL_FOLLOW_FRIENDS` | `PUBLIC_TO_EVERYONE`
- Caption max: 2200 chars
- Credentials: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` in .env
- Callback: `/api/tiktok/oauth/callback`

---

## Known Issues / Gotchas

- Frontend routes use `/api/upload/video` — NOT `/api/video` (causes 404)
- YouTube token refresh is auto-handled in `youtube_service.py`
- TikTok `publish_id` from upload init must be saved to check status later
- Database URL needs `?sslmode=require` for Synology production deployment
- OAuth callbacks require public URL — cannot test full OAuth flow locally without tunneling
- `VITE_API_URL` is baked in at frontend build time — change requires frontend rebuild

---

## Environment Variables

See `.env.example` for all required variables. Key ones:
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — strong random string in production
- `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET`
- `OPENAI_API_KEY` — for AI features
- `ENCRYPTION_KEY` — for OAuth token encryption
- `AI_MOCK_MODE=true` — skip OpenAI calls in dev
- `UPLOAD_MOCK_MODE=true` — skip all platform API calls in dev
- `DEBUG=false` in production
