from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables
from contextlib import asynccontextmanager
from .api.tasks import router as tasks_router
from .api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the application.
    Runs startup and shutdown logic.
    """
    # Startup: Create database tables if they don't exist
    print("Initializing database...")
    create_db_and_tables()
    print("Database initialized.")

    yield  # This is where the application runs

    # Shutdown: Cleanup operations would go here
    print("Shutting down...")


app = FastAPI(
    title="Todo Backend API",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Allow Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Todo Backend API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)