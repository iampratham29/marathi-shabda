"""
marathi-shabda: Deterministic, offline Marathi word analysis library.

shabda (शब्द) = word in Marathi

This library provides:
1. Lemma (stem) extraction from Marathi words
2. Dictionary lookup (Marathi ↔ English)
3. Morphological analysis (रूप परिचय)

Philosophy: When unsure, defer. When confident, explain why.
"""

__version__ = "0.1.0"

from marathi_shabda.api import get_lemma, lookup_word, analyze_word
from marathi_shabda.models import (
    LemmaResult,
    LookupResult,
    MorphologyResult,
    POSTag,
    VibhaktiType,
    KaalType,
)

__all__ = [
    # Main API functions
    "get_lemma",
    "lookup_word",
    "analyze_word",
    # Data models
    "LemmaResult",
    "LookupResult",
    "MorphologyResult",
    "POSTag",
    "VibhaktiType",
    "KaalType",
]
