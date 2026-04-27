# Fix a Bug

You are helping fix a bug in the SMM platform (FastAPI backend + Vue 3 frontend).

## Steps

1. **Understand the bug first** — ask the user to describe what happens vs. what should happen, and which part of the app is affected (upload, auth, platform connection, etc.)

2. **Trace the code path** — follow the request from frontend (`api.ts` → composable → component) to backend (router → service → model). Read the relevant files before suggesting anything.

3. **Check the logs** — if the user hasn't shared error details, remind them to run:
   ```
   docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f backend
   ```

4. **Propose the fix** — show the exact file path and line numbers. Explain WHY the fix works, not just what it does.

5. **Verify before rebuild** — confirm the fix is complete and no other places reference the broken code.

6. **Remind the user** to test with Docker rebuild if frontend changed:
   ```
   docker-compose -f docker-compose.yml -f docker-compose.local.yml build --no-cache frontend
   ```
   Or for backend: `build --no-cache backend`

## Important
- Never guess — read the actual file before proposing a change
- Never suggest adding error-swallowing try/catch to hide a bug
- If the bug is in a platform service (tiktok_service.py, youtube_service.py), check the API docs before assuming it's a code error
