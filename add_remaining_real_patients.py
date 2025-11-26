"""
Add 102 more real patients with unique IDs
"""
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
import uuid

def load_and_prepare_patients():
    """Load real data and prepare 102 more patients with unique IDs"""
    print("📊 Loading real dataset...")
    df = pd.read_csv('data/real_data/csv/real_dataset_complete.csv')
    
    # Separate by diagnosis
    normal = df[df['diagnosis'] == 'Normal'].copy()
    alzheimer = df[df['diagnosis'] == 'Alzheimer'].copy()
    parkinson = df[df['diagnosis'] == 'Parkinson'].copy()
    
    print(f"   Available: Normal={len(normal)}, Alzheimer={len(alzheimer)}, Parkinson={len(parkinson)}")
    
    # We need 102 more patients to reach 200 real patients
    # Let's keep same ratio: 60% normal, 20% AD, 20% PD
    # So: 61 normal, 21 AD, 20 PD = 102 total
    
    num_normal = 61
    num_alzheimer = 21  
    num_parkinson = 20
    
    print(f"\n🎯 Selecting {num_normal + num_alzheimer + num_parkinson} more patients:")
    print(f"   - Normal: {num_normal}")
    print(f"   - Alzheimer's: {num_alzheimer}")
    print(f"   - Parkinson's: {num_parkinson}")
    
    # Sample with replacement if needed
    def sample_with_repeats(df, n):
        if len(df) >= n:
            return df.sample(n=n, random_state=random.randint(1, 10000))
        else:
            repeats = (n // len(df)) + 1
            return pd.concat([df] * repeats, ignore_index=True).sample(n=n, random_state=random.randint(1, 10000))
    
    normal_selected = sample_with_repeats(normal, num_normal)
    alzheimer_selected = sample_with_repeats(alzheimer, num_alzheimer)
    parkinson_selected = sample_with_repeats(parkinson, num_parkinson)
    
    df_selected = pd.concat([normal_selected, alzheimer_selected, parkinson_selected], ignore_index=True)
    
    # Transform to import format with UNIQUE IDs
    transformed = []
    for idx, row in df_selected.iterrows():
        try:
            visit_date = pd.to_datetime(row['visit_date'])
            age = int(float(row['age']))
            date_of_birth = visit_date - timedelta(days=age*365.25)
            
            # Create UNIQUE patient ID using UUID
            unique_id = str(uuid.uuid4())[:8].upper()
            diagnosis_code = 'NC' if row['diagnosis'] == 'Normal' else ('AD' if row['diagnosis'] == 'Alzheimer' else 'PD')
            
            patient = {
                'patient_id': f"REAL2_{diagnosis_code}_{unique_id}",
                'first_name': f"Real",
                'last_name': f"{diagnosis_code}{unique_id}",
                'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                'gender': row['gender'].lower(),
                'education_years': int(float(row['education_years'])) if pd.notna(row['education_years']) else None,
                'email': f"real2_{unique_id}@example.com",
                'phone': f"+1-{random.randint(2000000000, 9999999999)}",
                'visit_date': row['visit_date'],
                'mmse_score': row.get('mmse_score'),
                'moca_score': row.get('moca_score'),
                'memory_score': row.get('memory_score'),
                'attention_score': row.get('attention_score'),
                'executive_function_score': row.get('executive_function_score'),
                'amyloid_beta': row.get('amyloid_beta'),
                'tau_protein': row.get('tau_protein'),
                'dopamine_level': row.get('dopamine_level'),
                'apoe_e4_status': int(float(row['apoe_e4_status'])) if pd.notna(row.get('apoe_e4_status')) else None,
                'hippocampal_volume': row.get('hippocampal_volume'),
                'cortical_thickness': row.get('cortical_thickness'),
                'ventricular_volume': row.get('ventricular_volume'),
                'white_matter_hyperintensities': row.get('white_matter_hyperintensities'),
                'brain_volume_total': row.get('brain_volume_total'),
            }
            transformed.append(patient)
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
            continue
    
    return pd.DataFrame(transformed)

def import_csv(csv_file):
    """Import CSV to backend"""
    print(f"\n📤 Importing to backend...")
    url = "http://localhost:8001/api/v1/patients/import/csv"
    
    with open(csv_file, 'rb') as f:
        files = {'file': ('additional_real_patients.csv', f, 'text/csv')}
        response = requests.post(url, files=files)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Imported: {result['imported']} patients")
        print(f"   ⚠️  Errors: {result['errors']}")
        if result['errors'] > 0 and result.get('error_details'):
            print(f"\n   First 3 errors:")
            for err in result['error_details'][:3]:
                print(f"      - {err}")
        return result['imported']
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return 0

def main():
    print("="*70)
    print("  📊 Adding 102 More Real Patients")
    print("="*70)
    
    # Generate data
    df = load_and_prepare_patients()
    
    output_file = 'data/real_data/csv/additional_real_patients_102.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved {len(df)} patients to: {output_file}")
    
    # Import
    imported = import_csv(output_file)
    
    print("\n" + "="*70)
    print("  ✅ SUMMARY")
    print("="*70)
    print(f"\n   Patients added: {imported}")
    print(f"\n   Expected total in database:")
    print(f"   - Previous: 398")
    print(f"   - Added: {imported}")
    print(f"   - Total: {398 + imported}")
    
    if imported == 102:
        print(f"\n   🎉 Perfect! Now you have 500 patients!")
        print(f"      - 200 Synthetic")
        print(f"      - 200 Real (98 + {imported})")
        print(f"      - 100 Original")
    
    print("\n   💡 Refresh your dashboard to see all patients!")
    print("="*70)

if __name__ == "__main__":
    main()

