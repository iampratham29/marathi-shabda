"""
Lemma extraction engine.

Philosophy: Rules generate candidates. Dictionary validates truth.
"""

from typing import List, Optional

from marathi_shabda.models import LemmaResult, VibhaktiType
from marathi_shabda.dictionary import DictionaryAdapter
from marathi_shabda.normalization import safe_normalize
from marathi_shabda.morphology.vibhakti_rules import get_vibhakti_rules_sorted
from marathi_shabda.morphology.stem_alternations import apply_stem_alternations
from marathi_shabda.morphology.exceptions import IRREGULAR_STEMS


def extract_lemma(
    word: str,
    dict_adapter: DictionaryAdapter
) -> LemmaResult:
    """
    Extract lemma from Marathi word using dictionary-first validation.
    
    Algorithm:
        1. Normalize input
        2. Check if word exists as-is in dictionary → return immediately (confidence=1.0)
        3. Try vibhakti detection (longest-first)
        4. For each detected vibhakti:
           - Strip suffix → candidate
           - Apply stem alternations → multiple candidates
           - Check each candidate in dictionary
           - If found → return with confidence=0.9
        5. If no match → return original word (confidence=0.0)
    
    Args:
        word: Marathi word (Devanagari)
        dict_adapter: Dictionary adapter instance
    
    Returns:
        LemmaResult with lemma, confidence, and metadata
    """
    # Step 1: Normalize
    normalized = safe_normalize(word)
    
    if not normalized:
        return LemmaResult(
            original=word,
            lemma=word,
            confidence=0.0,
            explanation="Empty input after normalization"
        )
    
    # Step 2: Dictionary-first check
    if dict_adapter.exists(normalized):
        return LemmaResult(
            original=word,
            lemma=normalized,
            confidence=1.0,
            detected_vibhakti=None,
            ambiguous=False,
            candidates=[normalized],
            explanation="Exact dictionary match"
        )
    
    # Step 3 & 4: Try vibhakti detection
    vibhakti_rules = get_vibhakti_rules_sorted()
    all_candidates: List[tuple[str, VibhaktiType]] = []
    
    for rule in vibhakti_rules:
        if normalized.endswith(rule.suffix):
            # Strip suffix
            candidate_stem = normalized[:-len(rule.suffix)]
            
            if not candidate_stem:  # Don't strip entire word
                continue
            
            # 3a. Check for irregular stem exceptions
            if candidate_stem in IRREGULAR_STEMS:
                exception_lemma = IRREGULAR_STEMS[candidate_stem]
                # Verify mapped lemma exists in dictionary
                if dict_adapter.exists(exception_lemma):
                    all_candidates.append((exception_lemma, rule.vibhakti_type))
                    # If we found an exception match, we might want to prioritize it
                    # But for now, let's treat it as a strong candidate
            
            # Apply stem alternations
            stem_variants = apply_stem_alternations(candidate_stem)
            
            # Check each variant in dictionary
            for variant in stem_variants:
                if dict_adapter.exists(variant):
                    all_candidates.append((variant, rule.vibhakti_type))
    
    # Step 5: Return best candidate or original
    if all_candidates:
        # Check for ambiguity
        unique_lemmas = list(set(c[0] for c in all_candidates))
        ambiguous = len(unique_lemmas) > 1
        
        # Use first match (highest priority rule)
        best_lemma, detected_vibhakti = all_candidates[0]
        
        explanation = f"Detected {detected_vibhakti.value} vibhakti"
        if ambiguous:
            explanation += f" (ambiguous: {len(unique_lemmas)} possible lemmas)"
        
        return LemmaResult(
            original=word,
            lemma=best_lemma,
            confidence=0.9 if not ambiguous else 0.7,
            detected_vibhakti=detected_vibhakti,
            ambiguous=ambiguous,
            candidates=unique_lemmas,
            explanation=explanation
        )
    
    # No match found
    return LemmaResult(
        original=word,
        lemma=normalized,
        confidence=0.0,
        detected_vibhakti=None,
        ambiguous=False,
        candidates=[normalized],
        explanation="No vibhakti detected, word not in dictionary"
    )
