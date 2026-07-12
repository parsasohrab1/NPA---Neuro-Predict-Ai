# 🚀 Getting Started with NeuroPredict-AI

## Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop installed
- 8GB RAM minimum
- 10GB free disk space

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd NPA---Neuro-Predict-Ai
```

### Step 2: Run Setup Script

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows (PowerShell):**
```powershell
.\setup.ps1
```

### Step 3: Access Application

| Service | Docker Compose URL | Local `npm run dev` URL |
|---------|-------------------|-------------------------|
| Clinician Frontend | http://localhost:3000 | http://localhost:3001 |
| Admin Dashboard | http://localhost:3001 | http://localhost:3000 |
| Backend API | http://localhost:8001 | http://localhost:8001 |
| API Docs | http://localhost:8001/api/docs | http://localhost:8001/api/docs |

Both frontends proxy `/api` to the backend, so you normally do not need to set `VITE_API_URL`.

### Step 4: Login

```
Username: admin
Password: admin123
```

## What's Next?

### 1. Create Your First Patient

1. Navigate to **Patients** section
2. Click **"+ Add Patient"**
3. Fill in patient information
4. Save

### 2. Add Medical Records

1. Open patient details
2. Add cognitive scores (MMSE, MoCA)
3. Input biomarker levels
4. Upload MRI images (optional)

### 3. Run Prediction

1. Click **"🔬 New Prediction"**
2. Select patient
3. Choose disease type
4. Click **"Run Prediction"**
5. View results with risk scores and recommendations

## Features Overview

### For Doctors 👨‍⚕️

- **Patient Management**: Complete patient records
- **AI Predictions**: Risk assessment for Alzheimer's & Parkinson's
- **Clinical Recommendations**: Evidence-based guidance
- **Medical History**: Track patient progress over time

### For Radiologists 🔬

- **Image Upload**: DICOM file support
- **Preprocessing**: Automated image quality assessment
- **Feature Extraction**: Volumetric analysis
- **Visualization**: Interactive image viewers

### For Administrators 🔧

- **User Management**: Create and manage users
- **System Monitoring**: Health checks and logs
- **Audit Trails**: Complete compliance logging
- **Configuration**: System settings management

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│  React App  │     │   FastAPI   │     │ PostgreSQL  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  AI Models  │
                    │   PyTorch   │
                    └─────────────┘
```

## Sample Workflow

1. **Patient Registration**
   ```
   Create patient → Add demographics → Save
   ```

2. **Data Collection**
   ```
   Upload MRI → Enter cognitive scores → Add biomarkers
   ```

3. **AI Analysis**
   ```
   Select patient → Run prediction → Get results
   ```

4. **Clinical Review**
   ```
   Review risk scores → Read recommendations → Make decision
   ```

## Common Tasks

### View All Predictions

```
Dashboard → Recent Predictions
```

### Search Patients

```
Patients → Search bar → Enter name/ID
```

### Review Prediction

```
Prediction Details → Review button → Add notes → Approve
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
./setup.sh
```

### Frontend Not Loading

```bash
# Rebuild frontend
cd frontend
npm install
npm run build
```

## Development Mode

### Backend Hot Reload

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## Configuration

### Environment Variables

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db

# Security - REQUIRED
# Generate a secure SECRET_KEY using:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
# Must be at least 32 characters long
SECRET_KEY=your-secure-random-secret-key-minimum-32-characters

# Environment Configuration
# Options: development, production, staging, test
# IMPORTANT: DEBUG=True is automatically blocked in production
ENVIRONMENT=development
DEBUG=False

# Features
ENABLE_AUDIT_LOG=true
MODEL_CONFIDENCE_THRESHOLD=0.75
```

### Customization

- **Logo**: Replace `frontend/public/logo.png`
- **Theme**: Edit `frontend/tailwind.config.js`
- **API Prefix**: Change in `backend/app/core/config.py`

## Data Management

### Generate Test Data

```bash
python data_generator_script.py
```

This creates:
- 100,000 normal controls
- 15,000 Alzheimer's patients
- 5,000 Parkinson's patients

### Backup Database

```bash
docker-compose exec postgres pg_dump -U postgres neuropredict_db > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U postgres neuropredict_db < backup.sql
```

## Security Best Practices

1. **Change Default Password** immediately after first login
2. **Use Strong Passwords** (min 12 characters)
3. **Enable HTTPS** in production
4. **Regular Backups** of database
5. **Update Dependencies** regularly
6. **Monitor Logs** for suspicious activity

## Performance Tips

- **Database**: Add indexes for frequently queried fields
- **Caching**: Enable Redis for faster response times
- **Images**: Use compressed formats when possible
- **Batch Processing**: Upload multiple images together

## Support & Resources

- **Documentation**: See `docs/` folder
- **API Reference**: http://localhost:8000/api/docs
- **Issues**: GitHub Issues
- **Email**: support@neuropredict-ai.com

## Next Steps

✅ You're ready to use NeuroPredict-AI!

Recommended reading:
- [Installation Guide](docs/INSTALLATION.md)
- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [SRS Document](README.md)

## License

Proprietary software for medical use. All rights reserved.

---

**Need Help?** Check the [documentation](docs/) or contact support.

