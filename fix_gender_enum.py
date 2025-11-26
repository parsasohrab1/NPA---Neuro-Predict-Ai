"""
Fix gender enum values in database
Convert lowercase 'male', 'female', 'other' to uppercase 'MALE', 'FEMALE', 'OTHER'
"""
import sqlite3

DB_PATH = 'backend/neuropredict.db'

print("="*80)
print("  Fixing Gender Enum Values in Database")
print("="*80)
print()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current values
cursor.execute("SELECT DISTINCT gender FROM patients")
current_values = [row[0] for row in cursor.fetchall()]
print(f"Current gender values: {current_values}")
print()

# Update to uppercase
print("Updating gender values to uppercase...")

cursor.execute("UPDATE patients SET gender = 'MALE' WHERE LOWER(gender) = 'male'")
male_count = cursor.rowcount

cursor.execute("UPDATE patients SET gender = 'FEMALE' WHERE LOWER(gender) = 'female'")
female_count = cursor.rowcount

cursor.execute("UPDATE patients SET gender = 'OTHER' WHERE LOWER(gender) IN ('other', 'o')")
other_count = cursor.rowcount

conn.commit()

print(f"  Updated {male_count:,} patients to 'MALE'")
print(f"  Updated {female_count:,} patients to 'FEMALE'")
print(f"  Updated {other_count:,} patients to 'OTHER'")
print()

# Verify
cursor.execute("SELECT DISTINCT gender FROM patients")
new_values = [row[0] for row in cursor.fetchall()]
print(f"New gender values: {new_values}")
print()

conn.close()

print("="*80)
print("  SUCCESS! Gender values fixed")
print("="*80)
print()

