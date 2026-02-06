from fastapi import FastAPI
from .database import create_db_and_tables
from contextlib import asynccontextmanager
from .api.tasks import router as tasks_router


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

# Include the tasks router
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