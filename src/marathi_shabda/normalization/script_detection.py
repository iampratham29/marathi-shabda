"""Script detection for Marathi text."""

from marathi_shabda.models import ScriptType


def detect_script(text: str) -> ScriptType:
    """
    Detect script type of input text.
    
    Args:
        text: Input text to analyze
    
    Returns:
        ScriptType enum value
    
    Algorithm:
        - Check Unicode ranges for Devanagari (U+0900–U+097F)
        - If >50% Devanagari characters → DEVANAGARI
        - Else if contains ASCII letters → ROMAN
        - Else → UNKNOWN
    """
    if not text or not text.strip():
        return ScriptType.UNKNOWN
    
    # Count Devanagari characters
    devanagari_count = 0
    ascii_letter_count = 0
    total_chars = 0
    
    for char in text:
        if char.isspace():
            continue
        
        total_chars += 1
        code_point = ord(char)
        
        # Devanagari Unicode range: U+0900 to U+097F
        if 0x0900 <= code_point <= 0x097F:
            devanagari_count += 1
        # ASCII letters
        elif char.isascii() and char.isalpha():
            ascii_letter_count += 1
    
    if total_chars == 0:
        return ScriptType.UNKNOWN
    
    # If more than 50% Devanagari
    if devanagari_count / total_chars > 0.5:
        return ScriptType.DEVANAGARI
    
    # If contains ASCII letters
    if ascii_letter_count > 0:
        return ScriptType.ROMAN
    
    return ScriptType.UNKNOWN
