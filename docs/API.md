# API Documentation - NeuroPredict-AI

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require Bearer token authentication.

### Login

**POST** `/auth/login`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Register

**POST** `/auth/register`

```json
{
  "email": "doctor@example.com",
  "username": "doctor1",
  "password": "secure_password",
  "full_name": "Dr. John Doe",
  "role": "doctor",
  "license_number": "MD123456",
  "department": "Neurology",
  "institution": "Memorial Hospital"
}
```

## Patients

### Create Patient

**POST** `/patients`

```json
{
  "patient_id": "P00001",
  "first_name": "John",
  "last_name": "Smith",
  "date_of_birth": "1950-01-15",
  "gender": "male",
  "email": "john.smith@email.com",
  "phone": "+1234567890",
  "education_years": 16
}
```

### Get All Patients

**GET** `/patients?skip=0&limit=100&search=john`

### Get Patient by ID

**GET** `/patients/{patient_id}`

### Update Patient

**PUT** `/patients/{patient_id}`

### Delete Patient

**DELETE** `/patients/{patient_id}`

## Predictions

### Create Prediction

**POST** `/predictions`

```json
{
  "patient_id": 1,
  "disease_type": "both"
}
```

Response:
```json
{
  "id": 1,
  "patient_id": 1,
  "disease_type": "both",
  "alzheimer_prediction": {
    "risk_score": 0.72,
    "risk_level": "high",
    "confidence": 0.85
  },
  "parkinson_prediction": {
    "risk_score": 0.34,
    "risk_level": "medium",
    "confidence": 0.78
  },
  "recommendations": "⚠️ High Alzheimer's risk detected...",
  "feature_importance": {
    "hippocampal_volume": 0.23,
    "mmse_score": 0.18,
    "age": 0.15
  },
  "created_at": "2024-11-03T10:30:00",
  "is_reviewed": false
}
```

### Get All Predictions

**GET** `/predictions?patient_id=1&skip=0&limit=100`

### Get Prediction by ID

**GET** `/predictions/{prediction_id}`

### Review Prediction

**POST** `/predictions/{prediction_id}/review`

```json
{
  "review_notes": "Reviewed and approved",
  "approved": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "User does not have required role: doctor"
}
```

### 404 Not Found
```json
{
  "detail": "Patient with ID 123 not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

## Rate Limiting

Currently no rate limiting is enforced in development.

In production:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

## Interactive Documentation

Visit the interactive API documentation:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

