# Real-Time Admin Dashboard Implementation

## خلاصه پیاده‌سازی

این مستند توضیح می‌دهد که چگونه داشبورد مدیریتی NeuroPredict-AI از یک داشبورد پایه (۴۰٪) به یک ابزار کامل پشتیبانی تصمیم‌گیری بالینی (CDS) با قابلیت‌های برخط تبدیل شده است.

## ویژگی‌های پیاده‌سازی شده

### ۱. مانیتورینگ عملکرد هوش مصنوعی (AI/ML Health)

#### API Endpoints:
- `GET /api/v1/monitoring/ai/ml-health` - سلامت کلی مدل AI/ML
- `GET /api/v1/monitoring/ai/feature-importance` - اهمیت ویژگی‌ها (Explainability)
- `GET /api/v1/monitoring/ai/model-performance` - عملکرد مدل

#### قابلیت‌ها:
- ✅ **پایش برخط عملکرد مدل (Model Drift)**
  - Data Drift: مقایسه توزیع آماری داده‌های ورودی جدید با داده‌های زمان آموزش
  - Performance Drift: نمایش دقت، حساسیت و F1-Score بر روی آخرین N پیش‌بینی
  - Confidence Score Distribution: توزیع برخط امتیازات اعتماد

- ✅ **نمایش توجیه‌پذیری (Explainability)**
  - Feature Importance: نمایش پرکاربردترین ویژگی‌های ورودی
  - نمایش تأثیر هر ویژگی در آخرین دسته‌بندی‌ها

### ۲. مانیتورینگ کلینیکی و طولی (Clinical & Longitudinal)

#### API Endpoints:
- `GET /api/v1/monitoring/clinical/longitudinal/{patient_id}` - ردیابی طولی بیمار
- `GET /api/v1/monitoring/clinical/smart-alerts` - هشدارهای هوشمند
- `GET /api/v1/monitoring/clinical/prediction-queue` - صف انتظار پیش‌بینی

#### قابلیت‌ها:
- ✅ **ردیابی طولی پیشرفته (Longitudinal Tracking)**
  - نمایش نمودارهای روند برای بیماران پرخطر
  - تغییرات معیارها در طول زمان (Episode/Visit)
  - روند کاهش نمرات MMSE یا افزایش آمیلوئید بتا

- ✅ **سیستم هشداردهی هوشمند (Smart Alerting)**
  - نمایش برخط بیماران جدید با ریسک افزایش یافته
  - پیش‌بینی‌های با تضاد بالا (High Discrepancy)
  - هشدار برای تغییرات ناگهانی در ریسک

- ✅ **صف انتظار پیش‌بینی**
  - نمایش تعداد درخواست‌های پیش‌بینی در حال پردازش

### ۳. مانیتورینگ زیرساخت و عملیات (DevOps & System Health)

#### API Endpoints:
- `GET /api/v1/monitoring/system/health` - سلامت کلی سیستم
- `GET /api/v1/monitoring/system/performance` - معیارهای عملکرد
- `GET /api/v1/monitoring/system/services` - وضعیت سرویس‌ها

#### قابلیت‌ها:
- ✅ **کارایی سرویس AI (Latency)**
  - نمایش برخط میانگین زمان پاسخ‌دهی مدل (هدف: زیر ۳ ثانیه)
  - P95 و P99 response times

- ✅ **توان عملیاتی (Throughput)**
  - تعداد درخواست‌های API در دقیقه/ساعت
  - تعداد مطالعات پردازش شده (هدف: بیش از ۱۰۰ مطالعه در ساعت)

- ✅ **سلامت سرویس‌های حیاتی**
  - وضعیت برخط (Up/Down) تمام میکروسرویس‌ها
  - PostgreSQL Database
  - Redis Cache
  - AI Model Service

- ✅ **نرخ خطا (Error Rate)**
  - نمایش برخط نرخ خطاهای سمت سرور (5xx)
  - نمایش برخط نرخ خطاهای سمت کاربر (4xx)

### ۴. مانیتورینگ امنیتی و انطباق (Security & Compliance)

#### API Endpoints:
- `GET /api/v1/monitoring/security/audit-logs` - لاگ ممیزی
- `GET /api/v1/monitoring/security/authentication-monitoring` - نظارت بر احراز هویت
- `GET /api/v1/monitoring/security/admin-activity` - فعالیت ادمین‌ها

#### قابلیت‌ها:
- ✅ **جریان لاگ ممیزی (Audit Log Stream)**
  - نمایش برخط آخرین فعالیت‌های پرخطر کاربران
  - حذف پرونده بیمار، تغییر نقش، ورود به سیستم
  - فیلتر بر اساس نوع فعالیت

- ✅ **نظارت بر احراز هویت**
  - نمایش برخط تلاش‌های ناموفق ورود به سیستم
  - هشدارهای مربوط به حملات Brute-Force
  - لیست IP های مشکوک

- ✅ **فعالیت کاربران ادمین**
  - نمایش تعداد کاربران ادمین فعال
  - آخرین فعالیت آن‌ها
  - خلاصه فعالیت‌های اخیر

## WebSocket Real-Time Updates

### پیاده‌سازی:
- **WebSocket Endpoint**: `ws://localhost:8000/api/v1/ws/monitoring`
- **Channels**: `all`, `ai_ml`, `clinical`, `system`, `security`
- **Authentication**: JWT Token-based

### قابلیت‌ها:
- ✅ اتصال برخط با احراز هویت
- ✅ به‌روزرسانی خودکار هر ۱۰-۳۰ ثانیه
- ✅ Heartbeat برای حفظ اتصال
- ✅ Reconnection خودکار در صورت قطع اتصال
- ✅ Broadcast به کانال‌های مختلف

### Message Types:
- `connection` - تأیید اتصال
- `heartbeat` - نگه‌داری اتصال
- `ai_ml_update` - به‌روزرسانی AI/ML
- `clinical_update` - به‌روزرسانی کلینیکی
- `system_update` - به‌روزرسانی سیستم
- `security_update` - به‌روزرسانی امنیتی
- `alert` - هشدار فوری

## Frontend Components

### کامپوننت‌های اصلی:

1. **AdminDashboard.tsx** - داشبورد اصلی با Tab Navigation
2. **AIMLHealth.tsx** - مانیتورینگ AI/ML با نمودارها
3. **ClinicalMonitoring.tsx** - مانیتورینگ کلینیکی و هشدارها
4. **SystemHealth.tsx** - مانیتورینگ سیستم و DevOps
5. **SecurityMonitoring.tsx** - مانیتورینگ امنیتی و انطباق

### Hook های استفاده شده:

- **useWebSocket** - مدیریت اتصال WebSocket
- **@tanstack/react-query** - مدیریت state و caching
- **recharts** - نمودارهای تعاملی

## ساختار فایل‌ها

### Backend:
```
backend/app/api/
├── monitoring.py          # API endpoints برای مانیتورینگ
└── websocket.py           # WebSocket server

backend/app/core/
└── security.py            # احراز هویت WebSocket
```

### Frontend:
```
admin-dashboard/src/
├── AdminDashboard.tsx     # داشبورد اصلی
├── components/
│   ├── AIMLHealth.tsx
│   ├── ClinicalMonitoring.tsx
│   ├── SystemHealth.tsx
│   └── SecurityMonitoring.tsx
├── hooks/
│   └── useWebSocket.ts    # Hook برای WebSocket
└── services/
    └── api.ts             # API client
```

## استفاده

### راه‌اندازی Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

### راه‌اندازی Admin Dashboard:
```bash
cd admin-dashboard
npm install
npm run dev
```

### دسترسی به داشبورد:
1. ورود به سیستم با نقش Admin
2. دسترسی به `http://localhost:3000` (یا پورت admin-dashboard)
3. انتخاب Tab های مختلف برای مشاهده مانیتورینگ

## الزامات رگولاتوری

این پیاده‌سازی الزامات زیر را پوشش می‌دهد:

- ✅ **FDA 21 CFR Part 11**: Audit logging کامل
- ✅ **HIPAA**: لاگ تمام دسترسی‌ها به داده‌های بیمار
- ✅ **GDPR**: نظارت بر فعالیت‌های کاربران
- ✅ **ISO 13485**: مانیتورینگ سیستم و کیفیت

## نکات مهم

1. **Real-Time Updates**: تمام بخش‌ها به صورت برخط به‌روزرسانی می‌شوند
2. **Security**: تمام endpoints نیاز به احراز هویت دارند
3. **Performance**: استفاده از caching و polling برای بهینه‌سازی
4. **Scalability**: WebSocket connection manager برای مدیریت اتصالات متعدد

## بهبودهای آینده

- [ ] اضافه کردن A/B Testing monitoring
- [ ] پیاده‌سازی Prometheus/Grafana integration
- [ ] اضافه کردن Alert notifications (Email/SMS)
- [ ] Export reports به PDF/Excel
- [ ] Customizable dashboards برای کاربران مختلف

