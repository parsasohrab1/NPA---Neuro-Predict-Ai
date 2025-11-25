# Troubleshooting Network Errors

## Common Error: "Failed to load patients - Network Error"

### Symptoms
- Frontend shows "Network Error" when trying to fetch data
- Error message: "Please check your connection and try again"
- Console shows CORS errors or connection refused

### Root Causes and Solutions

#### 1. Protocol Mismatch (HTTP vs HTTPS)

**Problem**: Frontend is configured for HTTPS but backend is running on HTTP (or vice versa).

**Solution**:
- Check `admin-dashboard/src/config/api.ts` - should use `http://localhost:8000` for local development
- Backend runs on HTTP by default (port 8000)
- Both should match: either both HTTP or both HTTPS

**How to fix**:
```typescript
// admin-dashboard/src/config/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

#### 2. Backend Not Running

**Check if backend is running**:
```powershell
# Windows
netstat -ano | findstr ":8000"

# Should show:
# TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       [PID]
```

**Solution**: Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Not Running

**Check if frontend is running**:
```powershell
netstat -ano | findstr ":5173"
```

**Solution**: Start the frontend:
```bash
cd admin-dashboard
npm run dev
```

#### 4. CORS Configuration Issue

**Problem**: Backend doesn't allow requests from the frontend origin.

**Check**: `backend/app/core/config.py`
```python
CORS_ORIGINS: list = [
    "http://localhost:5173",     # Frontend HTTP
    "https://localhost:5173",    # Frontend HTTPS
    "http://127.0.0.1:5173",
]
```

**Restart backend after changing CORS settings!**

#### 5. Authentication Issues

**Problem**: API requires authentication but no token is present.

**Solution**:
1. Create an admin user (see `docs/DISEASE_TRACKING_FIX.md`)
2. Login through the frontend to get a token
3. Or temporarily disable auth for testing (not recommended for production)

**Check token**:
```javascript
// In browser console
localStorage.getItem('auth_token')
sessionStorage.getItem('auth_token')
```

#### 6. Port Already in Use

**Problem**: Another process is using port 8000 or 5173.

**Find process**:
```powershell
# Windows
netstat -ano | findstr ":8000"
# Note the PID and kill it:
taskkill /PID [PID] /F
```

**Solution**: Either kill the process or use a different port.

#### 7. Firewall Blocking

**Problem**: Windows Firewall is blocking local connections.

**Solution**:
1. Allow Python/Node through Windows Firewall
2. Or temporarily disable firewall for testing (not recommended)

### Quick Diagnostic Checklist

Run these checks in order:

1. ✅ **Backend is running**
   ```powershell
   netstat -ano | findstr ":8000"
   ```

2. ✅ **Frontend is running**
   ```powershell
   netstat -ano | findstr ":5173"
   ```

3. ✅ **Backend is accessible**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/api/v1/disease-tracking/health" -UseBasicParsing
   ```
   Should return: `{"status":"ok","message":"Disease tracking API is running"}`

4. ✅ **Protocol matches**
   - Frontend config: `admin-dashboard/src/config/api.ts`
   - Should be `http://` not `https://` for local dev

5. ✅ **CORS is configured**
   - Check `backend/app/core/config.py`
   - Includes `http://localhost:5173`

6. ✅ **Environment variables loaded**
   ```bash
   cd backend
   cat .env  # Check SECRET_KEY is set
   ```

### Testing the Connection

**Test backend health endpoint** (no auth required):
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/disease-tracking/health" -UseBasicParsing
```

**Test with authentication**:
```bash
# First login (replace with your credentials)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Use the returned token
curl -X GET http://localhost:8000/api/v1/disease-tracking/patients-summary \
  -H "Authorization: Bearer [YOUR_TOKEN]"
```

### Environment-Specific Configuration

#### Development (Local)
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- No SSL/TLS required
- CORS: Allow localhost origins

#### Production
- Backend: `https://your-domain.com`
- Frontend: `https://your-domain.com`
- SSL/TLS required
- CORS: Specific domain only
- Environment variables set properly

### Common Console Errors and Fixes

#### "CORS policy: No 'Access-Control-Allow-Origin' header"
**Fix**: Add frontend URL to `CORS_ORIGINS` in backend config and restart backend.

#### "net::ERR_CONNECTION_REFUSED"
**Fix**: Backend is not running. Start it with `uvicorn app.main:app --reload`.

#### "Network Error" with no details
**Fix**: Check protocol (HTTP vs HTTPS) matches between frontend and backend.

#### "401 Unauthorized"
**Fix**: Login required. Create user and login, or check token is saved.

#### "403 Forbidden"
**Fix**: User doesn't have required role. Check user permissions.

### Still Having Issues?

1. **Clear browser cache and localStorage**
   ```javascript
   // In browser console
   localStorage.clear()
   sessionStorage.clear()
   ```

2. **Check backend logs** for error messages

3. **Check browser console** (F12) for detailed error messages

4. **Restart both frontend and backend**

5. **Check `.env` file** exists and has correct values

6. **Verify database is running** (PostgreSQL on port 5432)

### Quick Fix Script

Save this as `fix_network_error.ps1`:
```powershell
# Quick fix for network errors
Write-Host "Checking backend..."
$backend = netstat -ano | findstr ":8000"
if ($backend) {
    Write-Host "✓ Backend is running" -ForegroundColor Green
} else {
    Write-Host "✗ Backend is NOT running" -ForegroundColor Red
    Write-Host "Start with: cd backend; uvicorn app.main:app --reload"
}

Write-Host "`nChecking frontend..."
$frontend = netstat -ano | findstr ":5173"
if ($frontend) {
    Write-Host "✓ Frontend is running" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend is NOT running" -ForegroundColor Red
    Write-Host "Start with: cd admin-dashboard; npm run dev"
}

Write-Host "`nTesting backend health..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/disease-tracking/health" -UseBasicParsing
    Write-Host "✓ Backend is responding" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "✗ Backend is not responding" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
```

Run with: `.\fix_network_error.ps1`

