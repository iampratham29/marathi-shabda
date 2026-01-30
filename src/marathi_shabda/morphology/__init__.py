"""Morphology package."""

from marathi_shabda.morphology.lemmatizer import extract_lemma
from marathi_shabda.morphology.vibhakti_rules import VibhaktiRule, VIBHAKTI_SUFFIXES

__all__ = [
    "extract_lemma",
    "VibhaktiRule",
    "VIBHAKTI_SUFFIXES",
]
