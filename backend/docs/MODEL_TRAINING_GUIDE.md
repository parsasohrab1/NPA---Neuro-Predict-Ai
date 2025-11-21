# راهنمای آموزش مدل هوش مصنوعی

این راهنما نحوه تولید داده‌های synthetic، آموزش مدل و استفاده از آن را توضیح می‌دهد.

## ⚠️ نکته مهم

**مدل‌های آموزش‌دیده با داده‌های synthetic تنها برای اهداف نمایشی هستند و برای استفاده بالینی در محیط production مناسب نیستند.**

برای استفاده بالینی:
1. نیاز به داده‌های پزشکی واقعی و تایید شده دارید
2. نیاز به مطالعات اعتبارسنجی بالینی دارید
3. نیاز به تاییدات نظارتی (مانند FDA 510(k)) دارید

---

## تولید داده‌های Synthetic و آموزش مدل

### پیش‌نیازها

```bash
# نصب وابستگی‌ها
cd backend
pip install -r requirements.txt
```

### تولید داده و آموزش مدل

```bash
# تولید 1000 نمونه synthetic و آموزش مدل
python scripts/generate_synthetic_data_and_train.py --samples 1000 --epochs 50 --set-active

# فقط تولید داده (بدون آموزش)
python scripts/generate_synthetic_data_and_train.py --samples 1000 --skip-training

# آموزش با تنظیمات سفارشی
python scripts/generate_synthetic_data_and_train.py \
    --samples 2000 \
    --epochs 100 \
    --batch-size 64 \
    --learning-rate 0.0001 \
    --set-active
```

### پارامترها

- `--samples`: تعداد نمونه‌های synthetic (پیش‌فرض: 1000)
- `--epochs`: تعداد epoch های آموزش (پیش‌فرض: 50)
- `--batch-size`: اندازه batch (پیش‌فرض: 32)
- `--learning-rate`: نرخ یادگیری (پیش‌فرض: 0.001)
- `--output-dir`: دایرکتوری خروجی (پیش‌فرض: `data/synthetic`)
- `--skip-training`: فقط داده تولید کن (بدون آموزش)
- `--set-active`: مدل آموزش‌دیده را به عنوان مدل فعال تنظیم کن

---

## آموزش با داده‌های واقعی

### فرمت داده

داده‌ها باید در قالب CSV با ستون‌های زیر باشند:

- `age`: سن
- `gender`: جنسیت (Male/Female)
- `education_years`: سال‌های تحصیل
- `mmse_score`: نمره MMSE (0-30)
- `moca_score`: نمره MOCA (0-30)
- `memory_score`: نمره حافظه (0-100)
- `attention_score`: نمره توجه (0-100)
- `executive_function_score`: نمره عملکرد اجرایی (0-100)
- `amyloid_beta`: سطح آمیلوئید بتا
- `tau_protein`: سطح پروتئین tau
- `dopamine_level`: سطح دوپامین
- `apoe_e4_status`: وضعیت APOE-e4 (0 یا 1)
- `hippocampal_volume`: حجم هیپوکامپ
- `cortical_thickness`: ضخامت قشر مغز
- `ventricular_volume`: حجم بطنی
- `white_matter_hyperintensities`: شدت هیپراینتنسیتی ماده سفید
- `brain_volume_total`: حجم کل مغز
- `diagnosis`: تشخیص (Normal/Alzheimer/Parkinson)

### آموزش با داده CSV

```bash
python scripts/train_model.py \
    --csv-file path/to/your/data.csv \
    --epochs 100 \
    --batch-size 32 \
    --set-active \
    --description "Model trained on real clinical data - Version 1.0"
```

---

## مدیریت مدل‌ها

### Model Registry

مدل‌های آموزش‌دیده در `models/registry.json` ثبت می‌شوند. هر مدل شامل:

- **Version**: نسخه مدل
- **Model Path**: مسیر فایل مدل
- **Metrics**: معیارهای آموزشی و تست
- **Description**: توضیحات مدل
- **Created At**: تاریخ ایجاد
- **Is Active**: آیا مدل فعال است

### مشاهده مدل‌های ثبت شده

```python
from pathlib import Path
from app.services.training.model_registry import ModelRegistry

registry = ModelRegistry(Path("models/registry.json"))
models = registry.list_models()

for model in models:
    print(f"Version: {model['version']}")
    print(f"Active: {model['is_active']}")
    print(f"Metrics: {model['metrics']}")
    print("-" * 50)
```

### فعال‌سازی یک مدل

```python
registry = ModelRegistry(Path("models/registry.json"))
registry.set_active_model("20241201_123456")  # Version number
```

یا از طریق اسکریپت:

```bash
python -c "
from pathlib import Path
from app.services.training.model_registry import ModelRegistry
registry = ModelRegistry(Path('models/registry.json'))
registry.set_active_model('YOUR_VERSION')
print('Model activated!')
"
```

---

## ارزیابی مدل

### اجرای ارزیابی

```bash
python scripts/evaluate_model.py \
    --model-path models/best_model_20241201_123456.pth \
    --test-data path/to/test_data.csv
```

### معیارهای ارزیابی

مدل روی معیارهای زیر ارزیابی می‌شود:

#### معیارهای کلینیکی:
- **Accuracy**: دقت کلی
- **Sensitivity (Recall)**: حساسیت - نسبت موارد مثبت درست شناسایی شده
- **Specificity**: ویژگی - نسبت موارد منفی درست شناسایی شده
- **Precision (PPV)**: دقت - ارزش پیش‌بینی مثبت
- **Negative Predictive Value (NPV)**: ارزش پیش‌بینی منفی
- **F1-Score**: میانگین هم‌ساز دقت و حساسیت
- **AUC-ROC**: مساحت زیر منحنی ROC

#### Confusion Matrix:
- True Positives (TP)
- False Positives (FP)
- True Negatives (TN)
- False Negatives (FN)

---

## استفاده از مدل در Production

### تنظیمات

در `.env`:

```bash
USE_TRAINED_MODEL=true
MODEL_REGISTRY_PATH=models/registry.json
ENSEMBLE_MODEL_PATH=models/ensemble_model.pth
```

### بررسی مدل فعال

```python
from app.services.ai_model_service import ai_model_service

# مدل باید از registry بارگذاری شود
if ai_model_service.model is not None:
    print("Model loaded successfully!")
    print(f"Model version: {ai_model_service.model_version}")
else:
    print("No model loaded - using random initialization")
```

---

## تست‌ها

### اجرای تست‌های AI Model Service

```bash
cd backend
pytest tests/test_ai_model_service.py -v
```

### اجرای تست‌های Training Pipeline

```bash
pytest tests/test_training_pipeline.py -v
```

### اجرای همه تست‌ها

```bash
pytest tests/ -v --cov=app --cov-report=html
```

---

## ساختار فایل‌ها

```
backend/
├── scripts/
│   ├── generate_synthetic_data_and_train.py  # تولید داده و آموزش
│   ├── train_model.py                         # آموزش با داده واقعی
│   └── evaluate_model.py                      # ارزیابی مدل
├── app/
│   └── services/
│       ├── ai_model_service.py                # سرویس پیش‌بینی
│       └── training/
│           ├── data_loader.py                 # بارگذاری و پیش‌پردازش داده
│           ├── trainer.py                     # آموزش مدل
│           ├── evaluator.py                   # ارزیابی مدل
│           └── model_registry.py              # مدیریت نسخه‌های مدل
├── tests/
│   ├── test_ai_model_service.py              # تست‌های سرویس AI
│   └── test_training_pipeline.py             # تست‌های pipeline آموزشی
├── models/
│   ├── registry.json                         # ثبت مدل‌ها
│   └── best_model_*.pth                      # فایل‌های مدل
└── data/
    └── synthetic/
        └── csv/
            └── synthetic_dataset.csv          # داده‌های synthetic
```

---

## عیب‌یابی

### خطا: "PyTorch not available"

```bash
pip install torch torchvision
```

### خطا: "Model file not found"

اطمینان حاصل کنید که:
1. مدل آموزش داده شده است
2. مسیر مدل در `registry.json` صحیح است
3. فایل `.pth` در مسیر مشخص شده وجود دارد

### خطا: "No pre-trained model found"

اگر مدل از registry بارگذاری نمی‌شود:
1. بررسی کنید که `USE_TRAINED_MODEL=true` در `.env` تنظیم شده است
2. بررسی کنید که `models/registry.json` وجود دارد
3. یک مدل را فعال کنید با `set_active_model()`

---

## منابع بیشتر

- [Training Implementation Guide (FA)](docs/TRAINING_IMPLEMENTATION_FA.md)
- [Model Registry Documentation](app/services/training/model_registry.py)
- [Clinical Validation Guidelines](docs/TRAINING_GUIDE.md)


