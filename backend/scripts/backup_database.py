#!/usr/bin/env python3
"""
Database Backup Script
اسکریپت پشتیبان‌گیری از دیتابیس
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from typing import Optional


def backup_postgres(
    db_name: str,
    db_user: str,
    db_password: str,
    db_host: str = "localhost",
    db_port: int = 5432,
    output_dir: str = "backups",
    compress: bool = True
) -> Optional[str]:
    """
    Backup PostgreSQL database
    
    Returns:
        Path to backup file or None if failed
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"neuropredict_db_{timestamp}.sql"
    backup_path = output_dir / backup_filename
    
    # Set password via environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    # pg_dump command
    cmd = [
        "pg_dump",
        "-h", db_host,
        "-p", str(db_port),
        "-U", db_user,
        "-d", db_name,
        "-F", "c",  # Custom format (compressed by default)
        "-f", str(backup_path)
    ]
    
    try:
        print(f"Creating backup: {backup_path}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Backup created successfully: {backup_path}")
        print(f"  Size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return str(backup_path)
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Backup failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print("✗ pg_dump not found. Please install PostgreSQL client tools.")
        return None


def restore_postgres(
    backup_file: str,
    db_name: str,
    db_user: str,
    db_password: str,
    db_host: str = "localhost",
    db_port: int = 5432
) -> bool:
    """
    Restore PostgreSQL database from backup
    
    Returns:
        True if successful, False otherwise
    """
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"✗ Backup file not found: {backup_file}")
        return False
    
    # Set password via environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    # pg_restore command
    cmd = [
        "pg_restore",
        "-h", db_host,
        "-p", str(db_port),
        "-U", db_user,
        "-d", db_name,
        "-c",  # Clean (drop) database objects before recreating
        str(backup_path)
    ]
    
    try:
        print(f"Restoring from backup: {backup_file}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✓ Database restored successfully")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Restore failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ pg_restore not found. Please install PostgreSQL client tools.")
        return False


def list_backups(backup_dir: str = "backups"):
    """List available backups"""
    backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        print(f"Backup directory not found: {backup_dir}")
        return
    
    backups = sorted(backup_dir.glob("neuropredict_db_*.sql"), reverse=True)
    
    if not backups:
        print("No backups found")
        return
    
    print(f"\nAvailable backups in {backup_dir}:")
    print("-" * 80)
    print(f"{'Filename':<50} {'Size':>15} {'Date':>15}")
    print("-" * 80)
    
    for backup in backups:
        size_mb = backup.stat().st_size / 1024 / 1024
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{backup.name:<50} {size_mb:>14.2f} MB {mtime.strftime('%Y-%m-%d %H:%M'):>15}")


def cleanup_old_backups(backup_dir: str = "backups", keep_days: int = 30):
    """Remove backups older than keep_days"""
    from datetime import timedelta
    
    backup_dir = Path(backup_dir)
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    backups = backup_dir.glob("neuropredict_db_*.sql")
    deleted = 0
    
    for backup in backups:
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        if mtime < cutoff_date:
            backup.unlink()
            deleted += 1
            print(f"Deleted old backup: {backup.name}")
    
    print(f"\n✓ Cleaned up {deleted} old backup(s)")


def main():
    parser = argparse.ArgumentParser(description='Database backup and restore utility')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--db-name', default=os.getenv('POSTGRES_DB', 'neuropredict_db'),
                       help='Database name')
    parser.add_argument('--db-user', default=os.getenv('POSTGRES_USER', 'postgres'),
                       help='Database user')
    parser.add_argument('--db-password', default=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                       help='Database password')
    parser.add_argument('--db-host', default=os.getenv('POSTGRES_HOST', 'localhost'),
                       help='Database host')
    parser.add_argument('--db-port', type=int, default=int(os.getenv('POSTGRES_PORT', '5432')),
                       help='Database port')
    parser.add_argument('--backup-file', help='Backup file path (for restore)')
    parser.add_argument('--output-dir', default='backups', help='Backup output directory')
    parser.add_argument('--keep-days', type=int, default=30,
                       help='Days to keep backups (for cleanup)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_postgres(
            db_name=args.db_name,
            db_user=args.db_user,
            db_password=args.db_password,
            db_host=args.db_host,
            db_port=args.db_port,
            output_dir=args.output_dir
        )
    
    elif args.action == 'restore':
        if not args.backup_file:
            print("✗ --backup-file is required for restore")
            sys.exit(1)
        
        confirm = input(f"⚠️  This will overwrite database {args.db_name}. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Restore cancelled")
            sys.exit(0)
        
        restore_postgres(
            backup_file=args.backup_file,
            db_name=args.db_name,
            db_user=args.db_user,
            db_password=args.db_password,
            db_host=args.db_host,
            db_port=args.db_port
        )
    
    elif args.action == 'list':
        list_backups(args.output_dir)
    
    elif args.action == 'cleanup':
        cleanup_old_backups(args.output_dir, args.keep_days)


if __name__ == "__main__":
    main()

