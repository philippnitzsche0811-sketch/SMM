# 🎥 Social Media Manager Frontend

Ein modernes Vue.js Frontend für den Social Media Manager - Upload Videos auf YouTube, TikTok und Instagram.

## ✨ Features

- 🎬 **Multi-Platform Upload**: Gleichzeitiger Upload zu mehreren Plattformen
- 🎨 **Modernes UI**: PrimeVue Components mit Custom Design
- 📱 **Responsive**: Funktioniert perfekt auf Desktop und Mobile
- 🔐 **Authentifizierung**: Login/Register mit Token-Management
- 📊 **Progress Tracking**: Echtzeit Upload-Fortschritt
- 🎯 **TypeScript**: Vollständige Type-Safety
- ⚡ **Vite**: Blitzschnelle Entwicklung

## 🚀 Installation

### 1. Repository klonen

```bash
git clone <your-repo>
cd frontend
```

### 2. Dependencies installieren

```bash
npm install
```

### 3. Environment Variables

```bash
cp .env.example .env
```

Bearbeite `.env` und setze deine Backend-URL:

```env
VITE_API_URL=http://localhost:8000
```

### 4. Development Server starten

```bash
npm run dev
```

Die App läuft auf: `http://localhost:3000`

## 📁 Projektstruktur

```
frontend/
├── public/                    # Statische Assets
├── src/
│   ├── assets/               # Styles, Images
│   │   └── styles/
│   │       └── main.css      # Global Styles
│   ├── components/           # Vue Components
│   │   ├── auth/            # Login, Register
│   │   ├── connect/         # Platform Connection
│   │   └── upload/          # Upload Components
│   ├── composables/         # Composition API
│   │   ├── useAuth.ts
│   │   └── useUpload.ts
│   ├── router/              # Vue Router
│   │   └── index.ts
│   ├── services/            # API Services
│   │   └── api.ts
│   ├── stores/              # Pinia Stores
│   │   ├── authStore.ts
│   │   └── platformStore.ts
│   ├── types/               # TypeScript Types
│   │   ├── user.types.ts
│   │   ├── video.types.ts
│   │   └── platform.types.ts
│   ├── utils/               # Helper Functions
│   │   ├── validators.ts
│   │   └── formatters.ts
│   ├── views/               # Page Components
│   │   ├── LoginView.vue
│   │   ├── ConnectView.vue
│   │   └── UploadView.vue
│   ├── App.vue              # Root Component
│   └── main.ts              # Entry Point
├── index.html               # HTML Entry
├── package.json             # Dependencies
├── vite.config.ts           # Vite Config
├── tsconfig.json            # TypeScript Config
└── README.md                # Diese Datei
```

## 🔧 Scripts

```bash
# Development Server
npm run dev

# Production Build
npm run build

# Preview Production Build
npm run preview

# Type Check
npm run type-check
```

## 🎨 Tech Stack

- **Framework**: Vue 3 (Composition API)
- **UI Library**: PrimeVue 3.50
- **State Management**: Pinia 2.1
- **Routing**: Vue Router 4
- **HTTP Client**: Axios
- **Build Tool**: Vite 5
- **Language**: TypeScript 5

## 📖 Verwendung

### 1. Anmeldung

Registriere einen neuen Account oder melde dich mit bestehenden Zugangsdaten an.

### 2. Plattformen verbinden

Verbinde deine Social Media Accounts:
- **YouTube**: Lade deine Client Secret JSON hoch
- **TikTok**: OAuth-Flow
- **Instagram**: OAuth-Flow

### 3. Video hochladen

1. Wähle ein Video (Drag & Drop oder File Picker)
2. Füge Titel, Beschreibung und Tags hinzu
3. Wähle die Plattformen aus
4. Klicke auf "Hochladen"

## 🔌 Backend Integration

Das Frontend kommuniziert mit dem Backend über REST API:

- **Base URL**: `http://localhost:8000`
- **Auth**: Bearer Token in Authorization Header
- **Endpoints**:
  - `POST /auth/login` - Login
  - `POST /auth/register` - Registrierung
  - `POST /connect_youtube` - YouTube verbinden
  - `POST /upload_video` - Video hochladen
  - `GET /user/:id/status` - User Status

## 🐛 Troubleshooting

### "Module not found"

```bash
npm install
```

### "Cannot find module '@/...'"

Prüfe `tsconfig.json` - Path Mapping sollte korrekt sein:

```json
"paths": {
  "@/*": ["./src/*"]
}
```

### CORS Fehler

Stelle sicher, dass dein Backend CORS erlaubt:

```python
# Backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 Entwicklung

### Neue Route hinzufügen

1. Erstelle Component in `src/views/`
2. Füge Route in `src/router/index.ts` hinzu
3. Füge Navigation hinzu

### Neuen API Endpoint hinzufügen

1. Füge Funktion in `src/services/api.ts` hinzu
2. Füge Types in `src/types/` hinzu
3. Nutze in Component/Composable

## 🚀 Deployment

### Production Build

```bash
npm run build
```

Die Build-Dateien befinden sich in `dist/`.

### Deployment auf Vercel/Netlify

1. Pushe Code zu Git Repository
2. Verbinde Repository mit Vercel/Netlify
3. Setze Environment Variables
4. Deploy!

## 📄 Lizenz

MIT License

## 👨‍💻 Autor

Dein Name

## 🤝 Contributing

Pull Requests sind willkommen!
