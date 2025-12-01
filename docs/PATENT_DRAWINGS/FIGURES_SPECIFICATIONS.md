# مشخصات نقشه‌های فنی Patent - NeuroPredict-AI
# Patent Drawing Figures Specifications

## 📋 فهرست نقشه‌ها

این سند مشخصات کامل تمام نقشه‌های مورد نیاز برای ثبت اختراع را شامل می‌شود.

---

## Figure 1: System Architecture

**عنوان کامل**: "FIG. 1 - Multi-Modal Clinical Decision Support System Architecture"

### توضیحات:
این نقشه معماری کلی سیستم NeuroPredict-AI را نشان می‌دهد.

### Reference Numerals:

- **100**: Frontend Web Application (React)
- **110**: Admin Dashboard (React)
- **120**: Mobile Application (React Native) - Optional
- **200**: API Gateway / Load Balancer
- **210**: Authentication Service
- **220**: Data Processing Engine
- **230**: AI Model Service
- **240**: Data Fusion Service (Patent-Pending)
- **250**: Image Processing Service
- **300**: PostgreSQL Database
- **310**: Image Storage (File System/Object Storage)
- **320**: Redis Cache
- **400**: External PACS System
- **410**: EHR/HIS Integration
- **500**: Network Interface
- **600**: Security Layer (Encryption, Firewall)

### اجزای اصلی:
- Client Layer
- Application Layer
- Data Layer
- External Systems Layer

---

## Figure 2: Multi-Modal Neural Network Architecture

**عنوان کامل**: "FIG. 2 - Multi-Modal Deep Learning Neural Network Architecture"

### توضیحات:
این نقشه معماری کامل شبکه عصبی چندوجهی را نشان می‌دهد.

### Reference Numerals:

**Input Layer (100-140):**
- **100**: Input Layer (50-dimensional feature vector)
- **110**: Demographic Features Input (Age, Gender, Education)
- **120**: Cognitive Features Input (MMSE, MoCA, Memory, Attention, Executive Function)
- **130**: Biomarker Features Input (Amyloid-beta, Tau, Dopamine)
- **140**: Imaging Features Input (Hippocampal Volume, Cortical Thickness, Ventricular Volume, etc.)
- **145**: Genetic Features Input (APOE ε4 Status)

**Normalization Layer (200):**
- **200**: Feature Normalization Module

**Feature Extraction Layers (300-330):**
- **300**: Feature Extractor Network
- **310**: Hidden Layer 1 (256 neurons)
- **315**: ReLU Activation Layer
- **320**: Hidden Layer 2 (128 neurons)
- **325**: Batch Normalization Layer
- **330**: Hidden Layer 3 (64 neurons)
- **335**: Dropout Layer (0.3)

**Fusion Layer (400):**
- **400**: Multi-Modal Feature Fusion Layer

**Output Heads (500-520):**
- **500**: Alzheimer's Disease Prediction Head
- **510**: Intermediate Layer (32 neurons)
- **515**: Output Neuron with Sigmoid Activation
- **520**: Parkinson's Disease Prediction Head
- **525**: Intermediate Layer (32 neurons)
- **530**: Output Neuron with Sigmoid Activation

**Output (600):**
- **600**: Alzheimer's Risk Probability Output
- **610**: Parkinson's Risk Probability Output
- **620**: Confidence Score Output

### جریان داده:
```
Input Features (110-145) → Normalization (200) → 
Feature Extractor (310→320→330) → Fusion (400) → 
Output Heads (500, 520) → Risk Scores (600, 610)
```

---

## Figure 3: Multi-Modal Data Fusion System

**عنوان کامل**: "FIG. 3 - Multi-Modal Data Fusion Algorithm Architecture"

### توضیحات:
این نقشه سیستم فیوژن داده چندوجهی (Patent-Pending) را نشان می‌دهد.

### Reference Numerals:

**Input Data Sources (100-140):**
- **100**: Cognitive Data Module
- **110**: Biomarker Data Module
- **120**: Imaging Data Module
- **130**: Genetic Data Module

**Preprocessing (200-240):**
- **200**: Data Validation Module
- **210**: Cognitive Data Preprocessor
- **220**: Biomarker Data Preprocessor
- **230**: Imaging Feature Extractor
- **240**: Genetic Data Encoder

**Feature Extraction (300-340):**
- **300**: Cognitive Score Calculator
- **310**: Biomarker Score Calculator
- **320**: Imaging Score Calculator
- **330**: Cross-Modal Correlation Analyzer

**Fusion Engine (400-450):**
- **400**: Weighted Fusion Module
- **410**: Attention Mechanism
- **420**: Conflict Resolution Module
- **430**: Confidence Calculation Module
- **440**: Fusion Algorithm (Patent-Pending)
- **450**: Fused Feature Vector Generator

**Output (500-520):**
- **500**: Unified Feature Representation
- **510**: Confidence Scores per Modality
- **520**: Cross-Modal Correlation Matrix

### الگوریتم Fusion:
```
1. Weight Calculation (based on data quality)
2. Attention Mechanism (dynamic weighting)
3. Correlation Analysis (cross-modal)
4. Conflict Resolution (inconsistency detection)
5. Weighted Combination
6. Confidence Scoring
```

---

## Figure 4: Clinical Decision Support Workflow

**عنوان کامل**: "FIG. 4 - Clinical Decision Support Workflow Diagram"

### توضیحات:
این نقشه جریان کامل فرآیند پشتیبانی تصمیم‌گیری بالینی را نشان می‌دهد.

### Reference Numerals:

**Initial Phase (100-150):**
- **100**: Patient Registration Module
- **110**: Consent and Authorization
- **120**: Patient Data Entry

**Data Collection Phase (200-250):**
- **200**: Medical History Collection
- **210**: Cognitive Assessment Input (MMSE, MoCA)
- **220**: Biomarker Data Entry
- **230**: Medical Image Upload (DICOM)
- **240**: Genetic Information Input

**Validation Phase (300-320):**
- **300**: Data Validation Module
- **310**: Quality Check Module
- **320**: Completeness Verification

**Processing Phase (400-450):**
- **400**: Image Preprocessing Module
- **410**: Feature Extraction Module
- **420**: Data Fusion Module (Patent-Pending)
- **430**: Data Normalization

**AI Analysis Phase (500-550):**
- **500**: Neural Network Inference Engine
- **510**: Alzheimer's Risk Calculation
- **520**: Parkinson's Risk Calculation
- **530**: Confidence Score Generation
- **540**: Feature Importance Analysis

**Output Phase (600-650):**
- **600**: Risk Stratification Module
- **610**: Clinical Recommendation Generator
- **620**: Report Generation Module
- **630**: Visualization Generator
- **640**: Interactive Dashboard

**Review Phase (700-720):**
- **700**: Clinical Review Interface
- **710**: Physician Approval Module
- **720**: Report Finalization

### Decision Points:
- Data Quality Check → Accept/Reject
- Risk Level → Low/Medium/High
- Confidence Level → Accept/Re-evaluate

---

## Figure 5: Medical Image Processing Pipeline

**عنوان کامل**: "FIG. 5 - Medical Image Processing and Feature Extraction Pipeline"

### Reference Numerals:

**Input (100):**
- **100**: DICOM Image Input

**Preprocessing (200-240):**
- **200**: DICOM Parser
- **210**: Image Normalization Module
- **220**: Skull Stripping Module
- **230**: Bias Field Correction
- **240**: Image Registration

**Quality Assessment (300-320):**
- **300**: SNR (Signal-to-Noise Ratio) Calculator
- **310**: CNR (Contrast-to-Noise Ratio) Calculator
- **320**: Image Quality Scorer

**Feature Extraction (400-450):**
- **400**: Volumetric Analysis Module
- **410**: Hippocampal Volume Calculator
- **420**: Cortical Thickness Analyzer
- **430**: Ventricular Volume Calculator
- **440**: White Matter Hyperintensity Detector
- **450**: Texture Feature Extractor

**Deep Learning Features (500-520):**
- **500**: CNN Feature Extractor
- **510**: Feature Vector (32 dimensions)

**Output (600):**
- **600**: Extracted Imaging Features
- **610**: Quality Metrics
- **620**: Processed Image Data

---

## Figure 6: Detailed Data Fusion Algorithm

**عنوان کامل**: "FIG. 6 - Detailed Multi-Modal Data Fusion Algorithm Flow"

### Reference Numerals:

**Input Modules (100-140):**
- **100**: Cognitive Score Input (0-100)
- **110**: Biomarker Score Input (0-100)
- **120**: Imaging Score Input (0-100)

**Weight Calculation (200-230):**
- **200**: Data Quality Assessor
- **210**: Confidence Weight Calculator
- **220**: Modality Reliability Scorer
- **230**: Dynamic Weight Adjuster

**Attention Mechanism (300-320):**
- **300**: Attention Weight Generator
- **310**: Cross-Modal Attention
- **320**: Self-Attention Module

**Fusion Algorithm (400-450):**
- **400**: Weighted Sum Calculator
- **410**: Correlation-Based Adjuster
- **420**: Conflict Resolver
- **430**: Consistency Checker
- **440**: Final Fusion Combiner
- **450**: Confidence Aggregator

**Output (500-510):**
- **500**: Fused Score (0-100)
- **510**: Overall Confidence Score

### Mathematical Formula (برای توضیحات):
```
Fused Score = Σ(Wi × Si × Ci) / Σ(Wi × Ci)

Where:
- Wi = Weight for modality i
- Si = Score for modality i
- Ci = Confidence for modality i
```

---

## Figure 7: Feature Extraction Process

**عنوان کامل**: "FIG. 7 - Multi-Modal Feature Extraction and Engineering Process"

### Reference Numerals:

**Raw Data Input (100-140):**
- **100**: Raw Imaging Data
- **110**: Raw Clinical Data
- **120**: Raw Biomarker Data
- **130**: Raw Genetic Data

**Feature Engineering (200-240):**
- **200**: Demographic Feature Engineering
- **210**: Cognitive Feature Engineering
- **220**: Biomarker Feature Engineering
- **230**: Imaging Feature Engineering

**Feature Selection (300-320):**
- **300**: Feature Importance Analyzer
- **310**: Feature Selector
- **320**: Dimensionality Reducer

**Normalized Features (400):**
- **400**: Normalized Feature Vector (50 dimensions)

---

## Figure 8: Risk Stratification Algorithm

**عنوان کامل**: "FIG. 8 - Risk Stratification and Clinical Decision Algorithm"

### Reference Numerals:

**Input (100):**
- **100**: Risk Probability Score (0.0-1.0)

**Threshold Calculation (200-230):**
- **200**: Low Risk Threshold (0.0-0.3)
- **210**: Medium Risk Threshold (0.31-0.7)
- **220**: High Risk Threshold (0.71-1.0)

**Risk Level Assignment (300-320):**
- **300**: Low Risk Classifier
- **310**: Medium Risk Classifier
- **320**: High Risk Classifier

**Recommendation Generator (400-430):**
- **400**: Low Risk Recommendation Engine
- **410**: Medium Risk Recommendation Engine
- **420**: High Risk Recommendation Engine
- **430**: Follow-up Scheduler

**Output (500-520):**
- **500**: Risk Level (Low/Medium/High)
- **510**: Clinical Recommendations
- **520**: Follow-up Timeline

---

## Figure 9: User Interface Layout

**عنوان کامل**: "FIG. 9 - Clinical Decision Support User Interface Layout"

### Reference Numerals:

**Interface Components (100-150):**
- **100**: Header Navigation Bar
- **110**: Sidebar Menu
- **120**: Main Content Area
- **130**: Patient Information Panel
- **140**: Data Input Forms
- **150**: Results Display Panel

**Visualization Components (200-250):**
- **200**: Risk Score Display
- **210**: Confidence Indicator
- **220**: Feature Importance Chart
- **230**: Trend Visualization
- **240**: Comparative Charts

**Action Buttons (300-320):**
- **300**: Run Prediction Button
- **310**: Generate Report Button
- **320**: Export Data Button

---

## Figure 10: Database Schema

**عنوان کامل**: "FIG. 10 - Database Schema and Data Relationships"

### Reference Numerals:

**Core Tables (100-150):**
- **100**: Users Table
- **110**: Patients Table
- **120**: Medical Records Table
- **130**: Imaging Studies Table
- **140**: Predictions Table
- **150**: Data Fusion Reports Table

**Relationship Lines:**
- **200**: One-to-Many Relationship
- **210**: Foreign Key Relationship

---

## 📐 مشخصات فنی برای Patent Drawings

### اندازه صفحه:
- **Width**: 21.6 cm (8.5 inches)
- **Height**: 27.9 cm (11 inches)

### Margins:
- **Top**: 2.5 cm (1 inch)
- **Bottom**: 1.3 cm (0.5 inches)
- **Left**: 1.3 cm (0.5 inches)
- **Right**: 1.3 cm (0.5 inches)

### Reference Numerals:
- **اندازه فونت**: حداقل 1.32 mm (0.052 inches)
- **Style**: Bold
- **رنگ**: مشکی (#000000)

### خطوط:
- **ضخامت**: 0.3-0.5 mm (خطوط اصلی)
- **رنگ**: مشکی (#000000)
- **Style**: Solid

### رزولوشن:
- **حداقل**: 300 DPI
- **ترجیحی**: 600 DPI

### فرمت:
- **TIFF**: ترجیح داده می‌شود
- **PDF**: قابل قبول (High Quality)
- **JPEG**: قابل قبول (Quality 95%+)

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: Ready for Drawing  
**نسخه**: 1.0

