"""
PATENT-PENDING: Data Fusion Service
Multi-Modal Medical Data Fusion and Interpretation Algorithm
Now uses Deep Learning model for score predictions
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import time
import numpy as np
import logging

from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.data_fusion_report import (
    DataFusionReport, 
    FusionConfidence, 
    FusionInterpretation
)

logger = logging.getLogger(__name__)
from .data_fusion_model_service import get_data_fusion_model_service
from .data_fusion_xai_service import get_data_fusion_xai_service
from .clinical_norms_service import get_clinical_norms_service
from .natural_language_service import get_natural_language_service


class DataFusionService:
    """
    PATENT-PENDING: Multi-Modal Data Fusion Algorithm
    
    This service implements our proprietary data fusion methodology that:
    1. Integrates cognitive, biomarker, and imaging data
    2. Applies weighted correlation analysis
    3. Detects cross-modal inconsistencies
    4. Generates confidence-weighted interpretations
    5. Produces natural language clinical reports
    
    Key Innovation: Multi-modal fusion with conflict resolution
    """
    
    @staticmethod
    async def generate_fusion_report(
        patient_id: int,
        medical_record_id: int,
        db: AsyncSession
    ) -> DataFusionReport:
        """
        Generate a comprehensive data fusion report for a patient
        
        PATENT-PENDING ALGORITHM:
        - Multi-modal weighted fusion
        - Cross-modal correlation analysis
        - Confidence-based interpretation
        - Automated natural language generation
        """
        start_time = time.time()
        
        # Fetch patient and medical record
        result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        
        result = await db.execute(
            select(MedicalRecord).where(MedicalRecord.id == medical_record_id)
        )
        medical_record = result.scalar_one_or_none()
        
        if not patient or not medical_record:
            raise ValueError("Patient or medical record not found")
        
        # ====================================================================
        # STEP 1: USE DEEP LEARNING MODEL FOR SCORE PREDICTIONS
        # ====================================================================
        
        # Try to use trained Deep Learning model
        model_service = get_data_fusion_model_service()
        using_dl_model = False
        
        if model_service.is_loaded():
            using_dl_model = True
            # Extract features
            features = DataFusionService._extract_features_for_model(medical_record, patient)
            
            # Get predictions from model
            predictions = model_service.predict_scores(features)
            
            # Extract scores from model predictions
            cognitive_score = predictions.get('cognitive_score', 50.0)
            biomarker_score = predictions.get('biomarker_score', 50.0)
            imaging_score = predictions.get('imaging_score', 50.0)
            cognitive_conf = predictions.get('cognitive_confidence', 0.5)
            biomarker_conf = predictions.get('biomarker_confidence', 0.5)
            imaging_conf = predictions.get('imaging_confidence', 0.5)
            
            # Correlations
            correlations = {
                'cognitive_biomarker': predictions.get('cognitive_biomarker_correlation', 0.5),
                'cognitive_imaging': predictions.get('cognitive_imaging_correlation', 0.5),
                'biomarker_imaging': predictions.get('biomarker_imaging_correlation', 0.5),
            }
            
            # Integrated fusion score
            integrated_score = predictions.get('integrated_fusion_score', 50.0)
            
            # Consistency score
            consistency_score = DataFusionService._assess_cross_modal_consistency(correlations)
            has_conflicts = consistency_score < 60
            
            # Fusion confidence
            fusion_confidence = DataFusionService._determine_fusion_confidence(
                cognitive_conf, biomarker_conf, imaging_conf, consistency_score
            )
            
            # Disease-specific analysis
            ad_analysis = {
                'score': predictions.get('alzheimer_fusion_score', 0.0),
                'confidence': (cognitive_conf + biomarker_conf) / 2.0,
                'amyloid_tau_concordance': predictions.get('alzheimer_concordance', 50.0),
                'cognitive_biomarker_alignment': predictions.get('alzheimer_alignment', 50.0),
                'hippocampal_correlation': predictions.get('alzheimer_hippo_corr', 50.0),
            }
            
            pd_analysis = {
                'score': predictions.get('parkinson_fusion_score', 0.0),
                'confidence': (cognitive_conf + biomarker_conf) / 2.0,
                'dopamine_cognitive_concordance': predictions.get('parkinson_concordance', 50.0),
                'motor_cognitive_alignment': predictions.get('parkinson_alignment', 50.0),
                'imaging_biomarker_correlation': predictions.get('parkinson_corr', 50.0),
            }
        else:
            # Fallback to manual calculations with clinical norms
            # ====================================================================
            # STEP 1: ASSESS INDIVIDUAL MODALITIES (Using Clinical Norms)
            # ====================================================================
            
            # Use age and gender-adjusted clinical norms instead of fixed thresholds
            cognitive_score, cognitive_conf = DataFusionService._assess_cognitive_modality(medical_record, patient)
            biomarker_score, biomarker_conf = DataFusionService._assess_biomarker_modality(medical_record, patient)
            imaging_score, imaging_conf = DataFusionService._assess_imaging_modality(medical_record, patient)
            
            # ====================================================================
            # STEP 2: CALCULATE CROSS-MODAL CORRELATIONS (PATENT-PENDING)
            # ====================================================================
            
            correlations = DataFusionService._calculate_cross_modal_correlations(
                medical_record, cognitive_score, biomarker_score, imaging_score
            )
            
            consistency_score = DataFusionService._assess_cross_modal_consistency(correlations)
            has_conflicts = consistency_score < 60
            
            # ====================================================================
            # STEP 3: WEIGHTED FUSION (PATENT-PENDING)
            # ====================================================================
            
            integrated_score = DataFusionService._calculate_integrated_fusion_score(
                cognitive_score, biomarker_score, imaging_score,
                cognitive_conf, biomarker_conf, imaging_conf
            )
            
            fusion_confidence = DataFusionService._determine_fusion_confidence(
                cognitive_conf, biomarker_conf, imaging_conf, consistency_score
            )
            
            # ====================================================================
            # STEP 4: DISEASE-SPECIFIC FUSION ANALYSIS (PATENT-PENDING)
            # ====================================================================
            
            ad_analysis = DataFusionService._analyze_alzheimer_fusion(medical_record, patient)
            pd_analysis = DataFusionService._analyze_parkinson_fusion(medical_record, patient)
        
        # ====================================================================
        # STEP 5: GENERATE INTERPRETATION (PATENT-PENDING)
        # ====================================================================
        
        interpretation = DataFusionService._generate_interpretation(
            integrated_score, ad_analysis, pd_analysis, correlations
        )
        
        # ====================================================================
        # STEP 6: GENERATE NATURAL LANGUAGE REPORT (PATENT-PENDING)
        # ====================================================================
        
            # Generate report using Natural Language Service
            nlg_service = get_natural_language_service()
            report_sections = nlg_service.generate_fusion_report(
                patient=patient,
                record=medical_record,
                cog_score=cognitive_score,
                bio_score=biomarker_score,
                img_score=imaging_score,
                fusion_score=integrated_score,
                ad_analysis=ad_analysis,
                pd_analysis=pd_analysis,
                interpretation=interpretation,
                correlations=correlations,
                xai_explanation=xai_explanation
            )
        
        # ====================================================================
        # STEP 7: DATA QUALITY ASSESSMENT
        # ====================================================================
        
        completeness = DataFusionService._assess_data_completeness(medical_record)
        outliers = DataFusionService._detect_outliers(medical_record)
        
        # ====================================================================
        # STEP 8: PATENT CLAIM 3 - GENERATE DYNAMIC EVIDENCE (XAI)
        # ====================================================================
        
        xai_evidence = None
        xai_method = None
        has_xai = False
        
        if using_dl_model:
            try:
                # Get XAI service
                xai_service = get_data_fusion_xai_service(model_service.model)
                
                # Prepare fusion scores for XAI
                fusion_scores_dict = {
                    'cognitive_score': cognitive_score,
                    'biomarker_score': biomarker_score,
                    'imaging_score': imaging_score,
                    'integrated_fusion_score': integrated_score,
                    'alzheimer_fusion_score': ad_analysis['score'],
                    'parkinson_fusion_score': pd_analysis['score'],
                    'fusion_confidence': float(fusion_confidence.value) if hasattr(fusion_confidence, 'value') else 0.5
                }
                
                # Generate dynamic evidence (PATENT CLAIM 3)
                xai_evidence = xai_service.generate_dynamic_evidence(
                    medical_record=medical_record,
                    patient=patient,
                    fusion_scores=fusion_scores_dict,
                    method='integrated_gradients'
                )
                xai_method = 'integrated_gradients'
                has_xai = True
                
            except Exception as e:
                logger.warning(f"Could not generate XAI evidence: {e}")
                xai_evidence = None
        
        # ====================================================================
        # CREATE FUSION REPORT
        # ====================================================================
        
        processing_time = int((time.time() - start_time) * 1000)
        
        fusion_report = DataFusionReport(
            patient_id=patient_id,
            medical_record_id=medical_record_id,
            
            # Modality Scores
            cognitive_modality_score=cognitive_score,
            biomarker_modality_score=biomarker_score,
            imaging_modality_score=imaging_score,
            
            # Confidence Weights
            cognitive_confidence=cognitive_conf,
            biomarker_confidence=biomarker_conf,
            imaging_confidence=imaging_conf,
            
            # Integrated Fusion
            integrated_fusion_score=integrated_score,
            fusion_confidence=fusion_confidence,
            
            # Cross-Modal Analysis
            cognitive_biomarker_correlation=correlations['cognitive_biomarker'],
            cognitive_imaging_correlation=correlations['cognitive_imaging'],
            biomarker_imaging_correlation=correlations['biomarker_imaging'],
            cross_modal_consistency_score=consistency_score,
            has_conflicting_findings=1 if has_conflicts else 0,
            
            # Alzheimer's Analysis
            alzheimer_fusion_score=ad_analysis['score'],
            alzheimer_confidence=ad_analysis['confidence'],
            ad_amyloid_tau_concordance=ad_analysis['amyloid_tau_concordance'],
            ad_cognitive_biomarker_alignment=ad_analysis['cognitive_biomarker_alignment'],
            ad_hippocampal_correlation=ad_analysis['hippocampal_correlation'],
            
            # Parkinson's Analysis
            parkinson_fusion_score=pd_analysis['score'],
            parkinson_confidence=pd_analysis['confidence'],
            pd_dopamine_cognitive_concordance=pd_analysis['dopamine_cognitive_concordance'],
            pd_motor_cognitive_alignment=pd_analysis['motor_cognitive_alignment'],
            pd_imaging_biomarker_correlation=pd_analysis['imaging_biomarker_correlation'],
            
            # Interpretation
            overall_interpretation=interpretation['overall'],
            primary_concern=interpretation['primary_concern'],
            interpretation_confidence=interpretation['confidence'],
            cognitive_evidence=interpretation['evidence']['cognitive'],
            biomarker_evidence=interpretation['evidence']['biomarker'],
            imaging_evidence=interpretation['evidence']['imaging'],
            
            # Report Sections
            executive_summary=report_sections.get('executive_summary', ''),
            detailed_findings=report_sections.get('detailed_findings', ''),
            risk_assessment=report_sections.get('risk_assessment') or report_sections.get('disease_analysis', ''),
            recommendations=report_sections.get('recommendations', ''),
            follow_up_plan=report_sections.get('follow_up_plan') or report_sections.get('technical_notes', ''),
            
            # Quality Metrics
            data_completeness_score=completeness,
            has_outlier_findings=1 if outliers['has_outliers'] else 0,
            data_quality_notes=outliers.get('description'),
            
            # Metadata
            processing_time_ms=processing_time,
            algorithm_version="2.0.0-DL" if using_dl_model else "1.0.0",
            report_version="1.0.0",
            
            # PATENT CLAIM 3: XAI Dynamic Evidence
            xai_evidence=xai_evidence,
            xai_method=xai_method,
            has_xai_explanation=1 if has_xai else 0,
        )
        
        return fusion_report
    
    # ========================================================================
    # Feature Extraction for Deep Learning Model
    # ========================================================================
    
    @staticmethod
    def _extract_features_for_model(medical_record: MedicalRecord, patient: Patient) -> np.ndarray:
        """
        Extract features from medical record for model input
        
        Returns normalized feature vector matching training data format
        """
        features = []
        
        # Cognitive features (normalized)
        features.append(medical_record.mmse_score / 30.0 if medical_record.mmse_score is not None else 0.0)
        features.append(medical_record.moca_score / 30.0 if medical_record.moca_score is not None else 0.0)
        features.append(medical_record.memory_score / 100.0 if medical_record.memory_score is not None else 0.0)
        features.append(medical_record.attention_score / 100.0 if medical_record.attention_score is not None else 0.0)
        features.append(medical_record.executive_function_score / 100.0 if medical_record.executive_function_score is not None else 0.0)
        
        # Biomarker features (normalized)
        features.append((medical_record.amyloid_beta - 200) / 800.0 if medical_record.amyloid_beta is not None else 0.0)
        features.append((medical_record.tau_protein - 100) / 700.0 if medical_record.tau_protein is not None else 0.0)
        features.append((medical_record.dopamine_level - 50) / 150.0 if medical_record.dopamine_level is not None else 0.0)
        features.append(1.0 if medical_record.apoe_e4_status else 0.0 if medical_record.apoe_e4_status is not None else 0.0)
        
        # Imaging features (normalized)
        features.append((medical_record.hippocampal_volume - 2000) / 2000.0 if medical_record.hippocampal_volume is not None else 0.0)
        features.append((medical_record.cortical_thickness - 1.5) / 1.5 if medical_record.cortical_thickness is not None else 0.0)
        features.append((medical_record.ventricular_volume - 20000) / 30000.0 if medical_record.ventricular_volume is not None else 0.0)
        features.append((medical_record.white_matter_hyperintensities - 0) / 20.0 if medical_record.white_matter_hyperintensities is not None else 0.0)
        features.append((medical_record.brain_volume_total - 1000000) / 200000.0 if medical_record.brain_volume_total is not None else 0.0)
        
        # Patient demographics
        age = (datetime.now().date() - patient.date_of_birth).days / 365.25
        features.append(age / 100.0)  # Normalize age
        features.append(1.0 if patient.gender.value == 'male' else 0.0)
        features.append((patient.education_years or 12) / 20.0)  # Normalize education
        
        return np.array(features, dtype=np.float32)
    
    # ========================================================================
    # PATENT-PENDING: Individual Modality Assessment Methods
    # (Kept as fallback when model is not available)
    # ========================================================================
    
    @staticmethod
    def _assess_cognitive_modality(record: MedicalRecord, patient: Optional[Patient] = None) -> tuple[float, float]:
        """
        Assess cognitive modality using clinical norms based on age and education
        Returns: (score 0-100, confidence 0-1)
        """
        if not patient:
            # Fallback to simple assessment if patient not provided
            return DataFusionService._assess_cognitive_modality_simple(record)
        
        norms_service = get_clinical_norms_service()
        
        # Calculate age
        age = (datetime.now().date() - patient.date_of_birth).days / 365.25
        education_years = patient.education_years or 12
        
        # Get cognitive norms
        cognitive_norms = norms_service.get_cognitive_score_norms(age, education_years)
        
        scores = []
        weights = []
        confidences = []
        
        # MMSE assessment against norms
        if record.mmse_score is not None:
            mmse_score, mmse_conf = norms_service.assess_against_norms(
                record.mmse_score,
                cognitive_norms['mmse'],
                higher_is_better=True
            )
            scores.append(mmse_score)
            weights.append(0.25)
            confidences.append(mmse_conf)
        
        # MoCA assessment against norms
        if record.moca_score is not None:
            moca_score, moca_conf = norms_service.assess_against_norms(
                record.moca_score,
                cognitive_norms['moca'],
                higher_is_better=True
            )
            scores.append(moca_score)
            weights.append(0.25)
            confidences.append(moca_conf)
        
        # Memory score assessment
        if record.memory_score is not None:
            memory_score, memory_conf = norms_service.assess_against_norms(
                record.memory_score,
                cognitive_norms['memory'],
                higher_is_better=True
            )
            scores.append(memory_score)
            weights.append(0.20)
            confidences.append(memory_conf)
        
        # Attention score assessment
        if record.attention_score is not None:
            attention_score, attention_conf = norms_service.assess_against_norms(
                record.attention_score,
                cognitive_norms['attention'],
                higher_is_better=True
            )
            scores.append(attention_score)
            weights.append(0.15)
            confidences.append(attention_conf)
        
        # Executive function score assessment
        if record.executive_function_score is not None:
            executive_score, executive_conf = norms_service.assess_against_norms(
                record.executive_function_score,
                cognitive_norms['executive'],
                higher_is_better=True
            )
            scores.append(executive_score)
            weights.append(0.15)
            confidences.append(executive_conf)
        
        if not scores:
            return 50.0, 0.0  # No data, neutral score, zero confidence
        
        # Weighted average
        total_weight = sum(weights)
        cognitive_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Confidence: average of individual confidences weighted by completeness
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            completeness_factor = len(scores) / 5.0  # Max 5 cognitive measures
            confidence = avg_confidence * completeness_factor
        else:
            confidence = len(scores) / 5.0
        
        return cognitive_score, confidence
    
    @staticmethod
    def _assess_cognitive_modality_simple(record: MedicalRecord) -> tuple[float, float]:
        """
        Simple cognitive assessment fallback (when patient info not available)
        Uses fixed thresholds instead of age/education-adjusted norms
        """
        scores = []
        weights = []
        
        if record.mmse_score is not None:
            mmse_norm = (record.mmse_score / 30) * 100
            scores.append(mmse_norm)
            weights.append(0.25)
        
        if record.moca_score is not None:
            moca_norm = (record.moca_score / 30) * 100
            scores.append(moca_norm)
            weights.append(0.25)
        
        if record.memory_score is not None:
            scores.append(record.memory_score)
            weights.append(0.20)
        
        if record.attention_score is not None:
            scores.append(record.attention_score)
            weights.append(0.15)
        
        if record.executive_function_score is not None:
            scores.append(record.executive_function_score)
            weights.append(0.15)
        
        if not scores:
            return 50.0, 0.0
        
        total_weight = sum(weights)
        cognitive_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        confidence = len(scores) / 5.0
        
        return cognitive_score, confidence
    
    @staticmethod
    def _assess_biomarker_modality(record: MedicalRecord, patient: Optional[Patient] = None) -> tuple[float, float]:
        """
        Assess biomarker modality using age-adjusted clinical norms
        Returns: (score 0-100, confidence 0-1)
        PATENT-PENDING: Disease-specific biomarker weighting with clinical norms
        """
        norms_service = get_clinical_norms_service()
        
        # Calculate age for age-adjusted norms
        if patient:
            age = (datetime.now().date() - patient.date_of_birth).days / 365.25
        else:
            age = 70.0  # Default age if patient not available
        
        # Get biomarker norms
        biomarker_norms = norms_service.get_biomarker_norms(age)
        
        scores = []
        weights = []
        confidences = []
        
        # Amyloid-beta assessment (Alzheimer indicator)
        # Lower is worse (pathological threshold: <450)
        if record.amyloid_beta is not None:
            abeta_score, abeta_conf = norms_service.assess_against_norms(
                record.amyloid_beta,
                biomarker_norms['amyloid_beta'],
                higher_is_better=True  # Higher amyloid-beta is better (normal)
            )
            # Additional penalty if below pathological threshold
            if record.amyloid_beta < biomarker_norms['amyloid_beta']['pathological_threshold']:
                abeta_score *= 0.7  # 30% penalty for pathological level
            scores.append(abeta_score)
            weights.append(0.30)
            confidences.append(abeta_conf)
        
        # Tau protein assessment (Alzheimer indicator)
        # Higher is worse (pathological threshold: >350)
        if record.tau_protein is not None:
            tau_score, tau_conf = norms_service.assess_against_norms(
                record.tau_protein,
                biomarker_norms['tau_protein'],
                higher_is_better=False  # Lower tau is better
            )
            # Additional penalty if above pathological threshold
            if record.tau_protein > biomarker_norms['tau_protein']['pathological_threshold']:
                tau_score *= 0.7  # 30% penalty for pathological level
            scores.append(tau_score)
            weights.append(0.30)
            confidences.append(tau_conf)
        
        # Dopamine assessment (Parkinson indicator)
        # Lower is worse (pathological threshold: <60)
        if record.dopamine_level is not None:
            dopamine_score, dopamine_conf = norms_service.assess_against_norms(
                record.dopamine_level,
                biomarker_norms['dopamine'],
                higher_is_better=True  # Higher dopamine is better
            )
            # Additional penalty if below pathological threshold
            if record.dopamine_level < biomarker_norms['dopamine']['pathological_threshold']:
                dopamine_score *= 0.6  # 40% penalty for pathological level
            scores.append(dopamine_score)
            weights.append(0.25)
            confidences.append(dopamine_conf)
        
        # APOE ε4 status (Alzheimer risk factor)
        # Genetic marker - fixed risk factor
        if record.apoe_e4_status is not None:
            if record.apoe_e4_status:
                apoe_score = 70.0  # Reduced score for APOE ε4 positive
            else:
                apoe_score = 100.0  # Normal score for negative
            scores.append(apoe_score)
            weights.append(0.15)
            confidences.append(0.8)  # Genetic marker, moderate confidence
        
        if not scores:
            return 50.0, 0.0
        
        # Weighted average
        total_weight = sum(weights)
        biomarker_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Confidence: average of individual confidences
        if confidences:
            confidence = sum(confidences) / len(confidences)
        else:
            confidence = len(scores) / 4.0  # Max 4 biomarker measures
        
        return biomarker_score, confidence
    
    @staticmethod
    def _assess_imaging_modality(record: MedicalRecord, patient: Optional[Patient] = None) -> tuple[float, float]:
        """
        Assess imaging modality using age and gender-adjusted clinical norms
        Returns: (score 0-100, confidence 0-1)
        PATENT-PENDING: Multi-metric MRI fusion with clinical norms
        """
        norms_service = get_clinical_norms_service()
        
        # Calculate age and get gender for norms
        if patient:
            age = (datetime.now().date() - patient.date_of_birth).days / 365.25
            gender = patient.gender.value
        else:
            age = 70.0  # Default age
            gender = 'male'  # Default gender
        
        scores = []
        weights = []
        confidences = []
        
        # Hippocampal volume assessment (age and gender adjusted)
        if record.hippocampal_volume is not None:
            hippo_norms = norms_service.get_hippocampal_volume_norms(age, gender)
            hippo_score, hippo_conf = norms_service.assess_against_norms(
                record.hippocampal_volume,
                hippo_norms,
                higher_is_better=True
            )
            # Additional assessment based on atrophy thresholds
            if record.hippocampal_volume < hippo_norms['severe_atrophy_threshold']:
                hippo_score *= 0.5  # Severe penalty for severe atrophy
            elif record.hippocampal_volume < hippo_norms['moderate_atrophy_threshold']:
                hippo_score *= 0.75  # Moderate penalty
            elif record.hippocampal_volume < hippo_norms['mild_atrophy_threshold']:
                hippo_score *= 0.9  # Mild penalty
            scores.append(hippo_score)
            weights.append(0.35)
            confidences.append(hippo_conf)
        
        # Cortical thickness assessment (age and gender adjusted)
        if record.cortical_thickness is not None:
            cortical_norms = norms_service.get_cortical_thickness_norms(age, gender)
            cortical_score, cortical_conf = norms_service.assess_against_norms(
                record.cortical_thickness,
                cortical_norms,
                higher_is_better=True
            )
            # Additional assessment based on thinning thresholds
            if record.cortical_thickness < cortical_norms['severe_thinning_threshold']:
                cortical_score *= 0.6  # Severe penalty
            elif record.cortical_thickness < cortical_norms['moderate_thinning_threshold']:
                cortical_score *= 0.8  # Moderate penalty
            elif record.cortical_thickness < cortical_norms['mild_thinning_threshold']:
                cortical_score *= 0.9  # Mild penalty
            scores.append(cortical_score)
            weights.append(0.25)
            confidences.append(cortical_conf)
        
        # Ventricular volume assessment (age adjusted)
        if record.ventricular_volume is not None:
            ventricular_norms = norms_service.get_ventricular_volume_norms(age)
            ventricular_score, ventricular_conf = norms_service.assess_against_norms(
                record.ventricular_volume,
                ventricular_norms,
                higher_is_better=False  # Lower is better
            )
            # Additional assessment based on enlargement thresholds
            if record.ventricular_volume > ventricular_norms['severe_enlargement_threshold']:
                ventricular_score *= 0.5  # Severe penalty
            elif record.ventricular_volume > ventricular_norms['moderate_enlargement_threshold']:
                ventricular_score *= 0.75  # Moderate penalty
            elif record.ventricular_volume > ventricular_norms['mild_enlargement_threshold']:
                ventricular_score *= 0.9  # Mild penalty
            scores.append(ventricular_score)
            weights.append(0.20)
            confidences.append(ventricular_conf)
        
        # White matter hyperintensities (WMH)
        # Fixed thresholds (less age-dependent, more pathology-dependent)
        if record.white_matter_hyperintensities is not None:
            wmh = record.white_matter_hyperintensities
            if wmh <= 2:
                wmh_score = 100.0
            elif wmh <= 5:
                wmh_score = 85.0
            elif wmh <= 10:
                wmh_score = 65.0
            else:
                wmh_score = 40.0
            scores.append(wmh_score)
            weights.append(0.10)
            confidences.append(0.8)
        
        # Total brain volume assessment (age and gender adjusted)
        if record.brain_volume_total is not None:
            brain_volume_norms = norms_service.get_brain_volume_norms(age, gender)
            brain_volume_score, brain_volume_conf = norms_service.assess_against_norms(
                record.brain_volume_total,
                brain_volume_norms,
                higher_is_better=True
            )
            scores.append(brain_volume_score)
            weights.append(0.10)
            confidences.append(brain_volume_conf)
        
        if not scores:
            return 50.0, 0.0
        
        # Weighted average
        total_weight = sum(weights)
        imaging_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Confidence: average of individual confidences
        if confidences:
            confidence = sum(confidences) / len(confidences)
        else:
            confidence = len(scores) / 5.0  # Max 5 imaging measures
        
        return imaging_score, confidence
    
    # ========================================================================
    # PATENT-PENDING: Cross-Modal Correlation Analysis
    # ========================================================================
    
    @staticmethod
    def _calculate_cross_modal_correlations(
        record: MedicalRecord,
        cognitive_score: float,
        biomarker_score: float,
        imaging_score: float
    ) -> Dict[str, float]:
        """
        PATENT-PENDING: Calculate correlations between modalities
        
        This method implements our proprietary algorithm for detecting
        concordance and discordance between different data modalities.
        """
        correlations = {}
        
        # Cognitive-Biomarker Correlation
        # Expected: Low cognitive should correlate with abnormal biomarkers
        # Use normalized scores (0-1) for better correlation calculation
        if cognitive_score is not None and biomarker_score is not None:
            # Normalize cognitive impairment (0 = normal, 1 = severe)
            cognitive_impairment = 1.0 - (cognitive_score / 100.0)
            # Normalize biomarker abnormality (0 = normal, 1 = severe)
            biomarker_abnormality = 1.0 - (biomarker_score / 100.0)
            # Correlation: how well they align (1.0 = perfect alignment, 0.0 = complete discordance)
            correlations['cognitive_biomarker'] = 1.0 - abs(cognitive_impairment - biomarker_abnormality)
        else:
            correlations['cognitive_biomarker'] = 0.5  # Neutral if data missing
        
        # Cognitive-Imaging Correlation
        # Expected: Low cognitive should correlate with imaging abnormalities
        if cognitive_score is not None and imaging_score is not None:
            cognitive_impairment = 1.0 - (cognitive_score / 100.0)
            imaging_abnormality = 1.0 - (imaging_score / 100.0)
            correlations['cognitive_imaging'] = 1.0 - abs(cognitive_impairment - imaging_abnormality)
        else:
            correlations['cognitive_imaging'] = 0.5
        
        # Biomarker-Imaging Correlation
        # Expected: Abnormal biomarkers should correlate with brain changes
        if biomarker_score is not None and imaging_score is not None:
            biomarker_abnormality = 1.0 - (biomarker_score / 100.0)
            imaging_abnormality = 1.0 - (imaging_score / 100.0)
            correlations['biomarker_imaging'] = 1.0 - abs(biomarker_abnormality - imaging_abnormality)
        else:
            correlations['biomarker_imaging'] = 0.5
        
        return correlations
    
    @staticmethod
    def _assess_cross_modal_consistency(correlations: Dict[str, float]) -> float:
        """
        PATENT-PENDING: Assess overall consistency between modalities
        Returns score 0-100
        """
        avg_correlation = sum(correlations.values()) / len(correlations)
        consistency_score = avg_correlation * 100
        
        # Penalize if any correlation is very low (conflict detected)
        min_correlation = min(correlations.values())
        if min_correlation < 0.4:
            consistency_score *= 0.7  # 30% penalty for major conflict
        elif min_correlation < 0.6:
            consistency_score *= 0.85  # 15% penalty for moderate conflict
        
        return min(100, max(0, consistency_score))
    
    # ========================================================================
    # PATENT-PENDING: Integrated Fusion Score Calculation
    # ========================================================================
    
    @staticmethod
    def _calculate_integrated_fusion_score(
        cog_score: float, bio_score: float, img_score: float,
        cog_conf: float, bio_conf: float, img_conf: float
    ) -> float:
        """
        PATENT-PENDING: Confidence-weighted multi-modal fusion
        
        Key Innovation: Dynamically weights each modality based on:
        - Data availability
        - Data quality
        - Cross-modal consistency
        """
        # Normalize confidences to sum to 1.0
        total_conf = cog_conf + bio_conf + img_conf
        
        if total_conf == 0:
            return 50.0  # Neutral score if no data
        
        w_cog = cog_conf / total_conf
        w_bio = bio_conf / total_conf
        w_img = img_conf / total_conf
        
        # Weighted fusion
        fusion_score = (cog_score * w_cog) + (bio_score * w_bio) + (img_score * w_img)
        
        return min(100, max(0, fusion_score))
    
    @staticmethod
    def _determine_fusion_confidence(
        cog_conf: float, bio_conf: float, img_conf: float, consistency: float
    ) -> FusionConfidence:
        """Determine overall confidence in fusion result"""
        avg_conf = (cog_conf + bio_conf + img_conf) / 3.0
        
        # Adjust based on consistency
        if consistency < 50:
            avg_conf *= 0.6  # Low consistency = lower confidence
        elif consistency < 70:
            avg_conf *= 0.8
        
        if avg_conf >= 0.9:
            return FusionConfidence.VERY_HIGH
        elif avg_conf >= 0.75:
            return FusionConfidence.HIGH
        elif avg_conf >= 0.5:
            return FusionConfidence.MODERATE
        elif avg_conf >= 0.3:
            return FusionConfidence.LOW
        else:
            return FusionConfidence.VERY_LOW
    
    # ========================================================================
    # PATENT-PENDING: Disease-Specific Fusion Analysis
    # ========================================================================
    
    @staticmethod
    def _analyze_alzheimer_fusion(record: MedicalRecord, patient: Patient) -> Dict[str, Any]:
        """
        PATENT-PENDING: Alzheimer's disease-specific multi-modal fusion
        Uses clinical norms instead of fixed thresholds
        """
        norms_service = get_clinical_norms_service()
        age = (datetime.now().date() - patient.date_of_birth).days / 365.25
        gender = patient.gender.value
        
        score = 0.0
        confidence_factors = []
        
        # Get clinical norms
        biomarker_norms = norms_service.get_biomarker_norms(age)
        cognitive_norms = norms_service.get_cognitive_score_norms(age, patient.education_years or 12)
        hippo_norms = norms_service.get_hippocampal_volume_norms(age, gender)
        
        # Amyloid-Tau Concordance (hallmark of AD)
        # Use pathological thresholds from norms
        if record.amyloid_beta is not None and record.tau_protein is not None:
            amyloid_pathological = record.amyloid_beta < biomarker_norms['amyloid_beta']['pathological_threshold']
            tau_pathological = record.tau_protein > biomarker_norms['tau_protein']['pathological_threshold']
            
            if amyloid_pathological and tau_pathological:
                concordance = 100.0
                score += 40
            elif amyloid_pathological or tau_pathological:
                concordance = 60.0
                score += 20
            else:
                concordance = 20.0
            
            confidence_factors.append(1.0)
        else:
            concordance = 50.0
        
        # Cognitive-Biomarker Alignment
        # Use age and education-adjusted cognitive norms
        alignment = 50.0
        if record.mmse_score is not None and record.amyloid_beta is not None:
            mmse_impaired = record.mmse_score < cognitive_norms['mmse']['mild_impairment']
            amyloid_abnormal = record.amyloid_beta < biomarker_norms['amyloid_beta']['pathological_threshold']
            
            if mmse_impaired and amyloid_abnormal:
                alignment = 100.0
                score += 25
            elif mmse_impaired or amyloid_abnormal:
                alignment = 60.0
                score += 12
            else:
                alignment = 30.0
            
            confidence_factors.append(0.9)
        
        # Hippocampal-Clinical Correlation
        # Use age and gender-adjusted hippocampal norms
        correlation = 50.0
        if record.hippocampal_volume is not None and record.mmse_score is not None:
            hippo_atrophy = record.hippocampal_volume < hippo_norms['moderate_atrophy_threshold']
            mmse_impaired = record.mmse_score < cognitive_norms['mmse']['mild_impairment']
            
            if hippo_atrophy and mmse_impaired:
                correlation = 100.0
                score += 35
            elif hippo_atrophy or mmse_impaired:
                correlation = 60.0
                score += 17
            else:
                correlation = 30.0
            
            confidence_factors.append(1.0)
        
        # Age factor (age > 65 increases risk)
        if age > 65:
            score += min(15, (age - 65) * 0.5)
        
        # APOE ε4 factor
        if record.apoe_e4_status:
            score += 10
            confidence_factors.append(0.8)
        
        confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
        
        return {
            'score': min(100, score),
            'confidence': confidence,
            'amyloid_tau_concordance': concordance,
            'cognitive_biomarker_alignment': alignment,
            'hippocampal_correlation': correlation,
        }
    
    @staticmethod
    def _analyze_parkinson_fusion(record: MedicalRecord, patient: Patient) -> Dict[str, Any]:
        """
        PATENT-PENDING: Parkinson's disease-specific multi-modal fusion
        Uses clinical norms instead of fixed thresholds
        """
        norms_service = get_clinical_norms_service()
        age = (datetime.now().date() - patient.date_of_birth).days / 365.25
        
        score = 0.0
        confidence_factors = []
        
        # Get clinical norms
        biomarker_norms = norms_service.get_biomarker_norms(age)
        cognitive_norms = norms_service.get_cognitive_score_norms(age, patient.education_years or 12)
        
        # Dopamine-Cognitive Concordance
        # Use age-adjusted dopamine norms and education-adjusted cognitive norms
        concordance = 50.0
        if record.dopamine_level is not None and record.attention_score is not None:
            dopamine_pathological = record.dopamine_level < biomarker_norms['dopamine']['pathological_threshold']
            attention_impaired = record.attention_score < cognitive_norms['attention']['normal_min']
            
            if dopamine_pathological and attention_impaired:
                concordance = 100.0
                score += 45
            elif dopamine_pathological or attention_impaired:
                concordance = 60.0
                score += 22
            else:
                concordance = 30.0
            
            confidence_factors.append(1.0)
        
        # Motor-Cognitive Alignment (implied by dopamine + executive function)
        alignment = 50.0
        if record.dopamine_level is not None and record.executive_function_score is not None:
            dopamine_pathological = record.dopamine_level < biomarker_norms['dopamine']['pathological_threshold']
            executive_impaired = record.executive_function_score < cognitive_norms['executive']['normal_min']
            
            if dopamine_pathological and executive_impaired:
                alignment = 100.0
                score += 30
            elif dopamine_pathological or executive_impaired:
                alignment = 60.0
                score += 15
            else:
                alignment = 30.0
            
            confidence_factors.append(0.9)
        
        # Imaging-Biomarker Correlation
        # Use age and gender-adjusted cortical thickness norms
        correlation = 50.0
        if record.dopamine_level is not None and record.cortical_thickness is not None:
            dopamine_pathological = record.dopamine_level < biomarker_norms['dopamine']['pathological_threshold']
            cortical_norms = norms_service.get_cortical_thickness_norms(age, patient.gender.value)
            cortical_thin = record.cortical_thickness < cortical_norms['moderate_thinning_threshold']
            
            if dopamine_pathological and cortical_thin:
                correlation = 90.0
                score += 25
            elif dopamine_pathological or cortical_thin:
                correlation = 55.0
                score += 12
            else:
                correlation = 35.0
            
            confidence_factors.append(0.85)
        
        # Age factor
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        if age > 60:
            score += min(10, (age - 60) * 0.3)
        
        confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
        
        return {
            'score': min(100, score),
            'confidence': confidence,
            'dopamine_cognitive_concordance': concordance,
            'motor_cognitive_alignment': alignment,
            'imaging_biomarker_correlation': correlation,
        }
    
    # ========================================================================
    # PATENT-PENDING: Interpretation Generation
    # ========================================================================
    
    @staticmethod
    def _generate_interpretation(
        fusion_score: float,
        ad_analysis: Dict,
        pd_analysis: Dict,
        correlations: Dict
    ) -> Dict[str, Any]:
        """
        PATENT-PENDING: Generate clinical interpretation from fused data
        """
        # Determine primary concern
        ad_score = ad_analysis['score']
        pd_score = pd_analysis['score']
        
        if fusion_score >= 85:
            overall = FusionInterpretation.NORMAL
            primary = "Normal cognitive and neurological function"
            confidence = 90.0
        elif fusion_score >= 70:
            overall = FusionInterpretation.MILD_CONCERN
            if ad_score > pd_score and ad_score > 30:
                primary = "Mild cognitive changes, possible MCI"
            elif pd_score > 30:
                primary = "Mild motor/cognitive changes"
            else:
                primary = "Mild age-related changes"
            confidence = 75.0
        elif fusion_score >= 50:
            overall = FusionInterpretation.MODERATE_CONCERN
            if ad_score > pd_score and ad_score > 50:
                primary = "Alzheimer's Disease - Probable"
            elif pd_score > ad_score and pd_score > 50:
                primary = "Parkinson's Disease - Probable"
            else:
                primary = "Moderate cognitive/neurological decline"
            confidence = 80.0
        elif fusion_score >= 30:
            overall = FusionInterpretation.HIGH_CONCERN
            if ad_score > 60:
                primary = "Alzheimer's Disease - Likely"
            elif pd_score > 60:
                primary = "Parkinson's Disease - Likely"
            else:
                primary = "Significant neurodegenerative process"
            confidence = 85.0
        else:
            overall = FusionInterpretation.CRITICAL
            if ad_score > pd_score:
                primary = "Advanced Alzheimer's Disease"
            elif pd_score > ad_score:
                primary = "Advanced Parkinson's Disease"
            else:
                primary = "Severe neurodegenerative disease"
            confidence = 90.0
        
        # Adjust confidence based on cross-modal consistency
        avg_corr = sum(correlations.values()) / len(correlations)
        if avg_corr < 0.5:
            confidence *= 0.7  # Reduce confidence if modalities conflict
        
        # Generate evidence from each modality
        evidence = DataFusionService._compile_evidence(
            overall, ad_score, pd_score, fusion_score
        )
        
        return {
            'overall': overall,
            'primary_concern': primary,
            'confidence': min(100, confidence),
            'evidence': evidence
        }
    
    @staticmethod
    def _compile_evidence(
        interpretation: FusionInterpretation,
        ad_score: float,
        pd_score: float,
        fusion_score: float
    ) -> Dict[str, str]:
        """Compile supporting evidence from each modality"""
        
        evidence = {
            'cognitive': "",
            'biomarker': "",
            'imaging': ""
        }
        
        if interpretation == FusionInterpretation.NORMAL:
            evidence['cognitive'] = "Cognitive scores within normal limits across all domains"
            evidence['biomarker'] = "Biomarker profile consistent with healthy aging"
            evidence['imaging'] = "No significant structural brain changes detected"
        
        elif interpretation in [FusionInterpretation.MILD_CONCERN, FusionInterpretation.MODERATE_CONCERN]:
            if ad_score > pd_score:
                evidence['cognitive'] = "Mild to moderate memory and executive function decline"
                evidence['biomarker'] = "Amyloid-beta and/or tau levels suggest early AD pathology"
                evidence['imaging'] = "Early hippocampal volume loss and/or cortical thinning"
            else:
                evidence['cognitive'] = "Attention and executive function changes noted"
                evidence['biomarker'] = "Dopamine markers suggest nigrostriatal dysfunction"
                evidence['imaging'] = "Mild to moderate structural changes in relevant regions"
        
        else:  # HIGH_CONCERN or CRITICAL
            if ad_score > pd_score:
                evidence['cognitive'] = "Significant impairment in memory, attention, and executive function"
                evidence['biomarker'] = "Marked amyloid-beta reduction and tau elevation (AD signature)"
                evidence['imaging'] = "Substantial hippocampal atrophy and ventricular enlargement"
            else:
                evidence['cognitive'] = "Progressive cognitive and motor decline"
                evidence['biomarker'] = "Severely reduced dopamine levels"
                evidence['imaging'] = "Structural changes consistent with advanced PD"
        
        return evidence
    
    # ========================================================================
    # PATENT-PENDING: Natural Language Report Generation
    # ========================================================================
    # NOTE: Report generation has been moved to NaturalLanguageService
    # for better separation of concerns and maintainability.
    # See: backend/app/services/natural_language_service.py
    
    # ========================================================================
    # Data Quality Assessment
    # ========================================================================
    
    @staticmethod
    def _assess_data_completeness(record: MedicalRecord) -> float:
        """Calculate data completeness score 0-100"""
        total_fields = 15  # Total important fields
        complete_fields = 0
        
        # Cognitive (5 fields)
        if record.mmse_score is not None: complete_fields += 1
        if record.moca_score is not None: complete_fields += 1
        if record.memory_score is not None: complete_fields += 1
        if record.attention_score is not None: complete_fields += 1
        if record.executive_function_score is not None: complete_fields += 1
        
        # Biomarkers (4 fields)
        if record.amyloid_beta is not None: complete_fields += 1
        if record.tau_protein is not None: complete_fields += 1
        if record.dopamine_level is not None: complete_fields += 1
        if record.apoe_e4_status is not None: complete_fields += 1
        
        # Imaging (5 fields)
        if record.hippocampal_volume is not None: complete_fields += 1
        if record.cortical_thickness is not None: complete_fields += 1
        if record.ventricular_volume is not None: complete_fields += 1
        if record.white_matter_hyperintensities is not None: complete_fields += 1
        if record.brain_volume_total is not None: complete_fields += 1
        
        # Additional field
        if record.visit_date is not None: complete_fields += 1
        
        return (complete_fields / (total_fields + 1)) * 100
    
    @staticmethod
    def _detect_outliers(record: MedicalRecord) -> Dict[str, Any]:
        """Detect outlier values that may indicate data quality issues"""
        outliers = []
        
        # Check each field for physiologically implausible values
        if record.mmse_score is not None and (record.mmse_score < 0 or record.mmse_score > 30):
            outliers.append(f"MMSE out of range: {record.mmse_score}")
        
        if record.amyloid_beta is not None and (record.amyloid_beta < 50 or record.amyloid_beta > 2000):
            outliers.append(f"Amyloid-beta unusual: {record.amyloid_beta}")
        
        if record.hippocampal_volume is not None and (record.hippocampal_volume < 1000 or record.hippocampal_volume > 6000):
            outliers.append(f"Hippocampal volume unusual: {record.hippocampal_volume}")
        
        has_outliers = len(outliers) > 0
        description = "; ".join(outliers) if outliers else None
        
        return {
            'has_outliers': has_outliers,
            'description': description
        }

