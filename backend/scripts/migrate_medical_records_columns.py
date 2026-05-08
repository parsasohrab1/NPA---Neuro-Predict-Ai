"""
Migration Script: Add missing columns to medical_records table
Adds vital signs and other columns that may be missing from older databases.
"""
import sqlite3
import sys
from pathlib import Path

# Get project root (backend folder)
project_root = Path(__file__).parent.parent
db_path = project_root / "neuropredict.db"

# Columns to add if missing (name, sqlite_type)
COLUMNS_TO_ADD = [
    ("blood_pressure_systolic", "REAL"),
    ("blood_pressure_diastolic", "REAL"),
    ("temperature", "REAL"),
    ("heart_rate", "REAL"),
    ("respiratory_rate", "REAL"),
    ("oxygen_saturation", "REAL"),
    ("weight", "REAL"),
    ("height", "REAL"),
    ("bmi", "REAL"),
    ("blood_glucose", "REAL"),
    ("cholesterol_total", "REAL"),
]


def migrate_database():
    """Add missing columns to medical_records table"""
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return False

    print(f"Opening database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(medical_records)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        added_count = 0
        for col_name, col_type in COLUMNS_TO_ADD:
            if col_name not in existing_columns:
                print(f"Adding column: {col_name} ({col_type})")
                try:
                    cursor.execute(
                        f"ALTER TABLE medical_records ADD COLUMN {col_name} {col_type}"
                    )
                    conn.commit()
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"  Error: {e}")
                    return False

        print(f"Migration complete. Added {added_count} column(s).")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
