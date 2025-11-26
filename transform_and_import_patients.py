import pandas as pd
import requests
from datetime import datetime, timedelta
import io

def transform_csv_for_import(input_csv_path):
    """Transform the CSV to match the patient import format"""
    print(f"Reading CSV: {input_csv_path}")
    df = pd.read_csv(input_csv_path)
    
    print(f"Found {len(df)} records")
    
    # Create a new DataFrame with required columns
    transformed_data = []
    
    for _, row in df.iterrows():
        try:
            # Calculate date_of_birth from age and visit_date
            visit_date = pd.to_datetime(row['visit_date'])
            age = int(float(row['age']))
            date_of_birth = visit_date - timedelta(days=age*365.25)
            
            # Create patient record
            patient = {
                'patient_id': row['patient_id'],
                'first_name': row['patient_id'].split('_')[0],  # Use first part as first name
                'last_name': row['patient_id'].split('_')[-1],   # Use last part as last name
                'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                'gender': row['gender'].lower(),
                'education_years': int(float(row['education_years'])) if pd.notna(row['education_years']) else None,
                'email': f"{row['patient_id'].lower()}@example.com",
                'phone': f"+1-{hash(row['patient_id']) % 9000000000 + 1000000000}",
                
                # Medical data for medical records (optional columns)
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
            
            transformed_data.append(patient)
            
        except Exception as e:
            print(f"Error processing row {row['patient_id']}: {str(e)}")
            continue
    
    return pd.DataFrame(transformed_data)

def import_patients_csv(csv_file_path):
    """Import patients from transformed CSV"""
    print(f"\n📤 Uploading CSV to backend...")
    url = "http://localhost:8001/api/v1/patients/import/csv"
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': ('patients.csv', f, 'text/csv')}
            response = requests.post(url, files=files)
            
        if response.status_code == 201:
            result = response.json()
            print(f"\n✅ Import Successful!")
            print(f"   - Imported: {result['imported']} patients")
            print(f"   - Errors: {result['errors']}")
            
            if result.get('imported_patients'):
                print(f"\n📋 Sample imported patients:")
                for patient in result['imported_patients'][:5]:
                    print(f"   - {patient['name']} (ID: {patient['patient_id']})")
            
            if result.get('error_details') and result['errors'] > 0:
                print(f"\n⚠️ Sample errors:")
                for error in result['error_details'][:3]:
                    print(f"   - {error}")
            
            return True
        else:
            print(f"\n❌ Import Failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    input_file = "data/real_data/csv/real_dataset_complete.csv"
    output_file = "data/real_data/csv/patients_for_import.csv"
    
    print("="*60)
    print("  Patient Data Import Tool")
    print("="*60)
    
    # Transform CSV
    df_transformed = transform_csv_for_import(input_file)
    
    # Save transformed CSV
    df_transformed.to_csv(output_file, index=False)
    print(f"\n✅ Transformed CSV saved to: {output_file}")
    print(f"   Total records: {len(df_transformed)}")
    
    # Import to backend
    success = import_patients_csv(output_file)
    
    if success:
        print("\n🎉 All done! Patients imported successfully.")
    else:
        print("\n❌ Import failed. Please check the errors above.")

