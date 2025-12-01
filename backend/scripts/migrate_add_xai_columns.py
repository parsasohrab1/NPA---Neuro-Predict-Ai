"""
Migration Script: Add XAI columns to data_fusion_reports table
این اسکریپت ستون‌های XAI را به جدول data_fusion_reports اضافه می‌کند
"""
import sqlite3
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent
db_path = project_root / "neuropredict.db"

def migrate_database():
    """Add missing XAI columns to data_fusion_reports table"""
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"📊 Opening database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(data_fusion_reports)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        print(f"\n📋 Existing columns: {len(existing_columns)}")
        
        # Columns to add
        columns_to_add = [
            ("xai_evidence", "JSON", "NULL"),
            ("xai_method", "VARCHAR(50)", "NULL"),
            ("has_xai_explanation", "INTEGER", "0")
        ]
        
        # Add missing columns
        added_count = 0
        for col_name, col_type, default_value in columns_to_add:
            if col_name not in existing_columns:
                print(f"\n➕ Adding column: {col_name} ({col_type})")
                
                # SQLite doesn't support default values in ALTER TABLE ADD COLUMN directly
                # We'll add the column first, then update existing rows if needed
                sql = f"ALTER TABLE data_fusion_reports ADD COLUMN {col_name} {col_type}"
                
                try:
                    cursor.execute(sql)
                    conn.commit()
                    
                    # Set default value for existing rows if needed
                    if default_value != "NULL":
                        update_sql = f"UPDATE data_fusion_reports SET {col_name} = {default_value} WHERE {col_name} IS NULL"
                        cursor.execute(update_sql)
                        conn.commit()
                    
                    print(f"   ✅ Column {col_name} added successfully")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"   ❌ Error adding {col_name}: {e}")
                    return False
            else:
                print(f"   ℹ️  Column {col_name} already exists, skipping")
        
        # Verify the changes
        print("\n🔍 Verifying changes...")
        cursor.execute("PRAGMA table_info(data_fusion_reports)")
        all_columns = {col[1] for col in cursor.fetchall()}
        
        missing = []
        for col_name, _, _ in columns_to_add:
            if col_name not in all_columns:
                missing.append(col_name)
        
        if missing:
            print(f"   ❌ Missing columns: {missing}")
            return False
        else:
            print(f"   ✅ All columns verified: {', '.join([c[0] for c in columns_to_add])}")
        
        print(f"\n✅ Migration completed successfully! ({added_count} columns added)")
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*80)
    print("  Database Migration: Add XAI Columns to data_fusion_reports")
    print("="*80)
    print("")
    
    success = migrate_database()
    
    print("")
    if success:
        print("="*80)
        print("  ✅ Migration Successful!")
        print("="*80)
        sys.exit(0)
    else:
        print("="*80)
        print("  ❌ Migration Failed!")
        print("="*80)
        sys.exit(1)

