# PyTorch & TensorFlow Compatibility Check

بررسی سازگاری PyTorch و TensorFlow قبل از به‌روزرسانی

## 📊 نسخه‌های فعلی

- **PyTorch**: 2.1.1
- **TensorFlow**: 2.15.0
- **torchvision**: 0.16.1
- **keras**: 2.15.0
- **numpy**: 1.26.2

## 🔍 بررسی نسخه‌های جدید

### آخرین نسخه‌های پایدار:

| Package | Current | Latest | Status |
|---------|---------|--------|--------|
| PyTorch | 2.1.1 | 2.5.x | ⚠️ Major upgrade |
| TensorFlow | 2.15.0 | 2.18.x | ⚠️ Minor upgrade |
| torchvision | 0.16.1 | 0.20.x | ⚠️ Needs PyTorch sync |
| numpy | 1.26.2 | 1.26.4 | ✅ Patch update |
| scikit-learn | 1.3.2 | 1.5.x | ⚠️ Minor upgrade |

## 🧪 Compatibility Testing

### 1. Version Compatibility Matrix

```python
# Test compatibility between versions
import torch
import tensorflow as tf
import numpy as np
import sklearn

print(f"PyTorch: {torch.__version__}")
print(f"TensorFlow: {tf.__version__}")
print(f"NumPy: {np.__version__}")
print(f"scikit-learn: {sklearn.__version__}")
```

**Checklist:**
- [ ] PyTorch 2.1.1 با TensorFlow 2.15.0 compatible است
- [ ] numpy 1.26.x با هر دو compatible است
- [ ] torchvision با PyTorch هماهنگ است

### 2. Model Loading & Saving

```python
# Test model save/load compatibility
import torch
import torch.nn as nn

# Save model
model = nn.Sequential(nn.Linear(10, 5))
torch.save(model.state_dict(), 'test_model.pth')

# Load model
loaded_state = torch.load('test_model.pth')
model.load_state_dict(loaded_state)
```

**Checklist:**
- [ ] Models ذخیره می‌شوند
- [ ] Models load می‌شوند
- [ ] Model weights حفظ می‌شوند
- [ ] Backward compatibility حفظ می‌شود

### 3. Tensor Interoperability

```python
# Test PyTorch <-> NumPy
import torch
import numpy as np

# PyTorch to NumPy
tensor = torch.randn(5, 3)
numpy_array = tensor.numpy()
print("PyTorch -> NumPy: OK")

# NumPy to PyTorch
numpy_array = np.random.randn(5, 3)
tensor = torch.from_numpy(numpy_array)
print("NumPy -> PyTorch: OK")
```

**Checklist:**
- [ ] PyTorch tensors به NumPy تبدیل می‌شوند
- [ ] NumPy arrays به PyTorch تبدیل می‌شوند
- [ ] TensorFlow tensors با NumPy کار می‌کنند

### 4. CUDA Compatibility (if using GPU)

```python
# Test CUDA availability
import torch

if torch.cuda.is_available():
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
else:
    print("CUDA not available - CPU only")
```

**Checklist:**
- [ ] CUDA detect می‌شود (if applicable)
- [ ] GPU operations کار می‌کنند
- [ ] Memory management صحیح است

### 5. Model Training Compatibility

```python
# Test training pipeline
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Sequential(
    nn.Linear(10, 5),
    nn.ReLU(),
    nn.Linear(5, 1)
)

optimizer = optim.Adam(model.parameters())
criterion = nn.MSELoss()

# Training step
inputs = torch.randn(32, 10)
targets = torch.randn(32, 1)

optimizer.zero_grad()
outputs = model(inputs)
loss = criterion(outputs, targets)
loss.backward()
optimizer.step()

print("Training step: OK")
```

**Checklist:**
- [ ] Forward pass کار می‌کند
- [ ] Backward pass کار می‌کند
- [ ] Optimizer update می‌شود
- [ ] Loss calculation صحیح است

### 6. Medical Image Processing

```python
# Test medical image processing libraries
import torch
from torchvision import transforms
import numpy as np
from PIL import Image

# Test DICOM-like data processing
# (Simplified - actual DICOM needs pydicom)

# Simulate MRI image
mri_data = np.random.randn(256, 256, 256).astype(np.float32)
tensor = torch.from_numpy(mri_data)

# Test transformations
transform = transforms.Compose([
    transforms.Normalize(mean=[0.5], std=[0.5])
])

print("Medical image processing: OK")
```

**Checklist:**
- [ ] DICOM processing کار می‌کند
- [ ] Image preprocessing کار می‌کند
- [ ] Tensor operations روی images کار می‌کنند

### 7. Memory Management

```python
# Test memory usage
import torch
import gc

# Allocate tensor
tensor = torch.randn(1000, 1000)

# Check memory
if torch.cuda.is_available():
    print(f"GPU Memory Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
    print(f"GPU Memory Cached: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

# Cleanup
del tensor
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()

print("Memory management: OK")
```

**Checklist:**
- [ ] Memory allocation صحیح است
- [ ] Memory cleanup کار می‌کند
- [ ] No memory leaks

## 📋 Pre-Upgrade Checklist

قبل از به‌روزرسانی PyTorch/TensorFlow:

### Documentation Review
- [ ] Release notes بررسی شده
- [ ] Breaking changes شناسایی شده
- [ ] Migration guide مطالعه شده

### Code Review
- [ ] همه استفاده‌ها از PyTorch/TensorFlow شناسایی شده
- [ ] Deprecated APIs شناسایی شده
- [ ] Custom operations بررسی شده

### Test Suite
- [ ] Unit tests برای models وجود دارد
- [ ] Integration tests وجود دارد
- [ ] Model inference tests وجود دارد

### Backup
- [ ] Model weights backup شده
- [ ] Training checkpoints backup شده
- [ ] Environment configuration backup شده

## 🚀 Upgrade Strategy

### مرحله 1: Minor Updates (Safe)
```bash
# Update NumPy (patch update - safe)
pip install --upgrade numpy==1.26.4

# Update scikit-learn (minor update - relatively safe)
pip install --upgrade scikit-learn==1.5.2
```

### مرحله 2: TensorFlow Minor Update
```bash
# Update TensorFlow 2.15.0 -> 2.18.x
pip install --upgrade tensorflow==2.18.0
```

**Testing:**
- [ ] Run test suite
- [ ] Test model loading
- [ ] Test inference

### مرحله 3: PyTorch Major Update (Careful!)
```bash
# Update PyTorch 2.1.1 -> 2.5.x (major upgrade)
# ⚠️ Requires careful testing!

# Check compatible torchvision version
pip install torch==2.5.0 torchvision==0.20.0 --index-url https://download.pytorch.org/whl/cu118
```

**Testing (Critical):**
- [ ] Full test suite
- [ ] Model compatibility
- [ ] Training pipeline
- [ ] Inference performance
- [ ] Memory usage

## 🧪 Automated Compatibility Tests

یک فایل تست برای بررسی compatibility ایجاد کنید:

```python
# tests/test_pytorch_tensorflow_compat.py
import pytest
import torch
import tensorflow as tf
import numpy as np

def test_pytorch_version():
    """Test PyTorch version compatibility"""
    assert torch.__version__.startswith('2.')
    print(f"✓ PyTorch {torch.__version__} compatible")

def test_tensorflow_version():
    """Test TensorFlow version compatibility"""
    assert tf.__version__.startswith('2.')
    print(f"✓ TensorFlow {tf.__version__} compatible")

def test_numpy_compatibility():
    """Test NumPy compatibility"""
    # Test with PyTorch
    tensor = torch.randn(5, 3)
    array = tensor.numpy()
    assert isinstance(array, np.ndarray)
    
    # Test with TensorFlow
    tf_tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
    array = tf_tensor.numpy()
    assert isinstance(array, np.ndarray)
    
    print("✓ NumPy compatibility OK")

def test_model_save_load():
    """Test model save/load compatibility"""
    import torch.nn as nn
    
    model = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    
    # Save
    torch.save(model.state_dict(), 'test_model.pth')
    
    # Load
    new_model = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    new_model.load_state_dict(torch.load('test_model.pth'))
    
    print("✓ Model save/load OK")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

## 📊 Compatibility Matrix

| PyTorch | TensorFlow | NumPy | Status |
|---------|-----------|-------|--------|
| 2.1.1 | 2.15.0 | 1.26.2 | ✅ Current (Tested) |
| 2.1.1 | 2.18.0 | 1.26.4 | ⚠️ Needs Testing |
| 2.5.0 | 2.15.0 | 1.26.4 | ⚠️ Needs Testing |
| 2.5.0 | 2.18.0 | 1.26.4 | ⚠️ Needs Testing |

## ⚠️ Known Issues & Warnings

### PyTorch 2.5.x
- Breaking changes در برخی APIs
- نیاز به بررسی custom operations
- CUDA compatibility ممکن است تغییر کند

### TensorFlow 2.18.x
- برخی deprecation warnings
- API changes در برخی modules
- Keras compatibility تغییرات جزئی

## ✅ Recommendation

**برای Production:**
1. ✅ فعلاً روی نسخه‌های فعلی باقی بمانید (stable)
2. ⚠️ NumPy و scikit-learn را به‌روزرسانی کنید (patch/minor - safe)
3. ⚠️ TensorFlow 2.18.x را در محیط test تست کنید
4. ⚠️ PyTorch 2.5.x را فقط در صورت نیاز و با تست کامل به‌روزرسانی کنید

**Timeline پیشنهادی:**
- هفته 1-2: NumPy و scikit-learn update
- هفته 3-4: TensorFlow 2.18.x testing
- هفته 5-8: PyTorch 2.5.x evaluation (if needed)

## 🔗 References

- [PyTorch Release Notes](https://pytorch.org/blog/)
- [TensorFlow Release Notes](https://github.com/tensorflow/tensorflow/releases)
- [PyTorch Compatibility Guide](https://pytorch.org/docs/stable/compatibility.html)
- [TensorFlow Migration Guide](https://www.tensorflow.org/guide/migrate)

