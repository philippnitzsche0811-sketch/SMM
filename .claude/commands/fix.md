# Fix a Bug

You are helping fix a bug in the SMM platform (FastAPI backend + Vue 3 frontend).

## Steps

1. **Understand the bug first** — ask what happens vs. what should happen, and which part of the app is affected (upload, auth, platform connection, etc.)

2. **Trace the code path** — follow the request:
   - Frontend: `api.ts` → composable → component
   - Backend: router → service → model
   - Read actual files before suggesting anything

3. **Check the logs** — if error details missing, run:
   ```powershell
   docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml logs -f backend
   ```
   Look for `❌` or `ERROR`. For upload issues, look for `[MOCK]` lines to confirm mock mode is active.

4. **Check the API directly** — Swagger UI at http://localhost:8001/docs lets you test endpoints without the frontend.

5. **Propose the fix** — show exact file path and line numbers. Explain WHY the fix works.

6. **Verify before rebuild** — confirm no other places reference the broken code.

7. **Rebuild if needed:**
   ```powershell
   # Frontend change:
   docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml build --no-cache frontend

   # Backend change (only for requirements.txt or Dockerfile changes — backend auto-reloads):
   docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml build --no-cache backend
   ```

## Important
- Never guess — read the actual file before proposing a change
- Never suggest adding try/catch to hide a bug
- If bug is in platform service (`tiktok_service.py` etc.), check whether `UPLOAD_MOCK_MODE=true` is active — if so, real API errors won't appear locally
- Platform OAuth errors always need the server (public URL required for callbacks)
