# TikTok API Research & Implementation

Use this when working on TikTok features — uploading, analytics, trending data, or OAuth.

## Current TikTok setup in this project
- Service file: `backend/services/tiktok_service.py`
- Router: `backend/routers/tiktok.py`
- API base: `https://open.tiktokapis.com`
- API version: v2
- Upload method: FILE_UPLOAD (single chunk for small files)
- OAuth callback: `/api/tiktok/oauth/callback`
- Credentials: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` in .env

## Key TikTok API endpoints to know about
- Upload init: `POST /v2/post/publish/inbox/video/init/`
- Upload status: `POST /v2/post/publish/status/fetch/`
- User info: `GET /v2/user/info/`
- Creator info (posting constraints): `POST /v2/post/publish/creator_info/query/`
- Video list: `POST /v2/video/list/`

## Before implementing any TikTok feature
1. Check if the access_token is available and not expired
2. Check the `creator_info` endpoint — it returns what the user is allowed to post (privacy levels, duet/stitch/comment settings)
3. TikTok API requires the `fields` query parameter for most GET endpoints

## Common TikTok errors
- `access_token_invalid` — token expired, need re-auth via OAuth
- `scope_not_authorized` — app doesn't have required permission scope
- `spam_risk_too_many_posts` — posting too frequently, back off

## Research prompt for Perplexity
When you need up-to-date TikTok API documentation, use the Perplexity prompt in the project notes.
