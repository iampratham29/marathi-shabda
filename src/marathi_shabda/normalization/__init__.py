"""Normalization package."""

from marathi_shabda.normalization.script_detection import detect_script
from marathi_shabda.normalization.transliterator import (
    roman_to_devanagari,
    dev_to_roman,
    roman_to_dev,
    transliterate,
    to_roman,
    to_devanagari,
    VOWEL_LETTERS,
    VOWEL_SIGNS,
    CONSONANTS,
)
from marathi_shabda.normalization.safe_normalizer import safe_normalize, normalize_input

__all__ = [
    # Script detection
    "detect_script",
    # Pratham Transliteration Style — bidirectional
    "dev_to_roman",
    "roman_to_dev",
    "transliterate",
    "to_roman",
    "to_devanagari",
    # Mapping tables (single source of truth)
    "VOWEL_LETTERS",
    "VOWEL_SIGNS",
    "CONSONANTS",
    # Legacy one-shot Roman → Devanagari (used by normalize_input)
    "roman_to_devanagari",
    # Safe normalization
    "safe_normalize",
    "normalize_input",
]

