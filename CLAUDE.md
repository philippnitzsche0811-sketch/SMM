# SMM – Social Media Management Platform

## What this app does
Central hub for uploading videos to YouTube, TikTok, and Instagram from one interface.
Users connect their accounts via OAuth, then upload once and the app posts to all selected platforms.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, APScheduler |
| Frontend | Vue 3, TypeScript, PrimeVue 3, Pinia |
| Database | PostgreSQL |
| Auth | JWT (30-day tokens) + OAuth2 per platform |
| Infrastructure | Docker Compose (3 services: postgres, backend, frontend) |
| Deployment | Synology NAS — push to git, server pulls and restarts |
| AI / Optimizer | OpenAI API (mockable via `AI_MOCK_MODE=true` in .env) |

---

## Project Structure

```
SMM/
├── backend/
│   ├── main.py              ← FastAPI app, router registration, APScheduler
│   ├── config.py            ← All settings loaded from .env
│   ├── models/
│   │   ├── database.py      ← DB init (SQLAlchemy), SessionLocal
│   │   ├── user.py          ← User model
│   │   └── video.py         ← Video model
│   ├── routers/
│   │   ├── auth.py          ← /api/auth/* (login, register, verify email)
│   │   ├── upload.py        ← /api/upload/* (main upload endpoint)
│   │   ├── youtube.py       ← /api/youtube/*
│   │   ├── tiktok.py        ← /api/tiktok/*
│   │   ├── instagram.py     ← /api/instagram/*
│   │   └── user.py          ← /api/user/*
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── video_service.py ← Core upload orchestration
│   │   ├── tiktok_service.py   ← TikTok v2 API (FILE_UPLOAD method)
│   │   ├── youtube_service.py
│   │   ├── instagram_service.py
│   │   ├── encryption_service.py ← OAuth token encryption at rest
│   │   ├── email_service.py
│   │   └── user_service.py
│   └── utils/
│       ├── auth.py          ← JWT helpers
│       └── utils.py
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── UploadView.vue   ← 3-step wizard: select → metadata → platforms
│       │   ├── ConnectView.vue  ← Platform OAuth connect
│       │   ├── DashboardView.vue
│       │   └── auth/
│       ├── components/
│       │   ├── upload/          ← DragDropZone, VideoMetaForm, PlatformSelector
│       │   ├── connect/         ← InstagramConnect, TikTokConnect, YouTubeConnect
│       │   └── platform/
│       ├── stores/
│       │   ├── authStore.ts     ← JWT, user state
│       │   └── platformStore.ts ← Connected platforms state
│       ├── composables/
│       │   ├── useUpload.ts     ← Upload logic
│       │   └── useAuth.ts
│       ├── services/
│       │   └── api.ts           ← All API calls (Axios)
│       └── types/
│           ├── user.types.ts
│           ├── video.types.ts
│           └── platform.types.ts
├── docker compose.yml
├── docker compose.local.yml     ← Local dev overrides
├── docker compose.prod.yml
└── deploy-synology.ps1
```

---

## Development Workflow

**Where things run:**
- Claude Code + VS Code edit files on Windows (`C:\Users\Philipp\SMM`)
- All testing happens on the **Linux server (Synology NAS)** — git push to deploy, then test there
- Server uses `docker compose` (space) — the old `docker-compose` hyphen binary is not installed


```powershell
# Start local dev environment
docker compose -f docker compose.yml -f docker compose.local.yml up -d

# Stop
docker compose -f docker compose.yml -f docker compose.local.yml down

# Rebuild after code changes (frontend only — backend auto-reloads in local mode)
docker compose -f docker compose.yml -f docker compose.local.yml build --no-cache frontend

# NOTE: In local dev, backend/  is mounted as a volume with --reload,
# so Python changes apply instantly. Only rebuild if you change requirements.txt or Dockerfile.
docker compose -f docker compose.yml -f docker compose.local.yml build --no-cache backend

# View logs — service names: postgres, backend, frontend
docker compose -f docker compose.yml -f docker compose.local.yml logs -f backend

# Deploy to Synology
./deploy-synology.ps1
```

---

## Key API Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/verify-email
POST   /api/auth/resend-verification
POST   /api/auth/forgot-password
POST   /api/auth/reset-password
POST   /api/auth/change-password
GET    /api/auth/me
PATCH  /api/auth/me
DELETE /api/auth/me

POST   /api/upload/upload_video          ← main upload (multipart/form-data)
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

---

## Current State (as of April 2026)

| Feature | Status |
|---|---|
| Auth (register, login, email verify) | Working |
| YouTube upload | Working (6/day limit for unverified apps) |
| TikTok upload | Implemented, needs external data integration |
| Instagram upload | In progress |
| Optimizer router | Registered in main.py, needs implementation |
| Upload wizard (frontend) | Working (3-step: file → metadata → platforms) |
| Token encryption | Working (encryption_service.py) |
| Scheduled cleanup | Working (unverified accounts removed after 2h) |

---

## Planned Features (in order of priority)

1. **TikTok external data** — trending hashtags, best posting times, creator analytics via TikTok API
2. **AI title/description/hashtag generator** — OpenAI API, uses video metadata + platform context
3. **Upload time optimizer** — combines platform data, personal upload history, video analysis
4. **Complete Instagram pipeline** — Reels publishing via Graph API
5. **Security hardening** — rate limiting, input validation audit, token refresh flows

---

## TikTok API Notes

- Base URL: `https://open.tiktokapis.com`
- Upload: v2 API, FILE_UPLOAD method, single-chunk for small files
- Privacy levels: `SELF_ONLY` | `MUTUAL_FOLLOW_FRIENDS` | `PUBLIC_TO_EVERYONE`
- Caption max: 2200 chars
- Credentials: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` in .env
- Callback: `/api/tiktok/oauth/callback`

---

## Coding Conventions

- **Backend**: snake_case, async functions where I/O is involved, follow existing service pattern (each platform has its own `_service.py`)
- **Frontend**: Vue Composition API (`<script setup>`), TypeScript, Pinia for global state, PrimeVue components
- **No new dependencies** without checking existing ones first
- **Never commit** `.env`, `.env.production`, or any file with credentials
- **Always verify** file changes are correct before suggesting a Docker rebuild

---

## Known Issues / Gotchas

- Frontend routes use `/api/upload/video` — NOT `/api/video` (causes 404)
- YouTube token refresh is auto-handled in youtube_service.py
- TikTok `publish_id` from upload init must be saved to check status later
- OpenAI calls can be mocked: set `AI_MOCK_MODE=true` in .env for development
- Database URL must include `?sslmode=require` for production Synology deployment

---

## Environment Variables

See `.env.example` for all required variables. Key ones:
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — must be strong random string in production
- `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET`
- `OPENAI_API_KEY` — for AI features (optional with mock mode)
- `ENCRYPTION_KEY` — for OAuth token encryption
- `DEBUG=false` in production
