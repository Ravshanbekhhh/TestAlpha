"""
Main FastAPI application entry point.
Updated for Railway deployment.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db, close_db
from app.api.v1 import auth, users, tests, sessions, results, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Starting up Testing Platform API...")
    print(f"📍 Running on port: {settings.PORT}")
    
    # Create directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    
    # Initialize database (only on first deploy)
    # For Railway, use migrations or manual init
    # await init_db()
    
    yield
    
    # Shutdown
    print("👋 Shutting down Testing Platform API...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Testing Platform API",
    description="Automated testing platform with Telegram bot integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allow all for Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(tests.router, prefix="/api/v1/tests", tags=["Tests"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(results.router, prefix="/api/v1/results", tags=["Results"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    print("⚠️ Static directory not found, skipping static file mount")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "message": "Testing Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "environment": "railway"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Railway provides PORT via environment variable
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
