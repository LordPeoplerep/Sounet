"""
Input Validation Utilities
Additional validation and sanitization for user inputs.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("souent.validation")


class InputValidator:
    """Validates and sanitizes user inputs for security"""
    
    # Maximum lengths for various inputs
    MAX_MESSAGE_LENGTH = 4000
    MAX_SESSION_ID_LENGTH = 64
    MAX_USER_ID_LENGTH = 128
    
    # Patterns for validation
    SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_@.-]+$')
    
    # Suspicious patterns that might indicate injection attempts
    SUSPICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'eval\(',
        r'exec\(',
    ]
    
    @classmethod
    def validate_message(cls, message: str) -> tuple[bool, Optional[str]]:
        """
        Validate user message content.
        
        Args:
            message: User message to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not message or not message.strip():
            return False, "Message cannot be empty"
        
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            return False, f"Message exceeds maximum length of {cls.MAX_MESSAGE_LENGTH} characters"
        
        # Check for suspicious patterns (basic XSS/injection detection)
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in message: {pattern}")
                return False, "Message contains potentially unsafe content"
        
        return True, None
    
    @classmethod
    def validate_session_id(cls, session_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate session ID format.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not session_id:
            return False, "Session ID cannot be empty"
        
        if len(session_id) > cls.MAX_SESSION_ID_LENGTH:
            return False, f"Session ID exceeds maximum length of {cls.MAX_SESSION_ID_LENGTH}"
        
        if not cls.SESSION_ID_PATTERN.match(session_id):
            return False, "Session ID contains invalid characters"
        
        return True, None
    
    @classmethod
    def validate_user_id(cls, user_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate user ID format.
        
        Args:
            user_id: User ID to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not user_id:
            return False, "User ID cannot be empty"
        
        if len(user_id) > cls.MAX_USER_ID_LENGTH:
            return False, f"User ID exceeds maximum length of {cls.MAX_USER_ID_LENGTH}"
        
        if not cls.USER_ID_PATTERN.match(user_id):
            return False, "User ID contains invalid characters"
        
        return True, None
    
    @classmethod
    def sanitize_output(cls, output: str) -> str:
        """
        Sanitize AI output before sending to user.
        Removes any potentially harmful content that might have been generated.
        
        Args:
            output: AI-generated output
            
        Returns:
            Sanitized output
        """
        # Remove any script tags that might have been generated
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', output, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove on* event handlers
        sanitized = re.sub(r'\son\w+\s*=\s*["\'].*?["\']', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def check_content_safety(cls, content: str) -> tuple[bool, Optional[str]]:
        """
        Check if content is safe and appropriate.
        
        Args:
            content: Content to check
            
        Returns:
            Tuple of (is_safe: bool, reason: Optional[str])
        """
        # Check for extremely long single words (potential DOS)
        words = content.split()
        for word in words:
            if len(word) > 200:
                return False, "Content contains unusually long words"
        
        # Check for excessive repetition (potential DOS)
        if len(content) > 100:
            # Check if content is mostly repeating characters
            unique_chars = len(set(content.lower().replace(' ', '')))
            if unique_chars < 10 and len(content) > 500:
                return False, "Content appears to be repetitive"
        
        return True, None
