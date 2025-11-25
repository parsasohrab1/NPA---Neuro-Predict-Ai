# 🚨 Quick Fix - Login Problem

## The Problem
You're seeing: **"Failed to load patients - Network Error"**

This is because the API requires you to be logged in, but you haven't logged in yet.

## ⚡ FASTEST Solution (2 minutes)

### Step 1: Open Dashboard
Go to: `http://localhost:5173`

### Step 2: Open Browser DevTools
Press **F12** (or right-click anywhere → "Inspect")

### Step 3: Go to Console Tab
Click on the **Console** tab at the top

### Step 4: Copy & Paste This Code

**COPY THIS ENTIRE CODE BLOCK** and paste it into the console, then press Enter:

```javascript
// Complete login solution
(async function() {
  console.log('🔐 Starting automatic login...');
  
  // First, let's check if backend is accessible
  try {
    console.log('📡 Testing backend connection...');
    
    // Try to login with default admin credentials
    const loginResponse = await fetch('https://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        email: 'admin@neuropredict.ai',
        password: 'admin123'
      })
    });
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      
      if (loginData.access_token) {
        // Save the token
        localStorage.setItem('auth_token', loginData.access_token);
        
        console.log('✅ LOGIN SUCCESSFUL!');
        console.log('🎉 Token has been saved!');
        console.log('🔄 Refreshing page in 2 seconds...');
        
        setTimeout(() => {
          location.reload();
        }, 2000);
      } else {
        console.error('❌ No token in response:', loginData);
      }
    } else {
      const errorData = await loginResponse.json();
      console.error('❌ Login failed:', loginResponse.status, errorData);
      
      if (loginResponse.status === 401) {
        console.log('');
        console.log('💡 The admin user might not exist yet.');
        console.log('');
        console.log('📝 SOLUTION: Try creating the user first:');
        console.log('');
        console.log('Run this in a NEW browser tab:');
        console.log('https://localhost:8000/docs');
        console.log('');
        console.log('Then find POST /api/v1/auth/register and use:');
        console.log(JSON.stringify({
          email: 'admin@neuropredict.ai',
          username: 'admin',
          password: 'admin123',
          first_name: 'Admin',
          last_name: 'User'
        }, null, 2));
      }
    }
  } catch (error) {
    console.error('❌ Network Error:', error);
    console.log('');
    console.log('🔍 TROUBLESHOOTING:');
    console.log('1. Is backend running? Check: netstat -ano | findstr ":8000"');
    console.log('2. Can you access: https://localhost:8000/docs');
    console.log('3. SSL Certificate: Click "Advanced" → "Proceed to localhost"');
  }
})();
```

### Step 5: Wait for Success Message

You should see:
```
✅ LOGIN SUCCESSFUL!
🎉 Token has been saved!
🔄 Refreshing page in 2 seconds...
```

The page will refresh automatically and you'll be logged in!

---

## 🔧 If Login Failed (User Doesn't Exist)

If you see "Login failed: 401", the admin user doesn't exist yet.

### Create Admin User:

#### Option A: Using Swagger UI (Easiest)

1. Open a new browser tab
2. Go to: `https://localhost:8000/docs`
3. Accept the SSL certificate warning
4. Find **POST /api/v1/auth/register**
5. Click "Try it out"
6. Use this JSON:
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
8. Go back to dashboard and run the login code again

#### Option B: Browser Console (Alternative)

Paste this in console:

```javascript
// Create admin user
fetch('https://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
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
  console.log('📝 Now run the login code again from above!');
})
.catch(err => console.error('❌ Error:', err));
```

Then run the login code again (the big code block from Step 4).

---

## 📱 SSL Certificate Warning?

When you access `https://localhost:8000`:
1. You'll see a security warning (red screen)
2. Click **"Advanced"**
3. Click **"Proceed to localhost (unsafe)"**
4. This is normal for local development with self-signed certificates

---

## ✅ Verify You're Logged In

After the page refreshes, open console again and run:

```javascript
console.log('Auth Token:', localStorage.getItem('auth_token'));
```

If you see a long string (token), you're logged in! ✅

---

## 🎯 Now Try Again

After successful login:
1. Go to **Disease Tracking** page
2. Try clicking **"Load All Data"** again
3. It should work now! 🎉

---

## 🆘 Still Having Problems?

### Check Backend is Running:
```powershell
netstat -ano | findstr ":8000"
```
Should show LISTENING on port 8000.

### Check Frontend is Running:
```powershell
netstat -ano | findstr ":5173"
```
Should show LISTENING on port 5173.

### Clear Everything and Start Fresh:
```javascript
// In console
localStorage.clear();
sessionStorage.clear();
location.reload();
```

Then try the login code again.

---

## 📞 Quick Reference

**Default Credentials:**
- Email: `admin@neuropredict.ai`
- Password: `admin123`

**Backend URLs:**
- API: `https://localhost:8000`
- Swagger Docs: `https://localhost:8000/docs`
- Health Check: `https://localhost:8000/api/v1/disease-tracking/health`

**Frontend URL:**
- Dashboard: `http://localhost:5173`

---

**Just run the code from Step 4 in browser console and you'll be good to go!** 🚀

