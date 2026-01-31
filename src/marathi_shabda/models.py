"""Data models for marathi-pratham library."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ScriptType(Enum):
    """Script detection types."""
    DEVANAGARI = "devanagari"
    ROMAN = "roman"
    UNKNOWN = "unknown"


class POSTag(Enum):
    """Part-of-speech tags (conservative)."""
    NOUN = "noun"  # नाम
    PRONOUN = "pronoun"  # सर्वनाम
    VERB = "verb"  # क्रियापद
    ADJECTIVE = "adjective"  # विशेषण
    ADVERB = "adverb"  # क्रियाविशेषण
    POSTPOSITION = "postposition"  # परसर्ग
    CONJUNCTION = "conjunction"  # उभयान्वयी अव्यय
    INTERJECTION = "interjection"  # केवलप्रयोगी अव्यय
    INDECLINABLE = "indeclinable"  # अव्यय
    UNKNOWN = "unknown"


class VibhaktiType(Enum):
    """Vibhakti (case) types in Marathi grammar."""
    PRATHAMA = "प्रथमा"  # Nominative (कर्ता)
    DVITIYA = "द्वितीया"  # Accusative (कर्म)
    TRUTIYA = "तृतीया"  # Instrumental (करण)
    CHATURTHI = "चतुर्थी"  # Dative (संप्रदान)
    PANCHAMI = "पंचमी"  # Ablative (अपादान)
    SHASHTHI = "षष्ठी"  # Genitive (संबोधन)
    SAPTAMI = "सप्तमी"  # Locative (अधिकरण)
    SAMBODHANA = "संबोधन"  # Vocative


class KaalType(Enum):
    """Kāl (tense) types for verbs."""
    BHOOTKAAL = "भूतकाळ"  # Past tense
    VARTAMAANKAAL = "वर्तमानकाळ"  # Present tense
    BHAVISHYAKAAL = "भविष्यकाळ"  # Future tense


@dataclass
class DictionaryEntry:
    """Entry from the dictionary database."""
    roman_key: str
    devanagari: str
    english_meanings: List[str]
    marathi_definition: Optional[str] = None
    pos: Optional[POSTag] = None  # Future: when DB schema extended
    gender: Optional[str] = None  # Future
    number: Optional[str] = None  # Future


@dataclass
class LemmaResult:
    """Result of lemma extraction."""
    original: str
    lemma: str
    confidence: float  # 0.0 to 1.0
    detected_vibhakti: Optional[VibhaktiType] = None
    ambiguous: bool = False
    candidates: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class LookupResult:
    """Result of dictionary lookup."""
    input: str
    normalized: str
    lemma: str
    english_meanings: List[str]
    marathi_definition: Optional[str]
    found: bool
    script_detected: ScriptType = ScriptType.UNKNOWN


@dataclass
class MorphologyResult:
    """Result of full morphological analysis."""
    input: str
    lemma: str
    pos: POSTag
    vibhakti: Optional[VibhaktiType] = None
    kaal: Optional[KaalType] = None
    confidence: float = 0.0
    ambiguous: bool = False
    explanation: str = ""
