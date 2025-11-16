import os
import secrets
from pathlib import Path

TEMPLATE = """ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY={secret}

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/neuropredict_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@postgres:5432/neuropredict_db

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

BACKUP_DIR=backups
BACKUP_OFFSITE_DIR=backups_offsite
BACKUP_FULL_INTERVAL_HOURS=24
BACKUP_WAL_INTERVAL_MINUTES=15
BACKUP_RETENTION_DAYS=14
BACKUP_VERIFY_WEEKLY=true
BACKUP_VERIFY_INTERVAL_DAYS=7
"""

def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        print(f"{env_path} already exists. Nothing to do.")
        return
    # generate a secure secret
    secret = secrets.token_urlsafe(48)
    env_content = TEMPLATE.format(secret=secret)
    env_path.write_text(env_content, encoding="utf-8")
    print(f"Wrote {env_path}")


if __name__ == "__main__":
    main()


