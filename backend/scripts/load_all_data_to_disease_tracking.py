#!/usr/bin/env python
"""
Script to load all synthetic and real data into disease tracking
This creates patients, medical records, and predictions from both datasets
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal, init_db
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.prediction import Prediction, DiseaseType, RiskLevel
from sqlalchemy import select


def calculate_risk_scores_from_diagnosis(diagnosis: str, mmse: float, moca: float, 
                                         amyloid_beta: float, tau_protein: float, 
                                         dopamine: float, hippocampal_volume: float) -> tuple:
    """
    Calculate risk scores based on diagnosis and biomarkers
    Returns: (alzheimer_risk, parkinson_risk, alzheimer_level, parkinson_level)
    """
    alzheimer_score = 0.0
    parkinson_score = 0.0
    
    if diagnosis == 'Alzheimer':
        alzheimer_score = 0.85
        if mmse < 20:
            alzheimer_score = 0.95
        elif mmse < 24:
            alzheimer_score = 0.80
        if tau_protein > 500 and amyloid_beta < 500:
            alzheimer_score = min(0.98, alzheimer_score + 0.1)
        if hippocampal_volume < 2500:
            alzheimer_score = min(0.98, alzheimer_score + 0.08)
    elif diagnosis == 'Parkinson':
        parkinson_score = 0.80
        if dopamine < 50:
            parkinson_score = 0.90
        elif dopamine < 70:
            parkinson_score = 0.75
        if mmse >= 26:
            parkinson_score = min(0.95, parkinson_score + 0.1)
    else:  # Normal
        alzheimer_score = 0.15
        parkinson_score = 0.12
        if mmse >= 28 and moca >= 26:
            alzheimer_score = 0.08
            parkinson_score = 0.05
    
    alzheimer_level = (
        RiskLevel.HIGH if alzheimer_score >= 0.66
        else RiskLevel.MEDIUM if alzheimer_score >= 0.33
        else RiskLevel.LOW
    )
    parkinson_level = (
        RiskLevel.HIGH if parkinson_score >= 0.66
        else RiskLevel.MEDIUM if parkinson_score >= 0.33
        else RiskLevel.LOW
    )
    
    return (alzheimer_score, parkinson_score, alzheimer_level, parkinson_level)


async def load_dataset(csv_path: str, dataset_name: str, session):
    """Load a single dataset into database"""
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return {"patients": 0, "records": 0, "predictions": 0, "skipped": 0}
    
    print(f"\n📊 Loading {dataset_name} from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} records from CSV")
    except Exception as e:
        print(f"   ❌ Error reading CSV: {e}")
        return {"patients": 0, "records": 0, "predictions": 0, "skipped": 0}
    
    patients_created = 0
    records_created = 0
    predictions_created = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            patient_id = str(row['patient_id'])
            
            # Check if patient already exists
            result = await session.execute(
                select(Patient).where(Patient.patient_id == patient_id)
            )
            patient = result.scalar_one_or_none()
            
            if patient:
                skipped += 1
                continue
            
            # Parse date of birth from age
            age = int(row['age'])
            dob = date(datetime.now().year - age, 1, 1)
            
            # Parse gender
            gender_str = str(row['gender']).lower()
            gender = Gender.MALE if gender_str == 'male' else Gender.FEMALE if gender_str == 'female' else Gender.OTHER
            
            # Create patient
            patient = Patient(
                patient_id=patient_id,
                first_name=f"Patient",
                last_name=patient_id.replace('PT_', ''),
                date_of_birth=dob,
                gender=gender,
                education_years=int(row.get('education_years', 12)) if pd.notna(row.get('education_years')) else None,
            )
            
            session.add(patient)
            await session.flush()
            patients_created += 1
            
            # Parse visit date
            try:
                visit_date = pd.to_datetime(row['visit_date'])
            except:
                visit_date = datetime.now()
            
            # Create medical record
            medical_record = MedicalRecord(
                patient_id=patient.id,
                visit_date=visit_date,
                visit_type="Initial",
                mmse_score=float(row['mmse_score']) if pd.notna(row['mmse_score']) else None,
                moca_score=float(row['moca_score']) if pd.notna(row['moca_score']) else None,
                memory_score=float(row['memory_score']) if pd.notna(row['memory_score']) else None,
                attention_score=float(row['attention_score']) if pd.notna(row['attention_score']) else None,
                executive_function_score=float(row['executive_function_score']) if pd.notna(row['executive_function_score']) else None,
                amyloid_beta=float(row['amyloid_beta']) if pd.notna(row['amyloid_beta']) else None,
                tau_protein=float(row['tau_protein']) if pd.notna(row['tau_protein']) else None,
                dopamine_level=float(row['dopamine_level']) if pd.notna(row['dopamine_level']) else None,
                apoe_e4_status=bool(int(row['apoe_e4_status'])) if pd.notna(row['apoe_e4_status']) else False,
                hippocampal_volume=float(row['hippocampal_volume']) if pd.notna(row['hippocampal_volume']) else None,
                cortical_thickness=float(row['cortical_thickness']) if pd.notna(row['cortical_thickness']) else None,
                ventricular_volume=float(row['ventricular_volume']) if pd.notna(row['ventricular_volume']) else None,
                white_matter_hyperintensities=float(row['white_matter_hyperintensities']) if pd.notna(row['white_matter_hyperintensities']) else None,
                brain_volume_total=float(row['brain_volume_total']) if pd.notna(row['brain_volume_total']) else None,
                clinical_notes=f"Imported from {dataset_name}: {row.get('diagnosis', 'Unknown')}",
            )
            
            session.add(medical_record)
            await session.flush()
            records_created += 1
            
            # Calculate risk scores
            diagnosis = str(row.get('diagnosis', 'Normal'))
            alzheimer_risk, parkinson_risk, alzheimer_level, parkinson_level = calculate_risk_scores_from_diagnosis(
                diagnosis,
                medical_record.mmse_score or 25,
                medical_record.moca_score or 24,
                medical_record.amyloid_beta or 600,
                medical_record.tau_protein or 200,
                medical_record.dopamine_level or 100,
                medical_record.hippocampal_volume or 3500
            )
            
            # Create prediction
            prediction = Prediction(
                patient_id=patient.id,
                disease_type=DiseaseType.BOTH,
                alzheimer_risk_score=alzheimer_risk,
                parkinson_risk_score=parkinson_risk,
                alzheimer_risk_level=alzheimer_level,
                parkinson_risk_level=parkinson_level,
                created_at=datetime.now(),
            )
            
            session.add(prediction)
            predictions_created += 1
            
            if (idx + 1) % 20 == 0:
                print(f"   Progress: {idx + 1}/{len(df)} records processed...")
                
        except Exception as e:
            print(f"   ⚠️ Error processing row {idx}: {e}")
            continue
    
    await session.commit()
    
    return {
        "patients": patients_created,
        "records": records_created,
        "predictions": predictions_created,
        "skipped": skipped
    }


async def main():
    """Main function"""
    print("=" * 70)
    print("Loading All Data to Disease Tracking")
    print("=" * 70)
    
    # Initialize database
    await init_db()
    
    # Paths to data files
    project_root = Path(__file__).parent.parent.parent
    synthetic_csv = project_root / 'data' / 'data' / 'csv' / 'sample_dataset_complete.csv'
    real_csv = project_root / 'data' / 'real_data' / 'csv' / 'real_dataset_complete.csv'
    
    total_stats = {
        "patients": 0,
        "records": 0,
        "predictions": 0,
        "skipped": 0
    }
    
    async with AsyncSessionLocal() as session:
        try:
            # Load synthetic data
            print("\n" + "=" * 70)
            print("1. Loading SYNTHETIC DATA")
            print("=" * 70)
            synthetic_stats = await load_dataset(synthetic_csv, "Synthetic Dataset", session)
            for key in total_stats:
                total_stats[key] += synthetic_stats[key]
            
            # Load real data
            print("\n" + "=" * 70)
            print("2. Loading REAL DATA")
            print("=" * 70)
            real_stats = await load_dataset(real_csv, "Real Dataset", session)
            for key in total_stats:
                total_stats[key] += real_stats[key]
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return
        finally:
            await session.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ SUMMARY")
    print("=" * 70)
    print(f"   Total Patients Created:     {total_stats['patients']}")
    print(f"   Total Medical Records:      {total_stats['records']}")
    print(f"   Total Predictions:          {total_stats['predictions']}")
    print(f"   Skipped (already exist):    {total_stats['skipped']}")
    print("=" * 70)
    print("\n🎉 All data loaded successfully into disease tracking!")
    print("   You can now view all indicators in the Disease Tracking Dashboard.")


if __name__ == "__main__":
    asyncio.run(main())

