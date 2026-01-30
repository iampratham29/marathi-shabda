"""Roman to Devanagari transliteration for Marathi."""

from typing import Dict, Tuple

# Transliteration mapping table (longest-match-first)
# Format: (roman_pattern, devanagari_equivalent)
TRANSLITERATION_MAP: list[Tuple[str, str]] = [
    # Three-character patterns (longest first)
    ("ksh", "क्ष"),
    ("dny", "ज्ञ"),
    ("shr", "श्र"),
    ("shch", "श्च"),
    
    # Two-character patterns
    ("kh", "ख"),
    ("gh", "घ"),
    ("ch", "च"),
    ("chh", "छ"),
    ("jh", "झ"),
    ("th", "थ"),
    ("dh", "ध"),
    ("ph", "फ"),
    ("bh", "भ"),
    ("sh", "श"),
    ("ny", "ञ"),
    ("ng", "ङ"),
    ("aa", "आ"),
    ("ee", "ई"),
    ("oo", "ऊ"),
    ("ai", "ऐ"),
    ("au", "औ"),
    ("ri", "ऋ"),
    
    # Vowel modifiers (matras)
    ("a", "ा"),  # When following consonant
    ("i", "ि"),
    ("u", "ु"),
    ("e", "े"),
    ("o", "ो"),
    
    # Single-character consonants
    ("k", "क"),
    ("g", "ग"),
    ("c", "च"),
    ("j", "ज"),
    ("t", "त"),
    ("d", "द"),
    ("n", "न"),
    ("p", "प"),
    ("b", "ब"),
    ("m", "म"),
    ("y", "य"),
    ("r", "र"),
    ("l", "ल"),
    ("v", "व"),
    ("w", "व"),  # Alternative for 'v'
    ("s", "स"),
    ("h", "ह"),
    ("f", "फ"),
    ("z", "झ"),
    
    # Vowels (independent)
    ("A", "अ"),
    ("I", "इ"),
    ("U", "उ"),
    ("E", "ए"),
    ("O", "ओ"),
]


def roman_to_devanagari(text: str) -> str:
    """
    Convert Roman Marathi to Devanagari.
    
    This is a deterministic, conservative transliteration designed for
    dictionary key matching, not general-purpose transliteration.
    
    Args:
        text: Roman Marathi text
    
    Returns:
        Devanagari text (best effort)
    
    Limitations:
        - Not linguistically perfect
        - Ambiguous cases use first match
        - Designed for DB key matching primarily
    
    Examples:
        >>> roman_to_devanagari("pani")
        'पानी'
        >>> roman_to_devanagari("cha")
        'चा'
    """
    if not text:
        return text
    
    result = []
    i = 0
    
    while i < len(text):
        matched = False
        
        # Try longest match first
        for pattern_len in range(4, 0, -1):
            if i + pattern_len > len(text):
                continue
            
            substring = text[i:i + pattern_len]
            
            # Check if this substring matches any pattern
            for roman, devanagari in TRANSLITERATION_MAP:
                if substring.lower() == roman.lower():
                    result.append(devanagari)
                    i += pattern_len
                    matched = True
                    break
            
            if matched:
                break
        
        # If no match found, keep original character
        if not matched:
            result.append(text[i])
            i += 1
    
    return ''.join(result)
