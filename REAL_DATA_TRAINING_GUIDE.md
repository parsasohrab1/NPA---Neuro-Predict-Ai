# راهنمای کامل جمع‌آوری داده‌های واقعی و آموزش مدل
# Complete Guide: Real Data Collection & Model Training

این راهنما شامل تمام مراحل لازم برای جمع‌آوری داده‌های واقعی بالینی، آموزش مجدد مدل و اعتبارسنجی آن می‌باشد.

---

## ⚠️ هشدار مهم - Important Warning

**برای استفاده بالینی، حتماً باید IRB Approval دریافت شود.**
**For clinical use, IRB Approval is mandatory.**

این اسکریپت‌ها داده‌های واقعی را از منابع مختلف جمع‌آوری می‌کنند، اما باید:
- تأیید اخلاقی (IRB) دریافت شود
- مجوزهای لازم از منابع داده اخذ شود
- قوانین HIPAA و GDPR رعایت شود

---

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش-نیازها)
2. [مرحله ۱: جمع‌آوری داده‌های واقعی](#مرحله-۱-جمع-آوری-داده-های-واقعی)
3. [مرحله ۲: آموزش مجدد مدل](#مرحله-۲-آموزش-مجدد-مدل)
4. [مرحله ۳: اعتبارسنجی مدل](#مرحله-۳-اعتبارسنجی-مدل)
5. [مرحله ۴: نمایش دقت در داشبورد](#مرحله-۴-نمایش-دقت-در-داشبورد)

---

## 🔧 پیش‌نیازها

### نصب پکیج‌های Python

```bash
cd backend
pip install -r requirements.txt

# پکیج‌های اضافی برای جمع‌آوری داده
pip install kaggle datasets huggingface-hub
```

### تنظیم Kaggle API (اختیاری - برای دانلود از Kaggle)

1. ثبت‌نام در [Kaggle](https://www.kaggle.com/)
2. رفتن به Account Settings → API
3. دانلود `kaggle.json`
4. قرار دادن در: `~/.kaggle/kaggle.json` (Linux/Mac) یا `C:\Users\<username>\.kaggle\kaggle.json` (Windows)

---

## 📊 مرحله ۱: جمع‌آوری داده‌های واقعی

### اجرای اسکریپت جمع‌آوری داده

```bash
# از دایرکتوری اصلی پروژه
python data/collect_real_clinical_data.py
```

### گزینه‌های خط فرمان

```bash
# جمع‌آوری با مقادیر پیش‌فرض (1000 MRI, 1000 Cognitive)
python data/collect_real_clinical_data.py

# جمع‌آوری با مقادیر سفارشی
python data/collect_real_clinical_data.py --mri 500 --cognitive 500

# فقط داده‌های شناختی
python data/collect_real_clinical_data.py --mri 0 --cognitive 2000
```

### خروجی

داده‌ها در پوشه `data/real_data/` ذخیره می‌شوند:

```
data/real_data/
├── csv/
│   └── real_cognitive_data_complete.csv    # داده‌های شناختی
├── images/
│   └── real_mri_*.npy                      # تصاویر MRI
└── collection_metadata.json                # Metadata جمع‌آوری
```

### منابع داده

اسکریپت داده‌ها را از منابع زیر جمع‌آوری می‌کند:

1. **Kaggle Datasets**:
   - Alzheimer's Dataset: `tourist55/alzheimers-dataset-4-class-of-images`
   - Brain Tumor Dataset: `masoudnickparvar/brain-tumor-mri-dataset`

2. **Hugging Face Datasets**: (در صورت وجود)

3. **الگوهای تحقیقاتی**:
   - ADNI-Inspired (Alzheimer's Disease Neuroimaging Initiative)
   - OASIS-Inspired (Open Access Series of Imaging Studies)
   - PPMI-Inspired (Parkinson's Progression Markers Initiative)

---

## 🧠 مرحله ۲: آموزش مجدد مدل

### اجرای اسکریپت آموزش

```bash
cd backend
python scripts/train_with_real_data.py
```

### گزینه‌های خط فرمان

```bash
# آموزش با داده‌های پیش‌فرض
python scripts/train_with_real_data.py

# استفاده از فایل داده خاص
python scripts/train_with_real_data.py --data-file ../data/real_data/csv/real_cognitive_data_complete.csv

# تنظیمات آموزش سفارشی
python scripts/train_with_real_data.py \
  --epochs 200 \
  --batch-size 64 \
  --learning-rate 0.0001 \
  --patience 20

# تنظیم مدل به عنوان مدل فعال
python scripts/train_with_real_data.py --set-active
```

### پارامترهای مهم

- `--epochs`: تعداد دوره‌های آموزش (پیش‌فرض: 150)
- `--batch-size`: اندازه batch (پیش‌فرض: 32)
- `--learning-rate`: نرخ یادگیری (پیش‌فرض: 0.001)
- `--patience`: Early stopping patience (پیش‌فرض: 15)
- `--train-ratio`: نسبت داده‌های آموزشی (پیش‌فرض: 0.7)
- `--val-ratio`: نسبت داده‌های اعتبارسنجی (پیش‌فرض: 0.15)
- `--test-ratio`: نسبت داده‌های تست (پیش‌فرض: 0.15)

### خروجی

مدل‌های آموزش دیده در پوشه `models/real_data_trained/` ذخیره می‌شوند:

```
models/real_data_trained/
├── model_*.pth                    # فایل‌های مدل
├── model_metrics.json             # متریک‌های مدل (برای داشبورد)
├── clinical_report_*.txt          # گزارش بالینی
└── registry.json                  # رجیستری مدل‌ها
```

---

## ✅ مرحله ۳: اعتبارسنجی مدل

### اجرای اسکریپت اعتبارسنجی

```bash
cd backend
python scripts/validate_model.py
```

### گزینه‌های خط فرمان

```bash
# اعتبارسنجی با مدل پیش‌فرض
python scripts/validate_model.py

# اعتبارسنجی با مدل خاص
python scripts/validate_model.py --model-path models/real_data_trained/model_v1.0.0.pth

# ذخیره متریک‌ها در فایل خاص
python scripts/validate_model.py --metrics-file models/my_metrics.json
```

### خروجی

متریک‌های اعتبارسنجی شامل:
- **Accuracy**: دقت کلی
- **Precision**: دقت
- **Recall**: حساسیت
- **F1-Score**: میانگین هم‌ساز Precision و Recall

برای هر دو:
- تشخیص آلزایمر (Alzheimer's Disease)
- تشخیص پارکینسون (Parkinson's Disease)

---

## 📊 مرحله ۴: نمایش دقت در داشبورد

### راه‌اندازی Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### راه‌اندازی Dashboard

```bash
cd admin-dashboard
npm run dev
```

### دسترسی به Dashboard

1. باز کردن مرورگر: `http://localhost:5173`
2. ورود با حساب Admin
3. رفتن به **System Overview**
4. دقت مدل در کارت **Model Accuracy** نمایش داده می‌شود

### API Endpoints

API endpoints برای دریافت متریک‌های مدل:

```bash
# دریافت متریک‌های فعلی
GET /api/v1/model-metrics/current

# دریافت خلاصه متریک‌ها
GET /api/v1/model-metrics/summary

# دریافت تاریخچه آموزش
GET /api/v1/model-metrics/training-history
```

---

## 🚀 اجرای کامل (All-in-One)

### Windows PowerShell

```powershell
# مرحله ۱: جمع‌آوری داده
python data/collect_real_clinical_data.py --mri 1000 --cognitive 1000

# مرحله ۲: آموزش مدل
cd backend
python scripts/train_with_real_data.py --epochs 150 --set-active

# مرحله ۳: اعتبارسنجی
python scripts/validate_model.py

# مرحله ۴: راه‌اندازی سرویس‌ها
# در یک Terminal جداگانه:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# در Terminal دیگر:
cd admin-dashboard
npm run dev
```

### Linux/Mac

```bash
# مرحله ۱: جمع‌آوری داده
python3 data/collect_real_clinical_data.py --mri 1000 --cognitive 1000

# مرحله ۲: آموزش مدل
cd backend
python3 scripts/train_with_real_data.py --epochs 150 --set-active

# مرحله ۳: اعتبارسنجی
python3 scripts/validate_model.py

# مرحله ۴: راه‌اندازی سرویس‌ها
# در یک Terminal جداگانه:
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# در Terminal دیگر:
cd admin-dashboard
npm run dev
```

---

## 📈 بررسی نتایج

### فایل‌های مهم

1. **متریک‌های مدل**: `models/real_data_trained/model_metrics.json`
   ```json
   {
     "overall_accuracy": 0.85,
     "alzheimer": {
       "accuracy": 0.87,
       "precision": 0.85,
       "recall": 0.89,
       "f1": 0.87
     },
     "parkinson": {
       "accuracy": 0.83,
       "precision": 0.81,
       "recall": 0.85,
       "f1": 0.83
     }
   }
   ```

2. **گزارش بالینی**: `models/real_data_trained/clinical_report_*.txt`

3. **Metadata داده‌ها**: `data/real_data/collection_metadata.json`

### استانداردهای دقت

- **عالی (Excellent)**: ≥ 85%
- **خوب (Good)**: 75% - 85%
- **متوسط (Fair)**: 65% - 75%
- **نیاز به بهبود**: < 65%

---

## 🔍 عیب‌یابی

### مشکل: داده‌ها دانلود نمی‌شوند

```bash
# بررسی Kaggle API
kaggle datasets list

# بررسی اتصال اینترنت
ping google.com
```

### مشکل: حافظه کافی نیست

```bash
# کاهش batch size
python scripts/train_with_real_data.py --batch-size 16

# کاهش تعداد نمونه‌ها
python data/collect_real_clinical_data.py --mri 500 --cognitive 500
```

### مشکل: مدل در داشبورد نمایش داده نمی‌شود

```bash
# بررسی وجود فایل متریک
ls models/real_data_trained/model_metrics.json

# بررسی API
curl http://localhost:8001/api/v1/model-metrics/summary
```

---

## 📚 منابع بیشتر

- [ADNI Dataset](https://adni.loni.usc.edu/)
- [OASIS Dataset](https://www.oasis-brains.org/)
- [PPMI Dataset](https://www.ppmi-info.org/)
- [Kaggle Medical Datasets](https://www.kaggle.com/datasets?search=alzheimer)
- [Hugging Face Medical Datasets](https://huggingface.co/datasets?search=medical)

---

## ⚖️ مجوزها و اخلاق

### رعایت اخلاق پزشکی

1. **IRB Approval**: دریافت تأیید اخلاقی برای استفاده بالینی
2. **Consent**: دریافت رضایت آگاهانه از بیماران
3. **Privacy**: حفظ حریم خصوصی داده‌ها
4. **Security**: امنیت داده‌های بیماران

### مجوزهای داده

- **CC0 Public Domain**: استفاده آزاد
- **Research Use Only**: فقط برای تحقیقات
- **MIT License**: با شرایط MIT
- **Custom License**: بررسی مجوز هر منبع

---

## 📞 پشتیبانی

برای سوالات و مشکلات:
- بررسی لاگ‌ها: `logs/training_real_data.log`
- بررسی لاگ اعتبارسنجی: `logs/validation.log`
- مراجعه به مستندات پروژه

---

**آخرین بروزرسانی**: دسامبر 2024  
**نسخه**: 1.0.0

