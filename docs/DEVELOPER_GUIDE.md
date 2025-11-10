# 👨‍💻 NeuroPredict-AI Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Setup & Installation](#setup--installation)
3. [Project Structure](#project-structure)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [API Development](#api-development)
7. [Database Schema](#database-schema)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Contributing](#contributing)

---

## Architecture Overview

NeuroPredict-AI follows a modern microservices architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│   (React)   │     │  (FastAPI)  │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  AI Models  │
                    │  (PyTorch)  │
                    └─────────────┘
```

### Technology Stack
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy (async)
- **Frontend**: React 18+, TypeScript, Vite
- **Database**: PostgreSQL 14+
- **AI/ML**: PyTorch, NumPy, SciPy
- **Image Processing**: PyDICOM, OpenCV, PIL

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd NPA

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Database setup
cd ../backend
alembic upgrade head

# Run development servers
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

---

## Project Structure

```
NPA/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/          # Configuration, security
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Test files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API clients
│   │   └── main.tsx
│   └── package.json
├── admin-dashboard/       # Admin interface
└── docs/                  # Documentation
```

---

## Backend Development

### Creating a New API Endpoint

1. **Define Schema** (`app/schemas/`):
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    field1: str
    field2: int

class MyResponse(BaseModel):
    id: int
    result: str
```

2. **Create Endpoint** (`app/api/`):
```python
from fastapi import APIRouter, Depends
from ..schemas import MyRequest, MyResponse
from ..core.security import get_current_user

router = APIRouter(prefix="/my-endpoint", tags=["MyTag"])

@router.post("/", response_model=MyResponse)
async def create_item(
    request: MyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation
    return MyResponse(id=1, result="success")
```

3. **Register Router** (`app/main.py`):
```python
from app.api import my_router
app.include_router(my_router)
```

### Database Models

```python
from sqlalchemy import Column, Integer, String
from ..db.session import Base

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

### Services

Business logic goes in `app/services/`:

```python
class MyService:
    async def process_data(self, data: dict) -> dict:
        # Business logic
        return processed_data

my_service = MyService()
```

---

## Frontend Development

### Creating a New Component

```typescript
// src/components/MyComponent.tsx
import React from 'react'

interface MyComponentProps {
  title: string
  onAction: () => void
}

export default function MyComponent({ title, onAction }: MyComponentProps) {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Action</button>
    </div>
  )
}
```

### API Integration

```typescript
// src/services/api.ts
export const myApi = {
  getData: async (id: number) => {
    const response = await axios.get(`${API_URL}/my-endpoint/${id}`)
    return response.data
  },
  
  createData: async (data: MyRequest) => {
    const response = await axios.post(`${API_URL}/my-endpoint`, data)
    return response.data
  }
}
```

### Using React Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { myApi } from '../services/api'

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['my-data', id],
    queryFn: () => myApi.getData(id)
  })
  
  const mutation = useMutation({
    mutationFn: myApi.createData,
    onSuccess: () => {
      // Handle success
    }
  })
  
  return <div>{/* Component JSX */}</div>
}
```

---

## API Development

### Authentication

All protected endpoints require JWT token:

```python
from ..core.security import get_current_user, require_role

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user.email}

@router.post("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_role("admin"))
):
    return {"message": "Admin access"}
```

### Error Handling

```python
from fastapi import HTTPException, status

@router.get("/item/{item_id}")
async def get_item(item_id: int):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```

### Async Database Operations

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_items(db: AsyncSession):
    result = await db.execute(select(Item))
    return result.scalars().all()

async def create_item(db: AsyncSession, data: dict):
    item = Item(**data)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
```

---

## Database Schema

### Key Models

- **User**: System users and authentication
- **Patient**: Patient demographic information
- **MedicalRecord**: Visit records and clinical data
- **Prediction**: AI prediction results
- **ImagingStudy**: DICOM studies and metadata
- **LongitudinalEpisode**: Tracking episodes
- **LongitudinalVisit**: Individual visits
- **LongitudinalMetric**: Metric values
- **LongitudinalReport**: Generated reports

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Testing

### Backend Tests

```python
# tests/test_my_endpoint.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    response = await client.post(
        "/api/v1/my-endpoint",
        json={"field1": "value", "field2": 123}
    )
    assert response.status_code == 201
    assert response.json()["result"] == "success"
```

Run tests:
```bash
pytest
pytest --cov=app --cov-report=html
```

### Frontend Tests

```typescript
// Component.test.tsx
import { render, screen } from '@testing-library/react'
import MyComponent from './MyComponent'

test('renders component', () => {
  render(<MyComponent title="Test" onAction={() => {}} />)
  expect(screen.getByText('Test')).toBeInTheDocument()
})
```

---

## Deployment

### Production Build

**Backend**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend**:
```bash
npm run build
# Serve with nginx or similar
```

### Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
SECRET_KEY=your-secret-key
DEBUG=False

# Frontend
VITE_API_URL=https://api.example.com
```

---

## Contributing

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Follow ESLint rules
- **Commits**: Use conventional commits

### Pull Request Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description
5. Address review comments

### Code Review Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No linter errors
- [ ] Security considerations addressed
- [ ] Performance optimized

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [API Documentation](API.md)
- [Architecture Documentation](ARCHITECTURE.md)

---

*Last Updated: November 2024*

