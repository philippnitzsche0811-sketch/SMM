# Deploy to Synology DiskStation
Write-Host "Deploying to DiskStation (192.168.178.100)..." -ForegroundColor Cyan

# Build images
docker-compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml build

# Save images
docker save -o socialhub-backend.tar socialhub-backend:latest
docker save -o socialhub-frontend.tar socialhub-frontend:latest
docker save -o postgres:15-alpine postgres-db.tar

Write-Host "Images saved. Upload to DiskStation:" -ForegroundColor Yellow
Write-Host "1. Copy .env.production, docker-compose.yml, docker-compose.prod.yml"
Write-Host "2. Copy *.tar files"
Write-Host "3. SSH into DiskStation and run: docker-compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml up -d"
