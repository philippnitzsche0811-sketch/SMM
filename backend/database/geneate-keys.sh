#!/bin/bash

echo "🔐 Generating secure keys for SocialHub Database..."

# Generate PostgreSQL password
POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

# Generate encryption key
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Generate backup password
BACKUP_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

# Create .env.db file
cat > .env.db << EOF
# Generated on $(date)
POSTGRES_USER=socialhub
POSTGRES_PASSWORD=${POSTGRES_PASS}
POSTGRES_DB=socialhub_db
ENCRYPTION_KEY=${ENCRYPTION_KEY}
BACKUP_ENCRYPTION_PASSWORD=${BACKUP_PASS}
EOF

echo "✅ Keys generated and saved to .env.db"
echo "⚠️  IMPORTANT: Backup this file securely!"
echo ""
echo "📋 Your PostgreSQL password: ${POSTGRES_PASS}"
echo "🔑 Your encryption key: ${ENCRYPTION_KEY}"
