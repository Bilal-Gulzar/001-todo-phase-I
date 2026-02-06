# Phase 2 Web API Specification: Task Management Backend

## Overview
This specification defines the backend API for managing tasks in the Todo application. The API will be built using FastAPI and will persist data using SQLModel with Neon PostgreSQL database.

## Data Model

### Task Entity
The primary entity for this API is the Task, which represents a single task item with the following attributes:

- `id`: UUID (Primary Key) - Unique identifier for each task
- `title`: String - Title of the task (required, max length: 100)
- `description`: String - Optional description of the task (max length: 500)
- `is_completed`: Boolean - Status indicating if the task is completed (default: false)
- `created_at`: DateTime - Timestamp when the task was created (auto-generated)

The Task model will be implemented using SQLModel to support both SQLAlchemy ORM and Pydantic validation features.

## API Endpoints

### 1. Create Task
- **Endpoint**: `POST /tasks`
- **Description**: Creates a new task with the provided details
- **Request Body**:
  ```json
  {
    "title": "Task title",
    "description": "Optional task description"
  }
  ```
- **Response**: `201 Created` with the created task object
  ```json
  {
    "id": "uuid-string",
    "title": "Task title",
    "description": "Optional task description",
    "is_completed": false,
    "created_at": "2026-02-06T10:00:00Z"
  }
  ```
- **Validation**: Title is required and must be between 1-100 characters

### 2. List All Tasks
- **Endpoint**: `GET /tasks`
- **Description**: Retrieves all tasks in the system
- **Query Parameters**:
  - `skip` (optional): Number of records to skip (for pagination)
  - `limit` (optional): Maximum number of records to return (for pagination)
  - `completed` (optional): Filter by completion status (true/false)
- **Response**: `200 OK` with an array of task objects
  ```json
  [
    {
      "id": "uuid-string",
      "title": "Task title",
      "description": "Optional task description",
      "is_completed": false,
      "created_at": "2026-02-06T10:00:00Z"
    }
  ]
  ```

### 3. Get Single Task
- **Endpoint**: `GET /tasks/{id}`
- **Description**: Retrieves a specific task by its UUID
- **Path Parameter**: `id` - UUID of the task to retrieve
- **Response**: `200 OK` with the task object
  ```json
  {
    "id": "uuid-string",
    "title": "Task title",
    "description": "Optional task description",
    "is_completed": false,
    "created_at": "2026-02-06T10:00:00Z"
  }
  ```
- **Error Response**: `404 Not Found` if task doesn't exist

### 4. Update Task
- **Endpoint**: `PATCH /tasks/{id}`
- **Description**: Updates specific fields of a task
- **Path Parameter**: `id` - UUID of the task to update
- **Request Body** (all fields optional):
  ```json
  {
    "title": "Updated task title",
    "description": "Updated task description",
    "is_completed": true
  }
  ```
- **Response**: `200 OK` with the updated task object
  ```json
  {
    "id": "uuid-string",
    "title": "Updated task title",
    "description": "Updated task description",
    "is_completed": true,
    "created_at": "2026-02-06T10:00:00Z"
  }
  ```
- **Error Response**: `404 Not Found` if task doesn't exist

### 5. Delete Task
- **Endpoint**: `DELETE /tasks/{id}`
- **Description**: Deletes a specific task by its UUID
- **Path Parameter**: `id` - UUID of the task to delete
- **Response**: `204 No Content` on successful deletion
- **Error Response**: `404 Not Found` if task doesn't exist

## Database Configuration

### Connection
- The application will connect to a Neon PostgreSQL database using connection pooling
- Database credentials will be loaded from environment variables
- Connection string format: `postgresql+asyncpg://username:password@host:port/database`

### Table Creation
- On application startup, the system will check if the required tables exist
- If tables don't exist, they will be automatically created using SQLModel's table creation functionality
- This initialization should happen before the application starts accepting requests

### Initialization Logic
The application will include startup logic to:
1. Establish database connection
2. Verify if the `tasks` table exists
3. Create the `tasks` table if it doesn't exist
4. Log the initialization status

## Error Handling
- Standard HTTP status codes will be used (200, 201, 204, 400, 404, 500, etc.)
- Error responses will follow a consistent format:
  ```json
  {
    "detail": "Error message"
  }
  ```
- Validation errors will return 422 status with field-specific details

## Authentication & Authorization
- For Phase 2, the API will be public (no authentication required)
- Future phases may introduce authentication mechanisms

## Validation Rules
- Task titles must be between 1-100 characters
- Descriptions must be 500 characters or less
- UUID format will be validated for path parameters

## Non-functional Requirements
- API should respond within 500ms for 95% of requests
- Support concurrent requests
- Automatic API documentation via FastAPI's integrated Swagger UI