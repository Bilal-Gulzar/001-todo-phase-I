# Evolution of Todo - Backend API

This is the backend API for the Evolution of Todo application, built with FastAPI and SQLModel.

## Features

- RESTful API for task management
- CRUD operations for tasks
- Database persistence with Neon PostgreSQL
- Type validation with Pydantic models
- Async support with FastAPI

## Endpoints

### Tasks API

All endpoints are prefixed with `/api/v1`

- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks (with optional filtering and pagination)
- `GET /tasks/{id}` - Get a specific task by ID
- `PATCH /tasks/{id}` - Update a specific task
- `DELETE /tasks/{id}` - Delete a specific task

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your database configuration:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@neon-host.region.neon.tech/dbname
   DEBUG=False
   DB_ECHO=False
   ```

3. Run the application:
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```

## Testing

Run the tests using pytest:
```bash
pytest tests/
```

## Data Model

### Task Entity

- `id` (UUID): Unique identifier for each task
- `title` (String): Title of the task (required, 1-100 characters)
- `description` (String): Optional description of the task (max 500 characters)
- `is_completed` (Boolean): Status indicating if the task is completed (default: false)
- `created_at` (DateTime): Timestamp when the task was created (auto-generated)

## Architecture

- `app/main.py`: Application entry point and routing
- `app/models/`: Data models using SQLModel
- `app/api/`: API route definitions
- `app/services/`: Business logic layer
- `app/database.py`: Database connection and initialization
- `app/config.py`: Configuration and environment variables
- `app/errors.py`: Custom error handling
- `tests/`: Test files