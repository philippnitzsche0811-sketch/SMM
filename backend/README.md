# 🎥 Social Media Upload API

Ein professionelles Backend für das automatisierte Hochladen von Videos auf YouTube, TikTok und Instagram.

## ✨ Features

- 🎬 **Multi-Platform Support**: YouTube, TikTok, Instagram Reels
- 🔐 **OAuth-Integration**: Sichere Authentifizierung für alle Plattformen
- 👥 **Multi-User-Support**: Verwaltet mehrere User gleichzeitig
- 📦 **Persistente Speicherung**: User-Credentials werden gespeichert
- 🚀 **Asynchron**: Schnelle Performance mit FastAPI
- 🐳 **Docker-Ready**: Einfaches Deployment
- 📝 **Logging**: Umfangreiches Error-Tracking

## 📁 Projektstruktur

```
Backend_V1/
├── main.py                    # FastAPI Hauptanwendung
├── config.py                  # Zentrale Konfiguration
├── upload_youtube.py          # YouTube Upload Service
├── upload_tiktok.py           # TikTok Upload Service
├── upload_instagram.py        # Instagram Upload Service
├── services/
│   ├── user_service.py       # User-Verwaltung
│   ├── file_service.py       # File-Handling
│   ├── token_storage.py
│   └── __init__.py
├── routers/
│   ├── instagram.py       
│   ├── staic_pages.py       
│   ├── tiktok.py
│   ├── upload.py       
│   ├── user.py       
│   ├── youtube.py
│   └── __init__.py
├── utils/
│   ├── utils.py              # Hilfsfunktionen
│   └── __init__.py
├── requirements.txt          # Python Dependencies
├── Dockerfile               # Docker Container
├── .env.example            # Beispiel-Konfiguration
├── .env
└── README.md              # Diese Datei
```

## 🚀 Installation

### Voraussetzungen

- Python 3.11+
- pip
- Docker (optional)

### 1. Repository klonen

```bash
git clone <your-repo>
cd Backend_V1
```

### 2. Virtual Environment erstellen

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. Konfiguration

```bash
cp .env.example .env
```

Fülle die `.env` Datei mit deinen API-Credentials:

```bash
TIKTOK_CLIENT_KEY=dein_key
TIKTOK_CLIENT_SECRET=dein_secret
INSTAGRAM_APP_ID=dein_id
INSTAGRAM_APP_SECRET=dein_secret
```

### 5. Server starten

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API ist nun verfügbar unter: `http://localhost:8000`

## 🐳 Docker Deployment

```bash
# Image bauen
docker build -t social-media-api .

# Container starten
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/tokens:/app/tokens \
  --name social-media-api \
  social-media-api
```

## 📖 API Endpoints

### Health Check

```http
GET /health
```

### YouTube Authentifizierung

```http
POST /connect_youtube
Content-Type: multipart/form-data

user_id: string
client_secrets_file: file (JSON)
```

### TikTok OAuth Callback

```http
GET /tiktok_oauth_callback?code={code}&state={user_id}
```

### Video Upload

```http
POST /upload_video
Content-Type: multipart/form-data

user_id: string
video: file
title: string
description: string
tags: string (komma-getrennt)
privacy_status: string (private/public/unlisted)
platforms: string (youtube,tiktok,instagram)
```

### User Status

```http
GET /user/{user_id}/status
```

### Plattform trennen

```http
DELETE /user/{user_id}/disconnect/{platform}
```

## 🔑 API-Credentials beschaffen

### YouTube

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt
3. Aktiviere YouTube Data API v3
4. Erstelle OAuth 2.0 Credentials
5. Lade die `client_secret.json` herunter

### TikTok

1. Registriere dich bei [TikTok for Developers](https://developers.tiktok.com/)
2. Erstelle eine App
3. Aktiviere "Content Posting API"
4. Kopiere Client Key und Client Secret

### Instagram

1. Erstelle eine App im [Meta for Developers](https://developers.facebook.com/)
2. Füge Instagram Graph API hinzu
3. Konvertiere deinen Account zu Business/Creator
4. Kopiere App ID und App Secret

## 🧪 Testing

```bash
# Einzelne Endpoints testen
curl http://localhost:8000/health

# Interaktive API-Dokumentation
open http://localhost:8000/docs
```

## 🛠️ Entwicklung

### Logging

Alle wichtigen Events werden geloggt:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("✅ Erfolg!")
logger.error("❌ Fehler!")
```

### Error Handling

Alle Exceptions werden zentral behandelt und liefern strukturierte Error-Responses.

### File Cleanup

Temporäre Dateien werden automatisch gelöscht - auch bei Fehlern.

## 📝 Verbesserungen gegenüber V1

### ✅ Sicherheit
- ❌ **Alt**: API-Keys hardcoded im Code
- ✅ **Neu**: Environment Variables (.env)

### ✅ Daten-Persistenz
- ❌ **Alt**: User-Daten nur im RAM
- ✅ **Neu**: JSON-basierte Speicherung

### ✅ Fehlerbehandlung
- ❌ **Alt**: Keine try-catch Blöcke
- ✅ **Neu**: Umfangreiches Error Handling

### ✅ Code-Organisation
- ❌ **Alt**: Alles in einer Datei
- ✅ **Neu**: Saubere Modul-Struktur

### ✅ Logging
- ❌ **Alt**: Nur print() Statements
- ✅ **Neu**: Professional Logging

### ✅ File-Handling
- ❌ **Alt**: Keine Cleanup-Garantie
- ✅ **Neu**: Automatisches Cleanup mit finally

### ✅ Docker
- ❌ **Alt**: Root-User, kein Health Check
- ✅ **Neu**: Non-root User, Multi-stage Build, Health Check

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Permission denied" (Docker)
```bash
chmod -R 755 temp/ data/ tokens/
```

### YouTube Token abgelaufen
```bash
rm tokens/youtube_token.pkl
# Nochmal authentifizieren
```

## 🤝 Contributing

Pull Requests sind willkommen! Für größere Änderungen öffne bitte zuerst ein Issue.

## 📄 Lizenz

MIT License

## 📧 Support

Bei Fragen oder Problemen öffne ein Issue auf GitHub.