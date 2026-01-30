"""
POS (Part-of-Speech) inference.

Philosophy: Conservative inference. When unsure, defer.
"""

from typing import Optional

from marathi_shabda.models import POSTag, VibhaktiType


# Common verb endings (very conservative list)
VERB_ENDINGS = [
    "तो", "ते", "ती",  # Present tense markers
    "ला", "ली", "ले",  # Past tense markers
    "तात", "तील",      # Future/continuous
    "ायचा", "ायची", "ायचे",  # Infinitive-like
]

# Common indeclinable words
INDECLINABLES = {
    "आणि", "पण", "किंवा", "तर", "म्हणून",  # Conjunctions
    "अरे", "अहो", "वा",  # Interjections
    "खूप", "फार", "थोडे",  # Adverbs
}


def infer_pos(
    lemma: str,
    vibhakti: Optional[VibhaktiType] = None
) -> POSTag:
    """
    Infer POS tag from lemma and vibhakti.
    
    This is a conservative heuristic for v0.1.0. Will be replaced with
    dictionary lookup when POS column is added to database.
    
    Args:
        lemma: Lemma (base form)
        vibhakti: Detected vibhakti (if any)
    
    Returns:
        POSTag (defaults to UNKNOWN if uncertain)
    
    Heuristics:
        - If vibhakti detected → likely NOUN
        - If ends in common verb suffix → VERB
        - If in indeclinable list → INDECLINABLE
        - Else → UNKNOWN
    """
    # Check indeclinables first
    if lemma in INDECLINABLES:
        return POSTag.INDECLINABLE
    
    # If vibhakti detected, likely a noun
    if vibhakti is not None:
        # Exception: संबोधन can be used with names/pronouns
        if vibhakti == VibhaktiType.SAMBODHANA:
            return POSTag.NOUN  # Conservative: treat as noun
        return POSTag.NOUN
    
    # Check for verb endings
    for ending in VERB_ENDINGS:
        if lemma.endswith(ending):
            return POSTag.VERB
    
    # Default: unknown
    return POSTag.UNKNOWN
