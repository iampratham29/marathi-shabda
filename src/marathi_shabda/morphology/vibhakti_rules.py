"""Vibhakti detection rules for Marathi."""

from dataclasses import dataclass
from typing import List

from marathi_shabda.models import VibhaktiType


@dataclass
class VibhaktiRule:
    """Rule for detecting vibhakti suffix."""
    suffix: str
    vibhakti_type: VibhaktiType
    priority: int  # Lower = higher priority


# Vibhakti suffix rules (LONGEST FIRST - critical for correct detection)
VIBHAKTI_SUFFIXES: List[VibhaktiRule] = [
    # Three+ character suffixes (highest priority)
    VibhaktiRule("मध्ये", VibhaktiType.SAPTAMI, 1),
    VibhaktiRule("पासून", VibhaktiType.PANCHAMI, 1),
    VibhaktiRule("साठी", VibhaktiType.CHATURTHI, 1),
    VibhaktiRule("विषयी", VibhaktiType.SAPTAMI, 1),
    VibhaktiRule("बद्दल", VibhaktiType.SAPTAMI, 1),
    VibhaktiRule("सारखा", VibhaktiType.TRUTIYA, 1),
    VibhaktiRule("सारखी", VibhaktiType.TRUTIYA, 1),
    VibhaktiRule("सारखे", VibhaktiType.TRUTIYA, 1),
    
    # Oblique + vibhakti combinations (common patterns)
    VibhaktiRule("ावर", VibhaktiType.SAPTAMI, 1),   # Oblique + locative
    VibhaktiRule("ाला", VibhaktiType.CHATURTHI, 1), # Oblique + dative
    VibhaktiRule("ाने", VibhaktiType.TRUTIYA, 1),   # Oblique + instrumental
    VibhaktiRule("ाशी", VibhaktiType.SAPTAMI, 1),   # Oblique + locative
    VibhaktiRule("ात", VibhaktiType.SAPTAMI, 1),    # Oblique + locative
    
    # Two-character suffixes
    VibhaktiRule("ने", VibhaktiType.TRUTIYA, 2),  # करण vibhakti
    VibhaktiRule("वर", VibhaktiType.SAPTAMI, 2),  # अधिकरण
    VibhaktiRule("ला", VibhaktiType.CHATURTHI, 2),  # संप्रदान
    VibhaktiRule("शी", VibhaktiType.SAPTAMI, 2),
    VibhaktiRule("ची", VibhaktiType.SAMBANDH, 2),  # संबोधन (feminine)
    VibhaktiRule("चा", VibhaktiType.SAMBANDH, 2),  # संबोधन (masculine)
    VibhaktiRule("चे", VibhaktiType.SAMBANDH, 2),  # संबोधन (neuter/plural)
    VibhaktiRule("त", VibhaktiType.SAPTAMI, 2),   # अधिकरण
    VibhaktiRule("स", VibhaktiType.CHATURTHI, 2),
    
    # Single-character suffixes (lowest priority)
    VibhaktiRule("ं", VibhaktiType.DVITIYA, 3),  # कर्म vibhakti (rare)
    VibhaktiRule("े", VibhaktiType.SAMBODHANA, 3),  # संबोधन
    VibhaktiRule("ा", VibhaktiType.PRATHAMA, 3),  # Often just masculine form
    VibhaktiRule("ी", VibhaktiType.PRATHAMA, 3),  # Often just feminine form
    
    # Oblique forms (common in compound vibhaktis)
    VibhaktiRule("ांना", VibhaktiType.CHATURTHI, 1),  # Plural dative
    VibhaktiRule("ांनी", VibhaktiType.TRUTIYA, 1),   # Plural instrumental
    VibhaktiRule("ांचा", VibhaktiType.SAMBANDH, 1),  # Plural possessive (masc)
    VibhaktiRule("ांची", VibhaktiType.SAMBANDH, 1),  # Plural possessive (fem)
    VibhaktiRule("ांचे", VibhaktiType.SAMBANDH, 1),  # Plural possessive (neut)
    VibhaktiRule("ांवर", VibhaktiType.SAPTAMI, 1),   # Plural locative
    VibhaktiRule("ांत", VibhaktiType.SAPTAMI, 1),    # Plural locative
]


def get_vibhakti_rules_sorted() -> List[VibhaktiRule]:
    """
    Get vibhakti rules sorted by priority and length.
    
    Returns:
        Sorted list of VibhaktiRule objects
    """
    # Sort by: 1) priority (ascending), 2) length (descending)
    return sorted(
        VIBHAKTI_SUFFIXES,
        key=lambda r: (r.priority, -len(r.suffix))
    )
