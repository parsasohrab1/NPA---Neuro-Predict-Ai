#!/bin/bash
# Automated Backup Scheduler
# برای استفاده با cron: 0 2 * * * /path/to/backup_scheduler.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$SCRIPT_DIR/../backups}"
LOG_FILE="${LOG_FILE:-$SCRIPT_DIR/../logs/backup.log}"

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting scheduled backup..."

# Daily backup
python3 "$SCRIPT_DIR/backup_database.py" backup \
    --output-dir "$BACKUP_DIR" \
    --db-name "${POSTGRES_DB:-neuropredict_db}" \
    --db-user "${POSTGRES_USER:-postgres}" \
    --db-password "${POSTGRES_PASSWORD}" \
    --db-host "${POSTGRES_HOST:-localhost}" \
    --db-port "${POSTGRES_PORT:-5432}" 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    log "✓ Backup completed successfully"
    
    # Cleanup old backups (keep 30 days)
    python3 "$SCRIPT_DIR/backup_database.py" cleanup \
        --output-dir "$BACKUP_DIR" \
        --keep-days 30 2>&1 | tee -a "$LOG_FILE"
else
    log "✗ Backup failed!"
    # Send alert (configure email/Slack notification here)
    exit 1
fi

log "Backup process completed"

