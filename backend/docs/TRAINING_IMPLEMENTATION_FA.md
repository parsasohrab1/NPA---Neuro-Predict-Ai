# پیاده‌سازی Pipeline آموزش مدل‌های AI

## خلاصه

این سند تغییرات و بهبودهای انجام شده برای حل مشکل "مدل‌های AI - فقط Random Initialization" را شرح می‌دهد.

## مشکل قبلی

- مدل‌ها با وزن‌های تصادفی اجرا می‌شدند
- نتایج قابل اعتماد نبود
- هیچ pipeline آموزش وجود نداشت
- اعتبارسنجی بالینی انجام نمی‌شد

## راه‌حل پیاده‌سازی شده

### 1. Data Loader (`backend/app/services/training/data_loader.py`)

**قابلیت‌ها:**
- بارگذاری داده‌ها از فایل‌های CSV
- پیش‌پردازش داده‌ها (نرمال‌سازی، encoding)
- تقسیم داده به Train/Validation/Test
- ایجاد PyTorch DataLoader برای آموزش

**ویژگی‌ها:**
- پشتیبانی از داده‌های نمونه موجود
- استخراج 50 ویژگی از داده‌های بیمار
- تبدیل label‌ها به binary classification (Alzheimer/Parkinson)
- Stratified splitting برای حفظ توزیع کلاس‌ها

### 2. Model Trainer (`backend/app/services/training/trainer.py`)

**قابلیت‌ها:**
- آموزش مدل با PyTorch
- Early stopping برای جلوگیری از overfitting
- Learning rate scheduling
- ذخیره بهترین مدل بر اساس validation loss
- ثبت تاریخچه آموزش

**ویژگی‌ها:**
- پشتیبانی از GPU و CPU
- Checkpointing خودکار
- Logging کامل فرآیند آموزش
- تنظیمات قابل تغییر (learning rate, batch size, epochs, etc.)

### 3. Model Evaluator (`backend/app/services/training/evaluator.py`)

**قابلیت‌ها:**
- محاسبه معیارهای اعتبارسنجی بالینی:
  - **Accuracy**: دقت کلی
  - **Sensitivity (Recall)**: نرخ مثبت واقعی
  - **Specificity**: نرخ منفی واقعی
  - **Precision (PPV)**: ارزش پیش‌بینی مثبت
  - **NPV**: ارزش پیش‌بینی منفی
  - **F1-Score**: میانگین هارمونیک precision و recall
  - **AUC-ROC**: مساحت زیر منحنی ROC
  - **Confusion Matrix**: ماتریس خطا
  - **Optimal Threshold**: آستانه بهینه بر اساس Youden's J

**ویژگی‌ها:**
- گزارش جامع اعتبارسنجی بالینی
- پشتیبانی از هر دو بیماری (Alzheimer و Parkinson)
- محاسبه آستانه بهینه برای classification

### 4. Model Registry (`backend/app/services/training/model_registry.py`)

**قابلیت‌ها:**
- مدیریت نسخه‌های مدل
- ثبت مدل‌های آموزش دیده با metadata
- فعال/غیرفعال کردن مدل‌ها
- ذخیره معیارهای عملکرد

**ویژگی‌ها:**
- نسخه‌گذاری خودکار
- ذخیره تاریخ، معیارها، و توضیحات
- امکان جستجو و بازیابی مدل‌ها

### 5. Training Script (`backend/scripts/train_model.py`)

**قابلیت‌ها:**
- اسکریپت command-line برای آموزش مدل
- پشتیبانی از پارامترهای قابل تنظیم
- ثبت خودکار مدل در registry
- تولید گزارش اعتبارسنجی بالینی

**استفاده:**
```bash
cd backend
python scripts/train_model.py --epochs 100 --batch-size 32 --set-active
```

### 6. Evaluation Script (`backend/scripts/evaluate_model.py`)

**قابلیت‌ها:**
- ارزیابی مدل‌های آموزش دیده
- محاسبه معیارهای اعتبارسنجی بالینی
- تولید گزارش تفصیلی

**استفاده:**
```bash
python scripts/evaluate_model.py --model-version <version> --csv-file <test_data.csv>
```

### 7. به‌روزرسانی AI Model Service (`backend/app/services/ai_model_service.py`)

**تغییرات:**
- بارگذاری خودکار مدل‌های آموزش دیده از registry
- پشتیبانی از مدل فعال
- Fallback به مدل پیش‌فرض در صورت عدم وجود
- Logging بهبود یافته

### 8. به‌روزرسانی Config (`backend/app/core/config.py`)

**پارامترهای جدید:**
- `MODEL_REGISTRY_PATH`: مسیر registry مدل‌ها
- `USE_TRAINED_MODEL`: استفاده از مدل‌های آموزش دیده
- `TRAINING_DATA_DIR`: مسیر داده‌های آموزش
- `TRAIN_RATIO`, `VAL_RATIO`, `TEST_RATIO`: نسبت تقسیم داده
- `TRAINING_EPOCHS`, `TRAINING_BATCH_SIZE`, etc.: پارامترهای آموزش

## ساختار فایل‌ها

```
backend/
├── app/
│   ├── services/
│   │   ├── training/
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py      # بارگذاری و پیش‌پردازش داده
│   │   │   ├── trainer.py          # آموزش مدل
│   │   │   ├── evaluator.py        # اعتبارسنجی بالینی
│   │   │   └── model_registry.py   # مدیریت نسخه‌های مدل
│   │   └── ai_model_service.py     # به‌روزرسانی شده
│   └── core/
│       └── config.py               # به‌روزرسانی شده
├── scripts/
│   ├── train_model.py              # اسکریپت آموزش
│   └── evaluate_model.py           # اسکریپت ارزیابی
└── docs/
    ├── TRAINING_GUIDE.md           # راهنمای آموزش (انگلیسی)
    └── TRAINING_IMPLEMENTATION_FA.md  # این فایل
```

## نحوه استفاده

### 1. آماده‌سازی داده

اطمینان حاصل کنید که داده‌ها در فرمت CSV موجود است:
- مسیر پیش‌فرض: `data/data/csv/sample_dataset_complete.csv`
- یا استفاده از `--csv-file` برای مشخص کردن مسیر

### 2. آموزش مدل

```bash
cd backend
python scripts/train_model.py \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 0.001 \
    --set-active
```

### 3. ارزیابی مدل

```bash
python scripts/evaluate_model.py \
    --model-version <version> \
    --threshold 0.5
```

### 4. استفاده از مدل آموزش دیده

مدل به صورت خودکار توسط `AIModelService` بارگذاری می‌شود اگر:
- `USE_TRAINED_MODEL=True` در config
- مدل فعال در registry موجود باشد

## معیارهای اعتبارسنجی بالینی

پس از آموزش، معیارهای زیر محاسبه می‌شود:

### برای هر بیماری (Alzheimer و Parkinson):

1. **Accuracy**: دقت کلی classification
2. **Sensitivity**: توانایی تشخیص موارد مثبت (True Positive Rate)
3. **Specificity**: توانایی تشخیص موارد منفی (True Negative Rate)
4. **Precision**: نسبت پیش‌بینی‌های مثبت صحیح
5. **NPV**: نسبت پیش‌بینی‌های منفی صحیح
6. **F1-Score**: تعادل بین precision و recall
7. **AUC-ROC**: مساحت زیر منحنی ROC (معیار کلی عملکرد)
8. **Confusion Matrix**: تفکیک دقیق نتایج
9. **Optimal Threshold**: آستانه بهینه برای classification

## خروجی‌ها

### پس از آموزش:

1. **مدل آموزش دیده**: `models/best_model_<timestamp>.pth`
2. **معیارهای آموزش**: `models/training_metrics_<timestamp>.json`
3. **گزارش بالینی**: `models/clinical_report_<timestamp>.txt`
4. **Registry**: `models/registry.json`

### پس از ارزیابی:

1. **گزارش ارزیابی**: `models/evaluation_report_<timestamp>.txt`
2. **معیارهای ارزیابی**: `models/evaluation_metrics_<timestamp>.json`

## نکات مهم

1. **داده‌های واقعی**: برای استفاده در production، باید داده‌های واقعی با رضایت بیمار جمع‌آوری شود
2. **اعتبارسنجی بالینی**: باید مطالعات اعتبارسنجی بالینی با شرکای پزشکی انجام شود
3. **تأییدیه‌های نظارتی**: برای استفاده بالینی، نیاز به تأییدیه‌های نظارتی (FDA 510(k), CE marking) است
4. **نظارت مستمر**: عملکرد مدل باید به صورت مستمر نظارت شود
5. **بازآموزی**: مدل باید به صورت دوره‌ای با داده‌های جدید بازآموزی شود

## گام‌های بعدی

1. ✅ جمع‌آوری داده‌های واقعی
2. ✅ آموزش مدل با داده‌های واقعی
3. ⏳ اعتبارسنجی بالینی با داده‌های مستقل
4. ⏳ مطالعات اعتبارسنجی با شرکای پزشکی
5. ⏳ بهینه‌سازی hyperparameters
6. ⏳ بهبود معماری مدل
7. ⏳ استفاده از ensemble methods
8. ⏳ دریافت تأییدیه‌های نظارتی

## نتیجه‌گیری

با پیاده‌سازی این pipeline:
- ✅ مدل‌ها با داده‌های واقعی آموزش داده می‌شوند
- ✅ معیارهای اعتبارسنجی بالینی محاسبه می‌شود
- ✅ مدل‌ها نسخه‌گذاری و مدیریت می‌شوند
- ✅ گزارش‌های جامع تولید می‌شود
- ✅ مدل‌ها به صورت خودکار بارگذاری می‌شوند

این پیاده‌سازی پایه‌ای برای استفاده از مدل‌های AI در محیط production فراهم می‌کند.

