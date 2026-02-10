"""
Logging Configuration Module
Configures structured logging for the application.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Simple text formatter for human-readable logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {record.levelname:8s} {record.name:20s} {record.getMessage()}"


def setup_logging() -> logging.Logger:
    """
    Setup application logging with appropriate formatter.
    Returns the root logger.
    """
    # Create root logger
    logger = logging.getLogger("souent")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Set formatter based on configuration
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
        
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
