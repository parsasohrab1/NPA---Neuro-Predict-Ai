#!/usr/bin/env python
"""
Script to add default medical records and predictions for all patients
This script adds sample medical data for patients who don't have any records yet
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal, init_db
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.prediction import Prediction, DiseaseType, RiskLevel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def generate_default_medical_data(age: int, gender: str) -> dict:
    """
    Generate default medical data based on patient age and gender
    Returns realistic values for disease tracking
    """
    # Base values for normal aging
    base_mmse = 28.0
    base_moca = 26.0
    base_memory = 75.0
    base_attention = 80.0
    base_executive = 75.0
    
    # Age-based adjustments
    age_factor = max(0, (age - 50) / 30)  # More decline after 50
    age_adjustment = age_factor * random.uniform(-3, -1)
    
    # Generate cognitive scores
    mmse_score = max(18, min(30, base_mmse + age_adjustment + random.uniform(-2, 2)))
    moca_score = max(16, min(30, base_moca + age_adjustment + random.uniform(-2, 2)))
    memory_score = max(50, min(100, base_memory + age_adjustment * 5 + random.uniform(-10, 10)))
    attention_score = max(60, min(100, base_attention + age_adjustment * 3 + random.uniform(-8, 8)))
    executive_score = max(55, min(100, base_executive + age_adjustment * 4 + random.uniform(-10, 10)))
    
    # Biomarkers - normal ranges with some variation
    amyloid_beta = random.uniform(450, 650)  # Normal range: 400-600
    tau_protein = random.uniform(180, 280)  # Normal range: 150-250
    dopamine_level = random.uniform(85, 115)  # Normal range: 80-120
    
    # Some patients may have elevated risk markers
    if random.random() < 0.2:  # 20% chance of elevated risk
        amyloid_beta = random.uniform(300, 400)  # Lower = higher AD risk
        tau_protein = random.uniform(300, 450)  # Higher = higher AD risk
    if random.random() < 0.15:  # 15% chance of low dopamine
        dopamine_level = random.uniform(50, 75)  # Lower = higher PD risk
    
    # Genetic marker
    apoe_e4_status = random.random() < 0.25  # 25% population has APOE ε4
    
    # MRI features - normal ranges
    hippocampal_volume = random.uniform(3500, 4800)  # Normal: 3500-5000
    cortical_thickness = random.uniform(2.3, 2.9)  # Normal: 2.2-3.0
    ventricular_volume = random.uniform(18000, 28000)  # Normal: 15000-30000
    white_matter_hyperintensities = random.uniform(0.5, 2.5)
    brain_volume_total = random.uniform(1050000, 1150000)
    
    # Adjust for age
    if age > 70:
        hippocampal_volume *= random.uniform(0.85, 0.95)
        cortical_thickness *= random.uniform(0.90, 0.98)
        ventricular_volume *= random.uniform(1.05, 1.15)
    
    return {
        "mmse_score": round(mmse_score, 1),
        "moca_score": round(moca_score, 1),
        "memory_score": round(memory_score, 1),
        "attention_score": round(attention_score, 1),
        "executive_function_score": round(executive_score, 1),
        "amyloid_beta": round(amyloid_beta, 1),
        "tau_protein": round(tau_protein, 1),
        "dopamine_level": round(dopamine_level, 1),
        "apoe_e4_status": apoe_e4_status,
        "hippocampal_volume": round(hippocampal_volume, 0),
        "cortical_thickness": round(cortical_thickness, 2),
        "ventricular_volume": round(ventricular_volume, 0),
        "white_matter_hyperintensities": round(white_matter_hyperintensities, 2),
        "brain_volume_total": round(brain_volume_total, 0),
    }


def calculate_risk_scores(medical_data: dict, age: int) -> tuple:
    """
    Calculate Alzheimer's and Parkinson's risk scores based on medical data
    Returns: (alzheimer_risk, parkinson_risk, alzheimer_level, parkinson_level)
    """
    alzheimer_risk = 0.0
    parkinson_risk = 0.0
    
    # Alzheimer's risk factors
    if medical_data["mmse_score"] < 24:
        alzheimer_risk += 0.3
    if medical_data["moca_score"] < 22:
        alzheimer_risk += 0.25
    if medical_data["amyloid_beta"] < 400:
        alzheimer_risk += 0.35
    if medical_data["tau_protein"] > 350:
        alzheimer_risk += 0.3
    if medical_data["hippocampal_volume"] < 3000:
        alzheimer_risk += 0.25
    if medical_data["apoe_e4_status"]:
        alzheimer_risk += 0.2
    if age > 75:
        alzheimer_risk += 0.15
    
    # Parkinson's risk factors
    if medical_data["dopamine_level"] < 70:
        parkinson_risk += 0.5
    if medical_data["dopamine_level"] < 50:
        parkinson_risk += 0.3
    if age > 70:
        parkinson_risk += 0.2
    if medical_data["attention_score"] < 65:
        parkinson_risk += 0.15
    
    # Normalize to 0-1 range
    alzheimer_risk = min(1.0, alzheimer_risk)
    parkinson_risk = min(1.0, parkinson_risk)
    
    # Determine risk levels
    alzheimer_level = (
        RiskLevel.HIGH if alzheimer_risk >= 0.66
        else RiskLevel.MEDIUM if alzheimer_risk >= 0.33
        else RiskLevel.LOW
    )
    
    parkinson_level = (
        RiskLevel.HIGH if parkinson_risk >= 0.66
        else RiskLevel.MEDIUM if parkinson_risk >= 0.33
        else RiskLevel.LOW
    )
    
    return (alzheimer_risk, parkinson_risk, alzheimer_level, parkinson_level)


async def add_default_data_for_patients(db: AsyncSession):
    """Add default medical records and predictions for all patients"""
    
    # Get all patients
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    
    if not patients:
        print("No patients found in database.")
        return
    
    print(f"\nFound {len(patients)} patients in database")
    print("Adding default medical records and predictions...\n")
    
    added_records = 0
    added_predictions = 0
    skipped = 0
    
    for patient in patients:
        # Check if patient already has medical records
        result = await db.execute(
            select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
        )
        existing_records = result.scalars().all()
        
        if existing_records:
            print(f"  ⏭ Skipping {patient.first_name} {patient.last_name} - already has {len(existing_records)} record(s)")
            skipped += 1
            continue
        
        # Calculate age
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        
        # Generate default medical data
        medical_data = generate_default_medical_data(age, patient.gender.value)
        
        # Create medical record
        visit_date = datetime.now() - timedelta(days=random.randint(0, 90))
        medical_record = MedicalRecord(
            patient_id=patient.id,
            visit_date=visit_date,
            visit_type="Initial",
            **medical_data,
            symptoms="Routine check-up",
            clinical_notes=f"Initial assessment for disease tracking. Age: {age}, Gender: {patient.gender.value}",
        )
        
        db.add(medical_record)
        await db.flush()  # Flush to get the record ID
        
        # Calculate risk scores
        alzheimer_risk, parkinson_risk, alzheimer_level, parkinson_level = calculate_risk_scores(
            medical_data, age
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
        
        db.add(prediction)
        
        added_records += 1
        added_predictions += 1
        
        print(f"  ✓ Added data for {patient.first_name} {patient.last_name} (Age: {age})")
        print(f"    - MMSE: {medical_data['mmse_score']}, MoCA: {medical_data['moca_score']}")
        print(f"    - Alzheimer Risk: {alzheimer_risk:.1%} ({alzheimer_level.value})")
        print(f"    - Parkinson Risk: {parkinson_risk:.1%} ({parkinson_level.value})")
    
    # Commit all changes
    await db.commit()
    
    print(f"\n✅ Summary:")
    print(f"   - Added {added_records} medical records")
    print(f"   - Added {added_predictions} predictions")
    print(f"   - Skipped {skipped} patients (already have data)")
    print(f"\n🎉 Default disease tracking data added successfully!")


async def main():
    """Main function"""
    print("=" * 60)
    print("Adding Default Disease Tracking Data")
    print("=" * 60)
    
    # Initialize database
    await init_db()
    
    # Create database session
    async with AsyncSessionLocal() as db:
        try:
            await add_default_data_for_patients(db)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())

