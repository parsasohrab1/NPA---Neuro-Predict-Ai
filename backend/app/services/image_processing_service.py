"""
Medical Image Processing Service
Handles DICOM files, MRI preprocessing, and feature extraction
"""
import numpy as np
import pydicom
from pathlib import Path
import logging
from typing import Dict, Tuple, Optional
import cv2
from scipy import ndimage

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """Service for processing medical images (DICOM, MRI, etc.)"""
    
    def __init__(self):
        self.supported_modalities = ['MRI', 'CT', 'PET', 'fMRI']
    
    def load_dicom(self, file_path: str) -> Tuple[np.ndarray, Dict]:
        """
        Load DICOM file and extract metadata
        
        Args:
            file_path: Path to DICOM file
        
        Returns:
            Tuple of (image_array, metadata_dict)
        """
        try:
            dicom_data = pydicom.dcmread(file_path)
            
            # Extract pixel array
            image_array = dicom_data.pixel_array
            
            # Extract metadata
            metadata = {
                'patient_id': str(dicom_data.get('PatientID', '')),
                'study_date': str(dicom_data.get('StudyDate', '')),
                'modality': str(dicom_data.get('Modality', '')),
                'series_description': str(dicom_data.get('SeriesDescription', '')),
                'slice_thickness': float(dicom_data.get('SliceThickness', 0)),
                'pixel_spacing': list(dicom_data.get('PixelSpacing', [1.0, 1.0])),
                'rows': int(dicom_data.Rows),
                'columns': int(dicom_data.Columns),
            }
            
            return image_array, metadata
            
        except Exception as e:
            logger.error(f"Error loading DICOM file {file_path}: {e}")
            raise
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image intensity to 0-1 range
        
        Args:
            image: Input image array
        
        Returns:
            Normalized image
        """
        image = image.astype(np.float32)
        
        # Clip outliers (1st and 99th percentiles)
        p1, p99 = np.percentile(image, (1, 99))
        image = np.clip(image, p1, p99)
        
        # Normalize to 0-1
        image_min = image.min()
        image_max = image.max()
        
        if image_max > image_min:
            image = (image - image_min) / (image_max - image_min)
        
        return image
    
    def resize_image(self, image: np.ndarray, target_size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """
        Resize image to target size
        
        Args:
            image: Input image
            target_size: Target (height, width)
        
        Returns:
            Resized image
        """
        return cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    
    def apply_bias_field_correction(self, image: np.ndarray) -> np.ndarray:
        """
        Simple bias field correction using morphological operations
        In production, use N4ITK bias field correction
        
        Args:
            image: Input image
        
        Returns:
            Corrected image
        """
        # Simple bias field estimation using large Gaussian blur
        bias_field = ndimage.gaussian_filter(image, sigma=20)
        
        # Avoid division by zero
        bias_field[bias_field == 0] = 1
        
        # Correct image
        corrected = image / bias_field
        corrected = self.normalize_image(corrected)
        
        return corrected
    
    def skull_stripping(self, image: np.ndarray) -> np.ndarray:
        """
        Simple skull stripping using thresholding
        In production, use FSL BET or similar tools
        
        Args:
            image: Input brain MRI
        
        Returns:
            Skull-stripped image
        """
        # Otsu's thresholding
        normalized = (image * 255).astype(np.uint8)
        _, binary = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean mask
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Apply mask
        mask = binary.astype(np.float32) / 255.0
        result = image * mask
        
        return result
    
    def extract_texture_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        Extract texture features using Gray Level Co-occurrence Matrix (GLCM)
        
        Args:
            image: Input image
        
        Returns:
            Dictionary of texture features
        """
        # Convert to uint8
        image_uint8 = (image * 255).astype(np.uint8)
        
        # Simple texture features
        features = {
            'mean_intensity': float(np.mean(image)),
            'std_intensity': float(np.std(image)),
            'skewness': float(self._calculate_skewness(image)),
            'kurtosis': float(self._calculate_kurtosis(image)),
            'entropy': float(self._calculate_entropy(image_uint8)),
        }
        
        return features
    
    def _calculate_skewness(self, image: np.ndarray) -> float:
        """Calculate skewness of image intensity distribution"""
        mean = np.mean(image)
        std = np.std(image)
        if std == 0:
            return 0.0
        return np.mean(((image - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, image: np.ndarray) -> float:
        """Calculate kurtosis of image intensity distribution"""
        mean = np.mean(image)
        std = np.std(image)
        if std == 0:
            return 0.0
        return np.mean(((image - mean) / std) ** 4) - 3.0
    
    def _calculate_entropy(self, image: np.ndarray) -> float:
        """Calculate Shannon entropy of image"""
        histogram, _ = np.histogram(image, bins=256, range=(0, 256))
        histogram = histogram[histogram > 0]
        probabilities = histogram / histogram.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
    
    def extract_volumetric_features(self, image_3d: np.ndarray, 
                                   voxel_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)) -> Dict[str, float]:
        """
        Extract volumetric features from 3D MRI
        
        Args:
            image_3d: 3D image volume
            voxel_spacing: Voxel dimensions in mm
        
        Returns:
            Dictionary of volumetric features
        """
        # Calculate voxel volume
        voxel_volume = np.prod(voxel_spacing)
        
        # Brain tissue segmentation (simplified)
        threshold = np.mean(image_3d) + 0.5 * np.std(image_3d)
        brain_mask = image_3d > threshold
        
        # Calculate volumes
        brain_volume = np.sum(brain_mask) * voxel_volume
        
        features = {
            'total_brain_volume': float(brain_volume),
            'mean_intensity': float(np.mean(image_3d[brain_mask])),
            'volume_std': float(np.std(image_3d[brain_mask])),
        }
        
        return features
    
    def preprocess_mri(self, image: np.ndarray, 
                       apply_correction: bool = True,
                       apply_skull_strip: bool = True) -> np.ndarray:
        """
        Complete MRI preprocessing pipeline
        
        Args:
            image: Input MRI image
            apply_correction: Whether to apply bias field correction
            apply_skull_strip: Whether to apply skull stripping
        
        Returns:
            Preprocessed image
        """
        # Normalize
        processed = self.normalize_image(image)
        
        # Bias field correction
        if apply_correction:
            processed = self.apply_bias_field_correction(processed)
        
        # Skull stripping
        if apply_skull_strip:
            processed = self.skull_stripping(processed)
        
        # Final normalization
        processed = self.normalize_image(processed)
        
        return processed
    
    def assess_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """
        Assess image quality metrics
        
        Args:
            image: Input image
        
        Returns:
            Dictionary of quality metrics
        """
        # Calculate Signal-to-Noise Ratio (SNR)
        signal = float(np.mean(image))
        low_band = image[image < np.percentile(image, 10)]
        noise = float(np.std(low_band)) if low_band.size > 1 else float(np.std(image) or 0.0)
        snr = signal / noise if noise > 0 else 0.0
        
        # Calculate Contrast-to-Noise Ratio (CNR)
        foreground = image[image > np.percentile(image, 50)]
        background = image[image < np.percentile(image, 50)]
        bg_std = float(np.std(background)) if background.size > 1 else 0.0
        cnr = (float(np.mean(foreground)) - float(np.mean(background))) / bg_std if bg_std > 0 and foreground.size and background.size else 0.0
        
        # Sharpness (using Laplacian variance)
        laplacian = cv2.Laplacian((image * 255).astype(np.uint8), cv2.CV_64F)
        sharpness = float(laplacian.var())
        
        quality_metrics = {
            'snr': float(snr),
            'cnr': float(cnr),
            'sharpness': float(sharpness),
            'quality_score': float(min((snr / 10 + cnr / 5 + sharpness / 100) / 3, 1.0))  # Normalized 0-1
        }
        
        return quality_metrics

    def build_deterministic_imaging_features(
        self,
        image: np.ndarray,
        texture_features: Optional[Dict[str, float]] = None,
        quality_metrics: Optional[Dict[str, float]] = None,
        length: int = 32,
    ) -> np.ndarray:
        """
        Build a fixed-length deterministic feature vector from texture/quality/stats.
        Same input image always yields the same 32 floats (no randomness).
        """
        flat = np.asarray(image, dtype=np.float64).ravel()
        if flat.size == 0:
            return np.zeros(length, dtype=np.float32)

        if texture_features is None:
            texture_features = self.extract_texture_features(
                image if image.ndim >= 2 else image.reshape(1, -1)
            )
        if quality_metrics is None:
            quality_metrics = self.assess_image_quality(
                image if image.ndim >= 2 else image.reshape(1, -1)
            )

        mean = float(np.mean(flat))
        std = float(np.std(flat))
        percentiles = np.percentile(flat, [5, 10, 25, 50, 75, 90, 95]).astype(np.float64)

        if image.ndim >= 2:
            gy, gx = np.gradient(np.asarray(image, dtype=np.float64))
            grad_mean = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))
            grad_std = float(np.std(gx) + np.std(gy))
        else:
            g = np.gradient(flat)
            grad_mean = float(np.mean(np.abs(g)))
            grad_std = float(np.std(g))

        hist_min = float(flat.min())
        hist_max = float(flat.max())
        if hist_max <= hist_min:
            hist_max = hist_min + 1.0
        hist, _ = np.histogram(flat, bins=16, range=(hist_min, hist_max))
        hist = hist.astype(np.float64)
        hist = hist / hist.sum() if hist.sum() > 0 else hist

        texture_vals = [
            float(texture_features.get("mean_intensity", mean)),
            float(texture_features.get("std_intensity", std)),
            float(texture_features.get("skewness", 0.0)),
            float(texture_features.get("kurtosis", 0.0)),
            float(texture_features.get("entropy", 0.0)),
        ]
        quality_vals = [
            float(quality_metrics.get("snr", 0.0)),
            float(quality_metrics.get("cnr", 0.0)),
            float(quality_metrics.get("sharpness", 0.0)),
            float(quality_metrics.get("quality_score", 0.0)),
        ]

        vec = np.concatenate([
            np.array([mean, std, grad_mean, grad_std], dtype=np.float64),
            percentiles,
            texture_vals,
            quality_vals,
            hist,
        ])
        # Pad or truncate to exactly `length`
        if vec.size < length:
            vec = np.pad(vec, (0, length - vec.size), mode="constant")
        else:
            vec = vec[:length]
        return vec.astype(np.float32)
    
    async def process_dicom_study(self, dicom_dir: str) -> Dict:
        """
        Process complete DICOM study
        
        Args:
            dicom_dir: Directory containing DICOM files
        
        Returns:
            Dictionary with processed images and extracted features
        """
        try:
            dicom_path = Path(dicom_dir)
            dicom_files = list(dicom_path.glob('*.dcm'))
            
            if not dicom_files:
                raise ValueError(f"No DICOM files found in {dicom_dir}")
            
            # Process first file as representative
            # In production, process entire 3D volume
            image, metadata = self.load_dicom(str(dicom_files[0]))
            
            # Preprocess
            processed_image = self.preprocess_mri(image)
            
            # Extract features
            texture_features = self.extract_texture_features(processed_image)
            quality_metrics = self.assess_image_quality(processed_image)
            
            # Deterministic 32-d features from texture + quality + image statistics
            deep_features = self.build_deterministic_imaging_features(
                processed_image,
                texture_features=texture_features,
                quality_metrics=quality_metrics,
                length=32,
            ).tolist()
            
            result = {
                'metadata': metadata,
                'texture_features': texture_features,
                'quality_metrics': quality_metrics,
                'imaging_features': deep_features,
                'processed_image_shape': processed_image.shape,
                'num_slices': len(dicom_files)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing DICOM study: {e}")
            raise


# Singleton instance
image_processing_service = ImageProcessingService()

