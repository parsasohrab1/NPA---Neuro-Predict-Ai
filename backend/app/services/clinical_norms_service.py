"""
Clinical Norms Service
Provides age and gender-specific normal ranges for medical assessments
Replaces magic numbers with evidence-based clinical norms
"""
from typing import Dict, Optional, Tuple
from datetime import date
import logging

logger = logging.getLogger(__name__)


class ClinicalNormsService:
    """
    Service for clinical normal ranges based on age and gender
    
    Provides evidence-based normal ranges for:
    - Hippocampal volume (age and gender adjusted)
    - Cortical thickness (age and gender adjusted)
    - Ventricular volume (age adjusted)
    - Cognitive scores (age and education adjusted)
    - Biomarker levels (age adjusted)
    """
    
    @staticmethod
    def get_hippocampal_volume_norms(age: float, gender: str) -> Dict[str, float]:
        """
        Get normal hippocampal volume ranges based on age and gender
        
        Based on clinical literature:
        - Normal range decreases with age
        - Males typically have larger volumes than females
        - Age-related atrophy accelerates after 65
        
        Returns:
            Dictionary with mean, std, normal_min, normal_max
        """
        # Base volumes (mm³) for healthy adults (age 20-30)
        if gender.lower() in ['male', 'm']:
            base_mean = 3800.0
            base_std = 400.0
        else:  # female
            base_mean = 3500.0
            base_std = 380.0
        
        # Age-related decline (mm³ per year)
        # Linear decline: ~15-20 mm³/year after age 30
        # Accelerated decline after 65: ~25-30 mm³/year
        
        if age <= 30:
            age_adjustment = 0.0
        elif age <= 65:
            age_adjustment = (age - 30) * 18.0  # ~18 mm³/year
        else:
            # Accelerated decline after 65
            age_adjustment = (35 * 18.0) + ((age - 65) * 27.0)  # ~27 mm³/year
        
        mean_volume = base_mean - age_adjustment
        std_volume = base_std + (age - 30) * 2.0 if age > 30 else base_std  # Increased variability with age
        
        # Normal range: mean ± 2*std (covers ~95% of healthy population)
        normal_min = mean_volume - 2 * std_volume
        normal_max = mean_volume + 2 * std_volume
        
        # Clinical thresholds
        mild_atrophy = mean_volume - 1 * std_volume
        moderate_atrophy = mean_volume - 2 * std_volume
        severe_atrophy = mean_volume - 3 * std_volume
        
        return {
            'mean': mean_volume,
            'std': std_volume,
            'normal_min': max(2000.0, normal_min),  # Floor at 2000
            'normal_max': normal_max,
            'mild_atrophy_threshold': mild_atrophy,
            'moderate_atrophy_threshold': moderate_atrophy,
            'severe_atrophy_threshold': severe_atrophy,
            'age': age,
            'gender': gender
        }
    
    @staticmethod
    def get_cortical_thickness_norms(age: float, gender: str) -> Dict[str, float]:
        """
        Get normal cortical thickness ranges based on age and gender
        
        Based on clinical literature:
        - Normal thickness: ~2.5-3.0 mm in young adults
        - Age-related thinning: ~0.01-0.02 mm/year
        - Accelerated thinning after 65
        
        Returns:
            Dictionary with mean, std, normal_min, normal_max
        """
        # Base thickness (mm) for healthy adults (age 20-30)
        if gender.lower() in ['male', 'm']:
            base_mean = 2.65
            base_std = 0.15
        else:  # female
            base_mean = 2.60
            base_std = 0.14
        
        # Age-related thinning (mm per year)
        if age <= 30:
            age_adjustment = 0.0
        elif age <= 65:
            age_adjustment = (age - 30) * 0.015  # ~0.015 mm/year
        else:
            # Accelerated thinning after 65
            age_adjustment = (35 * 0.015) + ((age - 65) * 0.025)  # ~0.025 mm/year
        
        mean_thickness = base_mean - age_adjustment
        std_thickness = base_std + (age - 30) * 0.001 if age > 30 else base_std
        
        normal_min = mean_thickness - 2 * std_thickness
        normal_max = mean_thickness + 2 * std_thickness
        
        # Clinical thresholds
        mild_thinning = mean_thickness - 1 * std_thickness
        moderate_thinning = mean_thickness - 2 * std_thickness
        severe_thinning = mean_thickness - 3 * std_thickness
        
        return {
            'mean': mean_thickness,
            'std': std_thickness,
            'normal_min': max(1.5, normal_min),  # Floor at 1.5 mm
            'normal_max': min(3.5, normal_max),  # Ceiling at 3.5 mm
            'mild_thinning_threshold': mild_thinning,
            'moderate_thinning_threshold': moderate_thinning,
            'severe_thinning_threshold': severe_thinning,
            'age': age,
            'gender': gender
        }
    
    @staticmethod
    def get_ventricular_volume_norms(age: float) -> Dict[str, float]:
        """
        Get normal ventricular volume ranges based on age
        
        Ventricular volume increases with age due to brain atrophy
        
        Returns:
            Dictionary with mean, std, normal_min, normal_max
        """
        # Base volume (mm³) for healthy adults (age 20-30)
        base_mean = 25000.0
        base_std = 5000.0
        
        # Age-related enlargement (mm³ per year)
        if age <= 30:
            age_adjustment = 0.0
        elif age <= 65:
            age_adjustment = (age - 30) * 400.0  # ~400 mm³/year
        else:
            # Accelerated enlargement after 65
            age_adjustment = (35 * 400.0) + ((age - 65) * 600.0)  # ~600 mm³/year
        
        mean_volume = base_mean + age_adjustment
        std_volume = base_std + (age - 30) * 200.0 if age > 30 else base_std
        
        normal_min = max(15000.0, mean_volume - 2 * std_volume)
        normal_max = mean_volume + 2 * std_volume
        
        # Clinical thresholds
        mild_enlargement = mean_volume + 1 * std_volume
        moderate_enlargement = mean_volume + 2 * std_volume
        severe_enlargement = mean_volume + 3 * std_volume
        
        return {
            'mean': mean_volume,
            'std': std_volume,
            'normal_min': normal_min,
            'normal_max': normal_max,
            'mild_enlargement_threshold': mild_enlargement,
            'moderate_enlargement_threshold': moderate_enlargement,
            'severe_enlargement_threshold': severe_enlargement,
            'age': age
        }
    
    @staticmethod
    def get_brain_volume_norms(age: float, gender: str) -> Dict[str, float]:
        """
        Get normal total brain volume ranges based on age and gender
        
        Returns:
            Dictionary with mean, std, normal_min, normal_max
        """
        # Base volumes (mm³) for healthy adults (age 20-30)
        if gender.lower() in ['male', 'm']:
            base_mean = 1200000.0
            base_std = 100000.0
        else:  # female
            base_mean = 1100000.0
            base_std = 95000.0
        
        # Age-related volume loss (mm³ per year)
        if age <= 30:
            age_adjustment = 0.0
        elif age <= 65:
            age_adjustment = (age - 30) * 2000.0  # ~2000 mm³/year
        else:
            # Accelerated loss after 65
            age_adjustment = (35 * 2000.0) + ((age - 65) * 3000.0)  # ~3000 mm³/year
        
        mean_volume = base_mean - age_adjustment
        std_volume = base_std + (age - 30) * 1000.0 if age > 30 else base_std
        
        normal_min = mean_volume - 2 * std_volume
        normal_max = mean_volume + 2 * std_volume
        
        return {
            'mean': mean_volume,
            'std': std_volume,
            'normal_min': max(800000.0, normal_min),
            'normal_max': normal_max,
            'age': age,
            'gender': gender
        }
    
    @staticmethod
    def get_cognitive_score_norms(age: float, education_years: int) -> Dict[str, float]:
        """
        Get normal cognitive score ranges based on age and education
        
        Education has protective effect on cognitive scores
        Age-related decline is expected but varies by education
        
        Returns:
            Dictionary with norms for MMSE, MoCA, and domain scores
        """
        # MMSE norms (0-30)
        # Base MMSE for highly educated (16+ years): ~29
        # Base MMSE for low education (<12 years): ~26
        
        if education_years >= 16:
            mmse_base = 29.0
            mmse_std = 1.0
        elif education_years >= 12:
            mmse_base = 28.0
            mmse_std = 1.5
        else:
            mmse_base = 26.0
            mmse_std = 2.0
        
        # Age-related decline
        if age <= 60:
            mmse_adjustment = 0.0
        elif age <= 75:
            mmse_adjustment = (age - 60) * 0.1  # ~0.1 points/year
        else:
            mmse_adjustment = (15 * 0.1) + ((age - 75) * 0.2)  # Accelerated after 75
        
        mmse_mean = mmse_base - mmse_adjustment
        mmse_normal_min = max(20.0, mmse_mean - 2 * mmse_std)
        
        # MoCA norms (0-30) - similar to MMSE but slightly more sensitive
        moca_base = mmse_base - 1.0  # MoCA typically 1-2 points lower
        moca_std = mmse_std + 0.5
        moca_mean = moca_base - mmse_adjustment
        moca_normal_min = max(20.0, moca_mean - 2 * moca_std)
        
        # Domain scores (0-100) - age and education adjusted
        # Higher education = higher baseline
        education_factor = min(1.0, education_years / 16.0)  # Normalize to 16 years
        
        memory_base = 75.0 + (education_factor * 15.0)  # 75-90 range
        attention_base = 70.0 + (education_factor * 20.0)  # 70-90 range
        executive_base = 72.0 + (education_factor * 18.0)  # 72-90 range
        
        # Age decline (more pronounced for memory)
        if age <= 60:
            age_factor = 0.0
        elif age <= 75:
            age_factor = (age - 60) / 15.0  # 0 to 1.0
        else:
            age_factor = 1.0 + ((age - 75) / 10.0)  # >1.0 after 75
        
        memory_mean = memory_base - (age_factor * 20.0)
        attention_mean = attention_base - (age_factor * 15.0)
        executive_mean = executive_base - (age_factor * 18.0)
        
        return {
            'mmse': {
                'mean': mmse_mean,
                'std': mmse_std,
                'normal_min': mmse_normal_min,
                'normal_max': 30.0,
                'mild_impairment': 24.0,
                'moderate_impairment': 20.0,
                'severe_impairment': 15.0
            },
            'moca': {
                'mean': moca_mean,
                'std': moca_std,
                'normal_min': moca_normal_min,
                'normal_max': 30.0,
                'mild_impairment': 22.0,
                'moderate_impairment': 18.0,
                'severe_impairment': 12.0
            },
            'memory': {
                'mean': memory_mean,
                'std': 10.0,
                'normal_min': max(50.0, memory_mean - 20.0),
                'normal_max': 100.0
            },
            'attention': {
                'mean': attention_mean,
                'std': 10.0,
                'normal_min': max(50.0, attention_mean - 20.0),
                'normal_max': 100.0
            },
            'executive': {
                'mean': executive_mean,
                'std': 10.0,
                'normal_min': max(50.0, executive_mean - 20.0),
                'normal_max': 100.0
            },
            'age': age,
            'education_years': education_years
        }
    
    @staticmethod
    def get_biomarker_norms(age: float) -> Dict[str, float]:
        """
        Get normal biomarker ranges based on age
        
        Some biomarkers change with age (e.g., amyloid-beta decreases with age)
        
        Returns:
            Dictionary with norms for amyloid-beta, tau, dopamine
        """
        # Amyloid-beta (pg/mL)
        # Normal range: 600-1200 pg/mL in young adults
        # Decreases with age (normal aging)
        # Pathological: <450 pg/mL
        
        if age <= 50:
            abeta_mean = 800.0
            abeta_std = 150.0
        elif age <= 70:
            abeta_mean = 700.0 - ((age - 50) * 5.0)  # ~5 pg/mL/year decline
            abeta_std = 180.0
        else:
            abeta_mean = 600.0 - ((age - 70) * 8.0)  # Accelerated decline
            abeta_std = 200.0
        
        abeta_normal_min = max(200.0, abeta_mean - 2 * abeta_std)
        abeta_normal_max = abeta_mean + 2 * abeta_std
        
        # Tau protein (pg/mL)
        # Normal range: 150-250 pg/mL
        # Pathological: >350 pg/mL
        tau_mean = 200.0
        tau_std = 50.0
        if age > 65:
            tau_mean = 220.0  # Slight increase with age
            tau_std = 60.0
        
        tau_normal_min = max(100.0, tau_mean - 2 * tau_std)
        tau_normal_max = tau_mean + 2 * tau_std
        
        # Dopamine (ng/mL)
        # Normal range: 80-150 ng/mL
        # Pathological: <60 ng/mL
        dopamine_mean = 120.0
        dopamine_std = 25.0
        if age > 60:
            dopamine_mean = 110.0 - ((age - 60) * 1.0)  # ~1 ng/mL/year decline
            dopamine_std = 30.0
        
        dopamine_normal_min = max(50.0, dopamine_mean - 2 * dopamine_std)
        dopamine_normal_max = dopamine_mean + 2 * dopamine_std
        
        return {
            'amyloid_beta': {
                'mean': abeta_mean,
                'std': abeta_std,
                'normal_min': abeta_normal_min,
                'normal_max': abeta_normal_max,
                'pathological_threshold': 450.0
            },
            'tau_protein': {
                'mean': tau_mean,
                'std': tau_std,
                'normal_min': tau_normal_min,
                'normal_max': tau_normal_max,
                'pathological_threshold': 350.0
            },
            'dopamine': {
                'mean': dopamine_mean,
                'std': dopamine_std,
                'normal_min': dopamine_normal_min,
                'normal_max': dopamine_normal_max,
                'pathological_threshold': 60.0
            },
            'age': age
        }
    
    @staticmethod
    def assess_against_norms(
        value: float,
        norms: Dict[str, float],
        higher_is_better: bool = True
    ) -> Tuple[float, float]:
        """
        Assess a value against clinical norms
        
        Args:
            value: Value to assess
            norms: Dictionary with 'mean', 'std', 'normal_min', 'normal_max'
            higher_is_better: Whether higher values are better (True) or lower (False)
        
        Returns:
            Tuple of (score 0-100, confidence 0-1)
        """
        if value is None:
            return 50.0, 0.0
        
        mean = norms['mean']
        std = norms['std']
        normal_min = norms.get('normal_min', mean - 2 * std)
        normal_max = norms.get('normal_max', mean + 2 * std)
        
        # Calculate z-score
        if std > 0:
            z_score = (value - mean) / std
        else:
            z_score = 0.0
        
        # Convert to score (0-100)
        if higher_is_better:
            # Higher is better (e.g., hippocampal volume, cognitive scores)
            if value >= normal_max:
                score = 100.0
            elif value >= mean:
                # Between mean and max: linear interpolation
                score = 75.0 + 25.0 * ((value - mean) / (normal_max - mean))
            elif value >= normal_min:
                # Between min and mean: linear interpolation
                score = 50.0 + 25.0 * ((value - normal_min) / (mean - normal_min))
            elif value >= normal_min - std:
                # Below normal but not severely
                score = 25.0 + 25.0 * ((value - (normal_min - std)) / std)
            else:
                # Severely below normal
                score = max(0.0, 25.0 * ((value / (normal_min - std))))
        else:
            # Lower is better (e.g., ventricular volume, tau protein)
            if value <= normal_min:
                score = 100.0
            elif value <= mean:
                score = 75.0 + 25.0 * ((mean - value) / (mean - normal_min))
            elif value <= normal_max:
                score = 50.0 + 25.0 * ((normal_max - value) / (normal_max - mean))
            elif value <= normal_max + std:
                score = 25.0 + 25.0 * (((normal_max + std) - value) / std)
            else:
                score = max(0.0, 100.0 - (25.0 * ((value - (normal_max + std)) / std)))
        
        # Confidence based on how far from mean (closer = higher confidence)
        # Also consider if value is within normal range
        if normal_min <= value <= normal_max:
            confidence = 0.9  # High confidence for normal range
        elif (normal_min - std) <= value <= (normal_max + std):
            confidence = 0.7  # Moderate confidence
        else:
            confidence = 0.5  # Lower confidence for outliers
        
        return min(100.0, max(0.0, score)), confidence


# Global instance
_clinical_norms_service = None


def get_clinical_norms_service() -> ClinicalNormsService:
    """Get or create the global clinical norms service instance"""
    global _clinical_norms_service
    if _clinical_norms_service is None:
        _clinical_norms_service = ClinicalNormsService()
    return _clinical_norms_service

