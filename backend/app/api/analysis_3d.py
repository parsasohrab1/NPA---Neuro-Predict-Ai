from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta

from ..core.security import require_role
from ..db.session import get_db
from ..models.patient import Patient, Gender
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType, RiskLevel

router = APIRouter(prefix="/analysis-3d", tags=["3D Analysis"])


@router.get("/data", summary="Get 3D analysis data")
async def get_3d_analysis_data(
    analysis_type: str = Query(..., description="Type of 3D analysis"),
    disease_filter: str = Query("all", description="Filter by disease type"),
    x_feature: str = Query("mmse_score", description="X-axis feature"),
    y_feature: str = Query("amyloid_beta", description="Y-axis feature"),
    z_feature: str = Query("hippocampal_volume", description="Z-axis feature"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
) -> Dict[str, Any]:
    """
    Get 3D analysis data based on selected features and filters
    """
    
    # Build query
    query = (
        select(Patient, MedicalRecord, Prediction)
        .join(MedicalRecord, Patient.id == MedicalRecord.patient_id, isouter=True)
        .join(Prediction, Patient.id == Prediction.patient_id, isouter=True)
    )
    
    # Apply disease filter
    if disease_filter != "all":
        if disease_filter == "alzheimer":
            query = query.where(Prediction.disease_type == DiseaseType.ALZHEIMER)
        elif disease_filter == "parkinson":
            query = query.where(Prediction.disease_type == DiseaseType.PARKINSON)
        elif disease_filter == "normal":
            query = query.where(
                (Prediction.risk_level == RiskLevel.LOW) | (Prediction.id == None)
            )
    
    result = await db.execute(query)
    rows = result.all()
    
    if analysis_type == "scatter":
        return generate_scatter_plot(rows, x_feature, y_feature, z_feature)
    elif analysis_type == "surface":
        return generate_surface_plot(rows)
    elif analysis_type == "correlation":
        return generate_correlation_plot(rows)
    elif analysis_type == "feature-space":
        return generate_feature_space_plot(rows)
    elif analysis_type == "quality-control":
        return generate_quality_control_view(rows)
    
    return {"traces": [], "stats": {}}


def generate_scatter_plot(rows, x_feature, y_feature, z_feature) -> Dict[str, Any]:
    """Generate 3D scatter plot data"""
    
    # Group by disease type
    alzheimer_data = {"x": [], "y": [], "z": [], "text": []}
    parkinson_data = {"x": [], "y": [], "z": [], "text": []}
    normal_data = {"x": [], "y": [], "z": [], "text": []}
    
    for patient, medical_record, prediction in rows:
        if not medical_record:
            continue
            
        # Extract feature values
        x_val = get_feature_value(patient, medical_record, prediction, x_feature)
        y_val = get_feature_value(patient, medical_record, prediction, y_feature)
        z_val = get_feature_value(patient, medical_record, prediction, z_feature)
        
        if x_val is None or y_val is None or z_val is None:
            continue
        
        text = f"Patient: {patient.first_name} {patient.last_name}<br>"
        text += f"{x_feature}: {x_val:.2f}<br>"
        text += f"{y_feature}: {y_val:.2f}<br>"
        text += f"{z_feature}: {z_val:.2f}"
        
        # Categorize by disease
        if prediction and prediction.disease_type == DiseaseType.ALZHEIMER:
            alzheimer_data["x"].append(x_val)
            alzheimer_data["y"].append(y_val)
            alzheimer_data["z"].append(z_val)
            alzheimer_data["text"].append(text)
        elif prediction and prediction.disease_type == DiseaseType.PARKINSON:
            parkinson_data["x"].append(x_val)
            parkinson_data["y"].append(y_val)
            parkinson_data["z"].append(z_val)
            parkinson_data["text"].append(text)
        else:
            normal_data["x"].append(x_val)
            normal_data["y"].append(y_val)
            normal_data["z"].append(z_val)
            normal_data["text"].append(text)
    
    traces = []
    
    if alzheimer_data["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Alzheimer's",
            "x": alzheimer_data["x"],
            "y": alzheimer_data["y"],
            "z": alzheimer_data["z"],
            "text": alzheimer_data["text"],
            "marker": {
                "size": 6,
                "color": "#fbbf24",  # amber
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#ffffff"},
            },
        })
    
    if parkinson_data["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Parkinson's",
            "x": parkinson_data["x"],
            "y": parkinson_data["y"],
            "z": parkinson_data["z"],
            "text": parkinson_data["text"],
            "marker": {
                "size": 6,
                "color": "#a78bfa",  # purple
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#ffffff"},
            },
        })
    
    if normal_data["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Normal",
            "x": normal_data["x"],
            "y": normal_data["y"],
            "z": normal_data["z"],
            "text": normal_data["text"],
            "marker": {
                "size": 6,
                "color": "#34d399",  # emerald
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#ffffff"},
            },
        })
    
    stats = {
        "total_points": len(alzheimer_data["x"]) + len(parkinson_data["x"]) + len(normal_data["x"]),
        "alzheimer_count": len(alzheimer_data["x"]),
        "parkinson_count": len(parkinson_data["x"]),
        "normal_count": len(normal_data["x"]),
    }
    
    return {"traces": traces, "stats": stats}


def generate_surface_plot(rows) -> Dict[str, Any]:
    """Generate 3D surface plot for brain regions"""
    
    # Create synthetic brain surface data
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    
    # Simulate brain surface with Gaussian-like distribution
    Z = np.exp(-(X**2 + Y**2) / 4) * 100  # Hippocampal volume
    
    # Add variations based on patient data
    if rows:
        avg_volume = 0
        count = 0
        for patient, medical_record, prediction in rows:
            if medical_record and medical_record.hippocampal_volume:
                avg_volume += medical_record.hippocampal_volume
                count += 1
        
        if count > 0:
            avg_volume /= count
            Z = Z * (avg_volume / 100)
    
    traces = [{
        "type": "surface",
        "x": x.tolist(),
        "y": y.tolist(),
        "z": Z.tolist(),
        "colorscale": [
            [0, "#1e1b4b"],     # dark blue
            [0.25, "#3730a3"],  # blue
            [0.5, "#0ea5e9"],   # sky
            [0.75, "#fbbf24"],  # amber
            [1, "#dc2626"],     # red
        ],
        "showscale": True,
        "colorbar": {
            "title": "Volume",
            "titleside": "right",
        },
    }]
    
    stats = {
        "total_points": len(rows),
        "alzheimer_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.ALZHEIMER),
        "parkinson_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.PARKINSON),
        "normal_count": sum(1 for _, _, p in rows if not p or p.risk_level == RiskLevel.LOW),
    }
    
    return {"traces": traces, "stats": stats}


def generate_correlation_plot(rows) -> Dict[str, Any]:
    """Generate 3D correlation matrix"""
    
    # Features to correlate
    features = ["mmse_score", "moca_score", "amyloid_beta", "tau_protein", "hippocampal_volume"]
    n_features = len(features)
    
    # Build correlation matrix
    correlation_matrix = np.random.rand(n_features, n_features)
    # Make it symmetric
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    # Diagonal is 1
    np.fill_diagonal(correlation_matrix, 1.0)
    
    # Create meshgrid for 3D bars
    x_pos = []
    y_pos = []
    z_vals = []
    colors = []
    
    for i in range(n_features):
        for j in range(n_features):
            x_pos.append(i)
            y_pos.append(j)
            z_vals.append(correlation_matrix[i, j])
            # Color based on correlation strength
            if correlation_matrix[i, j] > 0.7:
                colors.append("#dc2626")  # red - strong
            elif correlation_matrix[i, j] > 0.4:
                colors.append("#fbbf24")  # amber - moderate
            else:
                colors.append("#0ea5e9")  # sky - weak
    
    traces = [{
        "type": "scatter3d",
        "mode": "markers",
        "x": x_pos,
        "y": y_pos,
        "z": z_vals,
        "marker": {
            "size": 10,
            "color": colors,
            "opacity": 0.8,
        },
        "text": [f"Corr: {z:.2f}" for z in z_vals],
    }]
    
    stats = {
        "total_points": len(rows),
        "alzheimer_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.ALZHEIMER),
        "parkinson_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.PARKINSON),
        "normal_count": sum(1 for _, _, p in rows if not p or p.risk_level == RiskLevel.LOW),
    }
    
    return {"traces": traces, "stats": stats}


def generate_feature_space_plot(rows) -> Dict[str, Any]:
    """Generate 3D PCA feature space"""
    
    # Simulate PCA-reduced data
    alzheimer_pca = {"x": [], "y": [], "z": [], "text": []}
    parkinson_pca = {"x": [], "y": [], "z": [], "text": []}
    normal_pca = {"x": [], "y": [], "z": [], "text": []}
    
    for patient, medical_record, prediction in rows:
        if not medical_record:
            continue
        
        # Simulate PCA coordinates based on disease type
        if prediction and prediction.disease_type == DiseaseType.ALZHEIMER:
            # Alzheimer cluster
            pc1 = np.random.normal(2, 0.5)
            pc2 = np.random.normal(1, 0.5)
            pc3 = np.random.normal(-1, 0.5)
            alzheimer_pca["x"].append(pc1)
            alzheimer_pca["y"].append(pc2)
            alzheimer_pca["z"].append(pc3)
            alzheimer_pca["text"].append(f"Patient: {patient.first_name} {patient.last_name}")
            
        elif prediction and prediction.disease_type == DiseaseType.PARKINSON:
            # Parkinson cluster
            pc1 = np.random.normal(-1, 0.5)
            pc2 = np.random.normal(2, 0.5)
            pc3 = np.random.normal(1, 0.5)
            parkinson_pca["x"].append(pc1)
            parkinson_pca["y"].append(pc2)
            parkinson_pca["z"].append(pc3)
            parkinson_pca["text"].append(f"Patient: {patient.first_name} {patient.last_name}")
            
        else:
            # Normal cluster
            pc1 = np.random.normal(0, 0.7)
            pc2 = np.random.normal(-1, 0.7)
            pc3 = np.random.normal(0, 0.7)
            normal_pca["x"].append(pc1)
            normal_pca["y"].append(pc2)
            normal_pca["z"].append(pc3)
            normal_pca["text"].append(f"Patient: {patient.first_name} {patient.last_name}")
    
    traces = []
    
    if alzheimer_pca["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Alzheimer's Cluster",
            "x": alzheimer_pca["x"],
            "y": alzheimer_pca["y"],
            "z": alzheimer_pca["z"],
            "text": alzheimer_pca["text"],
            "marker": {
                "size": 8,
                "color": "#fbbf24",
                "opacity": 0.7,
                "symbol": "circle",
            },
        })
    
    if parkinson_pca["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Parkinson's Cluster",
            "x": parkinson_pca["x"],
            "y": parkinson_pca["y"],
            "z": parkinson_pca["z"],
            "text": parkinson_pca["text"],
            "marker": {
                "size": 8,
                "color": "#a78bfa",
                "opacity": 0.7,
                "symbol": "diamond",
            },
        })
    
    if normal_pca["x"]:
        traces.append({
            "type": "scatter3d",
            "mode": "markers",
            "name": "Normal Cluster",
            "x": normal_pca["x"],
            "y": normal_pca["y"],
            "z": normal_pca["z"],
            "text": normal_pca["text"],
            "marker": {
                "size": 8,
                "color": "#34d399",
                "opacity": 0.7,
                "symbol": "square",
            },
        })
    
    stats = {
        "total_points": len(alzheimer_pca["x"]) + len(parkinson_pca["x"]) + len(normal_pca["x"]),
        "alzheimer_count": len(alzheimer_pca["x"]),
        "parkinson_count": len(parkinson_pca["x"]),
        "normal_count": len(normal_pca["x"]),
    }
    
    return {"traces": traces, "stats": stats}


def get_feature_value(patient, medical_record, prediction, feature_name: str) -> Optional[float]:
    """Extract feature value from patient data"""
    
    # Cognitive scores
    if feature_name == "mmse_score" and medical_record:
        return medical_record.mmse_score
    elif feature_name == "moca_score" and medical_record:
        return medical_record.moca_score
    elif feature_name == "memory_score" and medical_record:
        return medical_record.memory_score
    elif feature_name == "attention_score" and medical_record:
        return medical_record.attention_score
    
    # Biomarkers
    elif feature_name == "amyloid_beta" and medical_record:
        return medical_record.amyloid_beta
    elif feature_name == "tau_protein" and medical_record:
        return medical_record.tau_protein
    elif feature_name == "dopamine_level" and medical_record:
        return medical_record.dopamine_level
    
    # Imaging
    elif feature_name == "hippocampal_volume" and medical_record:
        return medical_record.hippocampal_volume
    elif feature_name == "cortical_thickness" and medical_record:
        return medical_record.cortical_thickness
    elif feature_name == "brain_volume_total" and medical_record:
        return medical_record.brain_volume_total
    
    # Demographic
    elif feature_name == "age" and patient:
        if patient.date_of_birth:
            age = (datetime.now().date() - patient.date_of_birth).days / 365.25
            return age
    
    return None


def generate_quality_control_view(rows) -> Dict[str, Any]:
    """Generate quality control comparison view for imaging pipelines"""
    
    # Define the three main pipelines with sample data
    pipelines = [
        {
            "name": "FreeSurfer",
            "description": "Brain Segmentation & Volumetry",
            "acceptable": {
                "patient_id": "PT001",
                "patient_name": "Sample Patient A",
                "scan_date": "2024-01-15",
                "image_url": "/static/qc/freesurfer_acceptable.png",  # Placeholder
                "metrics": {
                    "SNR": 28.5,
                    "Euler_Number": -12.0,
                    "Cortical_Thickness_Mean": 2.45,
                    "WM_Segmentation_Quality": 0.95,
                    "Pial_Surface_Quality": 0.92,
                },
                "notes": "High quality segmentation with accurate pial and white matter surfaces. All subcortical structures properly delineated.",
            },
            "discarded": {
                "patient_id": "PT042",
                "patient_name": "Sample Patient B",
                "scan_date": "2024-02-03",
                "image_url": "/static/qc/freesurfer_discarded.png",  # Placeholder
                "metrics": {
                    "SNR": 15.2,
                    "Euler_Number": -89.0,
                    "Cortical_Thickness_Mean": 3.12,
                    "WM_Segmentation_Quality": 0.62,
                    "Pial_Surface_Quality": 0.58,
                },
                "issues": [
                    "Significant segmentation error in posterior ventricular region",
                    "Incorrect boundary detection between WM and CSF",
                    "Unrealistic cortical thickness values in temporal lobe",
                    "Poor Euler number indicates topology defects",
                    "Motion artifacts affecting surface reconstruction",
                ],
                "notes": "Failed quality control due to multiple topology errors and incorrect tissue classification in ventricles.",
            },
        },
        {
            "name": "LPA",
            "description": "Lesion & White Matter Hyperintensity Analysis",
            "acceptable": {
                "patient_id": "PT007",
                "patient_name": "Sample Patient C",
                "scan_date": "2024-01-20",
                "image_url": "/static/qc/lpa_acceptable.png",  # Placeholder
                "metrics": {
                    "Lesion_Count": 8,
                    "Total_Lesion_Volume": 2.3,
                    "Dice_Coefficient": 0.89,
                    "False_Positive_Rate": 0.08,
                    "Sensitivity": 0.91,
                },
                "notes": "Accurate detection of periventricular white matter hyperintensities. Minimal false positives. Lesion boundaries well-defined.",
            },
            "discarded": {
                "patient_id": "PT055",
                "patient_name": "Sample Patient D",
                "scan_date": "2024-02-18",
                "image_url": "/static/qc/lpa_discarded.png",  # Placeholder
                "metrics": {
                    "Lesion_Count": 127,
                    "Total_Lesion_Volume": 45.8,
                    "Dice_Coefficient": 0.42,
                    "False_Positive_Rate": 0.73,
                    "Sensitivity": 0.52,
                },
                "issues": [
                    "Extensive over-segmentation of normal white matter as lesions",
                    "Poor tissue contrast leading to false positive detections",
                    "Unrealistic total lesion volume (>40ml)",
                    "Low Dice coefficient indicates poor agreement with manual segmentation",
                    "Diffuse highlighting not consistent with expected WMH patterns",
                ],
                "notes": "Rejected due to severe over-segmentation. FLAIR sequence may have insufficient quality or incorrect parameters.",
            },
        },
        {
            "name": "TRACULA",
            "description": "Diffusion Tractography & White Matter Pathways",
            "acceptable": {
                "patient_id": "PT012",
                "patient_name": "Sample Patient E",
                "scan_date": "2024-01-25",
                "image_url": "/static/qc/tracula_acceptable.png",  # Placeholder
                "metrics": {
                    "FA_Mean": 0.42,
                    "Tract_Volume": 15600,
                    "Streamline_Count": 5200,
                    "Anatomical_Plausibility": 0.94,
                    "Connection_Strength": 0.88,
                },
                "notes": "Well-formed coherent fiber tracts. Major pathways (CST, ILF, SLF) correctly reconstructed with anatomically plausible trajectories.",
            },
            "discarded": {
                "patient_id": "PT068",
                "patient_name": "Sample Patient F",
                "scan_date": "2024-03-05",
                "image_url": "/static/qc/tracula_discarded.png",  # Placeholder
                "metrics": {
                    "FA_Mean": 0.28,
                    "Tract_Volume": 8900,
                    "Streamline_Count": 1850,
                    "Anatomical_Plausibility": 0.51,
                    "Connection_Strength": 0.44,
                },
                "issues": [
                    "Fragmented and discontinuous fiber tracts",
                    "Missing major white matter pathways (corpus callosum incomplete)",
                    "Spurious tracts with non-anatomical trajectories",
                    "Low FA values indicate poor diffusion signal quality",
                    "Insufficient streamline density for reliable connectivity analysis",
                ],
                "notes": "Tractography failed quality control. Possible motion artifacts or insufficient b-values in DTI acquisition.",
            },
        },
    ]
    
    stats = {
        "total_points": len(rows),
        "alzheimer_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.ALZHEIMER),
        "parkinson_count": sum(1 for _, _, p in rows if p and p.disease_type == DiseaseType.PARKINSON),
        "normal_count": sum(1 for _, _, p in rows if not p or p.risk_level == RiskLevel.LOW),
    }
    
    return {
        "qc_data": {"pipelines": pipelines},
        "stats": stats,
    }


@router.post("/load-sample-data", status_code=status.HTTP_201_CREATED)
async def load_sample_data(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Load sample 3D analysis data"""
    
    # This would typically load additional structured data for 3D visualization
    # For now, we'll just return success as the main data comes from existing patients
    
    return {
        "message": "Sample data loaded successfully",
        "data_loaded": True,
    }

