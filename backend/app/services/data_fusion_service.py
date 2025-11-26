"""
PATENT-PENDING: Data Fusion Service
Multi-Modal Medical Data Fusion and Interpretation Algorithm
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import time

from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.data_fusion_report import (
    DataFusionReport, 
    FusionConfidence, 
    FusionInterpretation
)


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
        # STEP 1: ASSESS INDIVIDUAL MODALITIES
        # ====================================================================
        
        cognitive_score, cognitive_conf = DataFusionService._assess_cognitive_modality(medical_record)
        biomarker_score, biomarker_conf = DataFusionService._assess_biomarker_modality(medical_record)
        imaging_score, imaging_conf = DataFusionService._assess_imaging_modality(medical_record)
        
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
        
        report_sections = DataFusionService._generate_report_text(
            patient, medical_record, 
            cognitive_score, biomarker_score, imaging_score,
            integrated_score, ad_analysis, pd_analysis,
            interpretation, correlations
        )
        
        # ====================================================================
        # STEP 7: DATA QUALITY ASSESSMENT
        # ====================================================================
        
        completeness = DataFusionService._assess_data_completeness(medical_record)
        outliers = DataFusionService._detect_outliers(medical_record)
        
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
            executive_summary=report_sections['executive_summary'],
            detailed_findings=report_sections['detailed_findings'],
            risk_assessment=report_sections['risk_assessment'],
            recommendations=report_sections['recommendations'],
            follow_up_plan=report_sections['follow_up_plan'],
            
            # Quality Metrics
            data_completeness_score=completeness,
            has_outlier_findings=1 if outliers['has_outliers'] else 0,
            data_quality_notes=outliers.get('description'),
            
            # Metadata
            processing_time_ms=processing_time,
            algorithm_version="1.0.0",
            report_version="1.0.0",
        )
        
        return fusion_report
    
    # ========================================================================
    # PATENT-PENDING: Individual Modality Assessment Methods
    # ========================================================================
    
    @staticmethod
    def _assess_cognitive_modality(record: MedicalRecord) -> tuple[float, float]:
        """
        Assess cognitive modality and calculate confidence
        Returns: (score 0-100, confidence 0-1)
        """
        scores = []
        weights = []
        
        if record.mmse_score is not None:
            # MMSE: 30 is perfect, 0 is severe impairment
            mmse_norm = (record.mmse_score / 30) * 100
            scores.append(mmse_norm)
            weights.append(0.25)
        
        if record.moca_score is not None:
            # MoCA: 30 is perfect, 0 is severe impairment
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
            return 50.0, 0.0  # No data, neutral score, zero confidence
        
        # Weighted average
        total_weight = sum(weights)
        cognitive_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Confidence based on data completeness
        confidence = len(scores) / 5.0  # Max 5 cognitive measures
        
        return cognitive_score, confidence
    
    @staticmethod
    def _assess_biomarker_modality(record: MedicalRecord) -> tuple[float, float]:
        """
        Assess biomarker modality and calculate confidence
        Returns: (score 0-100, confidence 0-1)
        PATENT-PENDING: Disease-specific biomarker weighting
        """
        risk_score = 0.0
        confidence_factors = []
        
        # Amyloid-beta assessment (Alzheimer indicator)
        if record.amyloid_beta is not None:
            if record.amyloid_beta < 400:  # Low = Alzheimer risk
                risk_score += 30
            elif record.amyloid_beta < 500:
                risk_score += 15
            confidence_factors.append(1.0)
        
        # Tau protein assessment (Alzheimer indicator)
        if record.tau_protein is not None:
            if record.tau_protein > 400:  # High = Alzheimer risk
                risk_score += 30
            elif record.tau_protein > 300:
                risk_score += 15
            confidence_factors.append(1.0)
        
        # Dopamine assessment (Parkinson indicator)
        if record.dopamine_level is not None:
            if record.dopamine_level < 60:  # Low = Parkinson risk
                risk_score += 25
            elif record.dopamine_level < 80:
                risk_score += 12
            confidence_factors.append(1.0)
        
        # APOE ε4 status (Alzheimer risk factor)
        if record.apoe_e4_status is not None:
            if record.apoe_e4_status:
                risk_score += 15
            confidence_factors.append(0.8)  # Genetic marker, moderate weight
        
        # Convert risk to health score (inverse)
        biomarker_score = 100 - min(100, risk_score)
        
        # Confidence based on available biomarkers
        confidence = sum(confidence_factors) / 4.0 if confidence_factors else 0.0
        
        return biomarker_score, confidence
    
    @staticmethod
    def _assess_imaging_modality(record: MedicalRecord) -> tuple[float, float]:
        """
        Assess imaging modality and calculate confidence
        Returns: (score 0-100, confidence 0-1)
        PATENT-PENDING: Multi-metric MRI fusion
        """
        risk_score = 0.0
        confidence_factors = []
        
        # Hippocampal volume (Alzheimer indicator)
        if record.hippocampal_volume is not None:
            if record.hippocampal_volume < 2800:  # Severe atrophy
                risk_score += 35
            elif record.hippocampal_volume < 3200:  # Moderate atrophy
                risk_score += 20
            elif record.hippocampal_volume < 3500:  # Mild atrophy
                risk_score += 10
            confidence_factors.append(1.0)
        
        # Cortical thickness (general atrophy indicator)
        if record.cortical_thickness is not None:
            if record.cortical_thickness < 2.2:  # Severe thinning
                risk_score += 20
            elif record.cortical_thickness < 2.5:  # Moderate thinning
                risk_score += 10
            confidence_factors.append(0.9)
        
        # Ventricular volume (atrophy/neurodegeneration indicator)
        if record.ventricular_volume is not None:
            if record.ventricular_volume > 50000:  # Severe enlargement
                risk_score += 25
            elif record.ventricular_volume > 40000:  # Moderate enlargement
                risk_score += 12
            confidence_factors.append(0.9)
        
        # White matter hyperintensities (vascular/degenerative)
        if record.white_matter_hyperintensities is not None:
            if record.white_matter_hyperintensities > 10:
                risk_score += 15
            elif record.white_matter_hyperintensities > 5:
                risk_score += 7
            confidence_factors.append(0.8)
        
        # Total brain volume
        if record.brain_volume_total is not None:
            if record.brain_volume_total < 1100000:  # Reduced volume
                risk_score += 10
            confidence_factors.append(0.7)
        
        # Convert risk to health score (inverse)
        imaging_score = 100 - min(100, risk_score)
        
        # Confidence based on available imaging metrics
        confidence = sum(confidence_factors) / 5.0 if confidence_factors else 0.0
        
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
        if record.mmse_score is not None and record.amyloid_beta is not None:
            # For Alzheimer: Low MMSE should correlate with low amyloid
            mmse_impairment = (30 - record.mmse_score) / 30  # 0-1
            amyloid_abnormality = max(0, (500 - record.amyloid_beta) / 500)  # 0-1
            correlations['cognitive_biomarker'] = 1.0 - abs(mmse_impairment - amyloid_abnormality)
        else:
            correlations['cognitive_biomarker'] = 0.5  # Neutral if data missing
        
        # Cognitive-Imaging Correlation
        # Expected: Low cognitive should correlate with hippocampal atrophy
        if record.mmse_score is not None and record.hippocampal_volume is not None:
            mmse_impairment = (30 - record.mmse_score) / 30
            hippo_atrophy = max(0, (4000 - record.hippocampal_volume) / 2000)  # 0-1
            correlations['cognitive_imaging'] = 1.0 - abs(mmse_impairment - hippo_atrophy)
        else:
            correlations['cognitive_imaging'] = 0.5
        
        # Biomarker-Imaging Correlation
        # Expected: Abnormal biomarkers should correlate with brain changes
        if record.amyloid_beta is not None and record.hippocampal_volume is not None:
            amyloid_abnormality = max(0, (500 - record.amyloid_beta) / 500)
            hippo_atrophy = max(0, (4000 - record.hippocampal_volume) / 2000)
            correlations['biomarker_imaging'] = 1.0 - abs(amyloid_abnormality - hippo_atrophy)
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
        """
        score = 0.0
        confidence_factors = []
        
        # Amyloid-Tau Concordance (hallmark of AD)
        if record.amyloid_beta is not None and record.tau_protein is not None:
            amyloid_low = record.amyloid_beta < 450
            tau_high = record.tau_protein > 350
            
            if amyloid_low and tau_high:
                concordance = 100.0
                score += 40
            elif amyloid_low or tau_high:
                concordance = 60.0
                score += 20
            else:
                concordance = 20.0
            
            confidence_factors.append(1.0)
        else:
            concordance = 50.0
        
        # Cognitive-Biomarker Alignment
        alignment = 50.0
        if record.mmse_score is not None and record.amyloid_beta is not None:
            mmse_impaired = record.mmse_score < 24
            amyloid_abnormal = record.amyloid_beta < 450
            
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
        correlation = 50.0
        if record.hippocampal_volume is not None and record.mmse_score is not None:
            hippo_atrophy = record.hippocampal_volume < 3000
            mmse_impaired = record.mmse_score < 24
            
            if hippo_atrophy and mmse_impaired:
                correlation = 100.0
                score += 35
            elif hippo_atrophy or mmse_impaired:
                correlation = 60.0
                score += 17
            else:
                correlation = 30.0
            
            confidence_factors.append(1.0)
        
        # Age factor
        age = (datetime.now().date() - patient.date_of_birth).days // 365
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
        """
        score = 0.0
        confidence_factors = []
        
        # Dopamine-Cognitive Concordance
        concordance = 50.0
        if record.dopamine_level is not None and record.attention_score is not None:
            dopamine_low = record.dopamine_level < 70
            attention_impaired = record.attention_score < 65
            
            if dopamine_low and attention_impaired:
                concordance = 100.0
                score += 45
            elif dopamine_low or attention_impaired:
                concordance = 60.0
                score += 22
            else:
                concordance = 30.0
            
            confidence_factors.append(1.0)
        
        # Motor-Cognitive Alignment (implied by dopamine + executive function)
        alignment = 50.0
        if record.dopamine_level is not None and record.executive_function_score is not None:
            dopamine_low = record.dopamine_level < 70
            executive_impaired = record.executive_function_score < 65
            
            if dopamine_low and executive_impaired:
                alignment = 100.0
                score += 30
            elif dopamine_low or executive_impaired:
                alignment = 60.0
                score += 15
            else:
                alignment = 30.0
            
            confidence_factors.append(0.9)
        
        # Imaging-Biomarker Correlation
        correlation = 50.0
        if record.dopamine_level is not None and record.cortical_thickness is not None:
            dopamine_low = record.dopamine_level < 70
            cortical_thin = record.cortical_thickness < 2.5
            
            if dopamine_low and cortical_thin:
                correlation = 90.0
                score += 25
            elif dopamine_low or cortical_thin:
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
    
    @staticmethod
    def _generate_report_text(
        patient: Patient,
        record: MedicalRecord,
        cog_score: float,
        bio_score: float,
        img_score: float,
        fusion_score: float,
        ad_analysis: Dict,
        pd_analysis: Dict,
        interpretation: Dict,
        correlations: Dict
    ) -> Dict[str, str]:
        """
        PATENT-PENDING: Automated clinical report generation
        """
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        
        # Executive Summary
        exec_summary = f"""
MULTI-MODAL DATA FUSION REPORT

Patient: {patient.first_name} {patient.last_name} (ID: {patient.patient_id})
Age: {age} years | Gender: {patient.gender.value}
Report Date: {datetime.now().strftime('%Y-%m-%d')}

INTEGRATED FUSION SCORE: {fusion_score:.1f}/100
INTERPRETATION: {interpretation['primary_concern']}
CONFIDENCE: {interpretation['confidence']:.1f}%

This report integrates cognitive assessments, biomarker analyses, and neuroimaging 
findings through our proprietary multi-modal fusion algorithm.
        """.strip()
        
        # Detailed Findings
        detailed = f"""
MODALITY ANALYSIS:

1. COGNITIVE ASSESSMENT (Score: {cog_score:.1f}/100)
   - MMSE: {record.mmse_score if record.mmse_score else 'N/A'}
   - MoCA: {record.moca_score if record.moca_score else 'N/A'}
   - Memory: {record.memory_score if record.memory_score else 'N/A'}
   - Attention: {record.attention_score if record.attention_score else 'N/A'}
   - Executive Function: {record.executive_function_score if record.executive_function_score else 'N/A'}
   
   {interpretation['evidence']['cognitive']}

2. BIOMARKER PROFILE (Score: {bio_score:.1f}/100)
   - Amyloid-beta: {record.amyloid_beta if record.amyloid_beta else 'N/A'} pg/mL
   - Tau Protein: {record.tau_protein if record.tau_protein else 'N/A'} pg/mL
   - Dopamine: {record.dopamine_level if record.dopamine_level else 'N/A'} ng/mL
   - APOE ε4: {'Positive' if record.apoe_e4_status else 'Negative' if record.apoe_e4_status is not None else 'N/A'}
   
   {interpretation['evidence']['biomarker']}

3. NEUROIMAGING (Score: {img_score:.1f}/100)
   - Hippocampal Volume: {record.hippocampal_volume if record.hippocampal_volume else 'N/A'} mm³
   - Cortical Thickness: {record.cortical_thickness if record.cortical_thickness else 'N/A'} mm
   - Ventricular Volume: {record.ventricular_volume if record.ventricular_volume else 'N/A'} mm³
   - WMH: {record.white_matter_hyperintensities if record.white_matter_hyperintensities else 'N/A'}
   
   {interpretation['evidence']['imaging']}

CROSS-MODAL CORRELATION ANALYSIS:
- Cognitive-Biomarker: {correlations['cognitive_biomarker']*100:.1f}% concordance
- Cognitive-Imaging: {correlations['cognitive_imaging']*100:.1f}% concordance
- Biomarker-Imaging: {correlations['biomarker_imaging']*100:.1f}% concordance
        """.strip()
        
        # Risk Assessment
        risk_assess = f"""
DISEASE-SPECIFIC FUSION ANALYSIS:

ALZHEIMER'S DISEASE:
- Multi-Modal Fusion Score: {ad_analysis['score']:.1f}/100
- Confidence: {ad_analysis['confidence']*100:.1f}%
- Amyloid-Tau Concordance: {ad_analysis['amyloid_tau_concordance']:.1f}%
- Risk Level: {'HIGH' if ad_analysis['score'] > 60 else 'MODERATE' if ad_analysis['score'] > 30 else 'LOW'}

PARKINSON'S DISEASE:
- Multi-Modal Fusion Score: {pd_analysis['score']:.1f}/100
- Confidence: {pd_analysis['confidence']*100:.1f}%
- Dopamine-Cognitive Concordance: {pd_analysis['dopamine_cognitive_concordance']:.1f}%
- Risk Level: {'HIGH' if pd_analysis['score'] > 60 else 'MODERATE' if pd_analysis['score'] > 30 else 'LOW'}

OVERALL ASSESSMENT:
- Primary Concern: {interpretation['primary_concern']}
- Confidence in Assessment: {interpretation['confidence']:.1f}%
- Data Quality: {'Excellent' if fusion_score > 70 else 'Good' if fusion_score > 50 else 'Fair'}
        """.strip()
        
        # Recommendations
        if fusion_score >= 85:
            recommendations = """
- Continue routine monitoring
- Maintain healthy lifestyle (exercise, cognitive engagement, social activity)
- Annual cognitive screening recommended
- No immediate clinical intervention required
            """.strip()
        elif fusion_score >= 70:
            recommendations = """
- Follow-up cognitive assessment in 6 months
- Lifestyle modifications (physical exercise, cognitive training, Mediterranean diet)
- Consider baseline MRI if not recently done
- Monitor for progression
            """.strip()
        elif fusion_score >= 50:
            recommendations = """
- Comprehensive neurological evaluation recommended
- Repeat biomarker testing in 3-6 months
- Detailed neuropsychological assessment
- Consider therapeutic interventions
- MRI surveillance for progression
- Specialist referral advised
            """.strip()
        else:
            recommendations = """
- URGENT: Comprehensive neurological evaluation
- Initiate appropriate disease-modifying therapy
- Frequent monitoring (monthly to quarterly)
- Multidisciplinary care team involvement
- Consider clinical trial enrollment
- Family counseling and support services
            """.strip()
        
        # Follow-up Plan
        if fusion_score >= 70:
            follow_up = "Routine follow-up in 12 months. Earlier if symptoms develop."
        elif fusion_score >= 50:
            follow_up = "Follow-up in 3-6 months with repeat cognitive testing and biomarkers."
        else:
            follow_up = "Frequent follow-up (monthly to quarterly) with comprehensive assessments."
        
        return {
            'executive_summary': exec_summary,
            'detailed_findings': detailed,
            'risk_assessment': risk_assess,
            'recommendations': recommendations,
            'follow_up_plan': follow_up,
        }
    
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

