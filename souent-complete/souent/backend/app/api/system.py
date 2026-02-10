"""
System API Endpoints
System information, health checks, and model status.
"""

import logging
import time
from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import SystemStatus
from app.core.config import settings
from app.services.ai_engine.engine import AIEngineService

logger = logging.getLogger("souent.api.system")

router = APIRouter()

# Initialize AI engine for model info
ai_engine = AIEngineService()

# Track startup time for uptime calculation
_startup_time = time.time()


@router.get("/health", response_model=SystemStatus)
async def health_check():
    """
    System health check endpoint.
    Returns current operational status and key metrics.
    
    Returns:
        SystemStatus with health information
    """
    try:
        uptime = time.time() - _startup_time
        
        return SystemStatus(
            status="healthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            model="SLM-A1 (Anthroi-1)",
            memory_storage=settings.MEMORY_STORAGE_TYPE,
            uptime_seconds=uptime,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return SystemStatus(
            status="degraded",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            model="SLM-A1 (Anthroi-1)",
            memory_storage=settings.MEMORY_STORAGE_TYPE,
            uptime_seconds=time.time() - _startup_time,
            timestamp=datetime.utcnow()
        )


@router.get("/models")
async def get_available_models():
    """
    Get information about available AI models.
    Currently returns SLM-A1 (Anthroi-1) information.
    
    Returns:
        Dictionary of available models and their characteristics
    """
    model_info = ai_engine.get_model_info()
    
    return {
        "current_model": model_info,
        "available_models": [
            {
                "id": "SLM-A1",
                "name": "Anthroi-1",
                "version": "1.0.0",
                "status": "active",
                "characteristics": model_info["characteristics"]
            }
        ],
        "future_models": [
            {
                "id": "SLM-A2",
                "name": "Anthroi-2",
                "status": "planned",
                "description": "Next generation Souent Logic Model"
            }
        ]
    }


@router.get("/status")
async def get_system_status():
    """
    Detailed system status including configuration and capabilities.
    
    Returns:
        Comprehensive system status information
    """
    uptime = time.time() - _startup_time
    
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG
        },
        "model": {
            "designation": "SLM-A1",
            "name": "Anthroi-1",
            "provider": settings.AI_PROVIDER,
            "underlying_model": settings.AI_MODEL
        },
        "memory": {
            "storage_type": settings.MEMORY_STORAGE_TYPE,
            "layers": [
                "Ephemeral Session Memory",
                "Persistent User Preferences",
                "Locked Canon Memory"
            ]
        },
        "features": {
            "tone_harmonization": True,
            "context_weave": True,
            "authorization_tiers": ["basic", "advisory", "admin_ready"],
            "rate_limiting": settings.RATE_LIMIT_ENABLED
        },
        "uptime_seconds": uptime,
        "status": "operational",
        "timestamp": datetime.utcnow()
    }


@router.get("/config")
async def get_configuration():
    """
    Get non-sensitive configuration information.
    Useful for debugging and integration.
    
    Returns:
        Public configuration parameters
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "memory_storage": settings.MEMORY_STORAGE_TYPE,
        "rate_limiting": {
            "enabled": settings.RATE_LIMIT_ENABLED,
            "requests_per_period": settings.RATE_LIMIT_REQUESTS if settings.RATE_LIMIT_ENABLED else None,
            "period_seconds": settings.RATE_LIMIT_PERIOD if settings.RATE_LIMIT_ENABLED else None
        },
        "model_settings": {
            "temperature": settings.MODEL_TEMPERATURE,
            "max_tokens": settings.MODEL_MAX_TOKENS,
            "top_p": settings.MODEL_TOP_P
        }
    }


@router.get("/capabilities")
async def get_capabilities():
    """
    Get information about Souent's capabilities and limitations.
    
    Returns:
        Dictionary describing what Souent can and cannot do
    """
    return {
        "capabilities": [
            "Logic-first reasoning and analysis",
            "Code review and debugging assistance",
            "Technical documentation analysis",
            "Data analysis and interpretation",
            "Problem-solving and strategic thinking",
            "Information synthesis",
            "Question answering with uncertainty markers"
        ],
        "characteristics": [
            "Conservative inference - doesn't speculate beyond data",
            "Explicit uncertainty handling",
            "Clear logical reasoning",
            "No emotional simulation",
            "No immersive roleplay"
        ],
        "limitations": [
            "Cannot access real-time information (unless web search is enabled)",
            "Cannot execute code or perform actions in external systems",
            "Cannot claim emotions or consciousness",
            "Cannot engage in extended fictional roleplay",
            "Limited to training data and provided context"
        ],
        "authorization_tiers": {
            "basic": "Standard user interaction",
            "advisory": "Enhanced context access for detailed analysis",
            "admin_ready": "System administration and canon memory modification"
        }
    }
