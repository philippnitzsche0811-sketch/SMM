# SMM Platform — Roadmap

Dieses File trackt geplante Features. Neue Einträge nach einer Planungssession einfach hier anfügen.
Status: `[ ]` geplant · `[~]` in Arbeit · `[x]` fertig

---

## Upload Flow

- [x] Simple Upload — Wizard mit AI-Optimierung + Schedule (Jetzt / Datum / Gruppe)
- [x] Smart Upload — Claude Vision Analyse (Frames → Feedback) + Schedule
- [x] Upload Groups — Density-Scheduling-Algorithmus, Auto-Upload zum besten Zeitpunkt
- [ ] **Video Editing (Phase 2)** — FFmpeg-Effekte direkt im Smart-Upload-Flow (Cuts, Zooms, Speed, Fade). Wurde bewusst rausgeschoben; Analyse-Infrastruktur steht bereits.
- [ ] **Drag-to-Reorder in Upload Groups** — Reihenfolge der Videos per Drag & Drop ändern, Schedule wird danach neu berechnet.
- [ ] **Thumbnail-Auswahl** — Frame aus dem Video wählen oder eigenes Bild hochladen, wird beim Upload als Custom Thumbnail gesetzt (YouTube unterstützt das bereits via API).

---

## Analytics & Daten

- [ ] **TikTok Creator Analytics** — Trending Hashtags, beste Upload-Zeiten und Reichweiten-Daten direkt aus der TikTok API ziehen (Endpoint: `/open.tiktokapis.com/v2/research/`).
- [ ] **Analytics Dashboard** — Views, Likes, Kommentare pro Video aggregiert über alle Plattformen. Erfordert periodischen Abruf via APScheduler + eigene `video_stats` Tabelle.
- [ ] **Upload-Zeit-Optimizer verbessern** — Aktuell nur auf `PLATFORM_PEAK_TIMES` + eigener History. Erweiterung: echte Plattform-Daten einbeziehen (YouTube Analytics API, TikTok Insights).

---

## KI / Optimierung

- [ ] **AI-Kontext aus Video-Transcript** — Whisper (lokal oder OpenAI) transkribiert das Audio, Transcript wird als Kontext für Titel/Tag-Generierung genutzt statt manueller Beschreibung.
- [ ] **Batch-Optimierung für Upload Groups** — Alle Videos einer Gruppe auf einmal durch Claude schicken, Titel/Tags konsistent über die Serie halten (z. B. einheitlicher Hashtag-Set).

---

## Sicherheit & Stabilität

- [ ] **Rate Limiting** — FastAPI-Middleware (z. B. `slowapi`) für Auth-Endpoints und Upload-Endpoints. Besonders `/api/auth/login` und `/api/upload/simple`.
- [ ] **Input Validation Audit** — Alle Form-Inputs auf Länge, Format und gefährliche Inhalte prüfen. Aktuell nur grundlegende Pydantic-Validierung.
- [ ] **Token Refresh Flow** — YouTube Refresh-Token läuft automatisch, TikTok/Instagram noch nicht. Unified Refresh-Job via APScheduler.

---

## UX / Frontend

- [ ] **Upload-Status Push Notifications** — Browser-Notification wenn ein geplanter Upload fertig ist (oder fehlschlägt). Service Worker + Backend-Webhook.
- [ ] **Mobile Optimierung Upload Groups** — Gruppenansicht auf kleinen Screens verbessern (aktuell funktionesfähig aber nicht optimiert).
- [ ] **Dark/Light Mode Toggle** — Aktuell hard-coded Dark Mode. PrimeVue Theme-Switch + CSS Variable Swap.

---

## Infrastruktur

- [ ] **Cloudflare R2 für Video-Storage** — Temp-Files aktuell lokal im Container. R2-Integration ist teilweise vorbereitet (`config.py` hat R2-Vars), aber Upload-Flow nutzt noch lokalen `/app/temp`.
- [ ] **Deployment-Automatisierung** — `deploy-synology.ps1` existiert, aber kein Health-Check nach Deploy. Rollback-Mechanismus wäre gut.
