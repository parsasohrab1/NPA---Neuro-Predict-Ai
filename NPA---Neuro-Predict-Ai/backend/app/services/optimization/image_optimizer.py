"""
Image Processing Optimization
بهینه‌سازی پردازش تصاویر
"""
import numpy as np
from typing import Tuple, Optional
import cv2
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """Service for optimizing image processing operations"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache = {}  # Simple in-memory cache for processed images
    
    async def preprocess_image_async(
        self,
        image: np.ndarray,
        normalize: bool = True,
        resize: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        Preprocess image asynchronously
        
        Args:
            image: Input image array
            normalize: Whether to normalize
            resize: Optional resize dimensions
        
        Returns:
            Preprocessed image
        """
        # Run CPU-intensive operation in thread pool
        loop = asyncio.get_event_loop()
        processed = await loop.run_in_executor(
            self.executor,
            self._preprocess_sync,
            image,
            normalize,
            resize
        )
        return processed
    
    def _preprocess_sync(
        self,
        image: np.ndarray,
        normalize: bool,
        resize: Optional[Tuple[int, int]]
    ) -> np.ndarray:
        """Synchronous preprocessing (runs in thread pool)"""
        # Resize if needed
        if resize:
            image = cv2.resize(image, resize, interpolation=cv2.INTER_LINEAR)
        
        # Normalize
        if normalize:
            # Convert to float and normalize to [0, 1]
            image = image.astype(np.float32)
            if image.max() > 1.0:
                image = image / 255.0
        
        return image
    
    async def batch_preprocess(
        self,
        images: list[np.ndarray],
        normalize: bool = True,
        resize: Optional[Tuple[int, int]] = None
    ) -> list[np.ndarray]:
        """
        Batch preprocess multiple images in parallel
        
        Args:
            images: List of image arrays
            normalize: Whether to normalize
            resize: Optional resize dimensions
        
        Returns:
            List of preprocessed images
        """
        # Process images in parallel
        tasks = [
            self.preprocess_image_async(img, normalize, resize)
            for img in images
        ]
        
        return await asyncio.gather(*tasks)
    
    def optimize_image_size(
        self,
        image: np.ndarray,
        max_dimension: int = 512,
        quality: int = 90
    ) -> np.ndarray:
        """
        Optimize image size for faster processing
        
        Args:
            image: Input image
            max_dimension: Maximum dimension (width or height)
            quality: Compression quality (0-100)
        
        Returns:
            Optimized image
        """
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            image = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA  # Better for downscaling
            )
        
        return image
    
    def extract_features_optimized(
        self,
        image: np.ndarray,
        feature_type: str = "basic"
    ) -> np.ndarray:
        """
        Extract features from image (optimized)
        
        Args:
            image: Input image
            feature_type: Type of features to extract
        
        Returns:
            Feature vector
        """
        features = []
        
        if feature_type == "basic":
            # Basic statistical features
            features.extend([
                np.mean(image),
                np.std(image),
                np.min(image),
                np.max(image),
                np.median(image)
            ])
        
        elif feature_type == "texture":
            # GLCM-like texture features (simplified)
            # In production, use proper GLCM implementation
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Calculate gradients
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            features.extend([
                np.mean(grad_x),
                np.std(grad_x),
                np.mean(grad_y),
                np.std(grad_y)
            ])
        
        return np.array(features)
    
    def close(self):
        """Close thread pool executor"""
        self.executor.shutdown(wait=True)

