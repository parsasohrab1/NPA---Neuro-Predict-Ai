# 3D Analysis - Quality Control Feature

## Overview

The Quality Control (QC) module in the 3D Analysis tab provides a comprehensive visualization and assessment system for neuroimaging pipeline outputs. It enables side-by-side comparison of **Acceptable** vs **Discarded** results from three major brain imaging analysis pipelines.

## Supported Pipelines

### 1. FreeSurfer
**Purpose**: Brain Segmentation & Volumetry

**What it does**:
- Automated cortical surface reconstruction
- Subcortical structure segmentation
- Volumetric measurements of brain regions
- Cortical thickness analysis

**Quality Metrics**:
- **SNR (Signal-to-Noise Ratio)**: Measures image quality (acceptable: >25)
- **Euler Number**: Topology metric (acceptable: -20 to +5)
- **Cortical Thickness Mean**: Average cortical thickness in mm (typical: 2.3-2.6)
- **WM Segmentation Quality**: White matter segmentation accuracy (acceptable: >0.85)
- **Pial Surface Quality**: Outer surface reconstruction quality (acceptable: >0.85)

**Common Issues in Discarded Results**:
- Segmentation errors in ventricular regions
- Incorrect WM/CSF boundary detection
- Topology defects (poor Euler number)
- Motion artifacts
- Unrealistic cortical thickness values

### 2. LPA (Lesion & White Matter Hyperintensity Analysis)
**Purpose**: Detection and quantification of white matter lesions

**What it does**:
- Automated detection of white matter hyperintensities (WMH)
- Lesion segmentation from FLAIR sequences
- Volume quantification
- Spatial distribution analysis

**Quality Metrics**:
- **Lesion Count**: Number of detected lesions (typical: 5-30 in elderly)
- **Total Lesion Volume**: Sum of all lesion volumes in ml (typical: <10ml)
- **Dice Coefficient**: Overlap with manual segmentation (acceptable: >0.75)
- **False Positive Rate**: Proportion of incorrect detections (acceptable: <0.15)
- **Sensitivity**: True positive detection rate (acceptable: >0.80)

**Common Issues in Discarded Results**:
- Over-segmentation of normal tissue
- Poor FLAIR image contrast
- Unrealistic lesion volumes (>40ml indicates error)
- High false positive rate
- Motion or scanner artifacts

### 3. TRACULA (Diffusion Tractography)
**Purpose**: White matter pathway reconstruction

**What it does**:
- Diffusion tensor imaging (DTI) analysis
- Fiber tract reconstruction
- White matter connectivity mapping
- Major pathway identification (CST, ILF, SLF, etc.)

**Quality Metrics**:
- **FA Mean**: Average fractional anisotropy (typical: 0.35-0.50)
- **Tract Volume**: Total volume of reconstructed tracts (typical: 12000-18000 mm³)
- **Streamline Count**: Number of fiber streamlines (typical: 4000-8000)
- **Anatomical Plausibility**: How anatomically correct the tracts are (acceptable: >0.85)
- **Connection Strength**: Measure of connectivity confidence (acceptable: >0.75)

**Common Issues in Discarded Results**:
- Fragmented/discontinuous tracts
- Missing major pathways
- Spurious non-anatomical tracts
- Low FA values (indicating poor DTI quality)
- Motion artifacts in diffusion data
- Insufficient b-values or directions

## Feature Details

### View Modes

#### 1. Grid View
- **Layout**: 3×2 comparison grid
- **Rows**: Acceptable (top) vs Discarded (bottom)
- **Columns**: FreeSurfer, LPA, TRACULA
- **Features**:
  - Quick visual comparison
  - At-a-glance quality metrics
  - Hover to see details
  - Click to switch to detailed view

#### 2. Detailed View
- **Layout**: Stacked pipeline-by-pipeline comparison
- **Features**:
  - Large image displays
  - Complete metric listings
  - Detailed issue descriptions
  - Patient information
  - Quality notes and recommendations

### Information Displayed

For each pipeline result, the system shows:

**Patient Information**:
- Patient ID
- Patient Name
- Scan Date

**Quality Metrics**:
- Pipeline-specific quantitative measures
- Color-coded values (green for acceptable, red for discarded)

**Visual Outputs**:
- Brain imaging with analysis overlays
- Segmentation boundaries
- Lesion highlights
- Fiber tract visualizations

**For Discarded Results**:
- List of specific issues detected
- Quality flags and warnings
- Recommendations for re-processing

**For Acceptable Results**:
- Quality assurance notes
- Confirmation of anatomical plausibility

## Clinical Significance

### Why Quality Control Matters

1. **Diagnostic Accuracy**: Poor quality imaging analysis can lead to incorrect clinical decisions
2. **Research Validity**: Studies using low-quality data produce unreliable results
3. **Automated Detection**: AI/ML models trained on poor data will have reduced accuracy
4. **Cost Efficiency**: Identifying failed analyses early prevents wasted processing time
5. **Patient Safety**: Ensures only high-confidence results inform treatment decisions

### When to Discard Results

Results should be discarded when:
- Quality metrics fall below acceptable thresholds
- Visual inspection reveals obvious errors
- Anatomical implausibility is detected
- Motion artifacts are severe
- Scanner/sequence parameters were incorrect
- Multiple quality flags are raised

### Re-processing Recommendations

When results are discarded:
1. **Check original scan quality**: Review raw DICOM images
2. **Verify acquisition parameters**: Ensure correct scanner settings
3. **Motion assessment**: Check for patient movement
4. **Re-run with adjusted parameters**: Modify pipeline settings if needed
5. **Manual review**: Consider manual correction or alternative methods
6. **Rescan if necessary**: Acquire new images if quality is unrecoverable

## Technical Implementation

### Frontend
- **Component**: `Analysis3DPage.tsx` with `QualityControlView` sub-component
- **Features**:
  - Responsive grid layout
  - Interactive image viewing
  - Toggle between grid and detailed views
  - Color-coded quality indicators
  - Issue highlighting with icons

### Backend
- **Endpoint**: `/api/v1/analysis-3d/data?analysis_type=quality-control`
- **Function**: `generate_quality_control_view()`
- **Returns**: Structured JSON with pipeline comparisons

### Data Structure
```typescript
interface QualityControlData {
  pipelines: Array<{
    name: string
    description: string
    acceptable: {
      patient_id: string
      patient_name: string
      scan_date: string
      image_url: string
      metrics: Record<string, number>
      notes: string
    }
    discarded: {
      patient_id: string
      patient_name: string
      scan_date: string
      image_url: string
      metrics: Record<string, number>
      issues: string[]
      notes: string
    }
  }>
}
```

## Usage Guide

### Accessing Quality Control

1. Navigate to **3D Analysis** tab in the main dashboard
2. Select **Quality Control** from the analysis type buttons
3. Choose between **Grid View** (overview) or **Detailed View** (in-depth)

### Interpreting Results

**Green Border/Icon (Acceptable)**:
- All quality metrics within acceptable range
- Visual inspection passed
- Safe to use for clinical/research purposes

**Red Border/Icon (Discarded)**:
- One or more quality metrics failed
- Visual artifacts detected
- Should NOT be used for analysis
- Requires attention/re-processing

### Best Practices

1. **Always review QC results** before including data in analyses
2. **Document rejection reasons** for audit trail
3. **Track QC pass/fail rates** by scanner and protocol
4. **Periodic manual review** of automated QC decisions
5. **Maintain QC thresholds** appropriate for your specific use case

## Future Enhancements

Planned improvements:
- [ ] Upload custom brain images for QC assessment
- [ ] Automated QC scoring with ML models
- [ ] Batch QC processing for multiple patients
- [ ] Export QC reports as PDF
- [ ] Integration with PACS systems
- [ ] Real-time QC during scan acquisition
- [ ] Historical QC trend analysis
- [ ] Scanner-specific QC benchmarks

## References

- FreeSurfer: https://surfer.nmr.mgh.harvard.edu/
- FSL (includes LPA tools): https://fsl.fmrib.ox.ac.uk/fsl/
- TRACULA: https://surfer.nmr.mgh.harvard.edu/fswiki/Tracula

## Support

For issues or questions about the Quality Control feature:
- Review the detailed metric descriptions above
- Check the interaction guide in the UI
- Consult neuroimaging documentation for pipeline-specific details
- Contact your system administrator for data-specific questions

