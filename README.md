# Todo Application - AI-Native Development Project

A full-stack todo application built following the AI-Native Development methodology, progressing through multiple phases from CLI to production-ready web application.

## Project Progress

| Phase | Status | Description | Implementation Details |
|-------|--------|-------------|------------------------|
| **Phase I: CLI Todo App** | ✅ Complete | Command-line todo application with local file storage | - Python CLI with argparse<br>- JSON file storage<br>- Basic CRUD operations<br>- Tag: `phase-1-complete` |
| **Phase II: Full-Stack Web App** | ✅ Complete | Modern web application with authentication | - FastAPI backend with RESTful API<br>- Next.js frontend (React + Tailwind)<br>- JWT authentication with bcrypt<br>- PostgreSQL database (Neon)<br>- User registration & login<br>- Protected routes & user isolation<br>- Tag: `phase-2-complete` |
| **Phase III: Production Deployment** | 🔄 Planned | Deploy to cloud with CI/CD | - Docker containerization<br>- Cloud deployment (AWS/Vercel)<br>- CI/CD pipeline<br>- Monitoring & logging |
| **Phase IV: Advanced Features** | 📋 Future | Enhanced functionality | - Real-time collaboration<br>- Mobile app<br>- Advanced analytics |

## Phase II: Full-Stack Web App (Current)

### Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Next.js       │         │   FastAPI       │         │   PostgreSQL    │
│   Frontend      │ ◄─────► │   Backend       │ ◄─────► │   (Neon)        │
│   (Port 3000)   │   JWT   │   (Port 8001)   │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLModel (ORM with Pydantic validation)
- PostgreSQL via Neon (cloud database)
- JWT tokens with python-jose
- Bcrypt password hashing with passlib
- Uvicorn ASGI server

**Frontend:**
- Next.js 16 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- React Context API (state management)
- localStorage (token persistence)

**Database:**
- PostgreSQL (Neon cloud hosting)
- Two main tables: `user` and `task`
- Foreign key relationship for user isolation

### Features Implemented

#### Authentication System
- ✅ User registration with email/password
- ✅ Secure password hashing (bcrypt)
- ✅ JWT token generation (30-minute expiration)
- ✅ Login/logout functionality
- ✅ Protected routes with auto-redirect
- ✅ Token validation on all API requests

#### Task Management
- ✅ Create tasks with title, description, priority
- ✅ View all tasks (user-specific)
- ✅ Update task status (pending/in-progress/completed)
- ✅ Delete tasks
- ✅ User isolation (users only see their own tasks)

#### User Interface
- ✅ Clean, responsive design with Tailwind CSS
- ✅ Login and signup pages
- ✅ Protected dashboard
- ✅ Task creation form
- ✅ Task cards with status indicators
- ✅ Logout button

### API Endpoints

**Authentication:**
- `POST /api/v1/auth/signup` - Create new user account
- `POST /api/v1/auth/login` - Login and get JWT token

**Tasks (Protected):**
- `GET /api/v1/tasks` - Get all tasks for current user
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

All task endpoints require `Authorization: Bearer <token>` header.

### Database Schema

```sql
-- User table
CREATE TABLE "user" (
    id VARCHAR PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL
);

-- Task table
CREATE TABLE task (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES "user"(id),
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    status taskstatus NOT NULL,
    priority taskpriority NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL database (or Neon account)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure database
echo "DATABASE_URL=your_postgresql_url" > .env

# Run server
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

```bash
cd frontend
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api/v1" > .env.local

# Run development server
npm run dev
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8001
- API Documentation: http://127.0.0.1:8001/docs

## Project Structure

```
todo-phase-1/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Security utilities
│   │   ├── models/       # Database models
│   │   └── services/     # Business logic
│   ├── tests/            # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   └── types/        # TypeScript types
│   └── package.json
└── README.md
```

## Development Notes

### Phase II Implementation Timeline
- **Internal Phase 2**: Backend API with FastAPI (9/9 tests passing)
- **Internal Phase 3**: Frontend UI with Next.js
- **Internal Phase 4**: JWT Authentication system

All three internal phases together constitute **Official Phase II** from the project roadmap.

### Security Features
- Passwords hashed with bcrypt (12 rounds)
- JWT tokens with 30-minute expiration
- User isolation at database level
- Protected API endpoints
- CORS configuration for frontend
- Input validation with Pydantic

### Testing
Backend includes comprehensive test suite:
- Database connection tests
- API endpoint tests
- Authentication flow tests
- User isolation tests

Run tests: `cd backend && pytest`

## Contributing

This project follows the AI-Native Development methodology. All development is done in collaboration with Claude (Anthropic's AI assistant).

## License

MIT License

## Acknowledgments

- Built with Claude Opus 4.6
- Following AI-Native Development principles
- Neon for PostgreSQL hosting
