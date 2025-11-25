@echo off
REM ============================================================
REM NeuroPredict-AI Dashboard - راه‌اندازی جامع (بدون اینترنت)
REM ============================================================
REM این فایل تمام قابلیت‌های لازم برای راه‌اندازی داشبورد را دارد
REM - بررسی خودکار مسیر
REM - بررسی پیش‌نیازها (Python, Node.js)
REM - بررسی پورت‌ها
REM - راه‌اندازی Backend و Frontend
REM - باز کردن خودکار مرورگر
REM ============================================================

REM تنظیم encoding برای نمایش فارسی
chcp 65001 >nul 2>&1

REM تغییر به دایرکتوری فایل
cd /d "%~dp0"

REM پاک کردن صفحه
cls

REM نمایش هدر
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║   NeuroPredict-AI Dashboard - راه‌اندازی جامع          ║
echo ║   Dashboard Startup - Complete Version                  ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM مرحله 1: بررسی و پیدا کردن مسیر صحیح
REM ============================================================
echo [1/5] بررسی مسیر و پوشه‌ها...
echo.

set "BACKEND_DIR="
set "FRONTEND_DIR="
set "PROJECT_ROOT=%CD%"

REM بررسی پوشه backend
if exist "%PROJECT_ROOT%\backend" (
    set "BACKEND_DIR=%PROJECT_ROOT%\backend"
    echo   [OK] پوشه backend یافت شد
) else (
    echo   [خطا] پوشه backend یافت نشد!
    echo   دایرکتوری فعلی: %PROJECT_ROOT%
    echo.
    echo   در حال جستجو در پوشه‌های مجاور...
    
    REM جستجو در پوشه والد
    if exist "%PROJECT_ROOT%\..\backend" (
        set "BACKEND_DIR=%PROJECT_ROOT%\..\backend"
        set "PROJECT_ROOT=%PROJECT_ROOT%\.."
        cd /d "%PROJECT_ROOT%"
        echo   [OK] پوشه backend در پوشه والد یافت شد
    ) else (
        echo   [خطا] پوشه backend پیدا نشد!
        echo.
        echo   لطفاً مطمئن شوید که در دایرکتوری پروژه هستید.
        echo   دایرکتوری باید شامل پوشه‌های backend و admin-dashboard باشد.
        echo.
        pause
        exit /b 1
    )
)

REM بررسی پوشه admin-dashboard
if exist "%PROJECT_ROOT%\admin-dashboard" (
    set "FRONTEND_DIR=%PROJECT_ROOT%\admin-dashboard"
    echo   [OK] پوشه admin-dashboard یافت شد
) else (
    echo   [خطا] پوشه admin-dashboard یافت نشد!
    echo   دایرکتوری فعلی: %PROJECT_ROOT%
    echo.
    pause
    exit /b 1
)

echo.
echo   مسیر پروژه: %PROJECT_ROOT%
echo.

REM ============================================================
REM مرحله 2: بررسی پیش‌نیازها
REM ============================================================
echo [2/5] بررسی پیش‌نیازها...
echo.

REM بررسی Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   [خطا] Python یافت نشد!
    echo.
    echo   لطفاً Python را از python.org دانلود و نصب کنید.
    echo   در زمان نصب، گزینه "Add Python to PATH" را انتخاب کنید.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   [OK] Python نصب شده: %PYTHON_VERSION%
)

REM بررسی Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo   [خطا] Node.js یافت نشد!
    echo.
    echo   لطفاً Node.js را از nodejs.org دانلود و نصب کنید.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo   [OK] Node.js نصب شده: %NODE_VERSION%
)

REM بررسی npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo   [خطا] npm یافت نشد!
    echo   npm معمولاً با Node.js نصب می‌شود.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
    echo   [OK] npm نصب شده: %NPM_VERSION%
)

echo.

REM ============================================================
REM مرحله 3: بررسی پورت‌ها
REM ============================================================
echo [3/5] بررسی پورت‌ها...
echo.

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"
set "PORT_CONFLICT=0"

REM بررسی پورت Backend
netstat -ano | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo   [هشدار] پورت %BACKEND_PORT% در حال استفاده است
    echo   Backend ممکن است قبلاً راه‌اندازی شده باشد.
    set "PORT_CONFLICT=1"
) else (
    echo   [OK] پورت %BACKEND_PORT% آزاد است
)

REM بررسی پورت Frontend
netstat -ano | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo   [هشدار] پورت %FRONTEND_PORT% در حال استفاده است
    echo   Frontend ممکن است قبلاً راه‌اندازی شده باشد.
    set "PORT_CONFLICT=1"
) else (
    echo   [OK] پورت %FRONTEND_PORT% آزاد است
)

echo.

REM ============================================================
REM مرحله 4: راه‌اندازی سرویس‌ها
REM ============================================================
echo [4/5] راه‌اندازی سرویس‌ها...
echo.

REM بررسی اینکه آیا سرویس‌ها قبلاً در حال اجرا هستند
if "%PORT_CONFLICT%"=="1" (
    echo   [اطلاع] برخی سرویس‌ها ممکن است قبلاً در حال اجرا باشند.
    echo   آیا می‌خواهید دوباره راه‌اندازی کنید؟ (Y/N)
    set /p RESTART_CHOICE=
    if /i not "%RESTART_CHOICE%"=="Y" (
        echo   راه‌اندازی لغو شد.
        echo.
        echo   برای دسترسی به داشبورد:
        echo   - Admin Dashboard: http://localhost:%FRONTEND_PORT%
        echo   - Disease Tracking: http://localhost:%FRONTEND_PORT%/disease-tracking
        echo   - API Docs: http://localhost:%BACKEND_PORT%/api/docs
        echo.
        pause
        exit /b 0
    )
)

REM راه‌اندازی Backend
echo   راه‌اندازی Backend...
if not exist "%BACKEND_DIR%\app\main.py" (
    echo   [خطا] فایل main.py در backend یافت نشد!
    pause
    exit /b 1
)

start "NeuroPredict-AI Backend" cmd /k "cd /d %BACKEND_DIR% && echo Starting Backend Server... && python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

REM صبر برای راه‌اندازی Backend
echo   منتظر راه‌اندازی Backend...
timeout /t 5 /nobreak >nul

REM بررسی اینکه Backend راه‌اندازی شد
netstat -ano | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   [هشدار] Backend ممکن است هنوز در حال راه‌اندازی باشد...
) else (
    echo   [OK] Backend راه‌اندازی شد
)

echo.

REM راه‌اندازی Frontend
echo   راه‌اندازی Frontend...
if not exist "%FRONTEND_DIR%\package.json" (
    echo   [خطا] فایل package.json در admin-dashboard یافت نشد!
    pause
    exit /b 1
)

REM بررسی node_modules
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   [هشدار] node_modules یافت نشد!
    echo   در حال نصب dependencies...
    start "Installing Dependencies" cmd /k "cd /d %FRONTEND_DIR% && npm install && pause"
    echo   منتظر نصب dependencies...
    timeout /t 10 /nobreak >nul
    echo   لطفاً صبر کنید تا نصب کامل شود، سپس دوباره این فایل را اجرا کنید.
    pause
    exit /b 0
)

start "NeuroPredict-AI Frontend" cmd /k "cd /d %FRONTEND_DIR% && echo Starting Frontend Server... && npm run dev"

REM صبر برای راه‌اندازی Frontend
echo   منتظر راه‌اندازی Frontend...
timeout /t 5 /nobreak >nul

REM بررسی اینکه Frontend راه‌اندازی شد
netstat -ano | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   [هشدار] Frontend ممکن است هنوز در حال راه‌اندازی باشد...
) else (
    echo   [OK] Frontend راه‌اندازی شد
)

echo.

REM ============================================================
REM مرحله 5: باز کردن مرورگر و نمایش اطلاعات
REM ============================================================
echo [5/5] باز کردن مرورگر...
echo.

REM صبر بیشتر برای اطمینان از راه‌اندازی کامل
timeout /t 3 /nobreak >nul

REM باز کردن مرورگر
start http://localhost:%FRONTEND_PORT%
timeout /t 1 /nobreak >nul
start http://localhost:%FRONTEND_PORT%/disease-tracking

REM نمایش خلاصه
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║   ✅ داشبورد با موفقیت راه‌اندازی شد!                  ║
echo ║   ✅ Dashboard Started Successfully!                     ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🌐 دسترسی به داشبوردها:
echo    - Admin Dashboard:  http://localhost:%FRONTEND_PORT%
echo    - Disease Tracking: http://localhost:%FRONTEND_PORT%/disease-tracking
echo    - System Overview:  http://localhost:%FRONTEND_PORT%/
echo    - API Documentation: http://localhost:%BACKEND_PORT%/api/docs
echo    - Health Check:     http://localhost:%BACKEND_PORT%/health
echo.
echo 📊 اطلاعات سرویس‌ها:
echo    - Backend Port:  %BACKEND_PORT%
echo    - Frontend Port: %FRONTEND_PORT%
echo    - Project Root:  %PROJECT_ROOT%
echo.
echo 📌 نکات مهم:
echo    - برای توقف سرویس‌ها، پنجره‌های Command Prompt را ببندید
echo    - اگر خطایی دیدید، پنجره‌های Backend و Frontend را بررسی کنید
echo    - برای راه‌اندازی مجدد، این فایل را دوباره اجرا کنید
echo.
echo ════════════════════════════════════════════════════════
echo   در حال اجرا... (برای بستن این پنجره Enter را فشار دهید)
echo ════════════════════════════════════════════════════════
echo.
pause

exit /b 0

