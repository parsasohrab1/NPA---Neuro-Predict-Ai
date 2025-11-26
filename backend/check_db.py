import sqlite3
import sys

try:
    conn = sqlite3.connect('neuropredict.db')
    cursor = conn.cursor()
    
    # Count total patients
    cursor.execute('SELECT COUNT(*) FROM patients')
    total = cursor.fetchone()[0]
    print(f'Total patients in database: {total}')
    
    if total > 0:
        # Get sample
        cursor.execute('SELECT patient_id, first_name, last_name FROM patients LIMIT 20')
        print(f'\nSample patients:')
        for row in cursor.fetchall():
            print(f'  - {row[0]}: {row[1]} {row[2]}')
        
        # Count by type
        cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id LIKE 'SYN_%'")
        synthetic = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id LIKE 'REAL_%'")
        real = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id NOT LIKE 'SYN_%' AND patient_id NOT LIKE 'REAL_%'")
        other = cursor.fetchone()[0]
        
        print(f'\nBreakdown:')
        print(f'  - Synthetic (SYN_*): {synthetic}')
        print(f'  - Real (REAL_*): {real}')
        print(f'  - Other: {other}')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)

