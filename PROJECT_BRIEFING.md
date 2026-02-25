# Social Media Management Platform - Project Brief

## Project Overview
Multi-platform video upload manager for YouTube, TikTok, and Instagram.

Tech Stack:
- Backend: Python/FastAPI
- Frontend: Vue 3, PrimeVue
- Infrastructure: Docker Compose, PostgreSQL

---

## Project Structure

SMM/
+-- frontend  # Vue 3 Frontend
|   +-- src  # Source Code
|   |   +-- views  # Vue Pages
|   |   |   +-- auth
|   |   |   +-- UploadView.vue
|   |   |   +-- UploadsView.vue
|   |   |   +-- SettingsView.vue
|   |   |   +-- PlatformsView.vue
|   |   |   +-- DashboardView.vue
|   |   |   +-- ConnectView.vue
|   |   +-- utils
|   |   |   +-- validators.ts
|   |   |   +-- formatters.ts
|   |   +-- types
|   |   |   +-- video.types.ts
|   |   |   +-- user.types.ts
|   |   |   +-- platform.types.ts
|   |   +-- stores  # Pinia Stores
|   |   |   +-- platformStore.ts
|   |   |   +-- authStore.ts
|   |   +-- services  # Business Logic
|   |   |   +-- api.ts
|   |   +-- router
|   |   |   +-- index.ts
|   |   +-- composables
|   |   |   +-- useUpload.ts
|   |   |   +-- useAuth.ts
|   |   +-- components  # Vue Components
|   |   |   +-- video
|   |   |   +-- upload  # Platform Uploads
|   |   |   +-- platform
|   |   |   +-- layout
|   |   |   +-- dashboard
|   |   |   +-- connect
|   |   |   +-- auth
|   |   +-- assets
|   |   |   +-- styles
|   |   |   +-- images
|   |   +-- main.ts
|   |   +-- env.d.ts
|   |   +-- App.vue
|   +-- public
|   |   +-- vite.svg
|   +-- vite.config.ts
|   +-- tsconfig.node.json
|   +-- tsconfig.json
|   +-- README.md
|   +-- package-lock.json
|   +-- package.json
|   +-- nginx.conf
|   +-- index.html
|   +-- Dockerfile
|   +-- .gitignore
|   +-- .dockerignore
+-- backend  # FastAPI Backend
|   +-- utils
|   |   +-- utils.py
|   |   +-- auth.py
|   |   +-- __init__.py
|   +-- tokens
|   +-- services  # Business Logic
|   |   +-- youtube_service.py
|   |   +-- video_service.py
|   |   +-- user_service.py
|   |   +-- token_storage.py
|   |   +-- tiktok_service.py
|   |   +-- instagram_service.py
|   |   +-- file_service.py
|   |   +-- encryption_service.py
|   |   +-- email_service.py
|   |   +-- auth_service.py
|   |   +-- __init__.py
|   +-- routers  # API Routes
|   |   +-- youtube.py
|   |   +-- user.py
|   |   +-- upload.py
|   |   +-- tiktok.py
|   |   +-- static_pages.py
|   |   +-- instagram.py
|   |   +-- auth.py
|   |   +-- __init__.py
|   +-- models  # Database Models
|   |   +-- video.py
|   |   +-- user.py
|   |   +-- database.py
|   |   +-- __init__.py
|   +-- migrations
|   |   +-- 001_migrate_to_encrypted.py
|   +-- logs
|   +-- database
|   |   +-- ssl
|   |   +-- init-scripts
|   |   |   +-- 02-create-tables.sql
|   |   |   +-- 01-extensions.sql
|   |   |   +-- 00-create-users.sh
|   |   +-- backups
|   |   +-- postgresql.conf
|   |   +-- pg_hba.conf
|   |   +-- generate_keys.ps1
|   |   +-- geneate-keys.sh
|   |   +-- backup.sh
|   |   +-- backup.ps1
|   +-- data
|   +-- alembic
|   |   +-- versions
|   +-- requirements.txt
|   +-- README.md
|   +-- migrate.py
|   +-- main.py
|   +-- Dockerfile
|   +-- config.py
|   +-- .gitignore
|   +-- .dockerignore
+-- tree-clean.ps1
+-- structure-clean.txt
+-- start-local.ps1
+-- PROJECT_BRIEFING.md
+-- docker-compose.yml
+-- docker-compose.prod.yml
+-- docker-compose.local.yml
+-- deploy-synology.ps1
+-- .gitignore
+-- .env.production
+-- .env.example

## Core Features

- YouTube Integration
- TikTok Integration
- Instagram Integration
- Video Upload Management

---

## Key API Endpoints

Upload:
- POST /api/upload/upload_video

Video Management:
- GET /api/upload/video/{id}
- GET /api/upload/videos/user/{userId}
- PATCH /api/upload/video/{id}
- DELETE /api/upload/video/{id}

Platform Auth:
- POST /api/youtube/connect
- POST /api/tiktok/connect
- POST /api/instagram/connect

---

## Development Commands

Start:
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

Stop:
docker-compose -f docker-compose.yml -f docker-compose.local.yml down

Rebuild Frontend:
docker-compose -f docker-compose.yml -f docker-compose.local.yml build --no-cache frontend

Logs:
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f [service]

---

## Common Issues

Frontend 404:
- Check paths use /api/upload/video not /api/video
- Clear browser cache
- Rebuild with --no-cache

YouTube upload fails:
- Token expired: Auto-refresh implemented
- Upload limit: 6 videos/day for unverified apps

---

## Working Guidelines

- Be concise and direct
- Use code blocks
- Show exact file paths
- Verify before rebuild

---

## Important Files

Backend:
- backend/main.py
- backend/routers/upload.py
- backend/services/video_service.py

Frontend:
- frontend/src/services/api.ts
- frontend/src/views/DashboardView.vue

---


Remember: Always verify file changes before rebuilds!

