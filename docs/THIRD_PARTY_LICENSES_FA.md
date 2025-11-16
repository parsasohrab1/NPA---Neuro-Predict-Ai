## مجوزهای نرم‌افزارهای استفاده‌شده (Third-Party Licenses)

این سند نمایی کلی از مجوزهای وابستگی‌های اصلی پروژه ارائه می‌دهد و روش تولید گزارش دقیق و قابل استناد را توضیح می‌دهد. برای استفاده نهایی در سازمان، حتماً خروجی ابزارهای خودکار را ضمیمه کنید.


### نکات مهم
- این فهرست غیرقطعی است و ممکن است با تغییر نسخه‌ها تغییر کند.
- برای گزارش رسمی، از ابزارهای پیشنهادی در بخش «نحوه تولید گزارش دقیق» استفاده کنید.
- اکثر کتابخانه‌های استفاده‌شده دارای مجوزهای متن‌باز سهل‌گیر (permissive) مانند MIT، BSD-3-Clause یا Apache-2.0 هستند.


### وابستگی‌های اصلی Backend (نمونه مجوزهای رایج)
- FastAPI (اغلب: MIT)
- Uvicorn (اغلب: BSD-3-Clause)
- Pydantic / pydantic-settings (اغلب: MIT)
- SQLAlchemy / Alembic (اغلب: MIT)
- asyncpg / aiosqlite (اغلب: BSD-3-Clause / MIT)
- python-jose / passlib / bcrypt / cryptography (اغلب: MIT/BSD/Apache-2.0)
- HTTPX / AIOHTTP / redis-py (اغلب: BSD-3-Clause / Apache-2.0 / MIT)
- Celery (اغلب: BSD-3-Clause)
- NumPy / SciPy / pandas / scikit-learn / scikit-image (اغلب: BSD-3-Clause)
- PyTorch (اغلب: BSD-3-Clause)؛ TensorFlow / Keras (اغلب: Apache-2.0)
- pydicom / nibabel / SimpleITK / OpenCV / Pillow (اغلب: MIT/BSD-3 / Apache-2.0 / BSD-3 / (Pillow License))
- matplotlib / seaborn (اغلب: PSF/BSD-Style / BSD-3-Clause)
- reportlab / openpyxl (اغلب: BSD-3-Clause / MIT)
- sentry-sdk / psutil / python-dateutil / pytz / aiofiles (اغلب: BSD-3 / BSD-3 / BSD-3 / MIT / Apache-2.0)

توجه: برخی پروژه‌ها مجوزهای چندگانه/ویژه دارند (مثل Pillow). حتماً گزارش ابزار را مرجع قرار دهید.


### وابستگی‌های اصلی Frontend (نمونه مجوزهای رایج)
- React / React DOM / React Router (اغلب: MIT)
- Axios (اغلب: MIT)
- TanStack React Query (اغلب: MIT)
- Zustand (اغلب: MIT)
- Headless UI / Heroicons (اغلب: MIT)
- Recharts (اغلب: MIT)
- react-hook-form / zod / @hookform/resolvers (اغلب: MIT)
- date-fns / clsx / tailwind-merge (اغلب: MIT)
- i18next / react-i18next / i18next-browser-languagedetector (اغلب: MIT)
- Vite / @vitejs/plugin-react (اغلب: MIT)
- TypeScript (اغلب: Apache-2.0)
- TailwindCSS / PostCSS / Autoprefixer (اغلب: MIT)
- ESLint و پلاگین‌های مرتبط (اغلب: MIT)


### نحوه تولید گزارش دقیق (قابل استناد)

- Backend (Python) — استفاده از pip-licenses:
  1) ایجاد/فعال‌سازی محیط مجزا و نصب وابستگی‌ها (production) بر اساس `backend/requirements.txt`.
  2) نصب ابزار:
     ```bash
     pip install pip-licenses
     ```
  3) تولید گزارش (CSV/Markdown/JSON):
     ```bash
     pip-licenses --format=markdown --with-authors --with-urls --with-license-file > backend_third_party_licenses.md
     ```
  4) بررسی موارد with-license-file برای ضمیمه متن کامل مجوزها (در صورت نیاز حقوقی).

- Frontend (Node) — استفاده از license-checker یا npm-license-crawler:
  1) در پوشه‌های `frontend/` و `admin-dashboard/` نصب وابستگی‌ها:
     ```bash
     npm ci
     ```
  2) نصب ابزار (به‌صورت global یا devDependency):
     ```bash
     npm install -g license-checker
     ```
  3) تولید گزارش (JSON/Markdown):
     ```bash
     license-checker --production --json > frontend_third_party_licenses.json
     ```
     یا
     ```bash
     license-checker --production --csv > frontend_third_party_licenses.csv
     ```
  4) در `admin-dashboard/` نیز مراحل را تکرار کنید.


### نگهداشت و انطباق
- گزارش‌های مجوز را در هر انتشار (Release) به‌روزرسانی و در ریپو بایگانی کنید.
- روی تغییر مجوزها بین نسخه‌ها نظارت داشته باشید (به‌ویژه هنگام ارتقای بزرگ).
- در صورت نیاز سازمانی، مجوزهای ناسازگار با سیاست را از وابستگی‌ها حذف/جایگزین کنید.


### سلب مسئولیت
این سند برای راهنمایی سریع تهیه شده است و جایگزین بررسی حقوقی رسمی نیست. نتایج ابزارهای خودکار (pip-licenses, license-checker) و مشاوره حقوقی سازمان مرجع نهایی هستند.


