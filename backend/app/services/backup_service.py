"""
Backup & Disaster Recovery Service
"""
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
import json

from ..core.config import settings


class BackupService:
    """Service for backup and disaster recovery"""
    
    @staticmethod
    async def create_database_backup(
        backup_dir: str = "backups",
        backup_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create database backup using pg_dump"""
        if not backup_name:
            backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
        
        backup_path = Path(backup_dir) / backup_name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract database connection info from DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        db_url = settings.DATABASE_URL_SYNC
        # Parse URL (simplified - should use proper URL parsing)
        # For now, assuming standard format
        
        try:
            # Use pg_dump to create backup
            # In production, this should be done with proper credentials
            cmd = [
                "pg_dump",
                "-h", "localhost",  # Should be parsed from DATABASE_URL
                "-U", "postgres",    # Should be parsed from DATABASE_URL
                "-d", "neuropredict_db",  # Should be parsed from DATABASE_URL
                "-f", str(backup_path),
                "--format=custom",  # Custom format for better compression
                "--compress=9"
            ]
            
            # Execute backup (in production, use proper async subprocess)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "backup_path": None
                }
            
            backup_size = backup_path.stat().st_size
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "backup_size_bytes": backup_size,
                "created_at": datetime.utcnow().isoformat(),
                "database": "neuropredict_db",
                "type": "full"
            }
            
            metadata_path = backup_path.with_suffix('.json')
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "backup_size_bytes": backup_size,
                "created_at": metadata["created_at"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_path": None
            }
    
    @staticmethod
    async def restore_database_backup(backup_path: str) -> Dict[str, Any]:
        """Restore database from backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                "success": False,
                "error": "Backup file not found"
            }
        
        try:
            # Use pg_restore to restore backup
            cmd = [
                "pg_restore",
                "-h", "localhost",
                "-U", "postgres",
                "-d", "neuropredict_db",
                "--clean",  # Drop objects before recreating
                "--if-exists",
                str(backup_file)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
            
            return {
                "success": True,
                "restored_at": datetime.utcnow().isoformat(),
                "backup_path": backup_path
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def list_backups(backup_dir: str = "backups") -> List[Dict[str, Any]]:
        """List all available backups"""
        backup_path = Path(backup_dir)
        
        if not backup_path.exists():
            return []
        
        backups = []
        
        for backup_file in backup_path.glob("*.sql"):
            metadata_file = backup_file.with_suffix('.json')
            
            if metadata_file.exists():
                async with aiofiles.open(metadata_file, 'r') as f:
                    metadata = json.loads(await f.read())
                    backups.append(metadata)
            else:
                # Create metadata from file info
                backups.append({
                    "backup_name": backup_file.name,
                    "backup_path": str(backup_file),
                    "backup_size_bytes": backup_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "type": "unknown"
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    @staticmethod
    async def cleanup_old_backups(
        backup_dir: str = "backups",
        keep_days: int = 30
    ) -> Dict[str, Any]:
        """Clean up old backups"""
        backup_path = Path(backup_dir)
        cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
        
        deleted_count = 0
        deleted_size = 0
        
        for backup_file in backup_path.glob("*.sql"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                file_size = backup_file.stat().st_size
                backup_file.unlink()
                
                # Also delete metadata file
                metadata_file = backup_file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()
                
                deleted_count += 1
                deleted_size += file_size
        
        return {
            "deleted_count": deleted_count,
            "deleted_size_bytes": deleted_size,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    @staticmethod
    async def verify_backup(backup_path: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                "valid": False,
                "error": "Backup file not found"
            }
        
        # Check file size
        file_size = backup_file.stat().st_size
        if file_size == 0:
            return {
                "valid": False,
                "error": "Backup file is empty"
            }
        
        # Try to read backup header (pg_dump custom format)
        try:
            async with aiofiles.open(backup_file, 'rb') as f:
                header = await f.read(100)
                # Check for pg_dump custom format magic bytes
                if header.startswith(b'PGDMP'):
                    return {
                        "valid": True,
                        "format": "custom",
                        "file_size_bytes": file_size
                    }
                else:
                    return {
                        "valid": True,
                        "format": "plain",
                        "file_size_bytes": file_size
                    }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

