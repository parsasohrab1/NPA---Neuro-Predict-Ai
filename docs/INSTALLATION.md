# Installation Guide - NeuroPredict-AI

## Prerequisites

- Docker & Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+

## Quick Start with Docker (Recommended)

### 1. Clone the repository

```bash
git clone <repository-url>
cd NPA---Neuro-Predict-Ai
```

### 2. Create environment file

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and update the SECRET_KEY and other settings as needed.

### 3. Start all services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- Backend API on port 8000
- Frontend application on port 3000
- Admin dashboard on port 3001

### 4. Initialize the database

```bash
docker-compose exec backend python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

### 5. Create admin user (optional)

```bash
docker-compose exec backend python scripts/create_admin.py
```

### 6. Access the application

- Frontend: http://localhost:3000
- Admin Dashboard: http://localhost:3001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Manual Installation (Without Docker)

### Backend Setup

1. **Create virtual environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL**

```bash
createdb neuropredict_db
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database**

```bash
python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Run backend**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**

```bash
cd frontend
npm install
```

2. **Run development server**

```bash
npm run dev
```

## Default Credentials

For development/testing purposes:

- Username: `admin`
- Password: `admin123`

**⚠️ Important:** Change these credentials in production!

## Data Generation

To generate synthetic training data:

```bash
cd backend
python ../data_generator_script.py
```

This will create synthetic medical data for model training.

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify firewall settings

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

Change ports in docker-compose.yml or run:

```bash
docker-compose down
# Edit ports in docker-compose.yml
docker-compose up -d
```

## Production Deployment

For production deployment:

1. Update SECRET_KEY in .env
2. Set DEBUG=False
3. Configure CORS_ORIGINS
4. Use production database
5. Enable HTTPS/SSL
6. Configure proper backup strategies
7. Setup monitoring and logging

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed production deployment guide.

