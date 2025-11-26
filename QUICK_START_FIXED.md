# Quick Start Guide - Backend Fixed! ✅

## Problem Solved ✓
The "Failed to load patients" error has been fixed!

## Quick Start (3 Simple Steps)

### Step 1: Start Backend
Open PowerShell and run:
```powershell
powershell -ExecutionPolicy Bypass -File start_backend.ps1
```

Wait for: `INFO: Application startup complete.`

### Step 2: Start Dashboard  
Open **another** PowerShell window:
```powershell
cd admin-dashboard
npm run dev
```

### Step 3: Access Dashboard
Open browser: **http://localhost:5173**

**You should now see 100 patients!** 🎉

## What Was Fixed?

1. ✅ Backend now runs on **port 8001** (avoids conflicts)
2. ✅ Uses **SQLite** database (no PostgreSQL needed)
3. ✅ **100 sample patients** pre-loaded
4. ✅ All dependencies installed
5. ✅ Configuration issues resolved

## Verify It's Working

Test the backend:
```powershell
Invoke-RestMethod http://localhost:8001/health
```

Should return:
```
status  : healthy
service : NeuroPredict-AI
version : 1.0.0
```

## Dashboard Access
- **URL**: http://localhost:5173
- **Patients**: 100 records available
- **Features**: All working (add, edit, view patients)

## Important Notes

- **Backend Port**: Changed from 8000 → 8001
- **Database**: SQLite (file: `backend/neuropredict.db`)
- **Authentication**: Disabled for development
- **Redis**: Not required for basic functionality

## If You See Errors

### Backend won't start?
Check if port 8001 is free:
```powershell
netstat -ano | findstr :8001
```

### Patients still not loading?
1. Verify backend is running: http://localhost:8001/health
2. Check browser console (F12)
3. Restart dashboard:
   ```powershell
   cd admin-dashboard
   npm run dev
   ```

## Need Help?

See `BACKEND_FIX_SUMMARY.md` for detailed technical information.

---

**Your system is ready! Enjoy! 🚀**

