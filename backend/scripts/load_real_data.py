#!/usr/bin/env python
"""
Script to load real data from CSV files into the database
This script loads data from data/real_data/csv/real_dataset_complete.csv
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, date
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal, init_db
from app.models.patient import Patient, Gender
from app.models.prediction import Prediction, DiseaseType, RiskLevel
from app.models.user import User
from sqlalchemy import select


def calculate_risk_level(score: float) -> RiskLevel:
    """Calculate risk level from score (0-1)"""
    if score >= 0.7:
        return RiskLevel.HIGH
    elif score >= 0.4:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def calculate_risk_score(diagnosis: str, mmse: float, moca: float, 
                        amyloid_beta: float, tau_protein: float, 
                        dopamine: float, hippocampal_volume: float) -> tuple:
    """
    Calculate risk scores based on diagnosis and biomarkers
    Returns: (alzheimer_score, parkinson_score)
    """
    alzheimer_score = 0.0
    parkinson_score = 0.0
    
    if diagnosis == 'Alzheimer':
        # Higher risk for Alzheimer
        alzheimer_score = 0.85
        # Lower MMSE/MoCA = higher risk
        if mmse < 20:
            alzheimer_score = 0.95
        elif mmse < 24:
            alzheimer_score = 0.80
        # High tau, low amyloid = AD pattern
        if tau_protein > 500 and amyloid_beta < 500:
            alzheimer_score = min(0.98, alzheimer_score + 0.1)
        # Hippocampal atrophy
        if hippocampal_volume < 2500:
            alzheimer_score = min(0.98, alzheimer_score + 0.08)
    elif diagnosis == 'Parkinson':
        # Higher risk for Parkinson
        parkinson_score = 0.80
        # Low dopamine = PD pattern
        if dopamine < 50:
            parkinson_score = 0.90
        elif dopamine < 70:
            parkinson_score = 0.75
        # MMSE usually preserved in PD
        if mmse >= 26:
            parkinson_score = min(0.95, parkinson_score + 0.1)
    else:  # Normal
        # Low risk for both
        alzheimer_score = 0.15
        parkinson_score = 0.12
        # Very good cognitive scores
        if mmse >= 28 and moca >= 26:
            alzheimer_score = 0.08
            parkinson_score = 0.05
    
    return (alzheimer_score, parkinson_score)


async def load_real_data(csv_path: str = None, admin_user_id: int = None):
    """
    Load real data from CSV file into database
    """
    # Default path
    if csv_path is None:
        project_root = Path(__file__).parent.parent.parent
        csv_path = project_root / 'data' / 'real_data' / 'csv' / 'real_dataset_complete.csv'
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    print(f"\nLoading real data from: {csv_path}")
    
    # Read CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from CSV")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            # Get or create admin user
            if admin_user_id is None:
                result = await session.execute(
                    select(User).where(User.role == 'admin').limit(1)
                )
                admin_user = result.scalar_one_or_none()
                
                if not admin_user:
                    print("No admin user found. Creating default admin...")
                    from app.core.security import get_password_hash
                    admin_user = User(
                        email="admin@neuropredict.ai",
                        username="admin",
                        full_name="System Administrator",
                        hashed_password=get_password_hash("admin123"),
                        role="admin",
                        is_active=True,
                        is_verified=True
                    )
                    session.add(admin_user)
                    await session.flush()
                    print(f"Created admin user: {admin_user.id}")
                else:
                    print(f"Using admin user: {admin_user.id}")
            else:
                admin_user = await session.get(User, admin_user_id)
                if not admin_user:
                    print(f"User with ID {admin_user_id} not found")
                    return
            
            # Check existing patients
            result = await session.execute(
                select(Patient).where(Patient.patient_id.in_(df['patient_id'].tolist()))
            )
            existing_patients = {p.patient_id: p for p in result.scalars().all()}
            print(f"Found {len(existing_patients)} existing patients")
            
            patients_created = 0
            patients_updated = 0
            predictions_created = 0
            
            # Process each row
            for idx, row in df.iterrows():
                patient_id = str(row['patient_id'])
                
                # Check if patient exists
                if patient_id in existing_patients:
                    patient = existing_patients[patient_id]
                    patients_updated += 1
                else:
                    # Create new patient
                    # Parse date of birth from age
                    age = int(row['age'])
                    birth_year = datetime.now().year - age
                    date_of_birth = date(birth_year, 1, 1)  # Use Jan 1 as default
                    
                    # Parse gender
                    gender_str = str(row['gender']).lower()
                    if gender_str == 'male':
                        gender = Gender.MALE
                    elif gender_str == 'female':
                        gender = Gender.FEMALE
                    else:
                        gender = Gender.OTHER
                    
                    # Create patient name from patient_id
                    name_parts = patient_id.split('_')
                    first_name = name_parts[0] if len(name_parts) > 0 else "Patient"
                    last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
                    
                    patient = Patient(
                        patient_id=patient_id,
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=date_of_birth,
                        gender=gender,
                        education_years=int(row['education_years']) if pd.notna(row['education_years']) else None,
                        email=f"{patient_id.lower()}@example.com",
                        medical_history=f"Data source: {row.get('data_source', 'Unknown')}",
                    )
                    session.add(patient)
                    await session.flush()  # Get patient.id
                    patients_created += 1
                    existing_patients[patient_id] = patient
                
                # Create prediction based on diagnosis
                diagnosis = str(row.get('diagnosis', 'Normal'))
                
                # Calculate risk scores
                alzheimer_score, parkinson_score = calculate_risk_score(
                    diagnosis=diagnosis,
                    mmse=float(row.get('mmse_score', 25)),
                    moca=float(row.get('moca_score', 23)),
                    amyloid_beta=float(row.get('amyloid_beta', 600)),
                    tau_protein=float(row.get('tau_protein', 300)),
                    dopamine=float(row.get('dopamine_level', 80)),
                    hippocampal_volume=float(row.get('hippocampal_volume', 3500))
                )
                
                # Determine disease type
                if diagnosis == 'Alzheimer':
                    disease_type = DiseaseType.ALZHEIMER
                elif diagnosis == 'Parkinson':
                    disease_type = DiseaseType.PARKINSON
                else:
                    disease_type = DiseaseType.ALZHEIMER  # Default
                
                # Create input features JSON
                input_features = {
                    'mmse_score': float(row.get('mmse_score', 0)),
                    'moca_score': float(row.get('moca_score', 0)),
                    'memory_score': float(row.get('memory_score', 0)),
                    'attention_score': float(row.get('attention_score', 0)),
                    'executive_function_score': float(row.get('executive_function_score', 0)),
                    'amyloid_beta': float(row.get('amyloid_beta', 0)),
                    'tau_protein': float(row.get('tau_protein', 0)),
                    'dopamine_level': float(row.get('dopamine_level', 0)),
                    'hippocampal_volume': float(row.get('hippocampal_volume', 0)),
                    'cortical_thickness': float(row.get('cortical_thickness', 0)),
                    'ventricular_volume': float(row.get('ventricular_volume', 0)),
                    'white_matter_hyperintensities': float(row.get('white_matter_hyperintensities', 0)),
                    'apoe_e4_status': int(row.get('apoe_e4_status', 0)),
                }
                
                # Create prediction
                prediction = Prediction(
                    patient_id=patient.id,
                    created_by=admin_user.id,
                    disease_type=disease_type,
                    alzheimer_risk_score=alzheimer_score,
                    alzheimer_risk_level=calculate_risk_level(alzheimer_score),
                    alzheimer_confidence=0.85,
                    parkinson_risk_score=parkinson_score,
                    parkinson_risk_level=calculate_risk_level(parkinson_score),
                    parkinson_confidence=0.85,
                    model_version="1.0.0",
                    model_name="NeuroPredict-AI Real Data Model",
                    input_features=input_features,
                    recommendations=f"Based on {diagnosis} diagnosis pattern. Data source: {row.get('data_source', 'Unknown')}",
                )
                session.add(prediction)
                predictions_created += 1
                
                # Progress indicator
                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(df)} records...")
            
            # Commit all changes
            await session.commit()
            
            print(f"\nData loading complete!")
            print(f"   - Patients created: {patients_created}")
            print(f"   - Patients updated: {patients_updated}")
            print(f"   - Predictions created: {predictions_created}")
            print(f"   - Total patients in database: {len(existing_patients)}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load real data from CSV into database')
    parser.add_argument('--csv', type=str, help='Path to CSV file', default=None)
    parser.add_argument('--admin-id', type=int, help='Admin user ID', default=None)
    
    args = parser.parse_args()
    
    asyncio.run(load_real_data(csv_path=args.csv, admin_user_id=args.admin_id))

