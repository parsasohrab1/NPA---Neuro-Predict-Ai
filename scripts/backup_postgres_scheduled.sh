#!/usr/bin/env bash
# Scheduled PostgreSQL backup + retention cleanup for NeuroPredict-AI.
# Usage (from repo root, with pg_dump on PATH):
#   ./scripts/backup_postgres_scheduled.sh
# Environment:
#   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
#   KEEP_DAYS (default 14)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEEP_DAYS="${KEEP_DAYS:-14}"
OUT_DIR="${BACKUP_DIR:-$ROOT/backups/db}"
mkdir -p "$OUT_DIR"

export POSTGRES_DB="${POSTGRES_DB:-neuropredict_db}"
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"

cd "$ROOT/backend"
python scripts/backup_database.py backup --output-dir "$OUT_DIR"
python scripts/backup_database.py cleanup --output-dir "$OUT_DIR" --keep-days "$KEEP_DAYS"

echo "Backup + retention complete. Output: $OUT_DIR"
