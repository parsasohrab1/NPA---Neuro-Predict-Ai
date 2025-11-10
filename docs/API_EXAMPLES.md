# 📡 NeuroPredict-AI API Examples

This document provides practical examples for using the NeuroPredict-AI API.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Patient Management

### Create Patient

```bash
curl -X POST "http://localhost:8000/api/v1/patients" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1950-01-15",
    "gender": "male",
    "email": "john.doe@example.com",
    "phone": "+1234567890"
  }'
```

### Get All Patients

```bash
curl -X GET "http://localhost:8000/api/v1/patients?skip=0&limit=100" \
  -H "Authorization: Bearer <token>"
```

### Get Patient by ID

```bash
curl -X GET "http://localhost:8000/api/v1/patients/1" \
  -H "Authorization: Bearer <token>"
```

### Get Patient Medical Records

```bash
curl -X GET "http://localhost:8000/api/v1/patients/1/medical-records" \
  -H "Authorization: Bearer <token>"
```

---

## Predictions

### Create Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "disease_type": "both"
  }'
```

Response:
```json
{
  "id": 1,
  "patient_id": 1,
  "alzheimer_prediction": {
    "risk_score": 0.75,
    "risk_level": "high",
    "confidence": 0.89
  },
  "parkinson_prediction": {
    "risk_score": 0.32,
    "risk_level": "low",
    "confidence": 0.85
  },
  "feature_importance": {
    "mmse_score": 0.25,
    "amyloid_beta": 0.20,
    "hippocampal_volume": 0.15
  },
  "recommendations": "Patient shows elevated risk...",
  "created_at": "2024-11-15T10:30:00Z"
}
```

### Get All Predictions

```bash
curl -X GET "http://localhost:8000/api/v1/predictions?patient_id=1" \
  -H "Authorization: Bearer <token>"
```

### Get Prediction by ID

```bash
curl -X GET "http://localhost:8000/api/v1/predictions/1" \
  -H "Authorization: Bearer <token>"
```

### Get Prediction Imaging Studies

```bash
curl -X GET "http://localhost:8000/api/v1/predictions/1/imaging-studies" \
  -H "Authorization: Bearer <token>"
```

---

## Imaging

### Upload DICOM File

```bash
curl -X POST "http://localhost:8000/api/v1/imaging/dicom" \
  -H "Authorization: Bearer <token>" \
  -F "patient_id=1" \
  -F "file=@/path/to/image.dcm"
```

Response:
```json
{
  "imaging_study_id": 1,
  "study_id": "1.2.840.113619.2.55.3.123456",
  "medical_record_id": 1,
  "metadata": {
    "modality": "MR",
    "study_date": "2024-11-15",
    "study_description": "Brain MRI"
  }
}
```

### Get Study Preview

```bash
curl -X GET "http://localhost:8000/api/v1/imaging/studies/1/preview?slice_index=0" \
  -H "Authorization: Bearer <token>" \
  --output preview.png
```

### Get Study Slices Info

```bash
curl -X GET "http://localhost:8000/api/v1/imaging/studies/1/slices" \
  -H "Authorization: Bearer <token>"
```

### Get Specific Slice

```bash
curl -X GET "http://localhost:8000/api/v1/imaging/studies/1/slice/5" \
  -H "Authorization: Bearer <token>" \
  --output slice_5.png
```

---

## Longitudinal Tracking

### Get Episodes

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes?patient_id=1" \
  -H "Authorization: Bearer <token>"
```

### Get Episode Timeline

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes/1/timeline" \
  -H "Authorization: Bearer <token>"
```

### Get Metric Trend

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes/1/trends?metric_key=mmse" \
  -H "Authorization: Bearer <token>"
```

### Get Personal Baseline

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes/1/baseline?metric_key=mmse&baseline_window_days=90" \
  -H "Authorization: Bearer <token>"
```

### Get Future Prediction

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes/1/prediction?metric_key=mmse&days_ahead=30" \
  -H "Authorization: Bearer <token>"
```

### Get Combined Alerts

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/episodes/1/combined-alerts" \
  -H "Authorization: Bearer <token>"
```

---

## Reports

### Generate Summary Report

```bash
curl -X POST "http://localhost:8000/api/v1/longitudinal/reports" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": 1,
    "report_type": "summary",
    "format": "pdf",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-11-15T00:00:00Z"
  }'
```

### Generate Cohort Report

```bash
curl -X POST "http://localhost:8000/api/v1/longitudinal/reports" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": 1,
    "report_type": "cohort_patient_vs_average",
    "format": "excel",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-11-15T00:00:00Z",
    "cohortPatientIds": "P001,P002,P003",
    "cohortGender": "male",
    "cohortAgeMin": 60,
    "cohortAgeMax": 80
  }'
```

### Download Report

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/reports/1/download?variant=pdf" \
  -H "Authorization: Bearer <token>" \
  --output report.pdf
```

### Get Report Schedules

```bash
curl -X GET "http://localhost:8000/api/v1/longitudinal/reports/schedules?episode_id=1" \
  -H "Authorization: Bearer <token>"
```

### Create Report Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/longitudinal/reports/schedules" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": 1,
    "report_type": "summary",
    "format": "pdf",
    "schedule_type": "weekly",
    "day_of_week": 1,
    "distribution_method": "email",
    "distribution_config": {
      "email": "doctor@example.com"
    },
    "sla_hours": 24
  }'
```

---

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@example.com", "password": "admin123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create patient
patient_data = {
    "patient_id": "P001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1950-01-15",
    "gender": "male"
}
response = requests.post(
    f"{BASE_URL}/patients",
    json=patient_data,
    headers=headers
)
patient = response.json()

# Create prediction
prediction_data = {
    "patient_id": patient["id"],
    "disease_type": "both"
}
response = requests.post(
    f"{BASE_URL}/predictions",
    json=prediction_data,
    headers=headers
)
prediction = response.json()
print(f"Alzheimer Risk: {prediction['alzheimer_prediction']['risk_score']}")
```

### Using httpx (async)

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get predictions
        response = await client.get(
            f"{BASE_URL}/predictions",
            headers=headers
        )
        predictions = response.json()
        print(f"Found {len(predictions)} predictions")

asyncio.run(main())
```

---

## JavaScript/TypeScript Examples

### Using fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
async function login(email, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.access_token;
}

// Get predictions
async function getPredictions(token, patientId) {
  const url = patientId 
    ? `${BASE_URL}/predictions?patient_id=${patientId}`
    : `${BASE_URL}/predictions`;
    
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// Usage
const token = await login('admin@example.com', 'admin123');
const predictions = await getPredictions(token, 1);
console.log(predictions);
```

### Using axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Create prediction
async function createPrediction(patientId) {
  const response = await api.post('/predictions', {
    patient_id: patientId,
    disease_type: 'both'
  });
  return response.data;
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

Example error handling:
```python
import requests

try:
    response = requests.get(f"{BASE_URL}/patients/999", headers=headers)
    response.raise_for_status()
    patient = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Patient not found")
    else:
        print(f"Error: {e.response.json()['detail']}")
```

---

## Rate Limiting

API requests are rate-limited:
- **Authenticated users**: 100 requests/minute
- **Unauthenticated**: 10 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637000000
```

---

*Last Updated: November 2024*

