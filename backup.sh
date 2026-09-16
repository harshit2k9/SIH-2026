#!/bin/bash

# Configuration
CONTAINER_NAME="dms_postgres"
DB_USER="admin"
DB_NAME="app_db"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.sql"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Run pg_dump inside the docker container
echo "Creating backup for $DB_NAME..."
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME --clean --if-exists > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "Backup successfully created at: $BACKUP_FILE"
else
  echo "Backup failed!"
  exit 1
fi