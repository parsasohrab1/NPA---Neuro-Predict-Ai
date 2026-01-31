"""
AI Model Inference Optimization
بهینه‌سازی استنتاج مدل AI
"""
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelOptimizer:
    """Service for optimizing AI model inference"""
    
    def __init__(self):
        self.model_cache: Dict[str, Any] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.half_precision = False  # FP16 for faster inference
    
    def load_model_optimized(
        self,
        model_path: str,
        model_class: type,
        use_cache: bool = True
    ) -> nn.Module:
        """
        Load model with optimizations
        
        Args:
            model_path: Path to model file
            model_class: Model class
            use_cache: Whether to cache loaded model
        
        Returns:
            Loaded and optimized model
        """
        # Check cache
        if use_cache and model_path in self.model_cache:
            return self.model_cache[model_path]
        
        # Load model
        model = model_class()
        
        if Path(model_path).exists():
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    model.load_state_dict(checkpoint)
            except Exception as e:
                logger.warning(f"Error loading model from {model_path}: {e}")
        
        # Move to device
        model = model.to(self.device)
        
        # Set to evaluation mode
        model.eval()
        
        # Enable half precision if available
        if self.half_precision and self.device.type == "cuda":
            model = model.half()
        
        # Optimize for inference
        if hasattr(torch.jit, 'script'):
            try:
                model = torch.jit.script(model)
            except Exception as e:
                logger.warning(f"Could not JIT compile model: {e}")
        
        # Cache model
        if use_cache:
            self.model_cache[model_path] = model
        
        return model
    
    @torch.no_grad()
    def predict_batch(
        self,
        model: nn.Module,
        inputs: torch.Tensor,
        batch_size: int = 32
    ) -> torch.Tensor:
        """
        Run batch prediction with optimizations
        
        Args:
            model: Trained model
            inputs: Input tensor
            batch_size: Batch size for processing
        
        Returns:
            Predictions tensor
        """
        model.eval()
        
        # Move inputs to device
        inputs = inputs.to(self.device)
        
        # Convert to half precision if enabled
        if self.half_precision and self.device.type == "cuda":
            inputs = inputs.half()
        
        # Process in batches
        predictions = []
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            
            # Inference with torch.no_grad() for memory efficiency
            with torch.no_grad():
                output = model(batch)
                predictions.append(output.cpu())
        
        return torch.cat(predictions, dim=0)
    
    def optimize_model_for_inference(self, model: nn.Module) -> nn.Module:
        """
        Apply inference optimizations to model
        
        Args:
            model: Model to optimize
        
        Returns:
            Optimized model
        """
        # Set to evaluation mode
        model.eval()
        
        # Fuse operations if possible
        if hasattr(torch.quantization, 'fuse_modules'):
            try:
                # Example: fuse conv+bn+relu
                # This is model-specific and should be customized
                pass
            except Exception as e:
                logger.warning(f"Could not fuse modules: {e}")
        
        # Enable optimizations
        if hasattr(torch.backends, 'cudnn'):
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        return model
    
    def clear_cache(self):
        """Clear model cache"""
        self.model_cache.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

