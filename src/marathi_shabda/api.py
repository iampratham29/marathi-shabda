"""
Public API for marathi-pratham library.

Three main functions:
1. get_lemma() - Extract lemma from word
2. lookup_word() - Dictionary lookup
3. analyze_word() - Full morphological analysis
"""

from typing import List

from marathi_shabda.models import (
    LemmaResult,
    LookupResult,
    MorphologyResult,
    POSTag,
    ScriptType,
)
from marathi_shabda.dictionary import DictionaryAdapter
from marathi_shabda.normalization import normalize_input, detect_script
from marathi_shabda.morphology import extract_lemma as _extract_lemma
from marathi_shabda.inference import infer_pos, infer_kaal
from marathi_shabda.exceptions import InvalidInputError


# Global dictionary adapter (lazy initialization)
_dict_adapter: DictionaryAdapter | None = None


def _get_dict_adapter() -> DictionaryAdapter:
    """Get or create global dictionary adapter."""
    global _dict_adapter
    if _dict_adapter is None:
        _dict_adapter = DictionaryAdapter()
    return _dict_adapter


def get_lemma(word: str) -> LemmaResult:
    """
    Extract lemma (base form) from Marathi word.
    
    Args:
        word: Marathi word (Devanagari or Roman)
    
    Returns:
        LemmaResult with lemma, confidence, and metadata
    
    Raises:
        InvalidInputError: If input is empty or invalid
    
    Examples:
        >>> result = get_lemma("पाण्यावर")
        >>> print(result.lemma)
        'पाणी'
        >>> print(result.confidence)
        0.9
        >>> print(result.detected_vibhakti)
        VibhaktiType.SAPTAMI
    """
    if not word or not word.strip():
        raise InvalidInputError("Input word cannot be empty")
    
    # Normalize input (handles Roman → Devanagari)
    normalized = normalize_input(word)
    
    # Extract lemma using dictionary-first approach
    dict_adapter = _get_dict_adapter()
    return _extract_lemma(normalized, dict_adapter)


def lookup_word(word: str) -> LookupResult:
    """
    Look up word in dictionary (Marathi → English).
    
    Args:
        word: Marathi word (Devanagari or Roman)
    
    Returns:
        LookupResult with meanings and metadata
    
    Raises:
        InvalidInputError: If input is empty or invalid
    
    Examples:
        >>> result = lookup_word("पाणी")
        >>> print(result.english_meanings)
        ['water']
        >>> print(result.found)
        True
    """
    if not word or not word.strip():
        raise InvalidInputError("Input word cannot be empty")
    
    # Detect script
    script = detect_script(word)
    
    # Normalize input
    normalized = normalize_input(word)
    
    # Get lemma (to handle inflected forms)
    dict_adapter = _get_dict_adapter()
    lemma_result = _extract_lemma(normalized, dict_adapter)
    
    # Look up lemma in dictionary
    entry = dict_adapter.lookup_by_devanagari(lemma_result.lemma)
    
    if entry:
        return LookupResult(
            input=word,
            normalized=normalized,
            lemma=lemma_result.lemma,
            english_meanings=entry[0].english_meanings if entry else [],
            marathi_definition=entry[0].marathi_definition if entry else None,
            found=True,
            script_detected=script,
        )
    else:
        return LookupResult(
            input=word,
            normalized=normalized,
            lemma=lemma_result.lemma,
            english_meanings=[],
            marathi_definition=None,
            found=False,
            script_detected=script,
        )


def analyze_word(word: str) -> MorphologyResult:
    """
    Perform full morphological analysis of Marathi word.
    
    This includes:
    - Lemma extraction
    - POS tagging (conservative)
    - Vibhakti detection
    - Kāl inference (for verbs, if possible)
    
    Args:
        word: Marathi word (Devanagari or Roman)
    
    Returns:
        MorphologyResult with complete analysis
    
    Raises:
        InvalidInputError: If input is empty or invalid
    
    Examples:
        >>> result = analyze_word("मुलाने")
        >>> print(result.lemma)
        'मुल'
        >>> print(result.pos)
        POSTag.NOUN
        >>> print(result.vibhakti)
        VibhaktiType.TRUTIYA
        >>> print(result.explanation)
        'Detected तृतीया vibhakti, inferred noun from vibhakti'
    """
    if not word or not word.strip():
        raise InvalidInputError("Input word cannot be empty")
    
    # Normalize and extract lemma
    normalized = normalize_input(word)
    dict_adapter = _get_dict_adapter()
    lemma_result = _extract_lemma(normalized, dict_adapter)
    
    # Infer POS
    pos = infer_pos(lemma_result.lemma, lemma_result.detected_vibhakti)
    
    # Infer kāl (only for verbs)
    kaal = None
    if pos == POSTag.VERB:
        kaal = infer_kaal(normalized)
    
    # Build explanation
    explanation_parts = []
    
    if lemma_result.detected_vibhakti:
        explanation_parts.append(
            f"Detected {lemma_result.detected_vibhakti.value} vibhakti"
        )
    
    if pos != POSTag.UNKNOWN:
        explanation_parts.append(f"Inferred {pos.value}")
    
    if kaal:
        explanation_parts.append(f"Inferred {kaal.value}")
    
    if lemma_result.ambiguous:
        explanation_parts.append(
            f"Ambiguous ({len(lemma_result.candidates)} possible lemmas)"
        )
    
    if not explanation_parts:
        explanation_parts.append("No morphological features detected")
    
    explanation = "; ".join(explanation_parts)
    
    return MorphologyResult(
        input=word,
        lemma=lemma_result.lemma,
        pos=pos,
        vibhakti=lemma_result.detected_vibhakti,
        kaal=kaal,
        confidence=lemma_result.confidence,
        ambiguous=lemma_result.ambiguous,
        explanation=explanation,
    )
