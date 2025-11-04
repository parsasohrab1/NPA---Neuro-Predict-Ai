"""
Generate Sample Medical Data for NeuroPredict-AI
This creates a small sample dataset for demonstration purposes
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Small sample size for git repository
TOTAL_SAMPLES = 100
DISTRIBUTIONS = {
    'normal': 70,
    'alzheimer': 20,
    'parkinson': 10
}

def generate_sample_data():
    """Generate sample medical data"""
    
    print("🧠 Generating Sample Medical Data for NeuroPredict-AI...")
    print(f"Total samples: {TOTAL_SAMPLES}")
    print(f"Distribution: {DISTRIBUTIONS}")
    
    # Demographics
    ages = np.concatenate([
        np.random.normal(45, 10, DISTRIBUTIONS['normal']),
        np.random.normal(75, 8, DISTRIBUTIONS['alzheimer']),
        np.random.normal(70, 10, DISTRIBUTIONS['parkinson'])
    ])
    
    genders = np.random.choice(['Male', 'Female'], TOTAL_SAMPLES)
    
    education_years = np.concatenate([
        np.random.normal(16, 3, DISTRIBUTIONS['normal']),
        np.random.normal(12, 4, DISTRIBUTIONS['alzheimer']),
        np.random.normal(13, 3, DISTRIBUTIONS['parkinson'])
    ])
    
    # Visit dates
    base_date = datetime.now()
    visit_dates = [base_date - timedelta(days=random.randint(0, 730)) 
                  for _ in range(TOTAL_SAMPLES)]
    
    # Cognitive Scores
    mmse_scores = np.concatenate([
        np.random.normal(29, 1, DISTRIBUTIONS['normal']),
        np.random.normal(20, 4, DISTRIBUTIONS['alzheimer']),
        np.random.normal(26, 2, DISTRIBUTIONS['parkinson'])
    ])
    
    moca_scores = np.concatenate([
        np.random.normal(28, 1.5, DISTRIBUTIONS['normal']),
        np.random.normal(18, 5, DISTRIBUTIONS['alzheimer']),
        np.random.normal(22, 3, DISTRIBUTIONS['parkinson'])
    ])
    
    # Biomarkers
    amyloid_beta = np.concatenate([
        np.random.normal(600, 100, DISTRIBUTIONS['normal']),
        np.random.normal(400, 150, DISTRIBUTIONS['alzheimer']),
        np.random.normal(550, 120, DISTRIBUTIONS['parkinson'])
    ])
    
    tau_protein = np.concatenate([
        np.random.normal(200, 50, DISTRIBUTIONS['normal']),
        np.random.normal(500, 150, DISTRIBUTIONS['alzheimer']),
        np.random.normal(250, 80, DISTRIBUTIONS['parkinson'])
    ])
    
    dopamine = np.concatenate([
        np.random.normal(100, 20, DISTRIBUTIONS['normal']),
        np.random.normal(90, 25, DISTRIBUTIONS['alzheimer']),
        np.random.normal(50, 30, DISTRIBUTIONS['parkinson'])
    ])
    
    # Genetic markers
    apoe_e4 = np.concatenate([
        np.random.choice([0, 1], DISTRIBUTIONS['normal'], p=[0.8, 0.2]),
        np.random.choice([0, 1], DISTRIBUTIONS['alzheimer'], p=[0.3, 0.7]),
        np.random.choice([0, 1], DISTRIBUTIONS['parkinson'], p=[0.7, 0.3])
    ])
    
    # MRI Features
    hippocampal_volume = np.concatenate([
        np.random.normal(4000, 300, DISTRIBUTIONS['normal']),
        np.random.normal(2500, 500, DISTRIBUTIONS['alzheimer']),
        np.random.normal(3500, 400, DISTRIBUTIONS['parkinson'])
    ])
    
    cortical_thickness = np.concatenate([
        np.random.normal(2.5, 0.2, DISTRIBUTIONS['normal']),
        np.random.normal(2.0, 0.3, DISTRIBUTIONS['alzheimer']),
        np.random.normal(2.3, 0.25, DISTRIBUTIONS['parkinson'])
    ])
    
    ventricular_volume = np.concatenate([
        np.random.normal(25000, 5000, DISTRIBUTIONS['normal']),
        np.random.normal(45000, 8000, DISTRIBUTIONS['alzheimer']),
        np.random.normal(30000, 6000, DISTRIBUTIONS['parkinson'])
    ])
    
    # Labels
    labels = np.concatenate([
        np.zeros(DISTRIBUTIONS['normal']),
        np.ones(DISTRIBUTIONS['alzheimer']),
        np.full(DISTRIBUTIONS['parkinson'], 2)
    ])
    
    diagnosis_labels = np.concatenate([
        ['Normal'] * DISTRIBUTIONS['normal'],
        ['Alzheimer'] * DISTRIBUTIONS['alzheimer'],
        ['Parkinson'] * DISTRIBUTIONS['parkinson']
    ])
    
    # Create DataFrame
    data = pd.DataFrame({
        'patient_id': [f'PT_{i:04d}' for i in range(1, TOTAL_SAMPLES + 1)],
        'age': np.clip(ages, 40, 95),
        'gender': genders,
        'education_years': np.clip(education_years, 5, 25),
        'visit_date': visit_dates,
        'mmse_score': np.clip(mmse_scores, 0, 30),
        'moca_score': np.clip(moca_scores, 0, 30),
        'memory_score': np.random.normal(50, 15, TOTAL_SAMPLES),
        'attention_score': np.random.normal(50, 15, TOTAL_SAMPLES),
        'executive_function_score': np.random.normal(50, 15, TOTAL_SAMPLES),
        'amyloid_beta': np.clip(amyloid_beta, 100, 1000),
        'tau_protein': np.clip(tau_protein, 50, 800),
        'dopamine_level': np.clip(dopamine, 10, 150),
        'apoe_e4_status': apoe_e4,
        'hippocampal_volume': np.clip(hippocampal_volume, 1500, 5000),
        'cortical_thickness': np.clip(cortical_thickness, 1.5, 3.0),
        'ventricular_volume': np.clip(ventricular_volume, 10000, 70000),
        'white_matter_hyperintensities': np.random.gamma(2, 2, TOTAL_SAMPLES),
        'brain_volume_total': np.random.normal(1100000, 100000, TOTAL_SAMPLES),
        'label': labels,
        'diagnosis': diagnosis_labels
    })
    
    return data


def generate_sample_images(data, output_dir='data/images'):
    """Generate sample MRI images (simplified for demo)"""
    print("\n📸 Generating Sample MRI Images...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a few sample images for each category
    samples_per_category = {
        'Normal': 5,
        'Alzheimer': 3,
        'Parkinson': 2
    }
    
    for diagnosis, count in samples_per_category.items():
        patients = data[data['diagnosis'] == diagnosis].head(count)
        
        for _, patient in patients.iterrows():
            # Create simple synthetic MRI image (64x64 for small size)
            image = np.random.normal(128, 30, (64, 64))
            
            # Add disease-specific patterns
            if diagnosis == 'Alzheimer':
                # Simulate hippocampal atrophy
                image[20:40, 20:40] *= 0.7
            elif diagnosis == 'Parkinson':
                # Simulate substantia nigra changes
                image[35:50, 35:50] *= 1.3
            
            # Normalize to 0-255
            image = np.clip(image, 0, 255).astype(np.uint8)
            
            # Save as simple text array (to keep size small)
            filename = f"{output_dir}/{patient['patient_id']}_{diagnosis}.npy"
            np.save(filename, image)
    
    print(f"✅ Generated {sum(samples_per_category.values())} sample MRI images")


def save_datasets(data, output_dir='data/csv'):
    """Save datasets as CSV files"""
    print("\n💾 Saving CSV Files...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save complete dataset
    data.to_csv(f'{output_dir}/sample_dataset_complete.csv', index=False)
    print(f"✅ Saved: sample_dataset_complete.csv")
    
    # Save separate tables
    data[['patient_id', 'age', 'gender', 'education_years', 'visit_date']].to_csv(
        f'{output_dir}/demographic_data.csv', index=False
    )
    print(f"✅ Saved: demographic_data.csv")
    
    data[['patient_id', 'mmse_score', 'moca_score', 'memory_score', 
          'attention_score', 'executive_function_score']].to_csv(
        f'{output_dir}/cognitive_data.csv', index=False
    )
    print(f"✅ Saved: cognitive_data.csv")
    
    data[['patient_id', 'amyloid_beta', 'tau_protein', 'dopamine_level']].to_csv(
        f'{output_dir}/biomarker_data.csv', index=False
    )
    print(f"✅ Saved: biomarker_data.csv")
    
    data[['patient_id', 'hippocampal_volume', 'cortical_thickness', 
          'ventricular_volume', 'white_matter_hyperintensities', 
          'brain_volume_total']].to_csv(
        f'{output_dir}/mri_features.csv', index=False
    )
    print(f"✅ Saved: mri_features.csv")
    
    data[['patient_id', 'label', 'diagnosis']].to_csv(
        f'{output_dir}/labels.csv', index=False
    )
    print(f"✅ Saved: labels.csv")


def print_statistics(data):
    """Print dataset statistics"""
    print("\n" + "="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)
    
    print(f"\nTotal Samples: {len(data)}")
    print(f"\nDiagnosis Distribution:")
    print(data['diagnosis'].value_counts())
    
    print(f"\n{'='*60}")
    print("Sample Data (First 5 Rows):")
    print("="*60)
    print(data[['patient_id', 'age', 'gender', 'diagnosis', 'mmse_score', 'moca_score']].head())
    
    print(f"\n{'='*60}")
    print("Statistical Summary:")
    print("="*60)
    print(data[['age', 'mmse_score', 'moca_score', 'hippocampal_volume']].describe())


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 NEUROPREDICT-AI SAMPLE DATA GENERATOR")
    print("="*60 + "\n")
    
    # Generate data
    data = generate_sample_data()
    
    # Generate sample images
    generate_sample_images(data)
    
    # Save datasets
    save_datasets(data)
    
    # Print statistics
    print_statistics(data)
    
    print("\n" + "="*60)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*60)
    print("\nOutput Files:")
    print("  📁 data/csv/          - CSV datasets")
    print("  📁 data/images/       - Sample MRI images")
    print("\n" + "="*60 + "\n")

