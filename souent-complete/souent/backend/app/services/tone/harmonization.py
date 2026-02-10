"""
Tone Harmonization Layer
Ensures responses maintain Anthroi-1 characteristics and user tone preferences.
"""

import logging
import re
from typing import Optional

from app.models.schemas import UserPreferences
from app.services.ai_engine.anthroi_prompts import TONE_HARMONIZATION_RULES

logger = logging.getLogger("souent.tone")


class ToneHarmonizationService:
    """
    Tone Harmonization Layer
    Post-processes AI responses to ensure consistency with Anthroi-1 behavior
    and user preferences.
    """
    
    # Prohibited phrases that suggest emotional states
    EMOTIONAL_PHRASES = [
        r"\bI feel\b",
        r"\bI'm excited\b",
        r"\bI'm sorry to hear\b",
        r"\bI'm happy\b",
        r"\bI'm sad\b",
        r"\bI love\b",
        r"\bI hate\b",
        r"\bI enjoy\b",
        r"\bI'm passionate about\b",
    ]
    
    # Prohibited roleplay indicators
    ROLEPLAY_INDICATORS = [
        r"\*[^*]+\*",  # Actions in asterisks
        r"^\[.*?\]",   # Scene descriptions
    ]
    
    def harmonize_response(
        self,
        response: str,
        user_preferences: Optional[UserPreferences] = None
    ) -> str:
        """
        Apply tone harmonization to ensure response meets Anthroi-1 standards.
        
        Args:
            response: Raw AI-generated response
            user_preferences: User's tone and format preferences
            
        Returns:
            Harmonized response
        """
        harmonized = response
        
        # 1. Remove emotional language
        harmonized = self._remove_emotional_language(harmonized)
        
        # 2. Remove roleplay elements
        harmonized = self._remove_roleplay_elements(harmonized)
        
        # 3. Apply length constraints based on user preferences
        if user_preferences:
            harmonized = self._apply_length_constraints(harmonized, user_preferences)
        
        # 4. Ensure uncertainty markers are preserved
        harmonized = self._preserve_uncertainty_markers(harmonized)
        
        # 5. Remove excessive apologies
        harmonized = self._reduce_apologies(harmonized)
        
        logger.debug("Applied tone harmonization")
        return harmonized.strip()
    
    def _remove_emotional_language(self, text: str) -> str:
        """Remove phrases that suggest emotional states"""
        modified = text
        
        for pattern in self.EMOTIONAL_PHRASES:
            # Replace with more neutral alternatives
            if re.search(pattern, modified, re.IGNORECASE):
                # Log the detection
                logger.debug(f"Detected emotional phrase: {pattern}")
                
                # Replace "I feel" with "It appears" or "Based on"
                modified = re.sub(r"\bI feel that\b", "It appears that", modified, flags=re.IGNORECASE)
                modified = re.sub(r"\bI feel\b", "Based on the information", modified, flags=re.IGNORECASE)
                
                # Replace excitement
                modified = re.sub(r"\bI'm excited to\b", "I will", modified, flags=re.IGNORECASE)
                
                # Replace "I'm sorry to hear"
                modified = re.sub(r"\bI'm sorry to hear\b", "That sounds difficult", modified, flags=re.IGNORECASE)
                modified = re.sub(r"\bI'm sorry that\b", "It appears that", modified, flags=re.IGNORECASE)
        
        return modified
    
    def _remove_roleplay_elements(self, text: str) -> str:
        """Remove asterisk actions and roleplay formatting"""
        modified = text
        
        # Remove *action* style text
        modified = re.sub(r'\*[^*]+\*', '', modified)
        
        # Remove [scene description] style text at start of lines
        modified = re.sub(r'^\[.*?\]\s*', '', modified, flags=re.MULTILINE)
        
        return modified
    
    def _apply_length_constraints(self, text: str, preferences: UserPreferences) -> str:
        """Apply length constraints based on user preferences"""
        tone = preferences.tone_preference or "balanced"
        max_words = preferences.max_response_length or 500
        
        words = text.split()
        word_count = len(words)
        
        # Get tone rules
        rules = TONE_HARMONIZATION_RULES.get(tone, TONE_HARMONIZATION_RULES["balanced"])
        
        # If response is too long, truncate intelligently
        if word_count > max_words:
            # Try to end at a sentence boundary
            truncated = ' '.join(words[:max_words])
            
            # Find last complete sentence
            sentences = re.split(r'[.!?]\s+', truncated)
            if len(sentences) > 1:
                truncated = '. '.join(sentences[:-1]) + '.'
            
            logger.debug(f"Truncated response from {word_count} to ~{max_words} words")
            return truncated
        
        return text
    
    def _preserve_uncertainty_markers(self, text: str) -> str:
        """
        Ensure uncertainty markers are present and not weakened.
        Anthroi-1 should be explicit about uncertainty.
        """
        # Common weakening phrases to avoid
        weakeners = [
            (r"\bperhaps I should mention\b", "I should mention"),
            (r"\bI think I'm uncertain\b", "I am uncertain"),
            (r"\bI might be wrong but\b", "I cannot verify, but"),
        ]
        
        modified = text
        for pattern, replacement in weakeners:
            modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)
        
        return modified
    
    def _reduce_apologies(self, text: str) -> str:
        """
        Reduce excessive apologizing while maintaining appropriate acknowledgment.
        Anthroi-1 should be calm and direct, not overly apologetic.
        """
        # Only one apology per response maximum
        apology_count = len(re.findall(r"\bI apologize\b|\bI'm sorry\b", text, re.IGNORECASE))
        
        if apology_count > 1:
            # Keep first apology, remove others
            first_match = True
            
            def replace_apology(match):
                nonlocal first_match
                if first_match:
                    first_match = False
                    return match.group(0)
                return ""
            
            text = re.sub(
                r"\bI apologize[^.!?]*[.!?]|\bI'm sorry[^.!?]*[.!?]",
                replace_apology,
                text,
                flags=re.IGNORECASE
            )
        
        return text
    
    def validate_response(self, response: str) -> bool:
        """
        Validate that response meets Anthroi-1 standards.
        
        Returns:
            True if response is valid, False if it needs regeneration
        """
        # Check for prohibited content
        for pattern in self.EMOTIONAL_PHRASES:
            if re.search(pattern, response, re.IGNORECASE):
                logger.warning(f"Response contains emotional language: {pattern}")
                return False
        
        # Check for roleplay
        for pattern in self.ROLEPLAY_INDICATORS:
            if re.search(pattern, response):
                logger.warning(f"Response contains roleplay elements: {pattern}")
                return False
        
        # Check minimum length (too short might indicate refusal without explanation)
        if len(response.split()) < 5 and not any(word in response.lower() for word in ["cannot", "unable", "not"]):
            logger.warning("Response is too short without clear refusal")
            return False
        
        return True
