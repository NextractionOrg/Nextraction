from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import ingest, status, ask, health
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import logger
import os

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Web-based RAG pipeline for extracting insights from public online sources"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(ingest.router)
app.include_router(status.router)
app.include_router(ask.router)
app.include_router(health.router)

# Mount static files for UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Root endpoint - redirects to UI or shows API info"""
    # Check if static UI exists
    ui_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(ui_path):
        from fastapi.responses import FileResponse
        return FileResponse(ui_path)
    return {
        "message": "NexTraction Web RAG API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Create data directories
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.chunks_dir, exist_ok=True)
    os.makedirs(f"{settings.data_dir}/indices", exist_ok=True)
    
    logger.info("Application started")
    logger.info(f"Embedding provider: {settings.embedding_provider}")
    logger.info(f"LLM provider: {settings.llm_provider}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down")
