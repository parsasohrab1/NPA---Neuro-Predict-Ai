# راهنمای اعتبارسنجی بالینی (Clinical Validation Guide)

این سند راهنمای جامع برای انجام مطالعات اعتبارسنجی بالینی مدل‌های هوش مصنوعی NeuroPredict-AI است.

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [الزامات قبل از اعتبارسنجی](#الزامات-قبل-از-اعتبارسنجی)
3. [مراحل اعتبارسنجی](#مراحل-اعتبارسنجی)
4. [جمع‌آوری داده‌های واقعی](#جمع‌آوری-داده‌های-واقعی)
5. [مطالعات اعتبارسنجی](#مطالعات-اعتبارسنجی)
6. [تحلیل نتایج](#تحلیل-نتایج)
7. [تاییدات نظارتی](#تاییدات-نظارتی)
8. [نگهداری و نظارت مداوم](#نگهداری-و-نظارت-مداوم)

---

## مقدمه

### اهمیت اعتبارسنجی بالینی

اعتبارسنجی بالینی یک **الزام اجباری** برای استفاده از ابزارهای AI در محیط‌های پزشکی است. بدون اعتبارسنجی مناسب:

- ❌ نمی‌توان از مدل در محیط production استفاده کرد
- ❌ نمی‌توان تاییدیه‌های نظارتی (FDA 510(k), CE Mark) دریافت کرد
- ❌ مسولیت قانونی و اخلاقی وجود دارد

### محدودیت‌های مدل‌های فعلی

⚠️ **هشدار مهم**: مدل‌های فعلی که با داده‌های synthetic آموزش داده شده‌اند:

- **فقط برای اهداف نمایشی** هستند
- **مناسب استفاده بالینی نیستند**
- **نیاز به آموزش مجدد با داده‌های واقعی** دارند

---

## الزامات قبل از اعتبارسنجی

### 1. جمع‌آوری داده‌های واقعی

#### الف) الزامات داده

- **حجم**: حداقل 1000-5000 نمونه تایید شده برای هر بیماری
- **کیفیت**: داده‌های با کیفیت بالا، کامل و دارای labels صحیح
- **توزیع**: نماینده جمعیت واقعی (سن، جنسیت، قومیت)
- **استاندارد**: داده‌ها باید بر اساس پروتکل‌های استاندارد جمع‌آوری شده باشند

#### ب) رضایت‌نامه و اخلاق پزشکی

- ✅ **Informed Consent**: رضایت‌نامه آگاهانه از بیماران
- ✅ **IRB Approval**: تایید کمیته اخلاق پزشکی
- ✅ **HIPAA/GDPR Compliance**: رعایت قوانین حریم خصوصی
- ✅ **Data Anonymization**: ناشناس‌سازی داده‌ها
- ✅ **Data Retention Policy**: سیاست نگهداری داده

#### ج) کیفیت داده

- **Completeness**: داده‌های کامل (حداقل 95% fields پر شده)
- **Accuracy**: صحت داده‌ها تایید شده توسط متخصصان
- **Consistency**: یکنواختی در نحوه جمع‌آوری
- **Validation**: تایید توسط radiologists و neurologists

---

## مراحل اعتبارسنجی

### Phase 1: جمع‌آوری و آماده‌سازی داده

```bash
# 1. جمع‌آوری داده‌های واقعی از بیمارستان‌ها
# 2. ناشناس‌سازی داده‌ها
# 3. تایید کیفیت توسط متخصصان
# 4. تقسیم به Train/Val/Test sets
```

**معیارهای تقسیم داده:**
- Training: 70%
- Validation: 15%
- Test (Hold-out): 15%

### Phase 2: آموزش مدل

```bash
python scripts/train_model.py \
    --csv-file data/real_clinical_data.csv \
    --epochs 200 \
    --batch-size 32 \
    --learning-rate 0.0001 \
    --description "Model trained on real clinical data - Version 1.0 - IRB Protocol #XXXX"
```

### Phase 3: ارزیابی اولیه

```bash
python scripts/evaluate_model.py \
    --model-path models/best_model_xxx.pth \
    --test-data data/test_set.csv
```

**معیارهای حداقلی:**
- Accuracy: > 85%
- Sensitivity: > 85%
- Specificity: > 85%
- AUC-ROC: > 0.90

---

## مطالعات اعتبارسنجی

### 1. مطالعه اعتبارسنجی Internal Validation

**هدف**: تایید عملکرد مدل روی داده‌های unseen

**روش:**
- استفاده از Test Set (Hold-out)
- Cross-validation (5-fold)
- Bootstrapping برای confidence intervals

**معیارها:**
- Accuracy, Sensitivity, Specificity
- Precision, NPV, F1-Score
- AUC-ROC, AUC-PR
- Confusion Matrix

**نتیجه‌گیری:**
- اگر معیارها به threshold رسیدند → ادامه به External Validation
- در غیر این صورت → بهبود مدل یا جمع‌آوری داده بیشتر

### 2. مطالعه اعتبارسنجی External Validation

**هدف**: تایید عملکرد روی داده‌های از مراکز دیگر

**روش:**
- جمع‌آوری داده از 2-3 مرکز دیگر
- تست مدل روی این داده‌ها بدون re-training
- مقایسه عملکرد

**معیارها:** (همانند Internal Validation)

**نتیجه‌گیری:**
- اگر عملکرد مشابه باشد → مدل generalizable است
- اگر کاهش عملکرد وجود دارد → نیاز به calibration یا retraining

### 3. مطالعه مقایسه‌ای (Comparative Study)

**هدف**: مقایسه با روش‌های استاندارد فعلی

**مقایسه با:**
- Radiologist interpretation
- Other clinical decision tools
- Existing diagnostic guidelines

**معیارها:**
- Agreement (Kappa score)
- Diagnostic accuracy
- Time to diagnosis

### 4. مطالعه تاثیر بالینی (Clinical Impact Study)

**هدف**: ارزیابی تاثیر واقعی مدل روی مراقبت از بیمار

**اندازه‌گیری:**
- تغییر در زمان تشخیص
- تغییر در درمان
- Patient outcomes
- Cost-effectiveness

---

## تحلیل نتایج

### 1. معیارهای عملکرد

```python
from app.services.training.evaluator import ModelEvaluator

evaluator = ModelEvaluator()
metrics = evaluator.calculate_clinical_metrics(
    alzheimer_preds, alzheimer_labels,
    parkinson_preds, parkinson_labels
)

# برای هر بیماری:
# - Accuracy
# - Sensitivity (Recall)
# - Specificity
# - Precision (PPV)
# - Negative Predictive Value (NPV)
# - F1-Score
# - AUC-ROC
# - Optimal Threshold
```

### 2. تحلیل Subgroup

- تحلیل بر اساس سن
- تحلیل بر اساس جنسیت
- تحلیل بر اساس شدت بیماری
- تحلیل بر اساس comorbidities

### 3. تحلیل خطاها

- False Positives: مواردی که به اشتباه مثبت تشخیص داده شدند
- False Negatives: مواردی که به اشتباه منفی تشخیص داده شدند
- تحلیل patterns در خطاها

### 4. گزارش بالینی

```bash
python scripts/evaluate_model.py --model-path models/best_model.pth --generate-report
```

گزارش شامل:
- Executive Summary
- Methodology
- Results
- Limitations
- Recommendations

---

## تاییدات نظارتی

### FDA 510(k) (برای آمریکا)

**الزامات:**
1. **Clinical Data**: داده‌های بالینی واقعی
2. **Performance Data**: معیارهای عملکرد
3. **Comparative Study**: مقایسه با predicate device
4. **Risk Analysis**: تحلیل ریسک
5. **Labeling**: برچسب‌گذاری مناسب

**مراحل:**
1. Pre-submission meeting با FDA
2. Submission package
3. FDA Review (60-90 days)
4. Approval/Denial

### CE Marking (برای اروپا)

**الزامات:**
1. Clinical Evaluation Report (CER)
2. Technical Documentation
3. Quality Management System (ISO 13485)
4. Risk Management (ISO 14971)
5. Labeling (MDD/MDR)

### سایر تاییدات

- **Health Canada**: Medical Device License
- **PMDA (Japan)**: Pre-market Approval
- **NMPA (China)**: Medical Device Registration

---

## نگهداری و نظارت مداوم

### 1. Post-Market Surveillance

**نظارت بر:**
- عملکرد مدل در production
- Model drift detection
- Adverse events
- User feedback

### 2. Periodic Re-validation

**زمانبندی:**
- Annual review
- Re-validation هنگام تغییرات عمده
- Re-validation هنگام جمع‌آوری داده‌های جدید

### 3. Continuous Improvement

- جمع‌آوری feedback از پزشکان
- بهبود مدل با داده‌های جدید
- Version control و tracking

---

## چک‌لیست پیش از Production

- [ ] داده‌های واقعی جمع‌آوری شده (حداقل 1000-5000 نمونه)
- [ ] IRB Approval دریافت شده
- [ ] رضایت‌نامه بیماران دریافت شده
- [ ] مدل با داده‌های واقعی آموزش داده شده
- [ ] Internal Validation انجام شده
- [ ] External Validation انجام شده
- [ ] Comparative Study انجام شده (اختیاری اما توصیه می‌شود)
- [ ] Clinical Impact Study انجام شده (اختیاری)
- [ ] معیارهای عملکرد به threshold رسیده‌اند
- [ ] گزارش بالینی تهیه شده
- [ ] Submission برای تاییدات نظارتی (FDA/CE)
- [ ] Post-market surveillance plan تعریف شده

---

## منابع و مراجع

1. **FDA Guidance**:
   - Clinical Evaluation of Software as a Medical Device (SaMD)
   - Good Machine Learning Practice (GMLP)

2. **Standards**:
   - ISO 14155: Clinical investigation of medical devices
   - ISO 13485: Quality management for medical devices
   - ISO 14971: Risk management for medical devices

3. **Medical Literature**:
   - SPIRIT-AI Extension guidelines
   - CONSORT-AI Extension guidelines
   - TRIPOD Statement for prediction models

---

## نکات مهم

⚠️ **این سند فقط یک راهنما است. برای اعتبارسنجی واقعی، باید با:**
- Radiologists و Neurologists مشورت کنید
- IRB و کمیته‌های اخلاق پزشکی هماهنگی کنید
- Legal و Regulatory consultants مشورت کنید
- FDA یا سازمان‌های نظارتی محلی هماهنگی کنید

✅ **هرگز از مدل‌های synthetic-trained در محیط production استفاده نکنید!**

---

**آخرین به‌روزرسانی**: 2024-12-XX  
**نسخه**: 1.0  
**تهیه شده توسط**: NeuroPredict-AI Clinical Validation Team


