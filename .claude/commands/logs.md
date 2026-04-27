# Show Docker Logs

Show the user the correct Docker log command for the service they need.

## Usage
User types: `/logs backend` or `/logs frontend` or `/logs` (all)

## Commands

**All services:**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f
```

**Backend only (most useful for debugging API errors):**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f backend
```

**Frontend:**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f frontend
```

**Database (service is named 'postgres', not 'db'):**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f postgres
```

**Last 50 lines only (useful for quick check):**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs --tail=50 backend
```

## What to look for
- `❌` or `ERROR` lines indicate failures
- `✅` lines confirm successful operations  
- TikTok upload errors often show the full API response body
- JWT errors appear as `401 Unauthorized` in backend logs
