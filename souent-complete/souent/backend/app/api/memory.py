"""
Memory API Endpoints
Manages user preferences and canon memory access.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime

from app.models.schemas import (
    UserPreferences,
    CanonMemory,
    AuthorizationTier,
    ErrorResponse
)
from app.services.memory.memory_service import MemoryService
from app.core.config import settings

logger = logging.getLogger("souent.api.memory")

router = APIRouter()

# Initialize memory service
memory_service = MemoryService()


def _verify_admin_access(api_key: Optional[str]) -> bool:
    """Verify admin-level API key"""
    return api_key == settings.ADMIN_API_KEY and api_key != ""


@router.get("/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """
    Retrieve user preferences (persistent memory layer).
    
    Args:
        user_id: User identifier
        
    Returns:
        UserPreferences if found
    """
    try:
        preferences = memory_service.get_user_preferences(user_id)
        
        if not preferences:
            # Return default preferences
            preferences = UserPreferences(
                user_id=user_id,
                tone_preference="balanced",
                max_response_length=500,
                enable_clarification_questions=True
            )
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error retrieving preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving user preferences")


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(preferences: UserPreferences):
    """
    Update user preferences (persistent memory layer).
    
    Args:
        preferences: UserPreferences object to save
        
    Returns:
        Updated UserPreferences
    """
    try:
        memory_service.save_user_preferences(preferences)
        return preferences
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error updating user preferences")


@router.get("/canon", response_model=CanonMemory)
async def get_canon_memory():
    """
    Retrieve canon memory (locked system knowledge).
    Read-only access for all authorization tiers.
    
    Returns:
        CanonMemory containing system knowledge
    """
    try:
        canon = memory_service.get_canon_memory()
        
        if not canon:
            raise HTTPException(
                status_code=404,
                detail="Canon memory not initialized"
            )
        
        return canon
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving canon memory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving canon memory")


@router.put("/canon")
async def update_canon_memory(
    updates: Dict[str, Any],
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Update canon memory (ADMIN ONLY).
    Requires valid admin API key in X-API-Key header.
    
    Args:
        updates: Dictionary of updates to apply to canon memory
        x_api_key: Admin API key (required)
        
    Returns:
        Success confirmation or error
    """
    # Verify admin authorization
    if not _verify_admin_access(x_api_key):
        logger.warning("Unauthorized canon memory update attempt")
        raise HTTPException(
            status_code=403,
            detail="Admin authorization required to modify canon memory"
        )
    
    try:
        success = memory_service.update_canon_memory(
            updates=updates,
            authorization_tier=AuthorizationTier.ADMIN_READY
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update canon memory"
            )
        
        return {
            "status": "success",
            "message": "Canon memory updated successfully",
            "timestamp": datetime.utcnow(),
            "updated_fields": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating canon memory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error updating canon memory")


@router.get("/canon/info")
async def get_canon_info():
    """
    Get information about canon memory without full content.
    Useful for checking lock status and version.
    
    Returns:
        Canon memory metadata
    """
    try:
        canon = memory_service.get_canon_memory()
        
        if not canon:
            raise HTTPException(status_code=404, detail="Canon memory not found")
        
        return {
            "locked": canon.locked,
            "version": canon.version,
            "last_updated": canon.last_updated,
            "model_name": canon.model_info.get("model_name", "Unknown"),
            "model_version": canon.model_info.get("version", "Unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving canon info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving canon information")
