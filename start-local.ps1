# Start Local Development Environment
Write-Host "🚀 Starting SMM Local Development..." -ForegroundColor Green

# Docker Container starten
Write-Host "📦 Starting Docker containers..." -ForegroundColor Cyan
docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build

# Warte auf Backend
Write-Host "⏳ Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Status-Ausgabe
Write-Host ""
Write-Host "✅ SMM Platform is running!" -ForegroundColor Green
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "📊 Logs anzeigen: docker-compose logs -f" -ForegroundColor Gray
Write-Host "🛑 Stoppen: docker-compose down" -ForegroundColor Gray



