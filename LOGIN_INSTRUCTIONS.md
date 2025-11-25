# Dashboard Login Instructions

## Problem
You're seeing "Failed to load datasets: Network Error" because the API requires authentication.

## Quick Solution - Browser Console Login

### Step 1: Open Browser Console
1. Open the dashboard: `http://localhost:5173`
2. Press `F12` or right-click → "Inspect"
3. Go to "Console" tab

### Step 2: Create Admin User (First Time Only)

If you haven't created an admin user yet, you need backend access. Since we don't have .env file, let's use an alternative approach.

### Step 3: Manual Token Setup (Temporary Workaround)

For testing purposes, you can temporarily disable authentication or create a mock token. However, the **proper solution** is:

## Proper Solution

### Option 1: Create .env File

1. Create `backend/.env` file:
```bash
cd backend
```

2. Add this content to `.env`:
```env
# Security
SECRET_KEY=your-super-secret-key-min-32-chars-long-change-this-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/neuropredict_db

# Redis (optional for development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Environment
ENVIRONMENT=development
DEBUG=True
```

3. Generate a secure SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Replace `your-super-secret-key-min-32-chars-long-change-this-in-production` with the generated key.

### Option 2: Use Login API Directly

1. **First, restart backend** (after creating .env):
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. **Create admin user**:
```bash
cd backend
python scripts/create_admin.py
```

3. **Login through Frontend**:
   - Go to `http://localhost:5173`
   - If there's a login page, use:
     - Email: `admin@neuropredict.ai`
     - Password: `admin123`

### Option 3: Browser Console Login (If no login UI)

If the dashboard doesn't have a visible login form, use this in browser console:

```javascript
// Login API call
fetch('https://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'admin@neuropredict.ai',
    password: 'admin123'
  })
})
.then(res => res.json())
.then(data => {
  if (data.access_token) {
    localStorage.setItem('auth_token', data.access_token);
    console.log('✓ Login successful! Token saved.');
    console.log('Refresh the page to use the token.');
    location.reload();
  } else {
    console.error('Login failed:', data);
  }
})
.catch(err => console.error('Error:', err));
```

## Checking Backend Status

### Is backend running with HTTPS?
```powershell
netstat -ano | findstr ":8000"
```

Should show a LISTENING process.

### Can you access health endpoint?

In browser, go to:
```
https://localhost:8000/api/v1/disease-tracking/health
```

You might see a security warning (self-signed certificate) - that's OK, click "Advanced" → "Proceed".

## Common Issues

### 1. "Failed to load datasets: Network Error"
**Cause**: No authentication token
**Fix**: Login using one of the methods above

### 2. "401 Unauthorized"
**Cause**: Token missing or expired
**Fix**: Login again

### 3. "CORS Error"
**Cause**: Protocol mismatch or CORS not configured
**Fix**: 
- Ensure backend uses HTTPS (or both use HTTP)
- Check `backend/app/core/config.py` → `CORS_ORIGINS` includes your frontend URL

### 4. "Cannot read properties of undefined"
**Cause**: Token exists but is invalid
**Fix**: Clear storage and login again:
```javascript
localStorage.clear();
sessionStorage.clear();
location.reload();
```

## After Successful Login

Once logged in, you should be able to:
- ✓ View patients in Disease Tracking
- ✓ Load datasets
- ✓ Access 3D Analysis
- ✓ View all dashboard features

## Security Notes

**Default credentials (CHANGE IN PRODUCTION)**:
- Email: `admin@neuropredict.ai`
- Password: `admin123`
- Role: ADMIN

**For production**:
1. Use strong SECRET_KEY
2. Change default admin password
3. Use proper SSL certificates
4. Enable rate limiting
5. Configure proper CORS origins

