# Show Docker Logs

Show the user the correct Docker log command for the service they need.

## Usage
User types: `/logs backend` or `/logs frontend` or `/logs` (all)

## Commands

**All services:**
```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f
```

**Backend only (most useful — shows upload mock output, API errors, auth issues):**
```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f backend
```

**Frontend:**
```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f frontend
```

**Database:**
```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f postgres
```

**Last 50 lines:**
```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs --tail=50 backend
```

## What to look for
- `[MOCK] ✅` — upload mock ran successfully (UPLOAD_MOCK_MODE=true)
- `❌` or `ERROR` — something failed
- `✅` — successful real operation
- `[MOCK]` lines — mock mode active, no real API calls were made
- `401 Unauthorized` — JWT or OAuth token issue
- `422 Unprocessable` — request validation error (check frontend payload)

## Local URLs
- Backend Swagger: http://localhost:8001/docs
- Frontend: http://localhost:8080
