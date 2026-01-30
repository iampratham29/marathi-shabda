"""
Kāl (tense) inference for verbs.

Philosophy: Very limited in v0.1.0. Return None if uncertain.
"""

from typing import Optional

from marathi_shabda.models import KaalType


# Tense markers (very conservative)
BHOOTKAAL_MARKERS = ["ला", "ली", "ले", "लो", "लं"]  # Past tense
VARTAMAANKAAL_MARKERS = ["तो", "ते", "ती", "तात"]  # Present tense
BHAVISHYAKAAL_MARKERS = ["ईल", "तील", "णार"]  # Future tense


def infer_kaal(verb_form: str) -> Optional[KaalType]:
    """
    Infer kāl (tense) from verb form.
    
    This is extremely conservative in v0.1.0. Only detects obvious patterns.
    Returns None for most cases.
    
    Args:
        verb_form: Verb form to analyze
    
    Returns:
        KaalType if confident, None otherwise
    """
    if not verb_form:
        return None
    
    # Check past tense markers
    for marker in BHOOTKAAL_MARKERS:
        if verb_form.endswith(marker):
            return KaalType.BHOOTKAAL
    
    # Check present tense markers
    for marker in VARTAMAANKAAL_MARKERS:
        if verb_form.endswith(marker):
            return KaalType.VARTAMAANKAAL
    
    # Check future tense markers
    for marker in BHAVISHYAKAAL_MARKERS:
        if verb_form.endswith(marker):
            return KaalType.BHAVISHYAKAAL
    
    # Default: uncertain
    return None
