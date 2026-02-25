# database/generate-keys.ps1
Write-Host "[INFO] Generating secure keys for SocialHub Database..." -ForegroundColor Cyan

# Function to generate random string
function Get-RandomString {
    param([int]$Length)
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    return [Convert]::ToBase64String($bytes) -replace '[+/=]', '' | Select-Object -First $Length
}

# Function to generate hex string
function Get-RandomHex {
    param([int]$Bytes)
    $randomBytes = New-Object byte[] $Bytes
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($randomBytes)
    return [BitConverter]::ToString($randomBytes) -replace '-', '' | ForEach-Object { $_.ToLower() }
}

# Generate PostgreSQL password (32 chars)
$POSTGRES_PASS = Get-RandomString -Length 32

# Generate encryption key (32 bytes hex = 64 chars)
$ENCRYPTION_KEY = Get-RandomHex -Bytes 32

# Generate backup password (32 chars)
$BACKUP_PASS = Get-RandomString -Length 32

# Get current date
$DATE = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create .env.db file
$envContent = @"
# Generated on $DATE
POSTGRES_USER=socialhub
POSTGRES_PASSWORD=$POSTGRES_PASS
POSTGRES_DB=socialhub_db
ENCRYPTION_KEY=$ENCRYPTION_KEY
BACKUP_ENCRYPTION_PASSWORD=$BACKUP_PASS
"@

$envContent | Out-File -FilePath ".env.db" -Encoding UTF8 -NoNewline

Write-Host "[OK] Keys generated and saved to .env.db" -ForegroundColor Green
Write-Host "[WARN] IMPORTANT: Backup this file securely!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Your PostgreSQL password: $POSTGRES_PASS" -ForegroundColor White
Write-Host "Your encryption key: $ENCRYPTION_KEY" -ForegroundColor White
Write-Host ""
Write-Host "Add ENCRYPTION_KEY to your main .env file:" -ForegroundColor Cyan
Write-Host "  ENCRYPTION_KEY=$ENCRYPTION_KEY" -ForegroundColor Gray

