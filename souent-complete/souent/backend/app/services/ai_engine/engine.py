"""
AI Engine Service
Handles interaction with underlying AI models and wraps them as SLM-A1 (Anthroi-1).
"""

import logging
from typing import List, Dict, Any, Optional
import openai
import anthropic

from app.core.config import settings
from app.models.schemas import Message, MessageRole, MemoryContext
from app.services.ai_engine.anthroi_prompts import ANTHROI_1_SYSTEM_PROMPT

logger = logging.getLogger("souent.ai_engine")


class AIEngineService:
    """
    AI Engine Service - Model abstraction layer
    Wraps external AI providers (OpenAI, Anthropic) as SLM-A1 (Anthroi-1)
    """
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.model = settings.AI_MODEL
        
        # Initialize appropriate client
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=settings.AI_API_KEY)
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.AI_API_KEY)
        else:
            logger.warning(f"Unknown AI provider: {self.provider}. Using mock mode.")
            self.client = None
    
    async def generate_response(
        self,
        user_message: str,
        memory_context: MemoryContext
    ) -> str:
        """
        Generate a response using SLM-A1 (Anthroi-1) logic model.
        
        Args:
            user_message: The user's input message
            memory_context: Complete memory context including session, preferences, and canon
            
        Returns:
            Generated response string
        """
        try:
            # Build message history with system prompt
            messages = self._build_message_history(user_message, memory_context)
            
            # Generate response based on provider
            if self.provider == "openai":
                response = await self._generate_openai(messages)
            elif self.provider == "anthropic":
                response = await self._generate_anthropic(messages)
            else:
                response = self._generate_mock(user_message)
            
            logger.info(f"Generated response for message (length: {len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return "I encountered an error processing your request. This is a system issue, not related to your message content."
    
    def _build_message_history(
        self,
        user_message: str,
        memory_context: MemoryContext
    ) -> List[Dict[str, str]]:
        """
        Build complete message history with system prompt and context.
        
        Args:
            user_message: Current user message
            memory_context: Memory context with session history and preferences
            
        Returns:
            List of message dictionaries for API call
        """
        messages = []
        
        # System prompt with Anthroi-1 instructions
        system_content = ANTHROI_1_SYSTEM_PROMPT
        
        # Add user preferences to system prompt if available
        if memory_context.user_preferences:
            prefs = memory_context.user_preferences
            system_content += f"\n\nUSER PREFERENCES:\n"
            system_content += f"- Tone: {prefs.tone_preference}\n"
            system_content += f"- Max response length: ~{prefs.max_response_length} words\n"
            system_content += f"- Clarification questions: {'enabled' if prefs.enable_clarification_questions else 'disabled'}\n"
        
        # Add authorization tier context
        system_content += f"\n\nUSER AUTHORIZATION TIER: {memory_context.authorization_tier.value}\n"
        
        # Add canon memory context if available and relevant
        if memory_context.canon_memory:
            system_content += f"\n\nSYSTEM CANON MEMORY (Read-Only):\n"
            system_content += f"Current Model: {memory_context.canon_memory.model_info.get('model_name', 'SLM-A1')}\n"
        
        messages.append({"role": "system", "content": system_content})
        
        # Add session history (ephemeral memory)
        for msg in memory_context.session_memory[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def _generate_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.MODEL_TEMPERATURE,
                max_tokens=settings.MODEL_MAX_TOKENS,
                top_p=settings.MODEL_TOP_P,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _generate_anthropic(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Anthropic API"""
        try:
            # Anthropic requires system message separate from messages
            system_message = next((m["content"] for m in messages if m["role"] == "system"), "")
            conversation_messages = [m for m in messages if m["role"] != "system"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.MODEL_MAX_TOKENS,
                temperature=settings.MODEL_TEMPERATURE,
                top_p=settings.MODEL_TOP_P,
                system=system_message,
                messages=conversation_messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def _generate_mock(self, user_message: str) -> str:
        """Generate mock response for testing without API keys"""
        return f"[MOCK RESPONSE - SLM-A1] I received your message: '{user_message[:50]}...'. This is a simulated response because no AI provider is configured. Configure AI_PROVIDER and AI_API_KEY in your .env file to enable real AI responses."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        return {
            "model_designation": "SLM-A1",
            "model_name": "Anthroi-1",
            "version": "1.0.0",
            "provider": self.provider,
            "underlying_model": self.model,
            "characteristics": [
                "Logic-first reasoning",
                "Conservative inference",
                "Explicit uncertainty handling",
                "No emotional simulation",
                "No immersive roleplay"
            ]
        }
