# Training Scripts - NeuroPredict-AI

این پوشه شامل اسکریپت‌های مربوط به آموزش و اعتبارسنجی مدل است.

## فایل‌ها

### 1. `train_and_validate.py`
اسکریپت اصلی برای آموزش و اعتبارسنجی مدل

**استفاده:**
```bash
python scripts/train_and_validate.py \
    --data data/training_data.csv \
    --epochs 100 \
    --lr 0.001 \
    --batch-size 32 \
    --output-dir models \
    --early-stopping 10 \
    --seed 42
```

**پارامترها:**
- `--data`: مسیر فایل CSV داده‌های آموزشی (الزامی)
- `--epochs`: تعداد epochs (پیش‌فرض: 100)
- `--lr`: Learning rate (پیش‌فرض: 0.001)
- `--batch-size`: اندازه batch (پیش‌فرض: 32)
- `--output-dir`: پوشه خروجی برای مدل‌ها (پیش‌فرض: models)
- `--early-stopping`: Patience برای early stopping (پیش‌فرض: 10)
- `--seed`: Random seed (پیش‌فرض: 42)

**خروجی:**
- مدل آموزش‌دیده: `models/model_YYYYMMDD_HHMMSS.pth`
- Scaler: `models/model_YYYYMMDD_HHMMSS_scaler.pkl`
- Metadata: `models/model_YYYYMMDD_HHMMSS_metadata.json`
- نتایج اعتبارسنجی: `models/validation_results_YYYYMMDD_HHMMSS.json`
- گزارش اعتبارسنجی: `models/validation_report_YYYYMMDD_HHMMSS.txt`
- نمودارها: `models/training_history_YYYYMMDD_HHMMSS.png`, `models/confusion_matrices_YYYYMMDD_HHMMSS.png`

### 2. `generate_training_data.py`
تولید داده‌های سنتتیک برای تست و توسعه

**استفاده:**
```bash
python scripts/generate_training_data.py \
    --samples 1000 \
    --output data/training_data.csv \
    --seed 42
```

**پارامترها:**
- `--samples`: تعداد نمونه‌ها (پیش‌فرض: 1000)
- `--output`: مسیر فایل خروجی (پیش‌فرض: data/training_data.csv)
- `--seed`: Random seed (پیش‌فرض: 42)

**⚠️ توجه:** این داده‌ها فقط برای تست و توسعه هستند و نمی‌توانند برای اعتبارسنجی بالینی استفاده شوند.

## مثال کامل

```bash
# 1. تولید داده سنتتیک
python scripts/generate_training_data.py \
    --samples 1000 \
    --output data/train.csv

# 2. آموزش و اعتبارسنجی
python scripts/train_and_validate.py \
    --data data/train.csv \
    --epochs 100 \
    --lr 0.001 \
    --output-dir models

# 3. بررسی نتایج
ls -lh models/
```

## ساختار داده

فایل CSV باید شامل ستون‌های زیر باشد:

### Features (50 ویژگی):
- Demographics: `age`, `gender_encoded`, `education_years`
- Cognitive Scores: `mmse_score`, `moca_score`, `memory_score`, `attention_score`, `executive_function_score`
- Biomarkers: `amyloid_beta`, `tau_protein`, `dopamine_level`
- Genetic: `apoe_e4_status`
- MRI Features: `hippocampal_volume`, `cortical_thickness`, `ventricular_volume`, `white_matter_hyperintensities`, `brain_volume_total`
- Imaging Features: `imaging_feature_0` تا `imaging_feature_31`

### Labels:
- `alzheimer_label`: 0 یا 1
- `parkinson_label`: 0 یا 1

## مستندات بیشتر

برای اطلاعات بیشتر، به `docs/MODEL_TRAINING_GUIDE.md` مراجعه کنید.

