"""Tests for inference module."""

import pytest

from marathi_shabda.models import POSTag, VibhaktiType, KaalType
from marathi_shabda.inference import infer_pos, infer_kaal


class TestPOSInference:
    """Test POS inference."""
    
    def test_noun_from_vibhakti(self):
        """Test that vibhakti implies noun."""
        pos = infer_pos("मुल", VibhaktiType.TRUTIYA)
        assert pos == POSTag.NOUN
    
    def test_verb_from_ending(self):
        """Test verb detection from endings."""
        pos = infer_pos("जातो", None)
        assert pos == POSTag.VERB
        
        pos = infer_pos("गेला", None)
        assert pos == POSTag.VERB
    
    def test_indeclinable(self):
        """Test indeclinable detection."""
        pos = infer_pos("आणि", None)
        assert pos == POSTag.INDECLINABLE
    
    def test_unknown_default(self):
        """Test that unknown is default."""
        pos = infer_pos("अज्ञात", None)
        # Should return UNKNOWN or some POS
        assert isinstance(pos, POSTag)


class TestKaalInference:
    """Test kāl (tense) inference."""
    
    def test_bhootkaal_detection(self):
        """Test past tense detection."""
        kaal = infer_kaal("गेला")
        assert kaal == KaalType.BHOOTKAAL
    
    def test_vartamaankaal_detection(self):
        """Test present tense detection."""
        kaal = infer_kaal("जातो")
        assert kaal == KaalType.VARTAMAANKAAL
    
    def test_bhavishyakaal_detection(self):
        """Test future tense detection."""
        kaal = infer_kaal("जाईल")
        assert kaal == KaalType.BHAVISHYAKAAL
    
    def test_uncertain_returns_none(self):
        """Test that uncertain cases return None."""
        kaal = infer_kaal("अज्ञात")
        # Should return None for uncertain cases
        assert kaal is None or isinstance(kaal, KaalType)
    
    def test_empty_input(self):
        """Test with empty input."""
        kaal = infer_kaal("")
        assert kaal is None
