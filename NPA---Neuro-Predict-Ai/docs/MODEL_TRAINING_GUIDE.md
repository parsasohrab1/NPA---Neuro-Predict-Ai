# راهنمای آموزش و اعتبارسنجی مدل - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [پیش‌نیازها](#پیش‌نیازها)
3. [جمع‌آوری داده](#جمع‌آوری-داده)
4. [آموزش مدل](#آموزش-مدل)
5. [اعتبارسنجی بالینی](#اعتبارسنجی-بالینی)
6. [مدیریت نسخه‌های مدل](#مدیریت-نسخه‌های-مدل)
7. [گزارش‌دهی](#گزارش‌دهی)

---

## مقدمه

این راهنما مراحل کامل آموزش و اعتبارسنجی مدل NeuroPredict-AI را شرح می‌دهد. این فرآیند برای اخذ تأییدیه نظارتی (مانند FDA 510(k)) ضروری است.

### اهمیت اعتبارسنجی بالینی

- ✅ الزام برای تأییدیه نظارتی
- ✅ تضمین دقت و ایمنی مدل
- ✅ اعتماد پزشکان و بیماران
- ✅ انطباق با استانداردهای بالینی

---

## پیش‌نیازها

### نرم‌افزار مورد نیاز

```bash
# Python 3.11+
python --version

# PyTorch
pip install torch torchvision

# سایر dependencies
pip install -r requirements.txt
```

### سخت‌افزار توصیه شده

- **GPU**: NVIDIA GPU با حداقل 8GB VRAM (برای آموزش سریع‌تر)
- **RAM**: حداقل 16GB
- **Storage**: حداقل 50GB فضای خالی

---

## جمع‌آوری داده

### 1. داده‌های واقعی (برای Production)

#### الزامات:
- ✅ رضایت‌نامه بیمار (Informed Consent)
- ✅ تأیید IRB (Institutional Review Board)
- ✅ De-identification داده‌ها
- ✅ استانداردسازی و Quality Control

#### ساختار داده:

فایل CSV باید شامل ستون‌های زیر باشد:

```csv
age,gender_encoded,education_years,
mmse_score,moca_score,memory_score,attention_score,executive_function_score,
amyloid_beta,tau_protein,dopamine_level,
apoe_e4_status,
hippocampal_volume,cortical_thickness,ventricular_volume,
white_matter_hyperintensities,brain_volume_total,
imaging_feature_0,imaging_feature_1,...,imaging_feature_31,
alzheimer_label,parkinson_label
```

### 2. داده‌های سنتتیک (برای تست و توسعه)

برای تست و توسعه، می‌توانید از داده‌های سنتتیک استفاده کنید:

```bash
cd backend
python scripts/generate_training_data.py \
    --samples 1000 \
    --output data/training_data.csv \
    --seed 42
```

**⚠️ توجه:** داده‌های سنتتیک فقط برای تست و توسعه هستند و نمی‌توانند برای اعتبارسنجی بالینی استفاده شوند.

---

## آموزش مدل

### 1. آماده‌سازی داده

```python
from app.services.training import ModelTrainer

trainer = ModelTrainer(
    input_dim=50,
    hidden_dims=[256, 128, 64]
)

train_loader, val_loader, test_loader = trainer.prepare_data(
    data_path="data/training_data.csv",
    test_size=0.2,
    val_size=0.1,
    random_seed=42
)
```

### 2. آموزش مدل

#### استفاده از Script:

```bash
cd backend
python scripts/train_and_validate.py \
    --data data/training_data.csv \
    --epochs 100 \
    --lr 0.001 \
    --batch-size 32 \
    --output-dir models \
    --early-stopping 10 \
    --seed 42
```

#### استفاده از Python API:

```python
from app.services.training import ModelTrainer

trainer = ModelTrainer()
train_loader, val_loader, test_loader = trainer.prepare_data("data/training_data.csv")

trainer.create_model()

training_results = trainer.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=100,
    learning_rate=0.001,
    early_stopping_patience=10
)

# ذخیره مدل
trainer.save_model("model_v1.0.pth", metadata={
    'training_results': training_results,
    'timestamp': datetime.now().isoformat()
})
```

### 3. Hyperparameter Tuning

برای بهینه‌سازی hyperparameters:

```python
# مثال: Grid Search
learning_rates = [0.0001, 0.001, 0.01]
hidden_dims_options = [[128, 64], [256, 128, 64], [512, 256, 128]]

best_score = 0
best_config = None

for lr in learning_rates:
    for hidden_dims in hidden_dims_options:
        trainer = ModelTrainer(hidden_dims=hidden_dims)
        # ... training code ...
        score = training_results['best_metrics']['alzheimer_f1']
        if score > best_score:
            best_score = score
            best_config = {'lr': lr, 'hidden_dims': hidden_dims}
```

---

## اعتبارسنجی بالینی

### 1. اعتبارسنجی روی Test Set

```python
from app.services.training import ClinicalValidator

validator = ClinicalValidator()

validation_results = validator.validate_model(
    model=trainer.model,
    test_loader=test_loader,
    device=trainer.device,
    threshold=0.5
)
```

### 2. معیارهای بالینی

مدل معیارهای زیر را محاسبه می‌کند:

#### معیارهای عملکرد:
- **Accuracy**: دقت کلی
- **Precision (PPV)**: Positive Predictive Value
- **Recall (Sensitivity)**: حساسیت
- **F1 Score**: میانگین هارمونیک Precision و Recall
- **AUC-ROC**: Area Under ROC Curve

#### معیارهای بالینی:
- **Sensitivity (TPR)**: نرخ مثبت واقعی
- **Specificity (TNR)**: نرخ منفی واقعی
- **PPV**: Positive Predictive Value
- **NPV**: Negative Predictive Value
- **LR+**: Positive Likelihood Ratio
- **LR-**: Negative Likelihood Ratio
- **DOR**: Diagnostic Odds Ratio

### 3. تولید گزارش اعتبارسنجی

```python
# گزارش متنی
report = validator.generate_validation_report()
print(report)

# ذخیره گزارش
validator.generate_validation_report("validation_report.txt")

# ذخیره نتایج JSON
validator.save_results("validation_results.json")

# تولید نمودارها
validator.plot_confusion_matrices("confusion_matrices.png")
validator.plot_validation_curves("validation_curves.png")
```

### 4. استانداردهای بالینی

#### اهداف پیشنهادی برای Production:

| معیار | هدف | حداقل قابل قبول |
|-------|-----|------------------|
| Sensitivity | > 90% | > 85% |
| Specificity | > 85% | > 80% |
| AUC-ROC | > 0.90 | > 0.85 |
| PPV | > 80% | > 75% |
| NPV | > 90% | > 85% |

---

## مدیریت نسخه‌های مدل

### 1. Versioning

هر مدل باید شامل metadata زیر باشد:

```json
{
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "training_config": {
    "epochs": 100,
    "learning_rate": 0.001,
    "batch_size": 32
  },
  "validation_metrics": {
    "alzheimer": {
      "sensitivity": 0.92,
      "specificity": 0.87,
      "auc_roc": 0.91
    },
    "parkinson": {
      "sensitivity": 0.89,
      "specificity": 0.85,
      "auc_roc": 0.88
    }
  },
  "data_info": {
    "n_samples": 1000,
    "train_split": 0.7,
    "val_split": 0.1,
    "test_split": 0.2
  }
}
```

### 2. ذخیره و بارگذاری

```python
# ذخیره
trainer.save_model("model_v1.0.pth", metadata=metadata)

# بارگذاری
trainer.load_model("models/model_v1.0.pth")
```

---

## گزارش‌دهی

### 1. گزارش آموزش

```python
# نمودار تاریخچه آموزش
trainer.plot_training_history("training_history.png")
```

### 2. گزارش اعتبارسنجی

گزارش اعتبارسنجی شامل:
- خلاصه معیارها
- Confusion Matrix
- ROC Curves
- Precision-Recall Curves
- تفسیر بالینی

### 3. گزارش برای FDA

برای درخواست تأییدیه FDA، گزارش باید شامل:
- ✅ Clinical Evaluation Report
- ✅ Validation Study Design
- ✅ Statistical Analysis
- ✅ Risk Assessment
- ✅ Comparison with Gold Standard

---

## مثال کامل

```bash
# 1. تولید داده سنتتیک (برای تست)
python scripts/generate_training_data.py --samples 1000 --output data/train.csv

# 2. آموزش و اعتبارسنجی
python scripts/train_and_validate.py \
    --data data/train.csv \
    --epochs 100 \
    --lr 0.001 \
    --output-dir models

# 3. بررسی نتایج
# - models/validation_report_*.txt
# - models/validation_results_*.json
# - models/training_history_*.png
# - models/confusion_matrices_*.png
```

---

## نکات مهم

### ⚠️ هشدارها:

1. **داده‌های واقعی**: برای Production، حتماً از داده‌های واقعی با IRB Approval استفاده کنید
2. **Data Leakage**: مطمئن شوید که Test Set در فرآیند آموزش استفاده نشده است
3. **Class Imbalance**: در صورت عدم تعادل کلاس‌ها، از techniques مانند SMOTE استفاده کنید
4. **Cross-Validation**: برای اعتبارسنجی قوی‌تر، از K-Fold Cross-Validation استفاده کنید
5. **External Validation**: مدل باید روی داده‌های خارجی (از مراکز دیگر) نیز تست شود

### ✅ Best Practices:

- ✅ استفاده از Early Stopping
- ✅ Learning Rate Scheduling
- ✅ Regularization (Dropout, Weight Decay)
- ✅ Data Augmentation (در صورت امکان)
- ✅ Ensemble Methods (برای بهبود دقت)
- ✅ Documentation کامل تمام مراحل

---

## منابع بیشتر

- [FDA Guidance on AI/ML Medical Devices](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-software-medical-device)
- [ISO 13485: Medical Devices Quality Management](https://www.iso.org/standard/59752.html)
- [Clinical Validation Best Practices](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6368012/)

---

## پشتیبانی

برای سوالات و مشکلات:
- Issues: GitHub Issues
- Documentation: `docs/` directory
- Email: support@neuropredict-ai.com

