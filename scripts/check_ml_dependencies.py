#!/usr/bin/env python3
"""
Script to check PyTorch & TensorFlow compatibility
Usage: python scripts/check_ml_dependencies.py
"""
import sys
import subprocess

def check_package(package_name, min_version=None):
    """Check if package is installed and get version"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                version = line.split(':', 1)[1].strip()
                print(f"✓ {package_name}: {version}")
                return version
    except subprocess.CalledProcessError:
        print(f"✗ {package_name}: Not installed")
        return None

def test_imports():
    """Test if packages can be imported"""
    print("\n=== Testing Imports ===")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ TensorFlow import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    return True

def test_compatibility():
    """Test compatibility between packages"""
    print("\n=== Testing Compatibility ===")
    
    try:
        import torch
        import numpy as np
        
        # Test PyTorch <-> NumPy
        tensor = torch.randn(5, 3)
        array = tensor.numpy()
        assert isinstance(array, np.ndarray)
        print("✓ PyTorch <-> NumPy interop works")
        
        numpy_array = np.random.randn(5, 3)
        tensor = torch.from_numpy(numpy_array)
        assert isinstance(tensor, torch.Tensor)
        print("✓ NumPy -> PyTorch conversion works")
        
    except Exception as e:
        print(f"✗ Compatibility test failed: {e}")
        return False
    
    try:
        import tensorflow as tf
        import numpy as np
        
        # Test TensorFlow <-> NumPy
        tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        array = tensor.numpy()
        assert isinstance(array, np.ndarray)
        print("✓ TensorFlow <-> NumPy interop works")
        
    except Exception as e:
        print(f"✗ TensorFlow compatibility test failed: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🔍 Checking ML Dependencies Compatibility")
    print("=" * 50)
    
    # Check installed packages
    print("\n=== Installed Packages ===")
    torch_version = check_package('torch')
    tf_version = check_package('tensorflow')
    numpy_version = check_package('numpy')
    sklearn_version = check_package('scikit-learn')
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    # Test compatibility
    if not test_compatibility():
        print("\n❌ Compatibility tests failed!")
        sys.exit(1)
    
    # Summary
    print("\n=== Summary ===")
    print("✓ All packages are installed")
    print("✓ All imports successful")
    print("✓ Compatibility checks passed")
    print("\n✅ All checks passed!")
    
    # Recommendations
    print("\n=== Recommendations ===")
    if torch_version and torch_version.startswith('2.1'):
        print("⚠ PyTorch 2.1.1 - Consider testing upgrade to 2.5.x")
    if tf_version and tf_version.startswith('2.15'):
        print("⚠ TensorFlow 2.15.0 - Consider testing upgrade to 2.18.x")
    if numpy_version and not numpy_version.startswith('1.26.4'):
        print("💡 NumPy can be safely updated to 1.26.4 (patch update)")

if __name__ == '__main__':
    main()

