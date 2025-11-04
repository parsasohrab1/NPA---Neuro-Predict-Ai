"""
Visualize Sample Medical Data
Creates charts and visualizations for the NeuroPredict-AI sample dataset
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_data():
    """Load the sample dataset"""
    csv_path = Path('data/csv/sample_dataset_complete.csv')
    if not csv_path.exists():
        csv_path = Path('csv/sample_dataset_complete.csv')
    
    return pd.read_csv(csv_path)

def plot_diagnosis_distribution(data):
    """Plot diagnosis distribution pie chart"""
    plt.figure(figsize=(10, 6))
    
    counts = data['diagnosis'].value_counts()
    colors = ['#4ade80', '#fbbf24', '#ef4444']
    
    plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Diagnosis Distribution', fontsize=16, fontweight='bold')
    plt.axis('equal')
    
    plt.tight_layout()
    plt.savefig('data/visualizations/diagnosis_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: diagnosis_distribution.png")

def plot_cognitive_scores(data):
    """Plot cognitive scores by diagnosis"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # MMSE scores
    sns.boxplot(data=data, x='diagnosis', y='mmse_score', ax=axes[0],
                palette={'Normal': '#4ade80', 'Alzheimer': '#ef4444', 'Parkinson': '#fbbf24'})
    axes[0].set_title('MMSE Score by Diagnosis', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('MMSE Score (0-30)')
    axes[0].set_xlabel('Diagnosis')
    
    # MoCA scores
    sns.boxplot(data=data, x='diagnosis', y='moca_score', ax=axes[1],
                palette={'Normal': '#4ade80', 'Alzheimer': '#ef4444', 'Parkinson': '#fbbf24'})
    axes[1].set_title('MoCA Score by Diagnosis', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('MoCA Score (0-30)')
    axes[1].set_xlabel('Diagnosis')
    
    plt.tight_layout()
    plt.savefig('data/visualizations/cognitive_scores.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: cognitive_scores.png")

def plot_biomarkers(data):
    """Plot biomarker levels by diagnosis"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    biomarkers = ['amyloid_beta', 'tau_protein', 'dopamine_level']
    titles = ['Amyloid-beta (pg/mL)', 'Tau Protein (pg/mL)', 'Dopamine (ng/mL)']
    
    for ax, biomarker, title in zip(axes, biomarkers, titles):
        sns.boxplot(data=data, x='diagnosis', y=biomarker, ax=ax,
                   palette={'Normal': '#4ade80', 'Alzheimer': '#ef4444', 'Parkinson': '#fbbf24'})
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Level')
        ax.set_xlabel('Diagnosis')
    
    plt.tight_layout()
    plt.savefig('data/visualizations/biomarkers.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: biomarkers.png")

def plot_mri_features(data):
    """Plot MRI features by diagnosis"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Hippocampal volume
    sns.boxplot(data=data, x='diagnosis', y='hippocampal_volume', ax=axes[0],
                palette={'Normal': '#4ade80', 'Alzheimer': '#ef4444', 'Parkinson': '#fbbf24'})
    axes[0].set_title('Hippocampal Volume by Diagnosis', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Volume (mm³)')
    axes[0].set_xlabel('Diagnosis')
    
    # Cortical thickness
    sns.boxplot(data=data, x='diagnosis', y='cortical_thickness', ax=axes[1],
                palette={'Normal': '#4ade80', 'Alzheimer': '#ef4444', 'Parkinson': '#fbbf24'})
    axes[1].set_title('Cortical Thickness by Diagnosis', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Thickness (mm)')
    axes[1].set_xlabel('Diagnosis')
    
    plt.tight_layout()
    plt.savefig('data/visualizations/mri_features.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: mri_features.png")

def plot_age_distribution(data):
    """Plot age distribution by diagnosis"""
    plt.figure(figsize=(12, 6))
    
    for diagnosis, color in [('Normal', '#4ade80'), ('Alzheimer', '#ef4444'), ('Parkinson', '#fbbf24')]:
        subset = data[data['diagnosis'] == diagnosis]
        plt.hist(subset['age'], alpha=0.6, label=diagnosis, bins=15, color=color)
    
    plt.title('Age Distribution by Diagnosis', fontsize=16, fontweight='bold')
    plt.xlabel('Age (years)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/visualizations/age_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: age_distribution.png")

def plot_correlation_matrix(data):
    """Plot correlation matrix of key features"""
    features = ['age', 'mmse_score', 'moca_score', 'amyloid_beta', 
                'tau_protein', 'dopamine_level', 'hippocampal_volume', 
                'cortical_thickness']
    
    plt.figure(figsize=(12, 10))
    
    corr = data[features].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1)
    
    plt.title('Feature Correlation Matrix', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('data/visualizations/correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: correlation_matrix.png")

def visualize_sample_mri():
    """Visualize sample MRI images"""
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()
    
    image_files = [
        ('data/images/PT_0001_Normal.npy', 'Normal 1'),
        ('data/images/PT_0002_Normal.npy', 'Normal 2'),
        ('data/images/PT_0003_Normal.npy', 'Normal 3'),
        ('data/images/PT_0004_Normal.npy', 'Normal 4'),
        ('data/images/PT_0005_Normal.npy', 'Normal 5'),
        ('data/images/PT_0071_Alzheimer.npy', 'Alzheimer 1'),
        ('data/images/PT_0072_Alzheimer.npy', 'Alzheimer 2'),
        ('data/images/PT_0073_Alzheimer.npy', 'Alzheimer 3'),
        ('data/images/PT_0091_Parkinson.npy', 'Parkinson 1'),
        ('data/images/PT_0092_Parkinson.npy', 'Parkinson 2'),
    ]
    
    for ax, (file_path, title) in zip(axes, image_files):
        try:
            img = np.load(file_path)
            ax.imshow(img, cmap='gray')
            ax.set_title(title, fontsize=10)
            ax.axis('off')
        except:
            ax.text(0.5, 0.5, 'Image not found', ha='center', va='center')
            ax.set_title(title, fontsize=10)
            ax.axis('off')
    
    plt.suptitle('Sample Synthetic MRI Images (64x64)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('data/visualizations/sample_mri_images.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: sample_mri_images.png")

def main():
    """Main visualization function"""
    print("\n" + "="*60)
    print("📊 NEUROPREDICT-AI DATA VISUALIZATION")
    print("="*60 + "\n")
    
    # Create output directory
    Path('data/visualizations').mkdir(exist_ok=True)
    
    # Load data
    print("📁 Loading data...")
    data = load_data()
    print(f"✅ Loaded {len(data)} samples\n")
    
    # Generate visualizations
    print("🎨 Generating visualizations...\n")
    
    plot_diagnosis_distribution(data)
    plot_age_distribution(data)
    plot_cognitive_scores(data)
    plot_biomarkers(data)
    plot_mri_features(data)
    plot_correlation_matrix(data)
    visualize_sample_mri()
    
    print("\n" + "="*60)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*60)
    print("\nOutput directory: data/visualizations/")
    print("\nGenerated files:")
    print("  📊 diagnosis_distribution.png")
    print("  📊 age_distribution.png")
    print("  📊 cognitive_scores.png")
    print("  📊 biomarkers.png")
    print("  📊 mri_features.png")
    print("  📊 correlation_matrix.png")
    print("  📊 sample_mri_images.png")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

