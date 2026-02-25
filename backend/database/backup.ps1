# database/backup.ps1
param(
    [string]$EnvFile = ".env.db"
)

Write-Host "[INFO] Creating encrypted backup..." -ForegroundColor Cyan

# Load environment variables from .env.db
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.+)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Variable -Name $key -Value $value -Scope Script
        }
    }
} else {
    Write-Host "[ERROR] .env.db file not found!" -ForegroundColor Red
    exit 1
}

# Configuration
$BACKUP_DIR = ".\database\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR\socialhub_$TIMESTAMP.sql"

# Create backup directory
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

Write-Host "Creating database dump..." -ForegroundColor Yellow

# Create database dump using docker exec
docker exec socialhub-db-secure pg_dump -U $POSTGRES_USER $POSTGRES_DB | Out-File -FilePath $BACKUP_FILE -Encoding UTF8

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database dump created: $BACKUP_FILE" -ForegroundColor Green
    
    # Compress with 7-Zip (if available) or .NET compression
    if (Get-Command 7z -ErrorAction SilentlyContinue) {
        Write-Host "Compressing with 7-Zip..." -ForegroundColor Yellow
        7z a -p"$BACKUP_ENCRYPTION_PASSWORD" -mhe=on "$BACKUP_FILE.7z" $BACKUP_FILE
        Remove-Item $BACKUP_FILE
        Write-Host "[OK] Encrypted backup created: $BACKUP_FILE.7z" -ForegroundColor Green
    } else {
        # Use .NET compression
        Write-Host "Compressing with .NET (install 7-Zip for encryption)..." -ForegroundColor Yellow
        Compress-Archive -Path $BACKUP_FILE -DestinationPath "$BACKUP_FILE.zip"
        Remove-Item $BACKUP_FILE
        Write-Host "[WARN] Backup compressed but NOT encrypted: $BACKUP_FILE.zip" -ForegroundColor Yellow
        Write-Host "[TIP] Install 7-Zip for encrypted backups: https://www.7-zip.org/" -ForegroundColor Cyan
    }
    
    # Keep only last 7 backups
    Get-ChildItem $BACKUP_DIR -Filter "socialhub_*.sql.*" | 
        Sort-Object CreationTime -Descending | 
        Select-Object -Skip 7 | 
        Remove-Item -Force
    
    Write-Host "[OK] Backup complete!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backup failed!" -ForegroundColor Red
    exit 1
}

