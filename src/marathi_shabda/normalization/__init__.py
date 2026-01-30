"""Normalization package."""

from marathi_shabda.normalization.script_detection import detect_script
from marathi_shabda.normalization.transliterator import roman_to_devanagari
from marathi_shabda.normalization.safe_normalizer import safe_normalize, normalize_input

__all__ = [
    "detect_script",
    "roman_to_devanagari",
    "safe_normalize",
    "normalize_input",
]
