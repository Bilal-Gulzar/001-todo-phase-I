# Local Development Setup (No Docker)

This guide explains how to run the Todo App locally without Docker or Kubernetes.

## Prerequisites

1. **Python 3.12+** - [Download](https://www.python.org/downloads/)
2. **Node.js 20+** - [Download](https://nodejs.org/)
3. **PostgreSQL** - Already using Neon cloud database (configured in backend/.env)

## Quick Start

### Option 1: Start Everything at Once

Simply double-click `start-all.bat` in the project root. This will open two terminal windows:
- Backend server on http://localhost:8000
- Frontend dev server on http://localhost:3000

### Option 2: Start Services Individually

#### Start Backend Only
```bash
# Double-click start-backend.bat
# OR run manually:
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Frontend Only
```bash
# Double-click start-frontend.bat
# OR run manually:
cd frontend
npm install
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

## Configuration

### Backend (.env)
Located at `backend/.env`:
- `DATABASE_URL` - PostgreSQL connection (Neon cloud)
- `GEMINI_API_KEY` - For AI chatbot features
- `GROQ_API_KEY` - Alternative AI provider

### Frontend (.env)
Located at `frontend/.env`:
- `VITE_API_URL=http://localhost:8000/api/v1` - Backend API endpoint

## Troubleshooting

### Backend won't start
- Verify Python is installed: `python --version`
- Check if port 8000 is available
- Ensure database connection in backend/.env is correct

### Frontend won't start
- Verify Node.js is installed: `node --version`
- Check if port 3000 is available
- Try deleting `node_modules` and running `npm install` again

### API connection errors
- Ensure backend is running before starting frontend
- Check that `VITE_API_URL` in frontend/.env points to `http://localhost:8000/api/v1`

## Development Notes

- Backend uses **FastAPI** with hot reload enabled
- Frontend uses **Vite** with hot module replacement (HMR)
- Database is hosted on **Neon** (cloud PostgreSQL)
- Changes to code will auto-reload in both services

## Removed Files

The following containerization files have been removed:
- `frontend/Dockerfile`
- `backend/Dockerfile`
- `docker-compose.yml`
- `k8s/` directory (all Kubernetes configs)
