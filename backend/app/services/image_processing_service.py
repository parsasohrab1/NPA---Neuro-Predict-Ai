"""
Medical Image Processing Service
Handles DICOM files, MRI preprocessing, and feature extraction
"""
import base64
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    import pydicom
except ImportError:  # pragma: no cover - optional dependency guard
    pydicom = None

from PIL import Image
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
        if pydicom is None:
            raise RuntimeError("pydicom_not_installed")
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
        signal = np.mean(image)
        noise = np.std(image[image < np.percentile(image, 10)])  # Background noise
        snr = signal / noise if noise > 0 else 0
        
        # Calculate Contrast-to-Noise Ratio (CNR)
        foreground = image[image > np.percentile(image, 50)]
        background = image[image < np.percentile(image, 50)]
        cnr = (np.mean(foreground) - np.mean(background)) / np.std(background) if np.std(background) > 0 else 0
        
        # Sharpness (using Laplacian variance)
        laplacian = cv2.Laplacian((image * 255).astype(np.uint8), cv2.CV_64F)
        sharpness = laplacian.var()
        
        quality_metrics = {
            'snr': float(snr),
            'cnr': float(cnr),
            'sharpness': float(sharpness),
            'quality_score': float(min((snr / 10 + cnr / 5 + sharpness / 100) / 3, 1.0))  # Normalized 0-1
        }
        
        return quality_metrics
    
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
            
            # Generate deep features (placeholder - in production use CNN)
            deep_features = np.random.randn(32).tolist()  # 32-dimensional feature vector
            
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
    
    def compute_diff_heatmap(self, image_a: np.ndarray, image_b: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute difference heatmap between two aligned MRI slices
        """
        try:
            normalized_a = self.normalize_image(image_a)
            normalized_b = self.normalize_image(image_b)

            if normalized_a.shape != normalized_b.shape:
                normalized_b = self.resize_image(normalized_b, target_size=normalized_a.shape[::-1])

            diff = np.abs(normalized_a - normalized_b)
            diff_norm = self.normalize_image(diff)

            threshold = np.percentile(diff_norm, 95)
            mask = (diff_norm >= threshold).astype(np.float32)
            return {
                'image_a': normalized_a,
                'image_b': normalized_b,
                'diff': diff_norm,
                'mask': mask,
            }
        except Exception as e:
            logger.error(f"Error computing diff heatmap: {e}")
            raise

    def _heatmap_to_data_uri(self, heatmap: np.ndarray, colormap: int = cv2.COLORMAP_JET) -> str:
        heatmap_uint8 = (self.normalize_image(heatmap) * 255).astype(np.uint8)
        colored = cv2.applyColorMap(heatmap_uint8, colormap)
        colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(colored_rgb)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    def compare_dicom_files(self, path_a: str, path_b: str) -> Dict[str, object]:
        """
        Compare two DICOM files and return diff metrics and heatmap
        """
        image_a, metadata_a = self.load_dicom(path_a)
        image_b, metadata_b = self.load_dicom(path_b)

        diff_data = self.compute_diff_heatmap(image_a, image_b)
        mean_diff = float(np.mean(np.abs(diff_data['image_a'] - diff_data['image_b'])))
        max_diff = float(np.max(np.abs(diff_data['image_a'] - diff_data['image_b'])))

        heatmap_uri = self._heatmap_to_data_uri(diff_data['diff'])

        return {
            "mean_absolute_difference": mean_diff,
            "max_absolute_difference": max_diff,
            "heatmap": heatmap_uri,
            "metadata": {
                "study_a": metadata_a,
                "study_b": metadata_b,
            },
        }

    def load_dicom_series(self, dicom_dir: str) -> Tuple[List[np.ndarray], Dict]:
        """
        Load entire DICOM series (multi-slice 3D volume)
        
        Args:
            dicom_dir: Directory containing DICOM files
        
        Returns:
            Tuple of (list of image arrays, metadata)
        """
        if pydicom is None:
            raise RuntimeError("pydicom_not_installed")
        
        dicom_path = Path(dicom_dir)
        dicom_files = sorted(list(dicom_path.glob('*.dcm')))
        
        if not dicom_files:
            raise ValueError(f"No DICOM files found in {dicom_dir}")
        
        slices = []
        metadata = {}
        
        for dicom_file in dicom_files:
            try:
                dicom_data = pydicom.dcmread(str(dicom_file))
                image_array = dicom_data.pixel_array
                slices.append(image_array)
                
                # Collect metadata from first slice
                if not metadata:
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
            except Exception as e:
                logger.warning(f"Error loading DICOM file {dicom_file}: {e}")
                continue
        
        metadata['num_slices'] = len(slices)
        return slices, metadata

    def compare_multi_slice(
        self, 
        slices_a: List[np.ndarray], 
        slices_b: List[np.ndarray],
        slice_indices: Optional[List[int]] = None
    ) -> Dict[str, object]:
        """
        Compare multi-slice MRI volumes
        
        Args:
            slices_a: List of slices from first study
            slices_b: List of slices from second study
            slice_indices: Optional list of slice indices to compare (default: all)
        
        Returns:
            Dictionary with comparison results for each slice
        """
        if slice_indices is None:
            min_slices = min(len(slices_a), len(slices_b))
            slice_indices = list(range(min_slices))
        
        comparisons = []
        for idx in slice_indices:
            if idx >= len(slices_a) or idx >= len(slices_b):
                continue
            
            diff_data = self.compute_diff_heatmap(slices_a[idx], slices_b[idx])
            mean_diff = float(np.mean(np.abs(diff_data['image_a'] - diff_data['image_b'])))
            
            comparisons.append({
                'slice_index': idx,
                'mean_absolute_difference': mean_diff,
                'heatmap': self._heatmap_to_data_uri(diff_data['diff']),
            })
        
        return {
            'slice_comparisons': comparisons,
            'total_slices_compared': len(comparisons),
        }

    def create_3d_volume_heatmap(
        self, 
        volume_a: np.ndarray, 
        volume_b: np.ndarray,
        projection: str = 'mip'  # 'mip', 'avg', 'max'
    ) -> Dict[str, object]:
        """
        Create 3D volume comparison heatmap using projections
        
        Args:
            volume_a: 3D numpy array (z, y, x)
            volume_b: 3D numpy array (z, y, x)
            projection: Type of projection ('mip', 'avg', 'max')
        
        Returns:
            Dictionary with projected heatmap
        """
        if volume_a.shape != volume_b.shape:
            # Resize volume_b to match volume_a
            from scipy.ndimage import zoom
            zoom_factors = [volume_a.shape[i] / volume_b.shape[i] for i in range(3)]
            volume_b = zoom(volume_b, zoom_factors, order=1)
        
        diff_volume = np.abs(volume_a - volume_b)
        
        if projection == 'mip':  # Maximum Intensity Projection
            projected = np.max(diff_volume, axis=0)
        elif projection == 'avg':
            projected = np.mean(diff_volume, axis=0)
        elif projection == 'max':
            projected = np.max(diff_volume, axis=0)
        else:
            projected = np.mean(diff_volume, axis=0)
        
        heatmap_uri = self._heatmap_to_data_uri(projected)
        
        return {
            'heatmap': heatmap_uri,
            'projection_type': projection,
            'volume_shape': list(volume_a.shape),
            'mean_volume_difference': float(np.mean(diff_volume)),
        }

    def create_interactive_overlay(
        self,
        base_image: np.ndarray,
        overlay_image: np.ndarray,
        opacity: float = 0.5,
        colormap: int = cv2.COLORMAP_JET
    ) -> str:
        """
        Create interactive overlay visualization
        
        Args:
            base_image: Base image array
            overlay_image: Overlay image array
            opacity: Overlay opacity (0-1)
            colormap: OpenCV colormap
        
        Returns:
            Data URI of blended image
        """
        normalized_base = self.normalize_image(base_image)
        normalized_overlay = self.normalize_image(overlay_image)
        
        if normalized_base.shape != normalized_overlay.shape:
            normalized_overlay = self.resize_image(
                normalized_overlay, 
                target_size=normalized_base.shape[::-1]
            )
        
        # Apply colormap to overlay
        overlay_uint8 = (normalized_overlay * 255).astype(np.uint8)
        overlay_colored = cv2.applyColorMap(overlay_uint8, colormap)
        overlay_rgb = cv2.cvtColor(overlay_colored, cv2.COLOR_BGR2RGB)
        
        # Convert base to RGB
        base_uint8 = (normalized_base * 255).astype(np.uint8)
        base_rgb = np.stack([base_uint8] * 3, axis=-1)
        
        # Blend images
        blended = (base_rgb * (1 - opacity) + overlay_rgb * opacity).astype(np.uint8)
        
        # Convert to data URI
        image = Image.fromarray(blended)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"


# Singleton instance
image_processing_service = ImageProcessingService()

