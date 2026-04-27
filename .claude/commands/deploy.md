# Pre-Deploy Checklist

Run this before pushing to the Synology server.

## Checklist

Check each item in the current code changes:

### Security
- [ ] No `.env`, `.env.production`, or credentials committed (`git diff --name-only`)
- [ ] No `DEBUG=true` hardcoded anywhere (should come from env)
- [ ] No API keys or secrets in source files
- [ ] JWT_SECRET is not the default value

### Code Quality  
- [ ] No `console.log()` left in frontend files (use properly or remove)
- [ ] No `print()` debug statements in backend
- [ ] No `TODO` that was supposed to be done before this deploy

### API / Backend
- [ ] New endpoints are registered in `backend/main.py`
- [ ] New settings are added to `backend/config.py` AND `.env.example`
- [ ] Database model changes have a migration if needed

### Frontend
- [ ] API base URL uses env variable, not hardcoded localhost
- [ ] New routes are added to `frontend/src/router/index.ts`

### Docker
- [ ] `docker-compose.yml` doesn't have local dev settings leaked in
- [ ] New environment variables are documented in `.env.example`

## Deploy command
```powershell
./deploy-synology.ps1
```

## After deploy — verify
```
docker-compose logs -f backend   # check for startup errors
curl https://your-domain/health  # should return {"status": "healthy"}
```
