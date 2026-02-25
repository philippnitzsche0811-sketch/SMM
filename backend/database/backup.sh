#!/bin/bash

# Load environment
source .env.db

BACKUP_DIR="./database/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/socialhub_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

echo "📦 Creating encrypted backup..."

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Dump database
docker exec socialhub-db-secure pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_FILE}

# Encrypt backup
gpg --batch --yes --passphrase="${BACKUP_ENCRYPTION_PASSWORD}" \
    --symmetric --cipher-algo AES256 \
    --output ${ENCRYPTED_FILE} ${BACKUP_FILE}

# Remove unencrypted backup
rm ${BACKUP_FILE}

# Keep only last 7 backups
ls -t ${BACKUP_DIR}/*.gpg | tail -n +8 | xargs -r rm

echo "✅ Encrypted backup created: ${ENCRYPTED_FILE}"
