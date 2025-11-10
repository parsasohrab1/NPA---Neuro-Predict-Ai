# 📖 NeuroPredict-AI User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Patient Management](#patient-management)
4. [Creating Predictions](#creating-predictions)
5. [Viewing Results](#viewing-results)
6. [Longitudinal Tracking](#longitudinal-tracking)
7. [Reports](#reports)
8. [MRI Viewer](#mri-viewer)
9. [Tips & Best Practices](#tips--best-practices)

---

## Introduction

NeuroPredict-AI is an AI-powered system for predicting and tracking neurodegenerative diseases, specifically Alzheimer's and Parkinson's. This guide will help you navigate and use all features effectively.

### Key Features
- **Patient Management**: Comprehensive patient records and medical history
- **AI Predictions**: Risk assessment using multi-modal neural networks
- **Longitudinal Tracking**: Monitor patient progression over time
- **MRI Analysis**: Advanced DICOM viewer with measurement tools
- **Reports**: Generate clinical, research, and administrative reports

---

## Getting Started

### First Login
1. Navigate to the login page
2. Use default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Change your password after first login

### Dashboard Overview
The dashboard provides:
- **Quick Stats**: Total patients, predictions, high-risk cases
- **Recent Activity**: Latest predictions and patient updates
- **Risk Distribution**: Visual breakdown of risk levels

---

## Patient Management

### Adding a New Patient
1. Go to **Patients** → Click **+ Add Patient**
2. Fill in required information:
   - Patient ID (unique identifier)
   - First Name, Last Name
   - Date of Birth
   - Gender
   - Contact Information
3. Optional fields:
   - Education Years
   - Medical History
   - Family History
   - Current Medications
4. Click **Save**

### Searching and Filtering
- **Search Bar**: Search by name or Patient ID
- **Advanced Filters**:
  - Gender
  - Age Range
  - Risk Level
  - Has Predictions
  - Date Range

### Bulk Operations
1. Select multiple patients using checkboxes
2. Options available:
   - **Export to CSV**: Download patient data
   - **Create Group**: Organize patients into groups
   - **Bulk Import**: Upload CSV file (coming soon)

---

## Creating Predictions

### Step 1: Select Patient
1. Go to **Predictions** → **New Prediction**
2. Select a patient from the dropdown
3. Ensure patient has medical records

### Step 2: Upload MRI (Optional)
1. Click **Choose DICOM file**
2. Select a `.dcm` file
3. Click **Upload DICOM**
4. Wait for upload confirmation

### Step 3: Choose Disease Type
- **Both**: Analyze for Alzheimer's and Parkinson's
- **Alzheimer's Only**: Focus on Alzheimer's risk
- **Parkinson's Only**: Focus on Parkinson's risk

### Step 4: Run Prediction
1. Click **🔬 Run Prediction**
2. Wait for AI analysis (typically 10-30 seconds)
3. Results will appear automatically

---

## Viewing Results

### Prediction Results Page
The results page includes:

#### 1. Risk Assessment Cards
- **Risk Score**: Percentage (0-100%)
- **Risk Level**: Low, Medium, or High
- **Confidence**: Model confidence in prediction

#### 2. MRI Viewer
- **Slice Navigation**: Use slider or arrow buttons
- **Zoom**: Click zoom in/out buttons
- **Window/Level**: Adjust image contrast
- **Measurements**: Click measurement tool, draw line
- **Overlay**: Compare with previous studies

#### 3. Interactive Charts
- **Feature Importance**: Top contributing factors
- **Risk Comparison**: Side-by-side comparison
- **Multi-dimensional Analysis**: Radar chart showing all dimensions

#### 4. Clinical Recommendations
- AI-generated recommendations based on results
- Follow-up suggestions
- Treatment considerations

### Exporting Results
- **Print**: Click print button for physical copy
- **Export PDF**: Download as PDF (coming soon)

---

## Longitudinal Tracking

### Creating an Episode
1. Go to **Longitudinal Tracking**
2. Select a patient
3. Click **Create New Episode**
4. Set start date and description

### Adding Visits
1. Select an episode
2. Click **Add Visit**
3. Enter visit date
4. Add metrics:
   - Cognitive scores (MMSE, MoCA)
   - Biomarkers (Amyloid-beta, Tau)
   - MRI features
5. Upload imaging studies if available

### Timeline View
- **Drag & Drop**: Reorder visits by dragging
- **Compare**: Select multiple visits for comparison
- **Reports**: Click link icon to view related reports

### Metric Trends
- Select a metric from dropdown
- View trend chart over time
- See progression speed indicators

---

## Reports

### Generating Reports
1. Go to **Reports** section
2. Select report type:
   - **Summary**: Patient overview
   - **Cohort Patient vs Average**: Compare with cohort
   - **Cohort vs Cohort**: Compare two cohorts
3. Set date range
4. Configure cohort filters (if applicable)
5. Click **Generate Report**

### Report Types

#### Clinical Reports
- Patient-specific analysis
- Risk assessment summary
- Clinical recommendations

#### Research Reports
- Cohort comparisons
- Statistical analysis
- Research insights

#### Administrative Reports
- Population statistics
- Resource utilization
- Compliance metrics

### Exporting Reports
- **Excel**: Download as `.xlsx`
- **PDF**: Download as `.pdf`
- **Heatmap**: Visual comparison charts

---

## MRI Viewer

### Basic Navigation
- **Slice Selection**: Use slider or arrow keys
- **Zoom**: Mouse wheel or zoom buttons
- **Pan**: Click and drag

### Measurement Tools
1. Click **Measurement** icon
2. Click start point on image
3. Click end point
4. Distance displayed in millimeters

### Window/Level Adjustment
- **Window**: Controls contrast range
- **Level**: Controls brightness center
- Adjust sliders for optimal viewing

### Overlay Mode
1. Select two studies
2. Click **Overlay** button
3. Adjust opacity slider
4. Compare side-by-side

### 3D Highlights
- Click **3D** button to highlight regions
- Useful for volume visualization

---

## Tips & Best Practices

### Data Quality
- **Complete Records**: Fill all available fields for better predictions
- **Regular Updates**: Update medical records after each visit
- **Image Quality**: Ensure DICOM files are properly formatted

### Prediction Accuracy
- **Multiple Data Points**: More visits = better predictions
- **Recent Data**: Use latest medical records
- **Complete Biomarkers**: Include all available biomarker data

### Workflow Optimization
- **Use Filters**: Quickly find patients with specific criteria
- **Create Groups**: Organize patients by condition or study
- **Schedule Reports**: Set up automated report generation
- **Review Alerts**: Check combined alerts regularly

### Security
- **Password Policy**: Use strong passwords
- **Access Control**: Assign appropriate roles
- **Audit Logs**: Review access logs regularly

---

## Troubleshooting

### Common Issues

**Problem**: Prediction fails
- **Solution**: Ensure patient has medical records
- **Solution**: Check DICOM file format

**Problem**: MRI viewer not loading
- **Solution**: Verify DICOM file is valid
- **Solution**: Check file size (max 100MB)

**Problem**: Reports not generating
- **Solution**: Ensure date range is valid
- **Solution**: Check cohort has sufficient data

### Getting Help
- Check [API Documentation](API.md)
- Review [Architecture Guide](ARCHITECTURE.md)
- Contact system administrator

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search | `Ctrl/Cmd + K` |
| New Patient | `Ctrl/Cmd + N` |
| New Prediction | `Ctrl/Cmd + P` |
| Save | `Ctrl/Cmd + S` |
| Print | `Ctrl/Cmd + P` |

---

*Last Updated: November 2024*

