"""
Generate and import 400 patients:
- 200 synthetic patients (40 Alzheimer, 40 Parkinson, 120 Normal)
- 200 real patients (40 Alzheimer, 40 Parkinson, 120 Normal)
"""
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import random

def generate_synthetic_patients(num_normal=120, num_alzheimer=40, num_parkinson=40):
    """Generate synthetic patient data"""
    print(f"\n🔬 Generating synthetic data...")
    print(f"   - Normal: {num_normal}")
    print(f"   - Alzheimer's: {num_alzheimer}")
    print(f"   - Parkinson's: {num_parkinson}")
    
    patients = []
    patient_id = 1000  # Start from 1000 for synthetic
    
    # Generate Normal patients
    for i in range(num_normal):
        age = np.random.normal(50, 12)
        age = max(40, min(95, age))
        
        patient = {
            'patient_id': f'SYN_NC_{patient_id}',
            'first_name': f'Patient',
            'last_name': f'N{patient_id}',
            'date_of_birth': (datetime.now() - timedelta(days=age*365.25)).strftime('%Y-%m-%d'),
            'gender': random.choice(['male', 'female']),
            'education_years': int(np.random.normal(14, 4)),
            'email': f'syn_nc_{patient_id}@example.com',
            'phone': f'+1-{random.randint(1000000000, 9999999999)}',
            'visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            
            # Normal cognitive scores
            'mmse_score': float(np.random.normal(29, 1)),
            'moca_score': float(np.random.normal(28, 1.5)),
            'memory_score': float(np.random.normal(85, 10)),
            'attention_score': float(np.random.normal(80, 10)),
            'executive_function_score': float(np.random.normal(85, 10)),
            
            # Normal biomarkers
            'amyloid_beta': float(np.random.normal(700, 150)),
            'tau_protein': float(np.random.normal(200, 80)),
            'dopamine_level': float(np.random.normal(120, 20)),
            'apoe_e4_status': 1 if random.random() < 0.2 else 0,
            
            # Normal MRI features
            'hippocampal_volume': float(np.random.normal(4000, 300)),
            'cortical_thickness': float(np.random.normal(2.8, 0.2)),
            'ventricular_volume': float(np.random.normal(30000, 5000)),
            'white_matter_hyperintensities': float(np.random.gamma(2, 3)),
            'brain_volume_total': float(np.random.normal(1300000, 50000)),
        }
        patients.append(patient)
        patient_id += 1
    
    # Generate Alzheimer's patients
    for i in range(num_alzheimer):
        age = np.random.normal(75, 8)
        age = max(60, min(95, age))
        
        patient = {
            'patient_id': f'SYN_AD_{patient_id}',
            'first_name': f'Patient',
            'last_name': f'A{patient_id}',
            'date_of_birth': (datetime.now() - timedelta(days=age*365.25)).strftime('%Y-%m-%d'),
            'gender': random.choice(['male', 'female']),
            'education_years': int(np.random.normal(12, 4)),
            'email': f'syn_ad_{patient_id}@example.com',
            'phone': f'+1-{random.randint(1000000000, 9999999999)}',
            'visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            
            # Impaired cognitive scores
            'mmse_score': float(np.random.normal(20, 4)),
            'moca_score': float(np.random.normal(18, 4)),
            'memory_score': float(np.random.normal(45, 15)),
            'attention_score': float(np.random.normal(50, 15)),
            'executive_function_score': float(np.random.normal(40, 15)),
            
            # Alzheimer's biomarkers
            'amyloid_beta': float(np.random.normal(300, 100)),  # Low
            'tau_protein': float(np.random.normal(600, 150)),    # High
            'dopamine_level': float(np.random.normal(110, 25)),
            'apoe_e4_status': 1 if random.random() < 0.7 else 0,  # 70% positive
            
            # Alzheimer's MRI features
            'hippocampal_volume': float(np.random.normal(2500, 500)),  # Atrophy
            'cortical_thickness': float(np.random.normal(2.2, 0.3)),
            'ventricular_volume': float(np.random.normal(55000, 8000)),  # Enlarged
            'white_matter_hyperintensities': float(np.random.gamma(4, 5)),
            'brain_volume_total': float(np.random.normal(1100000, 70000)),
        }
        patients.append(patient)
        patient_id += 1
    
    # Generate Parkinson's patients
    for i in range(num_parkinson):
        age = np.random.normal(70, 10)
        age = max(50, min(95, age))
        
        patient = {
            'patient_id': f'SYN_PD_{patient_id}',
            'first_name': f'Patient',
            'last_name': f'P{patient_id}',
            'date_of_birth': (datetime.now() - timedelta(days=age*365.25)).strftime('%Y-%m-%d'),
            'gender': random.choice(['male', 'female']),
            'education_years': int(np.random.normal(13, 4)),
            'email': f'syn_pd_{patient_id}@example.com',
            'phone': f'+1-{random.randint(1000000000, 9999999999)}',
            'visit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            
            # Mild cognitive impairment
            'mmse_score': float(np.random.normal(26, 2)),
            'moca_score': float(np.random.normal(24, 3)),
            'memory_score': float(np.random.normal(70, 12)),
            'attention_score': float(np.random.normal(65, 12)),
            'executive_function_score': float(np.random.normal(60, 15)),
            
            # Parkinson's biomarkers
            'amyloid_beta': float(np.random.normal(650, 150)),
            'tau_protein': float(np.random.normal(250, 100)),
            'dopamine_level': float(np.random.normal(50, 25)),  # Low dopamine
            'apoe_e4_status': 1 if random.random() < 0.3 else 0,
            
            # Parkinson's MRI features
            'hippocampal_volume': float(np.random.normal(3500, 400)),
            'cortical_thickness': float(np.random.normal(2.6, 0.25)),
            'ventricular_volume': float(np.random.normal(38000, 6000)),
            'white_matter_hyperintensities': float(np.random.gamma(3, 4)),
            'brain_volume_total': float(np.random.normal(1250000, 60000)),
        }
        patients.append(patient)
        patient_id += 1
    
    df = pd.DataFrame(patients)
    print(f"   ✅ Generated {len(df)} synthetic patients")
    return df

def prepare_real_patients(csv_path, num_normal=120, num_alzheimer=40, num_parkinson=40):
    """Prepare real patient data with balanced distribution"""
    print(f"\n📊 Loading real data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Separate by diagnosis
    normal = df[df['diagnosis'] == 'Normal'].copy()
    alzheimer = df[df['diagnosis'] == 'Alzheimer'].copy()
    parkinson = df[df['diagnosis'] == 'Parkinson'].copy()
    
    print(f"   Available: Normal={len(normal)}, Alzheimer={len(alzheimer)}, Parkinson={len(parkinson)}")
    
    # Sample or repeat to get desired counts
    if len(normal) >= num_normal:
        normal_selected = normal.sample(n=num_normal, random_state=42)
    else:
        # Repeat if not enough
        repeats = (num_normal // len(normal)) + 1
        normal_selected = pd.concat([normal] * repeats, ignore_index=True).sample(n=num_normal, random_state=42)
    
    if len(alzheimer) >= num_alzheimer:
        alzheimer_selected = alzheimer.sample(n=num_alzheimer, random_state=42)
    else:
        repeats = (num_alzheimer // len(alzheimer)) + 1
        alzheimer_selected = pd.concat([alzheimer] * repeats, ignore_index=True).sample(n=num_alzheimer, random_state=42)
    
    if len(parkinson) >= num_parkinson:
        parkinson_selected = parkinson.sample(n=num_parkinson, random_state=42)
    else:
        repeats = (num_parkinson // len(parkinson)) + 1
        parkinson_selected = pd.concat([parkinson] * repeats, ignore_index=True).sample(n=num_parkinson, random_state=42)
    
    # Combine
    df_selected = pd.concat([normal_selected, alzheimer_selected, parkinson_selected], ignore_index=True)
    
    # Transform to import format
    transformed = []
    for idx, row in df_selected.iterrows():
        try:
            visit_date = pd.to_datetime(row['visit_date'])
            age = int(float(row['age']))
            date_of_birth = visit_date - timedelta(days=age*365.25)
            
            patient = {
                'patient_id': f"REAL_{row['patient_id']}",
                'first_name': row['patient_id'].split('_')[0],
                'last_name': row['patient_id'].split('_')[-1],
                'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                'gender': row['gender'].lower(),
                'education_years': int(float(row['education_years'])) if pd.notna(row['education_years']) else None,
                'email': f"{row['patient_id'].lower()}_real@example.com",
                'phone': f"+1-{hash(row['patient_id']) % 9000000000 + 1000000000}",
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
            print(f"   ⚠️ Error processing {row['patient_id']}: {str(e)}")
            continue
    
    df_transformed = pd.DataFrame(transformed)
    print(f"   ✅ Prepared {len(df_transformed)} real patients")
    print(f"      - Normal: {len(df_transformed[df_transformed['patient_id'].str.contains('NC')])}")
    print(f"      - Alzheimer: {len(df_transformed[df_transformed['patient_id'].str.contains('AD')])}")
    print(f"      - Parkinson: {len(df_transformed[df_transformed['patient_id'].str.contains('PD')])}")
    
    return df_transformed

def import_to_backend(csv_file_path, dataset_name):
    """Import CSV to backend"""
    print(f"\n📤 Uploading {dataset_name} to backend...")
    url = "http://localhost:8001/api/v1/patients/import/csv"
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': (f'{dataset_name}.csv', f, 'text/csv')}
            response = requests.post(url, files=files)
        
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Import successful!")
            print(f"      - Imported: {result['imported']} patients")
            print(f"      - Errors: {result['errors']}")
            
            if result.get('error_details') and result['errors'] > 0:
                print(f"      ⚠️ First 3 errors:")
                for error in result['error_details'][:3]:
                    print(f"         - {error}")
            
            return result['imported']
        else:
            print(f"   ❌ Import failed! Status: {response.status_code}")
            print(f"      Response: {response.text}")
            return 0
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return 0

def main():
    print("="*70)
    print("  📊 Patient Data Generation and Import Tool")
    print("="*70)
    print("\n🎯 Target: 400 patients total")
    print("   - 200 Synthetic (40 AD, 40 PD, 120 Normal)")
    print("   - 200 Real (40 AD, 40 PD, 120 Normal)")
    print("="*70)
    
    # Step 1: Generate synthetic data
    df_synthetic = generate_synthetic_patients(
        num_normal=120,
        num_alzheimer=40,
        num_parkinson=40
    )
    synthetic_file = 'data/real_data/csv/synthetic_patients_200.csv'
    df_synthetic.to_csv(synthetic_file, index=False)
    print(f"   💾 Saved to: {synthetic_file}")
    
    # Step 2: Prepare real data
    df_real = prepare_real_patients(
        'data/real_data/csv/real_dataset_complete.csv',
        num_normal=120,
        num_alzheimer=40,
        num_parkinson=40
    )
    real_file = 'data/real_data/csv/real_patients_200.csv'
    df_real.to_csv(real_file, index=False)
    print(f"   💾 Saved to: {real_file}")
    
    # Step 3: Import to backend
    print("\n" + "="*70)
    print("  📤 IMPORTING TO BACKEND")
    print("="*70)
    
    imported_synthetic = import_to_backend(synthetic_file, "synthetic_patients")
    imported_real = import_to_backend(real_file, "real_patients")
    
    # Summary
    print("\n" + "="*70)
    print("  ✅ IMPORT COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   - Synthetic patients imported: {imported_synthetic}")
    print(f"   - Real patients imported: {imported_real}")
    print(f"   - Total patients imported: {imported_synthetic + imported_real}")
    print(f"\n💡 Distribution per dataset:")
    print(f"   - Normal: 120 (60%)")
    print(f"   - Alzheimer's: 40 (20%)")
    print(f"   - Parkinson's: 40 (20%)")
    print("\n🎉 All done! Refresh your dashboard to see the patients.")
    print("="*70)

if __name__ == "__main__":
    main()

