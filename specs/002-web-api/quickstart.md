# Quickstart Guide: Task API Backend

## Prerequisites
- Python 3.9+
- Poetry (for dependency management) or pip
- Access to Neon PostgreSQL database

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd <repository-directory>
git checkout 002-web-api-evolution
```

### 2. Navigate to backend directory
```bash
cd backend
```

### 3. Install dependencies

Using Poetry:
```bash
poetry install
poetry shell
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql+asyncpg://username:password@neon-host.region.neon.tech/dbname
```

### 5. Run the application
```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

## Usage Examples

### Create a task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample task", "description": "This is a sample task"}'
```

### List all tasks
```bash
curl http://localhost:8000/tasks
```

### Get a specific task
```bash
curl http://localhost:8000/tasks/{task-id}
```

### Update a task
```bash
curl -X PATCH http://localhost:8000/tasks/{task-id} \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

### Delete a task
```bash
curl -X DELETE http://localhost:8000/tasks/{task-id}
```

## Running Tests
```bash
pytest tests/
```