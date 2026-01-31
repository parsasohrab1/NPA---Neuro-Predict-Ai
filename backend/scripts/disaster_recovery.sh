#!/bin/bash
# Disaster Recovery Script
# برای بازیابی از فاجعه

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$SCRIPT_DIR/../backups}"
LOG_FILE="${LOG_FILE:-$SCRIPT_DIR/../logs/dr.log}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root for full system recovery"
fi

log "=========================================="
log "NeuroPredict-AI Disaster Recovery"
log "=========================================="

# Step 1: Verify backup availability
log "Step 1: Verifying backup availability..."
if [ ! -d "$BACKUP_DIR" ]; then
    error "Backup directory not found: $BACKUP_DIR"
fi

LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/neuropredict_db_*.sql 2>/dev/null | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    error "No backup files found in $BACKUP_DIR"
fi

success "Latest backup found: $LATEST_BACKUP"

# Step 2: Stop services
log "Step 2: Stopping services..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.prod.yml down || warning "Failed to stop docker-compose services"
fi

# Step 3: Restore database
log "Step 3: Restoring database..."
python3 "$SCRIPT_DIR/backup_database.py" restore \
    --backup-file "$LATEST_BACKUP" \
    --db-name "${POSTGRES_DB:-neuropredict_db}" \
    --db-user "${POSTGRES_USER:-postgres}" \
    --db-password "${POSTGRES_PASSWORD}" \
    --db-host "${POSTGRES_HOST:-localhost}" \
    --db-port "${POSTGRES_PORT:-5432}"

if [ $? -eq 0 ]; then
    success "Database restored successfully"
else
    error "Database restore failed"
fi

# Step 4: Verify database
log "Step 4: Verifying database..."
# Add verification queries here

# Step 5: Start services
log "Step 5: Starting services..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.prod.yml up -d
    success "Services started"
fi

# Step 6: Health check
log "Step 6: Performing health check..."
sleep 10
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "failed")
if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    success "Health check passed"
else
    warning "Health check failed - manual verification required"
fi

log "=========================================="
log "Disaster Recovery Completed"
log "=========================================="
log "Recovery Time: $(date)"
log "Backup Used: $LATEST_BACKUP"
log "=========================================="

