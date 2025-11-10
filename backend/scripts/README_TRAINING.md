# Training Scripts - راهنمای استفاده

## آموزش مدل

برای آموزش مدل با داده‌های واقعی:

```bash
cd backend
python scripts/train_model.py
```

### مثال‌های استفاده:

#### آموزش با تنظیمات پیش‌فرض:
```bash
python scripts/train_model.py
```

#### آموزش با پارامترهای سفارشی:
```bash
python scripts/train_model.py \
    --epochs 200 \
    --batch-size 64 \
    --learning-rate 0.0001 \
    --patience 20 \
    --set-active
```

#### آموزش با فایل داده خاص:
```bash
python scripts/train_model.py \
    --csv-file path/to/your/data.csv \
    --epochs 100 \
    --set-active
```

## ارزیابی مدل

برای ارزیابی مدل آموزش دیده:

```bash
python scripts/evaluate_model.py --model-version <version>
```

### مثال‌های استفاده:

#### ارزیابی مدل فعال:
```bash
python scripts/evaluate_model.py
```

#### ارزیابی مدل خاص:
```bash
python scripts/evaluate_model.py --model-version 20240101_120000
```

#### ارزیابی با فایل تست:
```bash
python scripts/evaluate_model.py \
    --model-path models/best_model_20240101_120000.pth \
    --csv-file data/test_data.csv \
    --threshold 0.5
```

## خروجی‌ها

### پس از آموزش:
- مدل: `models/best_model_<timestamp>.pth`
- معیارها: `models/training_metrics_<timestamp>.json`
- گزارش: `models/clinical_report_<timestamp>.txt`
- Registry: `models/registry.json`

### پس از ارزیابی:
- گزارش: `models/evaluation_report_<timestamp>.txt`
- معیارها: `models/evaluation_metrics_<timestamp>.json`

## نکات مهم

1. اطمینان حاصل کنید که داده‌ها در مسیر صحیح موجود است
2. برای production، از داده‌های واقعی با رضایت بیمار استفاده کنید
3. مدل‌ها به صورت خودکار در registry ثبت می‌شوند
4. از `--set-active` برای فعال کردن مدل استفاده کنید

## کمک

برای مشاهده راهنمای کامل:
- `backend/docs/TRAINING_GUIDE.md` (انگلیسی)
- `backend/docs/TRAINING_IMPLEMENTATION_FA.md` (فارسی)

