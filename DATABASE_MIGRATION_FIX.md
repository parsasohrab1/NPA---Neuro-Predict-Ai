# رفع مشکل Database Migration - ستون‌های XAI
# Database Migration Fix - XAI Columns

## 🔧 مشکل

خطای زیر در هنگام استفاده از دکمه "Clear All Data" در داشبورد رخ می‌داد:

```
sqlite3.OperationalError) no such column: data_fusion_reports.xai_evidence
```

**علت:**
- مدل `DataFusionReport` شامل ستون‌های XAI (`xai_evidence`, `xai_method`, `has_xai_explanation`) بود
- اما دیتابیس SQLite فاقد این ستون‌ها بود
- هنگام حذف داده‌ها، SQLAlchemy سعی می‌کرد تمام ستون‌های مدل را query کند که باعث خطا می‌شد

---

## ✅ راه حل

### 1. Migration Script ایجاد شد

**فایل:** `backend/scripts/migrate_add_xai_columns.py`

این اسکریپت:
- ✅ ستون‌های XAI را به جدول `data_fusion_reports` اضافه می‌کند
- ✅ ستون‌های موجود را بررسی می‌کند
- ✅ فقط ستون‌های مفقود را اضافه می‌کند

### 2. ستون‌های اضافه شده

```sql
ALTER TABLE data_fusion_reports ADD COLUMN xai_evidence JSON;
ALTER TABLE data_fusion_reports ADD COLUMN xai_method VARCHAR(50);
ALTER TABLE data_fusion_reports ADD COLUMN has_xai_explanation INTEGER DEFAULT 0;
```

### 3. Endpoint `clear-all-data` به‌روزرسانی شد

**فایل:** `backend/app/api/disease_tracking.py`

تغییرات:
- ✅ Import مدل `DataFusionReport`
- ✅ حذف `DataFusionReport` ها قبل از حذف `Patient` ها
- ✅ مدیریت خطاها با try-except
- ✅ گزارش تعداد `fusion_reports_deleted`

---

## 📋 مراحل اجرا

### Migration اجرا شد:

```bash
python backend/scripts/migrate_add_xai_columns.py
```

**نتیجه:**
```
✅ Migration completed successfully!
   - xai_evidence added
   - xai_method added
   - has_xai_explanation added
```

---

## 🔍 بررسی

می‌توانید بررسی کنید که ستون‌ها اضافه شده‌اند:

```python
import sqlite3
conn = sqlite3.connect('backend/neuropredict.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(data_fusion_reports)")
columns = cursor.fetchall()
xai_cols = [col for col in columns if 'xai' in col[1].lower()]
print("XAI columns:", [col[1] for col in xai_cols])
```

---

## 🎯 نتیجه

✅ **مشکل برطرف شد!**

حالا می‌توانید:
1. ✅ از دکمه "Clear All Data" بدون خطا استفاده کنید
2. ✅ `DataFusionReport` ها به درستی حذف می‌شوند
3. ✅ تمام داده‌های مرتبط به درستی پاک می‌شوند

---

## 💡 نکات مهم

### اگر مشکل ادامه داشت:

1. **Restart Backend:**
   ```bash
   # Stop backend
   # Start backend again
   ```

2. **بررسی دیتابیس:**
   ```bash
   python backend/scripts/migrate_add_xai_columns.py
   ```

3. **اگر ستون‌ها هنوز وجود ندارند:**
   - Migration script را دوباره اجرا کنید
   - یا به صورت دستی با SQLite اضافه کنید

### برای Future Migrations:

این اسکریپت را می‌توانید به عنوان template استفاده کنید برای migration های بعدی.

---

**تاریخ:** دسامبر 2024  
**وضعیت:** ✅ Fixed  
**نسخه:** 1.0

