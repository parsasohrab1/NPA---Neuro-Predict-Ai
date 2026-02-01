#!/usr/bin/env python
"""
Script to create sample data for the dashboard
Creates patients, medical records, and predictions
"""
import asyncio
import random
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, init_db
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.prediction import Prediction, DiseaseType, RiskLevel
from app.models.user import User, UserRole


# Sample patient data
SAMPLE_PATIENTS = [
    {
        "patient_id": "PT-2024-001",
        "first_name": "احمد",
        "last_name": "محمدی",
        "date_of_birth": date(1955, 3, 15),
        "gender": Gender.MALE,
        "email": "ahmad.mohammadi@example.com",
        "phone": "09123456789",
        "education_years": 12,
        "medical_history": "فشار خون بالا، دیابت نوع 2",
        "family_history": "سابقه آلزایمر در مادر",
    },
    {
        "patient_id": "PT-2024-002",
        "first_name": "فاطمه",
        "last_name": "حسینی",
        "date_of_birth": date(1948, 7, 22),
        "gender": Gender.FEMALE,
        "email": "fateme.hosseini@example.com",
        "phone": "09123456790",
        "education_years": 16,
        "medical_history": "پوکی استخوان",
        "family_history": "سابقه پارکینسون در پدر",
    },
    {
        "patient_id": "PT-2024-003",
        "first_name": "محمد",
        "last_name": "کریمی",
        "date_of_birth": date(1960, 11, 8),
        "gender": Gender.MALE,
        "email": "mohammad.karimi@example.com",
        "phone": "09123456791",
        "education_years": 14,
        "medical_history": "بیماری قلبی",
        "family_history": "بدون سابقه",
    },
    {
        "patient_id": "PT-2024-004",
        "first_name": "زهرا",
        "last_name": "احمدی",
        "date_of_birth": date(1952, 5, 30),
        "gender": Gender.FEMALE,
        "email": "zahra.ahmadi@example.com",
        "phone": "09123456792",
        "education_years": 10,
        "medical_history": "کم‌خونی",
        "family_history": "سابقه آلزایمر در خواهر",
    },
    {
        "patient_id": "PT-2024-005",
        "first_name": "علی",
        "last_name": "نوری",
        "date_of_birth": date(1958, 9, 12),
        "gender": Gender.MALE,
        "email": "ali.nouri@example.com",
        "phone": "09123456793",
        "education_years": 18,
        "medical_history": "آرتریت",
        "family_history": "بدون سابقه",
    },
    {
        "patient_id": "PT-2024-006",
        "first_name": "مریم",
        "last_name": "صادقی",
        "date_of_birth": date(1945, 12, 3),
        "gender": Gender.FEMALE,
        "email": "maryam.sadeghi@example.com",
        "phone": "09123456794",
        "education_years": 8,
        "medical_history": "دیابت، فشار خون",
        "family_history": "سابقه پارکینسون در مادر",
    },
    {
        "patient_id": "PT-2024-007",
        "first_name": "حسن",
        "last_name": "رضایی",
        "date_of_birth": date(1962, 2, 18),
        "gender": Gender.MALE,
        "email": "hasan.rezaei@example.com",
        "phone": "09123456795",
        "education_years": 15,
        "medical_history": "بدون سابقه",
        "family_history": "بدون سابقه",
    },
    {
        "patient_id": "PT-2024-008",
        "first_name": "سمیه",
        "last_name": "موسوی",
        "date_of_birth": date(1950, 8, 25),
        "gender": Gender.FEMALE,
        "email": "somayeh.mousavi@example.com",
        "phone": "09123456796",
        "education_years": 12,
        "medical_history": "مشکلات تیروئید",
        "family_history": "سابقه آلزایمر در مادربزرگ",
    },
]


def generate_medical_record(patient: Patient, visit_date: datetime):
    """Generate a medical record for a patient"""
    age = (datetime.now().date() - patient.date_of_birth).days / 365.25
    
    # Base scores (decline with age)
    base_mmse = max(15, 30 - (age - 60) * 0.5)
    base_moca = max(15, 30 - (age - 60) * 0.5)
    
    # Add random variation
    mmse = max(10, min(30, base_mmse + random.uniform(-3, 3)))
    moca = max(10, min(30, base_moca + random.uniform(-3, 3)))
    
    # Cognitive scores (0-100)
    memory = max(30, min(100, (mmse / 30) * 80 + random.uniform(-10, 10)))
    attention = max(30, min(100, (moca / 30) * 75 + random.uniform(-10, 10)))
    executive = max(30, min(100, (moca / 30) * 70 + random.uniform(-10, 10)))
    
    # Biomarkers
    amyloid_beta = random.uniform(400, 900)  # pg/mL
    tau_protein = random.uniform(100, 600)  # pg/mL
    dopamine_level = random.uniform(50, 150)  # ng/mL
    
    # Genetic
    apoe_e4 = random.choice([True, False])
    
    # MRI Features
    hippocampal_volume = random.uniform(2500, 4500)  # mm³
    cortical_thickness = random.uniform(2.0, 3.0)  # mm
    ventricular_volume = random.uniform(20000, 60000)  # mm³
    white_matter = random.uniform(0, 8)  # score
    brain_volume = random.uniform(1000000, 1400000)  # mm³
    
    return MedicalRecord(
        patient_id=patient.id,
        visit_date=visit_date,
        visit_type=random.choice(["Initial", "Follow-up", "Routine Check"]),
        mmse_score=round(mmse, 1),
        moca_score=round(moca, 1),
        memory_score=round(memory, 1),
        attention_score=round(attention, 1),
        executive_function_score=round(executive, 1),
        amyloid_beta=round(amyloid_beta, 2),
        tau_protein=round(tau_protein, 2),
        dopamine_level=round(dopamine_level, 2),
        apoe_e4_status=apoe_e4,
        hippocampal_volume=round(hippocampal_volume, 2),
        cortical_thickness=round(cortical_thickness, 2),
        ventricular_volume=round(ventricular_volume, 2),
        white_matter_hyperintensities=round(white_matter, 2),
        brain_volume_total=round(brain_volume, 2),
        symptoms="Mild forgetfulness, short-term memory issues",
        clinical_notes="Patient presented for initial assessment",
    )


def generate_prediction(patient: Patient, medical_record: MedicalRecord, created_by: int):
    """Generate a prediction based on medical record"""
    age = (datetime.now().date() - patient.date_of_birth).days / 365.25
    
    # Calculate risk scores based on data
    # Alzheimer's risk factors: age, low MMSE, high tau, low hippocampal volume
    alzheimer_base = (age - 60) / 40.0  # Normalized age factor
    mmse_factor = (30 - medical_record.mmse_score) / 30.0
    tau_factor = medical_record.tau_protein / 800.0
    hippocampus_factor = (4500 - medical_record.hippocampal_volume) / 2000.0
    
    alzheimer_risk = min(0.95, max(0.05, 
        alzheimer_base * 0.3 + mmse_factor * 0.3 + tau_factor * 0.2 + hippocampus_factor * 0.2
    ))
    
    # Parkinson's risk factors: age, low dopamine, family history
    parkinson_base = (age - 60) / 40.0
    dopamine_factor = (150 - medical_record.dopamine_level) / 150.0
    
    parkinson_risk = min(0.95, max(0.05,
        parkinson_base * 0.4 + dopamine_factor * 0.4 + random.uniform(-0.1, 0.1)
    ))
    
    # Determine risk levels
    def get_risk_level(score):
        if score < 0.33:
            return RiskLevel.LOW
        elif score < 0.66:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    alzheimer_level = get_risk_level(alzheimer_risk)
    parkinson_level = get_risk_level(parkinson_risk)
    
    # Confidence (higher when score is extreme)
    alzheimer_confidence = 1.0 - 2.0 * abs(alzheimer_risk - 0.5)
    parkinson_confidence = 1.0 - 2.0 * abs(parkinson_risk - 0.5)
    
    # Determine disease type
    if alzheimer_risk > 0.5 and parkinson_risk > 0.5:
        disease_type = DiseaseType.BOTH
    elif alzheimer_risk > parkinson_risk:
        disease_type = DiseaseType.ALZHEIMER
    else:
        disease_type = DiseaseType.PARKINSON
    
    return Prediction(
        patient_id=patient.id,
        created_by=created_by,
        disease_type=disease_type,
        alzheimer_risk_score=round(alzheimer_risk, 3),
        alzheimer_risk_level=alzheimer_level,
        alzheimer_confidence=round(alzheimer_confidence, 3),
        parkinson_risk_score=round(parkinson_risk, 3),
        parkinson_risk_level=parkinson_level,
        parkinson_confidence=round(parkinson_confidence, 3),
        model_version="1.0.0-mock",
        model_name="MockPredictionModel",
        input_features={
            "age": age,
            "mmse_score": medical_record.mmse_score,
            "tau_protein": medical_record.tau_protein,
            "hippocampal_volume": medical_record.hippocampal_volume,
        }
    )


async def create_sample_data():
    """Create sample data in the database"""
    print("Starting sample data creation...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Get or create a doctor user
        from sqlalchemy import select
        
        result = await session.execute(
            select(User).where(User.role == UserRole.DOCTOR).limit(1)
        )
        doctor = result.scalar_one_or_none()
        
        if not doctor:
            # Create a doctor user if none exists
            from app.core.security import get_password_hash
            doctor = User(
                email="doctor@neuropredict.ai",
                username="doctor",
                full_name="Sample Doctor",
                hashed_password=get_password_hash("doctor123"),
                role=UserRole.DOCTOR,
                is_active=True
            )
            session.add(doctor)
            await session.commit()
            await session.refresh(doctor)
            print(f"[OK] Created doctor user: {doctor.username}")
        
        doctor_id = doctor.id
        
        # Create patients
        created_patients = []
        for patient_data in SAMPLE_PATIENTS:
            # Check if patient already exists
            result = await session.execute(
                select(Patient).where(Patient.patient_id == patient_data["patient_id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"[SKIP] Patient {patient_data['patient_id']} already exists, skipping...")
                created_patients.append(existing)
                continue
            
            patient = Patient(**patient_data)
            session.add(patient)
            await session.flush()
            created_patients.append(patient)
            print(f"[OK] Created patient: {patient.first_name} {patient.last_name} ({patient.patient_id})")
            
            # Create 1-3 medical records per patient
            num_records = random.randint(1, 3)
            for i in range(num_records):
                visit_date = datetime.now() - timedelta(days=random.randint(0, 180))
                medical_record = generate_medical_record(patient, visit_date)
                session.add(medical_record)
                await session.flush()
                
                # Create prediction for each medical record
                prediction = generate_prediction(patient, medical_record, doctor_id)
                session.add(prediction)
        
        await session.commit()
        print(f"\n[OK] Successfully created {len(created_patients)} patients with medical records and predictions!")
        print(f"[INFO] Total predictions created: {len(created_patients) * 2}")
        print("\n[DONE] Sample data creation completed!")


if __name__ == "__main__":
    asyncio.run(create_sample_data())
