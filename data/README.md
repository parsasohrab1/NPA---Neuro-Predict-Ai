# 📊 Sample Medical Data

This directory contains sample medical data for testing and demonstration of the NeuroPredict-AI system.

## ⚠️ Important Notice

**This is SYNTHETIC DATA for demonstration purposes only.**
- Not real patient data
- Should NOT be used for actual medical decisions
- Generated using statistical distributions
- For development and testing only

## 📁 Directory Structure

```
data/
├── csv/                          # CSV datasets
│   ├── sample_dataset_complete.csv   # Complete dataset (100 samples)
│   ├── demographic_data.csv          # Patient demographics
│   ├── cognitive_data.csv            # Cognitive test scores
│   ├── biomarker_data.csv            # Biomarker levels
│   ├── mri_features.csv              # MRI volumetric features
│   └── labels.csv                    # Diagnosis labels
├── images/                       # Sample MRI images
│   └── *.npy                    # Numpy arrays (64x64 synthetic MRI)
└── generate_sample_data.py      # Data generation script
```

## 📈 Dataset Statistics

- **Total Samples**: 100
- **Normal Controls**: 70 (70%)
- **Alzheimer's Patients**: 20 (20%)
- **Parkinson's Patients**: 10 (10%)

## 🔬 Data Features

### Demographics
- Patient ID
- Age (40-95 years)
- Gender (Male/Female)
- Education Years (5-25 years)
- Visit Date

### Cognitive Scores
- **MMSE** (Mini-Mental State Examination): 0-30
- **MoCA** (Montreal Cognitive Assessment): 0-30
- Memory Score: 0-100
- Attention Score: 0-100
- Executive Function Score: 0-100

### Biomarkers
- **Amyloid-beta**: 100-1000 pg/mL
- **Tau Protein**: 50-800 pg/mL
- **Dopamine Level**: 10-150 ng/mL

### Genetic Markers
- **APOE ε4 Status**: 0 (negative) or 1 (positive)

### MRI Features
- **Hippocampal Volume**: 1500-5000 mm³
- **Cortical Thickness**: 1.5-3.0 mm
- **Ventricular Volume**: 10000-70000 mm³
- **White Matter Hyperintensities**: Gamma distribution
- **Total Brain Volume**: ~1,100,000 mm³

## 📊 Sample Data Preview

| patient_id | age | gender | diagnosis  | mmse_score | moca_score |
|------------|-----|--------|------------|------------|------------|
| PT_0001    | 50  | Male   | Normal     | 27.0       | 26.8       |
| PT_0071    | 75  | Female | Alzheimer  | 20.5       | 18.2       |
| PT_0091    | 70  | Male   | Parkinson  | 26.0       | 22.0       |

## 🖼️ Sample MRI Images

The `images/` folder contains 10 sample synthetic MRI images:
- 5 Normal controls
- 3 Alzheimer's patients
- 2 Parkinson's patients

**Format**: NumPy arrays (.npy files, 64x64 pixels)

**Disease-specific patterns**:
- **Alzheimer's**: Simulated hippocampal atrophy (reduced intensity in hippocampal region)
- **Parkinson's**: Simulated substantia nigra changes (increased intensity)

## 🚀 Regenerating Data

To regenerate the sample data:

```bash
cd data
python generate_sample_data.py
```

This will create:
- 100 patient records
- 6 CSV files
- 10 sample MRI images

## 📖 Usage in Application

### Loading Complete Dataset

```python
import pandas as pd

# Load complete dataset
df = pd.read_csv('data/csv/sample_dataset_complete.csv')

print(f"Total samples: {len(df)}")
print(df['diagnosis'].value_counts())
```

### Loading MRI Images

```python
import numpy as np

# Load sample MRI image
image = np.load('data/images/PT_0001_Normal.npy')

print(f"Image shape: {image.shape}")
print(f"Value range: {image.min()} - {image.max()}")
```

### Training AI Models

```python
from sklearn.model_selection import train_test_split

# Prepare features and labels
X = df.drop(['patient_id', 'diagnosis', 'label'], axis=1)
y = df['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
```

## ⚙️ Data Generation Parameters

The synthetic data is generated using statistical distributions that approximate real medical data patterns:

### Normal Controls
- Age: μ=45, σ=10
- MMSE: μ=29, σ=1
- Hippocampal Volume: μ=4000, σ=300
- APOE ε4: 20% positive

### Alzheimer's Patients
- Age: μ=75, σ=8
- MMSE: μ=20, σ=4 (impaired)
- Hippocampal Volume: μ=2500, σ=500 (atrophy)
- APOE ε4: 70% positive (high risk)

### Parkinson's Patients
- Age: μ=70, σ=10
- MMSE: μ=26, σ=2 (mild impairment)
- Dopamine: μ=50, σ=30 (reduced)
- APOE ε4: 30% positive

## 🔒 Privacy & Ethics

- All data is **100% synthetic**
- No real patient information
- No PHI (Protected Health Information)
- Safe for public repositories
- Complies with HIPAA/GDPR (no real data)

## 📚 References

For real medical data collection and usage, please refer to:
- [ADNI](https://adni.loni.usc.edu/) - Alzheimer's Disease Neuroimaging Initiative
- [PPMI](https://www.ppmi-info.org/) - Parkinson's Progression Markers Initiative
- [OASIS](https://www.oasis-brains.org/) - Open Access Series of Imaging Studies

## ⚠️ Disclaimer

This synthetic data is for **demonstration and testing purposes only**. Do not use this data for:
- Actual medical research
- Clinical decision making
- Model validation in production
- Publication of results

For production use, collect real data with proper:
- Ethics committee approval
- Patient consent
- Data privacy compliance
- Clinical validation

---

**Generated**: November 2024  
**Format**: CSV + NumPy arrays  
**Purpose**: Development & Testing  
**Status**: Sample Data ✅

