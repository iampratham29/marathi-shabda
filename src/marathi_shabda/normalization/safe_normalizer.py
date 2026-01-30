"""Safe normalization utilities for Marathi text."""

import unicodedata

from marathi_shabda.models import ScriptType
from marathi_shabda.normalization.script_detection import detect_script
from marathi_shabda.normalization.transliterator import roman_to_devanagari


def safe_normalize(word: str) -> str:
    """
    Apply safe normalization to Marathi word.
    
    Operations:
        - Remove zero-width characters
        - Normalize Unicode to NFC (canonical composition)
        - Trim whitespace
        - Preserve Devanagari structure
    
    Args:
        word: Input word
    
    Returns:
        Normalized word
    """
    if not word:
        return word
    
    # Normalize Unicode (NFC = canonical composition)
    normalized = unicodedata.normalize('NFC', word)
    
    # Remove zero-width characters
    zero_width_chars = [
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\ufeff',  # Zero-width no-break space
    ]
    
    for char in zero_width_chars:
        normalized = normalized.replace(char, '')
    
    # Trim whitespace
    normalized = normalized.strip()
    
    return normalized


def normalize_input(text: str) -> str:
    """
    Normalize input text to canonical Devanagari.
    
    This is the main entry point for input normalization:
    1. Detect script
    2. If Roman, transliterate to Devanagari
    3. Apply safe normalization
    
    Args:
        text: Input text (Roman or Devanagari)
    
    Returns:
        Normalized Devanagari text
    """
    if not text:
        return text
    
    # Detect script
    script = detect_script(text)
    
    # If Roman, transliterate
    if script == ScriptType.ROMAN:
        text = roman_to_devanagari(text)
    
    # Apply safe normalization
    return safe_normalize(text)
