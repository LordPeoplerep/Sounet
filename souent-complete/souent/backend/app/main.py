"""
Souent AI Chatbot - Main Application
Developed by VelaPlex Systems

This is the main FastAPI application entry point for the Souent chatbot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api import chat, memory, system
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.utils.rate_limiter import RateLimiterMiddleware

# Setup logging
logger = setup_logging()

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Souent AI Chatbot - Powered by Souent Logic Models (SLM-A1: Anthroi-1)",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimiterMiddleware)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AI Provider: {settings.AI_PROVIDER}")
    logger.info(f"Memory Storage: {settings.MEMORY_STORAGE_TYPE}")
    
    # Initialize data directories if using file storage
    if settings.MEMORY_STORAGE_TYPE == "file":
        import os
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        os.makedirs(settings.USER_PREFERENCES_PATH, exist_ok=True)
        os.makedirs(settings.SESSION_MEMORY_PATH, exist_ok=True)
        
        # Initialize canon memory if it doesn't exist
        if not os.path.exists(settings.CANON_MEMORY_PATH):
            import json
            with open(settings.CANON_MEMORY_PATH, 'w') as f:
                json.dump({
                    "system_knowledge": {},
                    "model_info": {
                        "current_model": "SLM-A1",
                        "model_name": "Anthroi-1",
                        "version": "1.0.0",
                        "characteristics": [
                            "Logic-first reasoning",
                            "Conservative inference",
                            "Explicit uncertainty handling",
                            "No emotional simulation",
                            "No immersive roleplay"
                        ]
                    },
                    "locked": True
                }, f, indent=2)
            logger.info("Initialized canon memory")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return JSONResponse({
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "model": "SLM-A1 (Anthroi-1)",
        "developer": "VelaPlex Systems"
    })


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "memory_storage": settings.MEMORY_STORAGE_TYPE
    })


# Include API routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
