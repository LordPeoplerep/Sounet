"""
Chat API Endpoints
Handles user message interactions with Souent AI.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    MessageRole,
    AuthorizationTier,
    ErrorResponse
)
from app.services.ai_engine.engine import AIEngineService
from app.services.memory.memory_service import MemoryService
from app.services.tone.harmonization import ToneHarmonizationService
from app.core.config import settings

logger = logging.getLogger("souent.api.chat")

router = APIRouter()

# Initialize services
ai_engine = AIEngineService()
memory_service = MemoryService()
tone_service = ToneHarmonizationService()


def _get_authorization_tier(api_key: Optional[str]) -> AuthorizationTier:
    """Determine authorization tier from API key"""
    if not api_key:
        return AuthorizationTier.BASIC
    
    if api_key == settings.ADMIN_API_KEY:
        return AuthorizationTier.ADMIN_READY
    elif api_key == settings.ADVISORY_API_KEY:
        return AuthorizationTier.ADVISORY
    
    return AuthorizationTier.BASIC


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send a message to Souent AI and receive a response.
    
    This endpoint processes user messages through:
    1. Memory context retrieval (session + user preferences + canon)
    2. AI generation via SLM-A1 (Anthroi-1)
    3. Tone harmonization
    4. Session memory update
    
    Args:
        request: Chat request containing message and context
        x_api_key: Optional API key for authorization tier elevation
        
    Returns:
        ChatResponse with AI-generated response
    """
    try:
        # Determine authorization tier
        auth_tier = _get_authorization_tier(x_api_key)
        if request.authorization_tier != AuthorizationTier.BASIC:
            # Use the higher tier
            auth_tier = request.authorization_tier
        
        # Generate or use provided session ID
        session_id = request.session_id or memory_service.generate_session_id()
        
        logger.info(f"Processing message for session {session_id}, tier: {auth_tier.value}")
        
        # Add user message to session memory
        memory_service.add_message_to_session(
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message
        )
        
        # Build complete memory context (Context Weave)
        memory_context = memory_service.build_memory_context(
            session_id=session_id,
            user_id=request.user_id,
            authorization_tier=auth_tier
        )
        
        # Generate AI response via SLM-A1
        raw_response = await ai_engine.generate_response(
            user_message=request.message,
            memory_context=memory_context
        )
        
        # Apply tone harmonization
        harmonized_response = tone_service.harmonize_response(
            response=raw_response,
            user_preferences=memory_context.user_preferences
        )
        
        # Validate response meets Anthroi-1 standards
        if not tone_service.validate_response(harmonized_response):
            logger.warning("Response failed validation, using fallback")
            harmonized_response = "I encountered an issue generating an appropriate response. Could you rephrase your question?"
        
        # Add assistant response to session memory
        memory_service.add_message_to_session(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=harmonized_response
        )
        
        # Build response
        return ChatResponse(
            response=harmonized_response,
            session_id=session_id,
            model="SLM-A1 (Anthroi-1)",
            timestamp=datetime.utcnow(),
            metadata={
                "authorization_tier": auth_tier.value,
                "user_id": request.user_id
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your message. Please try again."
        )


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(session_id: str):
    """
    Retrieve conversation history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        ConversationHistory with all messages in the session
    """
    try:
        messages = memory_service.get_session_history(session_id)
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=f"No conversation history found for session {session_id}"
            )
        
        return ConversationHistory(
            session_id=session_id,
            messages=messages,
            created_at=messages[0].timestamp if messages else datetime.utcnow(),
            updated_at=messages[-1].timestamp if messages else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving conversation history")


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session and its ephemeral memory.
    
    Args:
        session_id: Session identifier to clear
        
    Returns:
        Success confirmation
    """
    try:
        memory_service.clear_session(session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} cleared",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error clearing session")


@router.post("/session/new")
async def create_new_session():
    """
    Create a new conversation session.
    
    Returns:
        New session ID
    """
    session_id = memory_service.generate_session_id()
    return {
        "session_id": session_id,
        "created_at": datetime.utcnow(),
        "status": "active"
    }
