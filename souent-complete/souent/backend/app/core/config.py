"""
Core Configuration Module
Loads and validates all environment variables and application settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Souent", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Security
    SECRET_KEY: str = Field(default="change-this-secret-key", description="Secret key for JWT tokens")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # AI Model Configuration
    AI_PROVIDER: str = Field(default="openai", description="AI provider: openai, anthropic, custom")
    AI_API_KEY: str = Field(default="", description="API key for AI provider")
    AI_MODEL: str = Field(default="gpt-4-turbo-preview", description="AI model identifier")
    
    # Memory System
    MEMORY_STORAGE_TYPE: str = Field(default="file", description="Storage type: redis or file")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Data Paths
    DATA_DIR: str = Field(default="./data", description="Data directory for file storage")
    CANON_MEMORY_PATH: str = Field(default="./data/canon_memory.json", description="Canon memory file path")
    USER_PREFERENCES_PATH: str = Field(default="./data/user_preferences", description="User preferences directory")
    SESSION_MEMORY_PATH: str = Field(default="./data/sessions", description="Session memory directory")
    
    # Authorization
    ADMIN_API_KEY: str = Field(default="", description="Admin API key for canon memory write access")
    ADVISORY_API_KEY: str = Field(default="", description="Advisory API key for enhanced access")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Max requests per period")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="Rate limit period in seconds")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")
    
    # Model Engine Settings (SLM-A1)
    MODEL_TEMPERATURE: float = Field(default=0.7, description="Model temperature for response generation")
    MODEL_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens in response")
    MODEL_TOP_P: float = Field(default=0.95, description="Top-p sampling parameter")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS if it's a comma-separated string"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS


# Global settings instance
settings = Settings()

# Override allowed origins if string
if isinstance(settings.ALLOWED_ORIGINS, str):
    settings.ALLOWED_ORIGINS = settings.get_allowed_origins_list()
