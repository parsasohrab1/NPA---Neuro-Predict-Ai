"""
Comprehensive Unit and Integration Tests for DataFusionService
Tests both manual calculations and Deep Learning model integration
"""
import pytest
import numpy as np
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from app.services.data_fusion_service import DataFusionService
from app.services.data_fusion_model_service import DataFusionModelService, get_data_fusion_model_service
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.data_fusion_report import DataFusionReport, FusionConfidence, FusionInterpretation


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_patient_complete():
    """Create a complete patient for testing"""
    return Patient(
        id=1,
        patient_id="PT-TEST-001",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1955, 6, 15),
        gender=Gender.MALE,
        education_years=16
    )


@pytest.fixture
def sample_medical_record_complete(sample_patient_complete):
    """Create a complete medical record with all fields"""
    return MedicalRecord(
        id=1,
        patient_id=sample_patient_complete.id,
        visit_date=datetime(2024, 1, 15),
        visit_type="Initial",
        # Cognitive scores
        mmse_score=24.0,
        moca_score=23.0,
        memory_score=65.0,
        attention_score=70.0,
        executive_function_score=68.0,
        # Biomarkers
        amyloid_beta=450.0,
        tau_protein=350.0,
        dopamine_level=75.0,
        apoe_e4_status=True,
        # Imaging
        hippocampal_volume=2800.0,
        cortical_thickness=2.2,
        ventricular_volume=45000.0,
        white_matter_hyperintensities=8.0,
        brain_volume_total=1080000.0
    )


@pytest.fixture
def sample_medical_record_minimal(sample_patient_complete):
    """Create a minimal medical record with few fields"""
    return MedicalRecord(
        id=2,
        patient_id=sample_patient_complete.id,
        visit_date=datetime(2024, 1, 15),
        visit_type="Follow-up",
        mmse_score=28.0,
        amyloid_beta=600.0
    )


@pytest.fixture
def mock_dl_model_service():
    """Mock Deep Learning model service"""
    service = Mock(spec=DataFusionModelService)
    service.is_loaded.return_value = False
    service.predict_scores.return_value = {}
    return service


# ============================================================================
# UNIT TESTS: Cognitive Modality Assessment
# ============================================================================

class TestCognitiveModalityAssessment:
    """Test cognitive modality scoring"""
    
    def test_assess_cognitive_modality_complete(self, sample_medical_record_complete):
        """Test with all cognitive fields present"""
        score, confidence = DataFusionService._assess_cognitive_modality(
            sample_medical_record_complete
        )
        
        assert 0 <= score <= 100
        assert 0 <= confidence <= 1
        assert confidence > 0.8  # Should have high confidence with all fields
    
    def test_assess_cognitive_modality_partial(self, sample_medical_record_minimal):
        """Test with partial cognitive data"""
        score, confidence = DataFusionService._assess_cognitive_modality(
            sample_medical_record_minimal
        )
        
        assert 0 <= score <= 100
        assert 0 <= confidence <= 1
        assert confidence < 0.5  # Lower confidence with less data
    
    def test_assess_cognitive_modality_empty(self):
        """Test with no cognitive data"""
        record = MedicalRecord(
            id=3,
            patient_id=1,
            visit_date=datetime.now()
        )
        score, confidence = DataFusionService._assess_cognitive_modality(record)
        
        assert score == 50.0  # Neutral score
        assert confidence == 0.0  # Zero confidence
    
    def test_assess_cognitive_modality_mmse_only(self):
        """Test with only MMSE score"""
        record = MedicalRecord(
            id=4,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=25.0
        )
        score, confidence = DataFusionService._assess_cognitive_modality(record)
        
        assert score > 0
        assert 0 < confidence < 1
    
    def test_assess_cognitive_modality_extreme_values(self):
        """Test with extreme cognitive scores"""
        record = MedicalRecord(
            id=5,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=30.0,  # Perfect
            moca_score=30.0,
            memory_score=100.0,
            attention_score=100.0,
            executive_function_score=100.0
        )
        score, confidence = DataFusionService._assess_cognitive_modality(record)
        
        assert score > 90  # Should be very high
        assert confidence == 1.0


# ============================================================================
# UNIT TESTS: Biomarker Modality Assessment
# ============================================================================

class TestBiomarkerModalityAssessment:
    """Test biomarker modality scoring"""
    
    def test_assess_biomarker_modality_complete(self, sample_medical_record_complete):
        """Test with all biomarker fields"""
        score, confidence = DataFusionService._assess_biomarker_modality(
            sample_medical_record_complete
        )
        
        assert 0 <= score <= 100
        assert 0 <= confidence <= 1
    
    def test_assess_biomarker_modality_alzheimer_risk(self):
        """Test with Alzheimer risk biomarkers"""
        record = MedicalRecord(
            id=6,
            patient_id=1,
            visit_date=datetime.now(),
            amyloid_beta=350.0,  # Low = risk
            tau_protein=450.0,   # High = risk
            apoe_e4_status=True
        )
        score, confidence = DataFusionService._assess_biomarker_modality(record)
        
        assert score < 50  # Should indicate risk
        assert confidence > 0.7
    
    def test_assess_biomarker_modality_parkinson_risk(self):
        """Test with Parkinson risk biomarkers"""
        record = MedicalRecord(
            id=7,
            patient_id=1,
            visit_date=datetime.now(),
            dopamine_level=50.0  # Low = risk
        )
        score, confidence = DataFusionService._assess_biomarker_modality(record)
        
        assert score < 80  # Should indicate some risk
        assert confidence > 0.2
    
    def test_assess_biomarker_modality_normal(self):
        """Test with normal biomarkers"""
        record = MedicalRecord(
            id=8,
            patient_id=1,
            visit_date=datetime.now(),
            amyloid_beta=650.0,  # Normal
            tau_protein=150.0,    # Normal
            dopamine_level=120.0, # Normal
            apoe_e4_status=False
        )
        score, confidence = DataFusionService._assess_biomarker_modality(record)
        
        assert score > 70  # Should be good
        assert confidence > 0.7


# ============================================================================
# UNIT TESTS: Imaging Modality Assessment
# ============================================================================

class TestImagingModalityAssessment:
    """Test imaging modality scoring"""
    
    def test_assess_imaging_modality_complete(self, sample_medical_record_complete):
        """Test with all imaging fields"""
        score, confidence = DataFusionService._assess_imaging_modality(
            sample_medical_record_complete
        )
        
        assert 0 <= score <= 100
        assert 0 <= confidence <= 1
    
    def test_assess_imaging_modality_atrophy(self):
        """Test with brain atrophy indicators"""
        record = MedicalRecord(
            id=9,
            patient_id=1,
            visit_date=datetime.now(),
            hippocampal_volume=2500.0,  # Low = atrophy
            cortical_thickness=2.0,     # Thin
            ventricular_volume=55000.0, # Enlarged
            brain_volume_total=1050000.0  # Reduced
        )
        score, confidence = DataFusionService._assess_imaging_modality(record)
        
        assert score < 50  # Should indicate problems
        assert confidence > 0.7
    
    def test_assess_imaging_modality_normal(self):
        """Test with normal imaging"""
        record = MedicalRecord(
            id=10,
            patient_id=1,
            visit_date=datetime.now(),
            hippocampal_volume=3800.0,
            cortical_thickness=2.6,
            ventricular_volume=30000.0,
            brain_volume_total=1150000.0
        )
        score, confidence = DataFusionService._assess_imaging_modality(record)
        
        assert score > 70  # Should be good
        assert confidence > 0.7


# ============================================================================
# UNIT TESTS: Cross-Modal Correlations
# ============================================================================

class TestCrossModalCorrelations:
    """Test cross-modal correlation calculations"""
    
    def test_calculate_correlations_complete(self, sample_medical_record_complete):
        """Test correlation calculation with complete data"""
        correlations = DataFusionService._calculate_cross_modal_correlations(
            sample_medical_record_complete,
            cognitive_score=65.0,
            biomarker_score=55.0,
            imaging_score=60.0
        )
        
        assert 'cognitive_biomarker' in correlations
        assert 'cognitive_imaging' in correlations
        assert 'biomarker_imaging' in correlations
        assert all(0 <= v <= 1 for v in correlations.values())
    
    def test_calculate_correlations_missing_data(self, sample_medical_record_minimal):
        """Test correlation with missing data"""
        correlations = DataFusionService._calculate_cross_modal_correlations(
            sample_medical_record_minimal,
            cognitive_score=80.0,
            biomarker_score=70.0,
            imaging_score=75.0
        )
        
        # Should return neutral correlations when data is missing
        assert all(0 <= v <= 1 for v in correlations.values())
    
    def test_assess_cross_modal_consistency_high(self):
        """Test consistency assessment with high correlations"""
        correlations = {
            'cognitive_biomarker': 0.9,
            'cognitive_imaging': 0.85,
            'biomarker_imaging': 0.88
        }
        consistency = DataFusionService._assess_cross_modal_consistency(correlations)
        
        assert consistency > 80  # High consistency
    
    def test_assess_cross_modal_consistency_low(self):
        """Test consistency assessment with low correlations"""
        correlations = {
            'cognitive_biomarker': 0.3,
            'cognitive_imaging': 0.35,
            'biomarker_imaging': 0.32
        }
        consistency = DataFusionService._assess_cross_modal_consistency(correlations)
        
        assert consistency < 50  # Low consistency, should be penalized
    
    def test_assess_cross_modal_consistency_conflict(self):
        """Test consistency with conflicting modalities"""
        correlations = {
            'cognitive_biomarker': 0.2,  # Very low = conflict
            'cognitive_imaging': 0.9,
            'biomarker_imaging': 0.85
        }
        consistency = DataFusionService._assess_cross_modal_consistency(correlations)
        
        assert consistency < 60  # Should be penalized for conflict


# ============================================================================
# UNIT TESTS: Integrated Fusion Score
# ============================================================================

class TestIntegratedFusionScore:
    """Test integrated fusion score calculation"""
    
    def test_calculate_integrated_fusion_score(self):
        """Test weighted fusion score calculation"""
        score = DataFusionService._calculate_integrated_fusion_score(
            cog_score=70.0,
            bio_score=65.0,
            img_score=68.0,
            cog_conf=0.9,
            bio_conf=0.8,
            img_conf=0.85
        )
        
        assert 0 <= score <= 100
        assert 65 <= score <= 72  # Should be weighted average
    
    def test_calculate_integrated_fusion_score_unequal_confidence(self):
        """Test with unequal confidences"""
        score = DataFusionService._calculate_integrated_fusion_score(
            cog_score=80.0,
            bio_score=50.0,
            img_score=60.0,
            cog_conf=1.0,  # High confidence
            bio_conf=0.2,  # Low confidence
            img_conf=0.3   # Low confidence
        )
        
        # Should weight cognitive more heavily
        assert score > 70
    
    def test_calculate_integrated_fusion_score_no_data(self):
        """Test with no data (zero confidence)"""
        score = DataFusionService._calculate_integrated_fusion_score(
            cog_score=50.0,
            bio_score=50.0,
            img_score=50.0,
            cog_conf=0.0,
            bio_conf=0.0,
            img_conf=0.0
        )
        
        assert score == 50.0  # Neutral score
    
    def test_determine_fusion_confidence(self):
        """Test fusion confidence determination"""
        confidence = DataFusionService._determine_fusion_confidence(
            cog_conf=0.9,
            bio_conf=0.85,
            img_conf=0.88,
            consistency=85.0
        )
        
        assert isinstance(confidence, FusionConfidence)
        assert confidence in [FusionConfidence.VERY_HIGH, FusionConfidence.HIGH]
    
    def test_determine_fusion_confidence_low_consistency(self):
        """Test with low consistency"""
        confidence = DataFusionService._determine_fusion_confidence(
            cog_conf=0.9,
            bio_conf=0.85,
            img_conf=0.88,
            consistency=40.0  # Low consistency
        )
        
        # Should be reduced due to low consistency
        assert confidence in [FusionConfidence.MODERATE, FusionConfidence.LOW]


# ============================================================================
# UNIT TESTS: Disease-Specific Analysis
# ============================================================================

class TestDiseaseSpecificAnalysis:
    """Test disease-specific fusion analysis"""
    
    def test_analyze_alzheimer_fusion(self, sample_patient_complete, sample_medical_record_complete):
        """Test Alzheimer's fusion analysis"""
        analysis = DataFusionService._analyze_alzheimer_fusion(
            sample_medical_record_complete,
            sample_patient_complete
        )
        
        assert 'score' in analysis
        assert 'confidence' in analysis
        assert 'amyloid_tau_concordance' in analysis
        assert 'cognitive_biomarker_alignment' in analysis
        assert 'hippocampal_correlation' in analysis
        assert 0 <= analysis['score'] <= 100
    
    def test_analyze_alzheimer_fusion_high_risk(self):
        """Test with high Alzheimer risk indicators"""
        patient = Patient(
            id=1,
            patient_id="PT-AD",
            first_name="Test",
            last_name="Patient",
            date_of_birth=date(1940, 1, 1),  # Older
            gender=Gender.FEMALE
        )
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=18.0,  # Low
            amyloid_beta=350.0,  # Low
            tau_protein=500.0,   # High
            apoe_e4_status=True,
            hippocampal_volume=2500.0  # Low
        )
        
        analysis = DataFusionService._analyze_alzheimer_fusion(record, patient)
        
        assert analysis['score'] > 50  # Should indicate high risk
    
    def test_analyze_parkinson_fusion(self, sample_patient_complete, sample_medical_record_complete):
        """Test Parkinson's fusion analysis"""
        analysis = DataFusionService._analyze_parkinson_fusion(
            sample_medical_record_complete,
            sample_patient_complete
        )
        
        assert 'score' in analysis
        assert 'confidence' in analysis
        assert 'dopamine_cognitive_concordance' in analysis
        assert 'motor_cognitive_alignment' in analysis
        assert 'imaging_biomarker_correlation' in analysis
        assert 0 <= analysis['score'] <= 100
    
    def test_analyze_parkinson_fusion_high_risk(self):
        """Test with high Parkinson risk indicators"""
        patient = Patient(
            id=2,
            patient_id="PT-PD",
            first_name="Test",
            last_name="Patient",
            date_of_birth=date(1950, 1, 1),
            gender=Gender.MALE
        )
        record = MedicalRecord(
            id=2,
            patient_id=2,
            visit_date=datetime.now(),
            dopamine_level=45.0,  # Very low
            attention_score=55.0,  # Low
            executive_function_score=58.0  # Low
        )
        
        analysis = DataFusionService._analyze_parkinson_fusion(record, patient)
        
        assert analysis['score'] > 40  # Should indicate risk


# ============================================================================
# UNIT TESTS: Feature Extraction
# ============================================================================

class TestFeatureExtraction:
    """Test feature extraction for Deep Learning model"""
    
    def test_extract_features_for_model_complete(self, sample_patient_complete, sample_medical_record_complete):
        """Test feature extraction with complete data"""
        features = DataFusionService._extract_features_for_model(
            sample_medical_record_complete,
            sample_patient_complete
        )
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (20,)
        assert features.dtype == np.float32
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()
    
    def test_extract_features_for_model_missing_data(self, sample_patient_complete, sample_medical_record_minimal):
        """Test feature extraction with missing data"""
        features = DataFusionService._extract_features_for_model(
            sample_medical_record_minimal,
            sample_patient_complete
        )
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (20,)
        # Missing features should be 0.0
        assert features[2] == 0.0  # memory_score missing
        assert features[3] == 0.0  # attention_score missing
    
    def test_extract_features_for_model_normalization(self, sample_patient_complete):
        """Test that features are properly normalized"""
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=30.0,  # Max value
            moca_score=30.0,
            memory_score=100.0,
            amyloid_beta=1000.0,  # High value
            hippocampal_volume=4000.0  # High value
        )
        
        features = DataFusionService._extract_features_for_model(record, sample_patient_complete)
        
        # Check normalization
        assert features[0] <= 1.0  # MMSE normalized
        assert features[1] <= 1.0  # MoCA normalized
        assert features[2] <= 1.0  # Memory normalized


# ============================================================================
# INTEGRATION TESTS: Full Report Generation
# ============================================================================

class TestGenerateFusionReport:
    """Integration tests for full report generation"""
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_complete(
        self, test_session, sample_patient_complete, sample_medical_record_complete
    ):
        """Test full report generation with complete data"""
        # Add to database
        test_session.add(sample_patient_complete)
        test_session.add(sample_medical_record_complete)
        await test_session.commit()
        
        # Generate report
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient_complete.id,
            medical_record_id=sample_medical_record_complete.id,
            db=test_session
        )
        
        assert isinstance(report, DataFusionReport)
        assert report.patient_id == sample_patient_complete.id
        assert report.medical_record_id == sample_medical_record_complete.id
        
        # Check scores
        assert 0 <= report.cognitive_modality_score <= 100
        assert 0 <= report.biomarker_modality_score <= 100
        assert 0 <= report.imaging_modality_score <= 100
        assert 0 <= report.integrated_fusion_score <= 100
        
        # Check confidences
        assert 0 <= report.cognitive_confidence <= 1
        assert 0 <= report.biomarker_confidence <= 1
        assert 0 <= report.imaging_confidence <= 1
        
        # Check correlations
        assert 0 <= report.cognitive_biomarker_correlation <= 1
        assert 0 <= report.cognitive_imaging_correlation <= 1
        assert 0 <= report.biomarker_imaging_correlation <= 1
        
        # Check report sections
        assert report.executive_summary
        assert report.detailed_findings
        assert report.risk_assessment
        assert report.recommendations
        assert report.follow_up_plan
        
        # Check metadata
        assert report.processing_time_ms > 0
        assert report.algorithm_version in ["1.0.0", "2.0.0-DL"]
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_minimal(
        self, test_session, sample_patient_complete, sample_medical_record_minimal
    ):
        """Test report generation with minimal data"""
        test_session.add(sample_patient_complete)
        test_session.add(sample_medical_record_minimal)
        await test_session.commit()
        
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient_complete.id,
            medical_record_id=sample_medical_record_minimal.id,
            db=test_session
        )
        
        assert isinstance(report, DataFusionReport)
        # Should still generate report even with minimal data
        assert report.cognitive_modality_score is not None
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_not_found(self, test_session):
        """Test error handling when patient/record not found"""
        with pytest.raises(ValueError, match="not found"):
            await DataFusionService.generate_fusion_report(
                patient_id=99999,
                medical_record_id=99999,
                db=test_session
            )
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_with_dl_model(
        self, test_session, sample_patient_complete, sample_medical_record_complete, monkeypatch
    ):
        """Test report generation using Deep Learning model"""
        # Mock the model service to return loaded model
        mock_service = Mock(spec=DataFusionModelService)
        mock_service.is_loaded.return_value = True
        mock_service.predict_scores.return_value = {
            'cognitive_score': 65.0,
            'biomarker_score': 60.0,
            'imaging_score': 62.0,
            'cognitive_confidence': 0.85,
            'biomarker_confidence': 0.80,
            'imaging_confidence': 0.82,
            'cognitive_biomarker_correlation': 0.75,
            'cognitive_imaging_correlation': 0.78,
            'biomarker_imaging_correlation': 0.72,
            'integrated_fusion_score': 62.5,
            'alzheimer_fusion_score': 55.0,
            'parkinson_fusion_score': 35.0,
            'alzheimer_concordance': 70.0,
            'alzheimer_alignment': 68.0,
            'alzheimer_hippo_corr': 72.0,
            'parkinson_concordance': 50.0,
            'parkinson_alignment': 45.0,
            'parkinson_corr': 48.0,
        }
        
        # Patch the service
        monkeypatch.setattr(
            'app.services.data_fusion_service.get_data_fusion_model_service',
            lambda: mock_service
        )
        
        test_session.add(sample_patient_complete)
        test_session.add(sample_medical_record_complete)
        await test_session.commit()
        
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient_complete.id,
            medical_record_id=sample_medical_record_complete.id,
            db=test_session
        )
        
        assert report.algorithm_version == "2.0.0-DL"
        assert report.cognitive_modality_score == 65.0
        assert report.biomarker_modality_score == 60.0
        assert report.imaging_modality_score == 62.0
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_fallback_to_manual(
        self, test_session, sample_patient_complete, sample_medical_record_complete, monkeypatch
    ):
        """Test fallback to manual calculations when model not available"""
        # Mock the model service to return unloaded model
        mock_service = Mock(spec=DataFusionModelService)
        mock_service.is_loaded.return_value = False
        
        monkeypatch.setattr(
            'app.services.data_fusion_service.get_data_fusion_model_service',
            lambda: mock_service
        )
        
        test_session.add(sample_patient_complete)
        test_session.add(sample_medical_record_complete)
        await test_session.commit()
        
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient_complete.id,
            medical_record_id=sample_medical_record_complete.id,
            db=test_session
        )
        
        assert report.algorithm_version == "1.0.0"
        # Should still have valid scores from manual calculations
        assert report.cognitive_modality_score is not None


# ============================================================================
# UNIT TESTS: Data Quality Assessment
# ============================================================================

class TestDataQualityAssessment:
    """Test data quality assessment methods"""
    
    def test_assess_data_completeness_complete(self, sample_medical_record_complete):
        """Test completeness with all fields"""
        completeness = DataFusionService._assess_data_completeness(
            sample_medical_record_complete
        )
        
        assert 0 <= completeness <= 100
        assert completeness > 80  # Should be high with complete data
    
    def test_assess_data_completeness_partial(self, sample_medical_record_minimal):
        """Test completeness with partial data"""
        completeness = DataFusionService._assess_data_completeness(
            sample_medical_record_minimal
        )
        
        assert 0 <= completeness <= 100
        assert completeness < 50  # Should be lower
    
    def test_detect_outliers_normal(self, sample_medical_record_complete):
        """Test outlier detection with normal values"""
        outliers = DataFusionService._detect_outliers(
            sample_medical_record_complete
        )
        
        assert 'has_outliers' in outliers
        assert outliers['has_outliers'] == False
    
    def test_detect_outliers_abnormal(self):
        """Test outlier detection with abnormal values"""
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=35.0,  # Out of range (>30)
            amyloid_beta=5000.0,  # Unusual
            hippocampal_volume=500.0  # Unusual
        )
        
        outliers = DataFusionService._detect_outliers(record)
        
        assert outliers['has_outliers'] == True
        assert outliers['description'] is not None


# ============================================================================
# UNIT TESTS: Interpretation Generation
# ============================================================================

class TestInterpretationGeneration:
    """Test interpretation generation"""
    
    def test_generate_interpretation_normal(self):
        """Test interpretation for normal scores"""
        interpretation = DataFusionService._generate_interpretation(
            fusion_score=85.0,
            ad_analysis={'score': 20.0, 'confidence': 0.8},
            pd_analysis={'score': 15.0, 'confidence': 0.8},
            correlations={'cognitive_biomarker': 0.8, 'cognitive_imaging': 0.85, 'biomarker_imaging': 0.82}
        )
        
        assert interpretation['overall'] == FusionInterpretation.NORMAL
        assert interpretation['confidence'] > 80
    
    def test_generate_interpretation_high_risk(self):
        """Test interpretation for high risk"""
        interpretation = DataFusionService._generate_interpretation(
            fusion_score=25.0,
            ad_analysis={'score': 75.0, 'confidence': 0.9},
            pd_analysis={'score': 20.0, 'confidence': 0.7},
            correlations={'cognitive_biomarker': 0.7, 'cognitive_imaging': 0.75, 'biomarker_imaging': 0.72}
        )
        
        assert interpretation['overall'] in [FusionInterpretation.HIGH_CONCERN, FusionInterpretation.CRITICAL]
        assert 'Alzheimer' in interpretation['primary_concern'] or 'Advanced' in interpretation['primary_concern']
    
    def test_generate_interpretation_conflicting_modalities(self):
        """Test interpretation with conflicting modalities"""
        interpretation = DataFusionService._generate_interpretation(
            fusion_score=60.0,
            ad_analysis={'score': 50.0, 'confidence': 0.6},
            pd_analysis={'score': 45.0, 'confidence': 0.6},
            correlations={'cognitive_biomarker': 0.3, 'cognitive_imaging': 0.85, 'biomarker_imaging': 0.82}
        )
        
        # Confidence should be reduced due to conflict
        assert interpretation['confidence'] < 80


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_all_none_values(self):
        """Test with all None values"""
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now()
        )
        patient = Patient(
            id=1,
            patient_id="PT-001",
            first_name="Test",
            last_name="Patient",
            date_of_birth=date(1980, 1, 1),
            gender=Gender.MALE
        )
        
        # Should not crash
        cog_score, cog_conf = DataFusionService._assess_cognitive_modality(record)
        bio_score, bio_conf = DataFusionService._assess_biomarker_modality(record)
        img_score, img_conf = DataFusionService._assess_imaging_modality(record)
        
        assert cog_score == 50.0
        assert cog_conf == 0.0
    
    def test_extreme_high_values(self):
        """Test with extremely high values"""
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=30.0,
            moca_score=30.0,
            memory_score=100.0,
            amyloid_beta=2000.0,
            tau_protein=1000.0,
            hippocampal_volume=6000.0
        )
        
        # Should handle gracefully
        cog_score, _ = DataFusionService._assess_cognitive_modality(record)
        bio_score, _ = DataFusionService._assess_biomarker_modality(record)
        img_score, _ = DataFusionService._assess_imaging_modality(record)
        
        assert 0 <= cog_score <= 100
        assert 0 <= bio_score <= 100
        assert 0 <= img_score <= 100
    
    def test_extreme_low_values(self):
        """Test with extremely low values"""
        record = MedicalRecord(
            id=1,
            patient_id=1,
            visit_date=datetime.now(),
            mmse_score=0.0,
            moca_score=0.0,
            memory_score=0.0,
            amyloid_beta=50.0,
            tau_protein=50.0,
            hippocampal_volume=1000.0
        )
        
        # Should handle gracefully
        cog_score, _ = DataFusionService._assess_cognitive_modality(record)
        bio_score, _ = DataFusionService._assess_biomarker_modality(record)
        img_score, _ = DataFusionService._assess_imaging_modality(record)
        
        assert 0 <= cog_score <= 100
        assert 0 <= bio_score <= 100
        assert 0 <= img_score <= 100
    
    @pytest.mark.asyncio
    async def test_concurrent_report_generation(
        self, test_session, sample_patient_complete, sample_medical_record_complete
    ):
        """Test concurrent report generation"""
        import asyncio
        
        test_session.add(sample_patient_complete)
        test_session.add(sample_medical_record_complete)
        await test_session.commit()
        
        # Generate multiple reports concurrently
        tasks = [
            DataFusionService.generate_fusion_report(
                patient_id=sample_patient_complete.id,
                medical_record_id=sample_medical_record_complete.id,
                db=test_session
            )
            for _ in range(5)
        ]
        
        reports = await asyncio.gather(*tasks)
        
        assert len(reports) == 5
        assert all(isinstance(r, DataFusionReport) for r in reports)

