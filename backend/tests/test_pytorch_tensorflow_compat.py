"""
PyTorch & TensorFlow Compatibility Tests
Run with: pytest tests/test_pytorch_tensorflow_compat.py -v
"""
import pytest
import torch
import numpy as np

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    pytest.skip("TensorFlow not available", allow_module_level=True)


class TestPyTorchCompatibility:
    """Test PyTorch version and basic operations"""
    
    def test_pytorch_version(self):
        """Verify PyTorch version is compatible"""
        version = torch.__version__
        assert version.startswith('2.'), f"PyTorch version {version} should be 2.x"
        print(f"✓ PyTorch {version} detected")
    
    def test_pytorch_cuda_availability(self):
        """Check if CUDA is available (optional)"""
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.version.cuda}")
            print(f"✓ Device: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠ CUDA not available - CPU only mode")
    
    def test_pytorch_tensor_creation(self):
        """Test basic tensor operations"""
        tensor = torch.randn(5, 3)
        assert tensor.shape == (5, 3)
        assert tensor.dtype == torch.float32
        print("✓ PyTorch tensor creation OK")
    
    def test_pytorch_model_save_load(self):
        """Test model save/load compatibility"""
        import torch.nn as nn
        import tempfile
        import os
        
        # Create simple model
        model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        
        # Save model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pth') as f:
            torch.save(model.state_dict(), f.name)
            
            # Load model
            new_model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            new_model.load_state_dict(torch.load(f.name))
            
            # Verify weights are loaded
            assert torch.allclose(
                model.state_dict()['0.weight'],
                new_model.state_dict()['0.weight']
            )
            
            os.unlink(f.name)
        
        print("✓ PyTorch model save/load OK")


class TestTensorFlowCompatibility:
    """Test TensorFlow version and basic operations"""
    
    def test_tensorflow_version(self):
        """Verify TensorFlow version is compatible"""
        version = tf.__version__
        assert version.startswith('2.'), f"TensorFlow version {version} should be 2.x"
        print(f"✓ TensorFlow {version} detected")
    
    def test_tensorflow_tensor_creation(self):
        """Test basic tensor operations"""
        tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        assert tensor.shape == (2, 2)
        assert tensor.dtype == tf.float32
        print("✓ TensorFlow tensor creation OK")


class TestNumPyCompatibility:
    """Test NumPy compatibility with PyTorch and TensorFlow"""
    
    def test_pytorch_numpy_interop(self):
        """Test PyTorch <-> NumPy interoperability"""
        # PyTorch to NumPy
        tensor = torch.randn(5, 3)
        array = tensor.numpy()
        assert isinstance(array, np.ndarray)
        assert array.shape == (5, 3)
        
        # NumPy to PyTorch
        numpy_array = np.random.randn(5, 3)
        tensor = torch.from_numpy(numpy_array)
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (5, 3)
        
        print("✓ PyTorch <-> NumPy interop OK")
    
    @pytest.mark.skipif(not TF_AVAILABLE, reason="TensorFlow not available")
    def test_tensorflow_numpy_interop(self):
        """Test TensorFlow <-> NumPy interoperability"""
        # TensorFlow to NumPy
        tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        array = tensor.numpy()
        assert isinstance(array, np.ndarray)
        assert array.shape == (2, 2)
        
        # NumPy to TensorFlow
        numpy_array = np.array([[1.0, 2.0], [3.0, 4.0]])
        tensor = tf.constant(numpy_array)
        assert isinstance(tensor, tf.Tensor)
        assert tensor.shape == (2, 2)
        
        print("✓ TensorFlow <-> NumPy interop OK")
    
    def test_numpy_version(self):
        """Verify NumPy version is compatible"""
        version = np.__version__
        # NumPy 1.26.x is compatible with both PyTorch 2.1.x and TensorFlow 2.15.x
        assert version.startswith('1.26.'), f"NumPy version {version} should be 1.26.x"
        print(f"✓ NumPy {version} detected and compatible")


class TestMemoryManagement:
    """Test memory management and cleanup"""
    
    def test_pytorch_memory_cleanup(self):
        """Test PyTorch memory cleanup"""
        # Allocate tensor
        tensor = torch.randn(1000, 1000)
        
        # Check memory (if CUDA available)
        if torch.cuda.is_available():
            memory_before = torch.cuda.memory_allocated()
        
        # Delete and cleanup
        del tensor
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            memory_after = torch.cuda.memory_allocated()
            # Memory should be released
            assert memory_after <= memory_before
        
        print("✓ PyTorch memory cleanup OK")


class TestVersionCompatibility:
    """Test version compatibility between packages"""
    
    def test_version_compatibility(self):
        """Check if current versions are compatible"""
        pytorch_version = torch.__version__
        numpy_version = np.__version__
        
        if TF_AVAILABLE:
            tf_version = tf.__version__
            print(f"Versions: PyTorch {pytorch_version}, TensorFlow {tf_version}, NumPy {numpy_version}")
        else:
            print(f"Versions: PyTorch {pytorch_version}, NumPy {numpy_version}")
        
        # Basic compatibility checks
        assert pytorch_version.startswith('2.'), "PyTorch should be 2.x"
        assert numpy_version.startswith('1.26.'), "NumPy should be 1.26.x"
        
        if TF_AVAILABLE:
            assert tf_version.startswith('2.'), "TensorFlow should be 2.x"
        
        print("✓ Version compatibility OK")
    
    def test_import_compatibility(self):
        """Test that all required packages can be imported"""
        import torch
        import numpy as np
        
        # Test PyTorch imports
        from torch import nn, optim
        from torchvision import transforms
        
        if TF_AVAILABLE:
            import tensorflow as tf
            from tensorflow import keras
        
        print("✓ All imports successful")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

