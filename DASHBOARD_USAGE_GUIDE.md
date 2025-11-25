# 📖 Dashboard Usage Guide

## 🚨 Common Error: "Failed to load 3D data" (or similar errors)

This error means **you need to login first**!

---

## ✅ Step-by-Step Solution

### Step 1: Open the Dashboard
Go to: `http://localhost:5173`

You should automatically be redirected to the **Login page**.

### Step 2: Login
Use the default credentials:

```
📧 Email:    admin@neuropredict.ai
🔑 Password: admin123
```

These credentials are shown on the login page itself.

Click **"Sign in"**

### Step 3: Access Features
After login, you can access all dashboard features:
- ✅ Disease Tracking
- ✅ Data Monitoring  
- ✅ 3D Analysis
- ✅ Reports
- ✅ Longitudinal Tracking
- ✅ And more...

---

## ⚠️ If Login Fails

### Error: "Invalid email or password" or "User not found"

The admin user doesn't exist yet. **Create it first:**

#### Method 1: Using Swagger UI (Recommended)

1. Open new browser tab
2. Go to: `https://localhost:8000/docs`
3. Accept SSL warning ("Advanced" → "Proceed to localhost")
4. Find: **POST /api/v1/auth/register**
5. Click "Try it out"
6. Paste this JSON:

```json
{
  "email": "admin@neuropredict.ai",
  "username": "admin",
  "password": "admin123",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin"
}
```

7. Click "Execute"
8. Go back to login page and try again!

#### Method 2: Browser Console

1. Open dashboard: `http://localhost:5173`
2. Press **F12** (DevTools)
3. Go to **Console** tab
4. Paste this code:

```javascript
fetch('https://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@neuropredict.ai',
    username: 'admin',
    password: 'admin123',
    first_name: 'Admin',
    last_name: 'User',
    role: 'admin'
  })
})
.then(res => res.json())
.then(data => {
  console.log('✅ User created!', data);
  alert('User created! Now you can login.');
})
.catch(err => console.error('❌ Error:', err));
```

5. Press Enter
6. Try logging in again!

---

## 📊 Dashboard Features Overview

### 1. System Overview
- System health metrics
- Active users
- Recent activity
- Quick stats

### 2. Disease Tracking
- View all patients
- Add new patients
- Add medical data
- Load datasets (synthetic & real data)
- Patient search

### 3. Data Monitoring  
- Cognitive tests monitoring
- Biomarker levels
- Imaging data
- Motor function tests
- Genetic markers
- Real-time alerts

### 4. 3D Analysis ⭐
- **3D Scatter Plot**: Explore patient data in 3D space
- **Brain Surface**: Visualize brain regions
- **Correlation Matrix**: Feature correlations in 3D
- **Feature Space**: PCA-based disease clustering
- **Quality Control** 🆕: Compare imaging pipeline outputs
  - FreeSurfer (segmentation)
  - LPA (lesion analysis)
  - TRACULA (tractography)

### 5. Reports
- Generate patient reports
- View historical reports
- Export capabilities
- Load sample data

### 6. Longitudinal Tracking
- Track patient progress over time
- Episodes and visits
- Metrics trends
- Alerts and schedules

### 7. Users Management
- View all users
- Create/edit/delete users
- Role assignment

### 8. Models
- AI model registry
- Model versions
- Performance metrics
- Activate/deactivate models

### 9. Settings
- System configuration
- Backup settings
- Security settings

---

## 🎯 Common Workflows

### Workflow 1: Add New Patient & Data

1. Login to dashboard
2. Go to **Disease Tracking**
3. Click **"Add Patient"** button
4. Fill in patient information
5. Click **"Add Data"** to add medical records
6. View patient in the list

### Workflow 2: Load Sample Data

1. Login to dashboard
2. Go to **Disease Tracking**
3. Click **"Load All Data"** button
4. Confirm the action
5. Wait for data to load (~200 patients)
6. Explore the data!

### Workflow 3: 3D Visualization

1. Login to dashboard
2. Go to **3D Analysis**
3. Select analysis type:
   - 3D Scatter
   - Brain Surface
   - Correlation
   - Feature Space
   - Quality Control
4. Choose features for axes (X, Y, Z)
5. Apply disease filter
6. Interact with the 3D visualization:
   - **Rotate**: Click and drag
   - **Zoom**: Scroll
   - **Pan**: Right-click and drag
   - **Reset**: Double-click

### Workflow 4: Quality Control Review

1. Login to dashboard
2. Go to **3D Analysis**
3. Select **"Quality Control"**
4. View Grid or Detailed view
5. Compare Acceptable vs Discarded results
6. Check quality metrics for each pipeline:
   - FreeSurfer: Segmentation quality
   - LPA: Lesion detection
   - TRACULA: Tractography quality

---

## 🔧 Troubleshooting

### Issue: "Failed to load patients"
**Solution**: Login first! All API endpoints require authentication.

### Issue: "Failed to load 3D data"
**Solution**: Login first! The endpoint requires authentication.

### Issue: "Failed to load datasets"
**Solution**: Login first! Also, make sure you have admin role.

### Issue: "Network Error"
**Solutions**:
1. Check backend is running: `netstat -ano | findstr ":8000"`
2. Check frontend is running: `netstat -ano | findstr ":5173"`
3. Verify protocol: frontend uses HTTP, backend uses HTTPS
4. Check CORS settings in backend

### Issue: Page keeps redirecting to login
**Solution**: Your token might be expired or invalid.
```javascript
// Clear tokens in browser console
localStorage.clear();
sessionStorage.clear();
location.reload();
```
Then login again.

### Issue: "403 Forbidden"
**Solution**: Your user role doesn't have permission.
- Some endpoints require `doctor` role
- Some require `admin` role
- Check your user role in the header

---

## 🔐 Security Notes

### Default Credentials (CHANGE IN PRODUCTION!)
```
Email:    admin@neuropredict.ai
Password: admin123
Role:     admin
```

### Important for Production:
1. Change default admin password
2. Use strong SECRET_KEY in backend/.env
3. Enable proper SSL certificates
4. Configure specific CORS origins
5. Enable rate limiting
6. Regular security audits

---

## 📱 Logout

To logout:
1. Look at the **top-right corner** of dashboard
2. Click the **"Logout"** button
3. You'll be redirected to login page
4. Token is removed from localStorage

---

## 🆘 Still Having Issues?

### Check System Status:

**Backend (API):**
```powershell
netstat -ano | findstr ":8000"
# Should show LISTENING
```

Access: `https://localhost:8000/docs`

**Frontend (Dashboard):**
```powershell
netstat -ano | findstr ":5173"
# Should show LISTENING
```

Access: `http://localhost:5173`

### Check Authentication:

Open browser console (F12) and run:
```javascript
console.log('Token:', localStorage.getItem('auth_token'));
```

If no token, you need to login!

### Reset Everything:

```javascript
// In browser console
localStorage.clear();
sessionStorage.clear();
location.reload();
```

Then login again fresh.

---

## 📚 Additional Resources

- **`LOGIN_INSTRUCTIONS.md`** - Detailed login guide
- **`QUICK_FIX_LOGIN.md`** - Fast console-based login
- **`TROUBLESHOOTING_NETWORK_ERRORS.md`** - Network issues
- **`docs/QUALITY_CONTROL_3D_ANALYSIS.md`** - 3D QC feature guide

---

## 💡 Tips

1. **Always login first** before using any feature
2. **Use Swagger UI** (`/docs`) for API testing
3. **Check browser console** (F12) for detailed errors
4. **Load sample data** to quickly populate the system
5. **Use logout button** to properly clear session

---

**Happy exploring! 🚀**

For any persistent issues, check the detailed error message in the browser console (F12 → Console tab).

