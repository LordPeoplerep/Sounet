"""
Data Models
Pydantic models for request/response validation and data structures.
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AuthorizationTier(str, Enum):
    """Authorization tier levels"""
    BASIC = "basic"
    ADVISORY = "advisory"
    ADMIN_READY = "admin_ready"


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Single message in conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User identifier")
    authorization_tier: AuthorizationTier = Field(default=AuthorizationTier.BASIC, description="User authorization level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the purpose of Souent?",
                "session_id": "session_123",
                "user_id": "user_456",
                "authorization_tier": "basic"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="AI-generated response")
    session_id: str = Field(..., description="Session identifier")
    model: str = Field(default="SLM-A1", description="Model used for generation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Souent is a logic-first AI chatbot developed by VelaPlex Systems.",
                "session_id": "session_123",
                "model": "SLM-A1",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class ConversationHistory(BaseModel):
    """Conversation history model"""
    session_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


class UserPreferences(BaseModel):
    """User preferences model"""
    user_id: str
    tone_preference: Optional[str] = Field(default="balanced", description="Tone preference: concise, balanced, detailed")
    max_response_length: Optional[int] = Field(default=500, description="Preferred max response length in words")
    enable_clarification_questions: bool = Field(default=True, description="Allow AI to ask clarification questions")
    custom_settings: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CanonMemory(BaseModel):
    """Canon memory (read-only system knowledge)"""
    system_knowledge: Dict[str, Any] = Field(default_factory=dict)
    model_info: Dict[str, Any] = Field(default_factory=dict)
    locked: bool = Field(default=True, description="Memory is locked from modification")
    version: str = Field(default="1.0.0")
    last_updated: Optional[datetime] = None


class MemoryContext(BaseModel):
    """Complete memory context for a request"""
    session_memory: List[Message] = Field(default_factory=list, description="Ephemeral session messages")
    user_preferences: Optional[UserPreferences] = None
    canon_memory: Optional[CanonMemory] = None
    authorization_tier: AuthorizationTier = Field(default=AuthorizationTier.BASIC)


class SystemStatus(BaseModel):
    """System status response"""
    status: Literal["healthy", "degraded", "offline"]
    app_name: str
    version: str
    model: str
    memory_storage: str
    uptime_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
