"""
Memory Service - Context Weave System
Manages three layers of memory:
1. Ephemeral Session Memory (cleared after session)
2. Persistent User Preferences
3. Locked Canon Memory (read-only unless admin)
"""

import json
import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.core.config import settings
from app.models.schemas import (
    Message,
    MessageRole,
    UserPreferences,
    CanonMemory,
    MemoryContext,
    AuthorizationTier
)

logger = logging.getLogger("souent.memory")


class MemoryService:
    """
    Context Weave Memory System
    Manages ephemeral, persistent, and canon memory layers.
    """
    
    def __init__(self):
        self.storage_type = settings.MEMORY_STORAGE_TYPE
        self._sessions: Dict[str, List[Message]] = {}  # In-memory session cache
        
        if self.storage_type == "redis":
            try:
                import redis
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                logger.info("Connected to Redis for memory storage")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Falling back to file storage.")
                self.storage_type = "file"
    
    # ============================================================
    # SESSION MEMORY (Ephemeral)
    # ============================================================
    
    def add_message_to_session(
        self,
        session_id: str,
        role: MessageRole,
        content: str
    ) -> None:
        """Add a message to ephemeral session memory"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append(message)
        
        # Persist to storage
        if self.storage_type == "file":
            self._save_session_file(session_id)
        elif self.storage_type == "redis":
            self._save_session_redis(session_id)
        
        logger.debug(f"Added {role.value} message to session {session_id}")
    
    def get_session_history(self, session_id: str) -> List[Message]:
        """Retrieve ephemeral session history"""
        # Check in-memory cache first
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Load from storage
        if self.storage_type == "file":
            return self._load_session_file(session_id)
        elif self.storage_type == "redis":
            return self._load_session_redis(session_id)
        
        return []
    
    def clear_session(self, session_id: str) -> None:
        """Clear ephemeral session memory"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        if self.storage_type == "file":
            filepath = os.path.join(settings.SESSION_MEMORY_PATH, f"{session_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
        elif self.storage_type == "redis":
            self.redis_client.delete(f"session:{session_id}")
        
        logger.info(f"Cleared session {session_id}")
    
    def _save_session_file(self, session_id: str) -> None:
        """Save session to file"""
        filepath = os.path.join(settings.SESSION_MEMORY_PATH, f"{session_id}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        messages_data = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self._sessions.get(session_id, [])
        ]
        
        with open(filepath, 'w') as f:
            json.dump(messages_data, f, indent=2)
    
    def _load_session_file(self, session_id: str) -> List[Message]:
        """Load session from file"""
        filepath = os.path.join(settings.SESSION_MEMORY_PATH, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r') as f:
                messages_data = json.load(f)
            
            messages = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"])
                )
                for msg in messages_data
            ]
            
            self._sessions[session_id] = messages
            return messages
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return []
    
    def _save_session_redis(self, session_id: str) -> None:
        """Save session to Redis"""
        messages_data = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self._sessions.get(session_id, [])
        ]
        
        self.redis_client.setex(
            f"session:{session_id}",
            3600,  # 1 hour TTL
            json.dumps(messages_data)
        )
    
    def _load_session_redis(self, session_id: str) -> List[Message]:
        """Load session from Redis"""
        data = self.redis_client.get(f"session:{session_id}")
        
        if not data:
            return []
        
        try:
            messages_data = json.loads(data)
            messages = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"])
                )
                for msg in messages_data
            ]
            
            self._sessions[session_id] = messages
            return messages
        except Exception as e:
            logger.error(f"Error loading session from Redis: {e}")
            return []
    
    # ============================================================
    # USER PREFERENCES (Persistent)
    # ============================================================
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Retrieve persistent user preferences"""
        if self.storage_type == "file":
            return self._load_preferences_file(user_id)
        elif self.storage_type == "redis":
            return self._load_preferences_redis(user_id)
        return None
    
    def save_user_preferences(self, preferences: UserPreferences) -> None:
        """Save persistent user preferences"""
        preferences.updated_at = datetime.utcnow()
        
        if self.storage_type == "file":
            self._save_preferences_file(preferences)
        elif self.storage_type == "redis":
            self._save_preferences_redis(preferences)
        
        logger.info(f"Saved preferences for user {preferences.user_id}")
    
    def _save_preferences_file(self, preferences: UserPreferences) -> None:
        """Save preferences to file"""
        filepath = os.path.join(settings.USER_PREFERENCES_PATH, f"{preferences.user_id}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(preferences.model_dump(), f, indent=2, default=str)
    
    def _load_preferences_file(self, user_id: str) -> Optional[UserPreferences]:
        """Load preferences from file"""
        filepath = os.path.join(settings.USER_PREFERENCES_PATH, f"{user_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return UserPreferences(**data)
        except Exception as e:
            logger.error(f"Error loading preferences for {user_id}: {e}")
            return None
    
    def _save_preferences_redis(self, preferences: UserPreferences) -> None:
        """Save preferences to Redis"""
        self.redis_client.set(
            f"preferences:{preferences.user_id}",
            json.dumps(preferences.model_dump(), default=str)
        )
    
    def _load_preferences_redis(self, user_id: str) -> Optional[UserPreferences]:
        """Load preferences from Redis"""
        data = self.redis_client.get(f"preferences:{user_id}")
        
        if not data:
            return None
        
        try:
            return UserPreferences(**json.loads(data))
        except Exception as e:
            logger.error(f"Error loading preferences from Redis: {e}")
            return None
    
    # ============================================================
    # CANON MEMORY (Locked, Read-Only unless Admin)
    # ============================================================
    
    def get_canon_memory(self) -> Optional[CanonMemory]:
        """Retrieve locked canon memory (read-only)"""
        try:
            with open(settings.CANON_MEMORY_PATH, 'r') as f:
                data = json.load(f)
            return CanonMemory(**data)
        except Exception as e:
            logger.error(f"Error loading canon memory: {e}")
            return None
    
    def update_canon_memory(
        self,
        updates: Dict[str, Any],
        authorization_tier: AuthorizationTier
    ) -> bool:
        """
        Update canon memory (requires ADMIN_READY authorization)
        
        Args:
            updates: Dictionary of updates to apply
            authorization_tier: User's authorization level
            
        Returns:
            True if successful, False if unauthorized or failed
        """
        if authorization_tier != AuthorizationTier.ADMIN_READY:
            logger.warning(f"Unauthorized canon memory update attempt with tier: {authorization_tier}")
            return False
        
        try:
            canon = self.get_canon_memory()
            if not canon:
                logger.error("Canon memory not found")
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(canon, key):
                    setattr(canon, key, value)
            
            canon.last_updated = datetime.utcnow()
            
            # Save
            with open(settings.CANON_MEMORY_PATH, 'w') as f:
                json.dump(canon.model_dump(), f, indent=2, default=str)
            
            logger.info("Canon memory updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating canon memory: {e}")
            return False
    
    # ============================================================
    # CONTEXT WEAVE - Combine all memory layers
    # ============================================================
    
    def build_memory_context(
        self,
        session_id: str,
        user_id: Optional[str],
        authorization_tier: AuthorizationTier
    ) -> MemoryContext:
        """
        Build complete memory context by weaving together all three layers.
        
        Args:
            session_id: Session identifier
            user_id: User identifier (optional)
            authorization_tier: User's authorization level
            
        Returns:
            Complete MemoryContext with all accessible memory layers
        """
        # Layer 1: Ephemeral session memory
        session_memory = self.get_session_history(session_id)
        
        # Layer 2: Persistent user preferences
        user_preferences = None
        if user_id:
            user_preferences = self.get_user_preferences(user_id)
        
        # Layer 3: Locked canon memory
        canon_memory = self.get_canon_memory()
        
        return MemoryContext(
            session_memory=session_memory,
            user_preferences=user_preferences,
            canon_memory=canon_memory,
            authorization_tier=authorization_tier
        )
    
    def generate_session_id(self) -> str:
        """Generate a new unique session ID"""
        return f"session_{uuid.uuid4().hex[:16]}"
