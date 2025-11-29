"""
Natural Language Generation Service
Handles report generation using templates and NLG patterns
Separates report generation logic from core data fusion algorithm
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Template = None
    Environment = None
    FileSystemLoader = None

logger = logging.getLogger(__name__)


class NaturalLanguageService:
    """
    Service for generating natural language reports from data fusion results
    
    Uses template-based approach for maintainability and flexibility
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "reports"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 if available
        if JINJA2_AVAILABLE:
            try:
                self.jinja_env = Environment(
                    loader=FileSystemLoader(str(self.templates_dir)),
                    autoescape=False,
                    trim_blocks=True,
                    lstrip_blocks=True
                )
                self.use_jinja = True
            except Exception as e:
                logger.warning(f"Could not initialize Jinja2: {e}. Using string templates.")
                self.use_jinja = False
        else:
            self.use_jinja = False
            logger.info("Jinja2 not available. Using string templates.")
    
    def generate_fusion_report(
        self,
        patient: Any,  # Patient model
        record: Any,  # MedicalRecord model
        cog_score: float,
        bio_score: float,
        img_score: float,
        fusion_score: float,
        ad_analysis: Dict[str, Any],
        pd_analysis: Dict[str, Any],
        interpretation: Dict[str, Any],
        correlations: Dict[str, float],
        xai_explanation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate comprehensive clinical report from data fusion results
        
        Args:
            patient: Patient model instance
            record: MedicalRecord model instance
            cog_score: Cognitive modality score (0-100)
            bio_score: Biomarker modality score (0-100)
            img_score: Imaging modality score (0-100)
            fusion_score: Integrated fusion score (0-100)
            ad_analysis: Alzheimer's disease analysis dict
            pd_analysis: Parkinson's disease analysis dict
            interpretation: Clinical interpretation dict
            correlations: Cross-modal correlations dict
            xai_explanation: Optional XAI explanation dict
        
        Returns:
            Dictionary with report sections: executive_summary, detailed_findings, 
            disease_analysis, recommendations, technical_notes
        """
        # Prepare template context
        context = self._prepare_context(
            patient, record, cog_score, bio_score, img_score,
            fusion_score, ad_analysis, pd_analysis, interpretation,
            correlations, xai_explanation
        )
        
        # Generate report sections
        if self.use_jinja:
            return self._generate_with_jinja(context)
        else:
            return self._generate_with_string_templates(context)
    
    def _prepare_context(
        self,
        patient: Any,
        record: Any,
        cog_score: float,
        bio_score: float,
        img_score: float,
        fusion_score: float,
        ad_analysis: Dict[str, Any],
        pd_analysis: Dict[str, Any],
        interpretation: Dict[str, Any],
        correlations: Dict[str, float],
        xai_explanation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare context dictionary for template rendering"""
        age = (datetime.now().date() - patient.date_of_birth).days // 365
        
        return {
            'patient': {
                'name': f"{patient.first_name} {patient.last_name}",
                'id': patient.patient_id,
                'age': age,
                'gender': patient.gender.value
            },
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'scores': {
                'cognitive': cog_score,
                'biomarker': bio_score,
                'imaging': img_score,
                'fusion': fusion_score
            },
            'cognitive': {
                'mmse': record.mmse_score,
                'moca': record.moca_score,
                'memory': record.memory_score,
                'attention': record.attention_score,
                'executive': record.executive_function_score
            },
            'biomarkers': {
                'amyloid_beta': record.amyloid_beta,
                'tau_protein': record.tau_protein,
                'dopamine': record.dopamine_level,
                'apoe_e4': 'Positive' if record.apoe_e4_status else 'Negative' if record.apoe_e4_status is not None else 'N/A'
            },
            'imaging': {
                'hippocampal_volume': record.hippocampal_volume,
                'cortical_thickness': record.cortical_thickness,
                'ventricular_volume': record.ventricular_volume,
                'wmh': record.white_matter_hyperintensities,
                'brain_volume_total': record.brain_volume_total
            },
            'interpretation': interpretation,
            'ad_analysis': ad_analysis,
            'pd_analysis': pd_analysis,
            'correlations': correlations,
            'xai_explanation': xai_explanation,
            'format_value': self._format_value,
            'format_score': self._format_score,
            'format_correlation': self._format_correlation
        }
    
    def _generate_with_jinja(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate report using Jinja2 templates"""
        try:
            # Try to load template file
            template_file = self.templates_dir / "fusion_report.j2"
            if template_file.exists():
                template = self.jinja_env.get_template("fusion_report.j2")
                full_report = template.render(**context)
                return self._parse_report_sections(full_report)
            else:
                # Fallback to string templates if file doesn't exist
                logger.warning("Jinja2 template file not found. Using string templates.")
                return self._generate_with_string_templates(context)
        except Exception as e:
            logger.error(f"Error rendering Jinja2 template: {e}. Falling back to string templates.")
            return self._generate_with_string_templates(context)
    
    def _generate_with_string_templates(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate report using string templates (fallback)"""
        p = context['patient']
        scores = context['scores']
        interp = context['interpretation']
        
        # Executive Summary
        executive_summary = f"""MULTI-MODAL DATA FUSION REPORT

Patient: {p['name']} (ID: {p['id']})
Age: {p['age']} years | Gender: {p['gender']}
Report Date: {context['report_date']}

INTEGRATED FUSION SCORE: {scores['fusion']:.1f}/100
INTERPRETATION: {interp['primary_concern']}
CONFIDENCE: {interp['confidence']:.1f}%

This report integrates cognitive assessments, biomarker analyses, and neuroimaging 
findings through our proprietary multi-modal fusion algorithm."""

        # Detailed Findings
        detailed_findings = self._generate_detailed_findings(context)
        
        # Disease Analysis
        disease_analysis = self._generate_disease_analysis(context)
        
        # Recommendations
        recommendations = self._generate_recommendations(context)
        
        # Technical Notes
        technical_notes = self._generate_technical_notes(context)
        
        return {
            'executive_summary': executive_summary,
            'detailed_findings': detailed_findings,
            'disease_analysis': disease_analysis,
            'recommendations': recommendations,
            'technical_notes': technical_notes
        }
    
    def _generate_detailed_findings(self, context: Dict[str, Any]) -> str:
        """Generate detailed findings section"""
        cog = context['cognitive']
        bio = context['biomarkers']
        img = context['imaging']
        scores = context['scores']
        evidence = context['interpretation']['evidence']
        
        return f"""MODALITY ANALYSIS:

1. COGNITIVE ASSESSMENT (Score: {scores['cognitive']:.1f}/100)
   - MMSE: {self._format_value(cog['mmse'])}
   - MoCA: {self._format_value(cog['moca'])}
   - Memory: {self._format_value(cog['memory'])}
   - Attention: {self._format_value(cog['attention'])}
   - Executive Function: {self._format_value(cog['executive'])}
   
   {evidence.get('cognitive', 'No specific cognitive findings.')}

2. BIOMARKER PROFILE (Score: {scores['biomarker']:.1f}/100)
   - Amyloid-beta: {self._format_value(bio['amyloid_beta'])} pg/mL
   - Tau Protein: {self._format_value(bio['tau_protein'])} pg/mL
   - Dopamine: {self._format_value(bio['dopamine'])} ng/mL
   - APOE ε4: {bio['apoe_e4']}
   
   {evidence.get('biomarker', 'No specific biomarker findings.')}

3. NEUROIMAGING (Score: {scores['imaging']:.1f}/100)
   - Hippocampal Volume: {self._format_value(img['hippocampal_volume'])} mm³
   - Cortical Thickness: {self._format_value(img['cortical_thickness'])} mm
   - Ventricular Volume: {self._format_value(img['ventricular_volume'])} mm³
   - WMH: {self._format_value(img['wmh'])}
   - Total Brain Volume: {self._format_value(img['brain_volume_total'])} mm³
   
   {evidence.get('imaging', 'No specific imaging findings.')}

CROSS-MODAL CORRELATIONS:
   - Cognitive-Biomarker: {self._format_correlation(context['correlations'].get('cognitive_biomarker', 0.5))}
   - Cognitive-Imaging: {self._format_correlation(context['correlations'].get('cognitive_imaging', 0.5))}
   - Biomarker-Imaging: {self._format_correlation(context['correlations'].get('biomarker_imaging', 0.5))}"""
    
    def _generate_disease_analysis(self, context: Dict[str, Any]) -> str:
        """Generate disease-specific analysis section"""
        ad = context['ad_analysis']
        pd = context['pd_analysis']
        
        ad_score = ad.get('score', 0)
        pd_score = pd.get('score', 0)
        
        sections = []
        
        # Alzheimer's Analysis
        if ad_score > 20:
            sections.append(f"""ALZHEIMER'S DISEASE RISK ASSESSMENT:
   Risk Score: {ad_score:.1f}/100
   Confidence: {ad.get('confidence', 0):.1f}%
   - Amyloid-Tau Concordance: {ad.get('amyloid_tau_concordance', 50):.1f}%
   - Cognitive-Biomarker Alignment: {ad.get('cognitive_biomarker_alignment', 50):.1f}%
   - Hippocampal Correlation: {ad.get('hippocampal_correlation', 50):.1f}%""")
        
        # Parkinson's Analysis
        if pd_score > 20:
            sections.append(f"""PARKINSON'S DISEASE RISK ASSESSMENT:
   Risk Score: {pd_score:.1f}/100
   Confidence: {pd.get('confidence', 0):.1f}%
   - Dopamine-Cognitive Concordance: {pd.get('dopamine_cognitive_concordance', 50):.1f}%
   - Motor-Cognitive Alignment: {pd.get('motor_cognitive_alignment', 50):.1f}%
   - Imaging-Biomarker Correlation: {pd.get('imaging_biomarker_correlation', 50):.1f}%""")
        
        if not sections:
            return "No significant disease-specific patterns detected."
        
        return "\n\n".join(sections)
    
    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate clinical recommendations based on findings"""
        fusion_score = context['scores']['fusion']
        interp = context['interpretation']
        overall = interp.get('overall', 'NORMAL')
        
        recommendations = []
        
        if fusion_score >= 85:
            recommendations.append("• Continue routine monitoring")
            recommendations.append("• Maintain healthy lifestyle (diet, exercise, cognitive activities)")
        elif fusion_score >= 70:
            recommendations.append("• Schedule follow-up assessment in 6-12 months")
            recommendations.append("• Consider cognitive training programs")
            recommendations.append("• Monitor for progression of symptoms")
        elif fusion_score >= 50:
            recommendations.append("• Comprehensive neurological evaluation recommended")
            recommendations.append("• Consider neuropsychological testing")
            recommendations.append("• Discuss treatment options with neurologist")
            recommendations.append("• Family counseling may be beneficial")
        elif fusion_score >= 30:
            recommendations.append("• Urgent neurological consultation recommended")
            recommendations.append("• Consider advanced imaging (PET, SPECT)")
            recommendations.append("• Discuss disease-modifying therapies if applicable")
            recommendations.append("• Caregiver support and resources")
        else:
            recommendations.append("• Immediate neurological evaluation required")
            recommendations.append("• Consider specialized dementia care")
            recommendations.append("• Advanced care planning recommended")
            recommendations.append("• Multidisciplinary team approach")
        
        # Add XAI-specific recommendations if available
        if context.get('xai_explanation'):
            xai = context['xai_explanation']
            if xai.get('top_contributing_features'):
                recommendations.append("\nKEY FACTORS IDENTIFIED:")
                for disease_exp in xai['top_contributing_features'][:3]:
                    disease_name = disease_exp.get('disease', 'General').capitalize()
                    recommendations.append(f"  • {disease_name} risk factors highlighted by explainable AI analysis")
        
        return "\n".join(recommendations)
    
    def _generate_technical_notes(self, context: Dict[str, Any]) -> str:
        """Generate technical notes section"""
        notes = [
            "TECHNICAL NOTES:",
            "",
            "• This report uses proprietary multi-modal data fusion algorithm",
            "• Scores are normalized to 0-100 scale (higher = better health)",
            "• Confidence levels reflect data quality and cross-modal consistency",
            "• Correlations indicate agreement between different data modalities"
        ]
        
        # Add XAI notes if available
        if context.get('xai_explanation'):
            notes.append("• Explainable AI (XAI) analysis provides feature-level attributions")
            notes.append("• XAI methods: Integrated Gradients (Patent Claim 3)")
        
        # Add correlation interpretation
        corr = context['correlations']
        avg_corr = sum(corr.values()) / len(corr) if corr else 0.5
        
        if avg_corr > 0.7:
            notes.append(f"• High cross-modal consistency ({avg_corr:.2f}) - findings are concordant")
        elif avg_corr < 0.4:
            notes.append(f"• Low cross-modal consistency ({avg_corr:.2f}) - findings may conflict, review carefully")
        else:
            notes.append(f"• Moderate cross-modal consistency ({avg_corr:.2f})")
        
        return "\n".join(notes)
    
    def _parse_report_sections(self, full_report: str) -> Dict[str, str]:
        """Parse full report into sections (for Jinja2 template output)"""
        # If template returns full report, try to parse sections
        # Otherwise, return as single section
        sections = full_report.split("\n\n---\n\n")
        
        if len(sections) >= 5:
            return {
                'executive_summary': sections[0],
                'detailed_findings': sections[1],
                'disease_analysis': sections[2],
                'recommendations': sections[3],
                'technical_notes': sections[4]
            }
        else:
            # Return full report in executive_summary
            return {
                'executive_summary': full_report,
                'detailed_findings': '',
                'disease_analysis': '',
                'recommendations': '',
                'technical_notes': ''
            }
    
    # Helper formatting methods
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format value for display (handle None)"""
        if value is None:
            return 'N/A'
        if isinstance(value, float):
            return f"{value:.2f}" if value % 1 != 0 else f"{int(value)}"
        return str(value)
    
    @staticmethod
    def _format_score(score: float) -> str:
        """Format score with interpretation"""
        if score >= 85:
            qualifier = "Excellent"
        elif score >= 70:
            qualifier = "Good"
        elif score >= 50:
            qualifier = "Moderate"
        elif score >= 30:
            qualifier = "Poor"
        else:
            qualifier = "Critical"
        
        return f"{score:.1f}/100 ({qualifier})"
    
    @staticmethod
    def _format_correlation(corr: float) -> str:
        """Format correlation value with interpretation"""
        if corr >= 0.7:
            qualifier = "Strong"
        elif corr >= 0.5:
            qualifier = "Moderate"
        elif corr >= 0.3:
            qualifier = "Weak"
        else:
            qualifier = "Very Weak"
        
        return f"{corr:.2f} ({qualifier})"


# Global instance
_natural_language_service: Optional[NaturalLanguageService] = None


def get_natural_language_service() -> NaturalLanguageService:
    """Get or create the global natural language service instance"""
    global _natural_language_service
    if _natural_language_service is None:
        _natural_language_service = NaturalLanguageService()
    return _natural_language_service

