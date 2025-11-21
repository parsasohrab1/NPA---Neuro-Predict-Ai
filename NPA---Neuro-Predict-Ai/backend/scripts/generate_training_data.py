#!/usr/bin/env python3
"""
Generate Synthetic Training Data
تولید داده‌های سنتتیک برای آموزش مدل (برای تست و توسعه)
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_synthetic_data(n_samples: int = 1000, 
                           output_path: str = "data/training_data.csv",
                           seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic training data
    
    Args:
        n_samples: Number of samples to generate
        output_path: Path to save CSV file
        seed: Random seed
    
    Returns:
        DataFrame with synthetic data
    """
    np.random.seed(seed)
    
    print(f"Generating {n_samples} synthetic samples...")
    
    data = {}
    
    # Demographics
    data['age'] = np.random.normal(70, 10, n_samples).clip(40, 100)
    data['gender_encoded'] = np.random.choice([0, 1], n_samples)  # 0=Female, 1=Male
    data['education_years'] = np.random.normal(12, 4, n_samples).clip(0, 25)
    
    # Cognitive Scores
    data['mmse_score'] = np.random.normal(25, 5, n_samples).clip(0, 30)
    data['moca_score'] = np.random.normal(24, 5, n_samples).clip(0, 30)
    data['memory_score'] = np.random.normal(50, 15, n_samples).clip(0, 100)
    data['attention_score'] = np.random.normal(50, 15, n_samples).clip(0, 100)
    data['executive_function_score'] = np.random.normal(50, 15, n_samples).clip(0, 100)
    
    # Biomarkers
    data['amyloid_beta'] = np.random.normal(600, 150, n_samples).clip(200, 1200)
    data['tau_protein'] = np.random.normal(200, 80, n_samples).clip(50, 600)
    data['dopamine_level'] = np.random.normal(100, 30, n_samples).clip(20, 200)
    
    # Genetic
    data['apoe_e4_status'] = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    
    # MRI Features
    data['hippocampal_volume'] = np.random.normal(3500, 500, n_samples).clip(2000, 5000)
    data['cortical_thickness'] = np.random.normal(2.3, 0.3, n_samples).clip(1.5, 3.0)
    data['ventricular_volume'] = np.random.normal(30000, 8000, n_samples).clip(10000, 60000)
    data['white_matter_hyperintensities'] = np.random.normal(2, 1.5, n_samples).clip(0, 10)
    data['brain_volume_total'] = np.random.normal(1100000, 100000, n_samples).clip(900000, 1300000)
    
    # Imaging features (32 features)
    for i in range(32):
        data[f'imaging_feature_{i}'] = np.random.normal(0, 1, n_samples)
    
    # Generate labels based on features (simplified logic)
    # Alzheimer's risk increases with:
    # - Lower MMSE/MoCA scores
    # - Higher tau protein
    # - Lower hippocampal volume
    # - APOE ε4 status
    # - Age
    
    alzheimer_risk = (
        (30 - data['mmse_score']) / 30 * 0.3 +
        (data['tau_protein'] - 200) / 400 * 0.2 +
        (3500 - data['hippocampal_volume']) / 1500 * 0.2 +
        data['apoe_e4_status'] * 0.2 +
        (data['age'] - 70) / 30 * 0.1
    )
    alzheimer_risk = np.clip(alzheimer_risk, 0, 1)
    data['alzheimer_label'] = (alzheimer_risk > 0.5).astype(int)
    
    # Parkinson's risk increases with:
    # - Lower dopamine levels
    # - Age
    # - Some cognitive decline
    
    parkinson_risk = (
        (100 - data['dopamine_level']) / 80 * 0.4 +
        (data['age'] - 70) / 30 * 0.3 +
        (30 - data['mmse_score']) / 30 * 0.2 +
        np.random.normal(0, 0.1, n_samples)
    )
    parkinson_risk = np.clip(parkinson_risk, 0, 1)
    data['parkinson_label'] = (parkinson_risk > 0.5).astype(int)
    
    # Add some noise to make it more realistic
    for key in data:
        if key not in ['alzheimer_label', 'parkinson_label', 'gender_encoded', 'apoe_e4_status']:
            data[key] += np.random.normal(0, data[key].std() * 0.05, n_samples)
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated {n_samples} samples")
    print(f"Alzheimer's positive: {df['alzheimer_label'].sum()} ({df['alzheimer_label'].mean()*100:.1f}%)")
    print(f"Parkinson's positive: {df['parkinson_label'].sum()} ({df['parkinson_label'].mean()*100:.1f}%)")
    print(f"Data saved to: {output_path}")
    
    return df


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic training data')
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of samples to generate')
    parser.add_argument('--output', type=str, default='data/training_data.csv',
                       help='Output CSV file path')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NeuroPredict-AI Synthetic Data Generator")
    print("=" * 80)
    print(f"NOTE: This generates SYNTHETIC data for testing and development.")
    print(f"For real clinical validation, use actual medical data with proper IRB approval.")
    print("=" * 80)
    print()
    
    df = generate_synthetic_data(
        n_samples=args.samples,
        output_path=args.output,
        seed=args.seed
    )
    
    print("\nData generation completed!")


if __name__ == "__main__":
    main()

