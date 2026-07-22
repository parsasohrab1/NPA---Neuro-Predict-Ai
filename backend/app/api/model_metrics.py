"""
Model Metrics API Endpoints
API for retrieving model training and validation metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

from ..db.session import get_db
from ..core.security import require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-metrics", tags=["Model Metrics"])


@router.get("/current")
async def get_current_model_metrics(
    current_user = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """
    Get current model metrics including accuracy, precision, recall, F1-score
    """
    try:
        # Try to load metrics from default location
        metrics_files = [
            Path("models") / "model_metrics.json",
            Path("models") / "real_data_trained" / "model_metrics.json",
            Path("backend") / "models" / "model_metrics.json"
        ]
        
        metrics = None
        for metrics_file in metrics_files:
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r', encoding='utf-8') as f:
                        metrics = json.load(f)
                    logger.info(f"Loaded metrics from {metrics_file}")
                    break
                except Exception as e:
                    logger.warning(f"Error reading {metrics_file}: {e}")
                    continue
        
        if metrics is None:
            # Return default/empty metrics
            return {
                "status": "no_metrics_available",
                "message": "Model metrics not found. Please train and validate the model first.",
                "alzheimer": {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0
                },
                "parkinson": {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0
                },
                "overall_accuracy": 0.0
            }
        
        # Format response
        response = {
            "status": "success",
            "model_path": metrics.get("model_path", "Unknown"),
            "validation_date": metrics.get("validation_date", "Unknown"),
            "test_samples": metrics.get("test_samples", 0),
            "alzheimer": metrics.get("alzheimer", {}),
            "parkinson": metrics.get("parkinson", {}),
            "overall_accuracy": metrics.get("overall_accuracy", 0.0)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving model metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model metrics: {str(e)}"
        )


@router.get("/training-history")
async def get_training_history(
    current_user = Depends(require_role("admin"))
) -> Dict[str, Any]:
    """
    Get training history including loss and accuracy curves
    """
    try:
        # Look for training metrics in model directory
        model_dirs = [
            Path("models") / "real_data_trained",
            Path("models"),
            Path("backend") / "models"
        ]
        
        training_data = None
        for model_dir in model_dirs:
            if not model_dir.exists():
                continue
                
            # Look for metrics JSON files
            metrics_files = list(model_dir.glob("**/model_metrics.json"))
            for metrics_file in metrics_files:
                try:
                    with open(metrics_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'training' in data and 'training_history' in data['training']:
                            training_data = data['training']
                            logger.info(f"Found training history in {metrics_file}")
                            break
                except Exception as e:
                    logger.warning(f"Error reading {metrics_file}: {e}")
                    continue
            
            if training_data:
                break
        
        if training_data is None:
            return {
                "status": "no_training_data",
                "message": "Training history not found.",
                "history": {}
            }
        
        return {
            "status": "success",
            "training": training_data
        }
        
    except Exception as e:
        logger.error(f"Error retrieving training history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving training history: {str(e)}"
        )


@router.get("/summary")
async def get_model_summary(
    current_user=Depends(require_role("admin")),
) -> Dict[str, Any]:
    """
    Get summary of model metrics for dashboard display
    """
    try:
        # Get current metrics
        metrics_response = await get_current_model_metrics(current_user=current_user)
        
        if metrics_response.get("status") == "no_metrics_available":
            return {
                "status": "no_data",
                "overall_accuracy": 0.0,
                "alzheimer_accuracy": 0.0,
                "parkinson_accuracy": 0.0,
                "has_metrics": False
            }
        
        return {
            "status": "success",
            "has_metrics": True,
            "overall_accuracy": metrics_response.get("overall_accuracy", 0.0),
            "alzheimer_accuracy": metrics_response.get("alzheimer", {}).get("accuracy", 0.0),
            "parkinson_accuracy": metrics_response.get("parkinson", {}).get("accuracy", 0.0),
            "alzheimer_f1": metrics_response.get("alzheimer", {}).get("f1", 0.0),
            "parkinson_f1": metrics_response.get("parkinson", {}).get("f1", 0.0),
            "validation_date": metrics_response.get("validation_date", "Unknown"),
            "test_samples": metrics_response.get("test_samples", 0)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model summary: {str(e)}"
        )

