"""Stem alternation rules for Marathi."""

from typing import List


# Known stem alternation patterns
# Format: (pattern_to_replace, replacement)
STEM_ALTERNATIONS = [
    # ण्य → णी pattern (common in oblique forms)
    ("ण्य", "णी"),  # पाण्य → पाणी
    
    # य → ई pattern
    ("य", "ई"),  # पापण्य → पापणी (after ण्य → णी)
    
    # Oblique to direct forms
    ("ा", ""),   # Remove final ा (masculine oblique)
    ("ी", ""),   # Remove final ी (feminine oblique)
    ("े", ""),   # Remove final े (neuter oblique)
    
    # Common consonant clusters
    ("्य", "ी"),  # General य-ending oblique
    
    # Vowel lengthening (Reverse Upantya Swar)
    ("ु", "ू"),  # Short u -> Long uu (e.g. मुल -> मूल)
    ("ि", "ी"),  # Short i -> Long ii (e.g. मिळ -> मीळ)

    # Oblique to direct (specific endings)
    ("ा", "गा"), # Oblique ending in 'aa' -> 'ga' (mul -> mulga)
]


def apply_stem_alternations(candidate: str) -> List[str]:
    """
    Apply known stem alternation rules to generate possible lemmas.
    
    Args:
        candidate: Candidate stem after suffix removal
    
    Returns:
        List of possible stems (includes original candidate)
    
    Examples:
        >>> apply_stem_alternations("पाण्य")
        ['पाण्य', 'पाणी']
        >>> apply_stem_alternations("मुला")
        ['मुला', 'मुल']
    """
    candidates = [candidate]  # Always include original
    
    for pattern, replacement in STEM_ALTERNATIONS:
        if pattern in candidate:
            # Apply this alternation
            new_candidate = candidate.replace(pattern, replacement, 1)
            if new_candidate and new_candidate not in candidates:
                candidates.append(new_candidate)
    
    # Also try combinations (e.g., ण्य → णी, then remove ी)
    # This handles cases like पाण्यावर → पाण्य → पाणी → पाण
    additional = []
    for cand in candidates[:]:  # Iterate over copy
        for pattern, replacement in STEM_ALTERNATIONS:
            if pattern in cand:
                new_cand = cand.replace(pattern, replacement, 1)
                if new_cand and new_cand not in candidates and new_cand not in additional:
                    additional.append(new_cand)
    
    candidates.extend(additional)
    
    return candidates
