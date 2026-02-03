"""Tests for morphology module."""

import pytest

from marathi_shabda.models import VibhaktiType
from marathi_shabda.morphology.vibhakti_rules import (
    VibhaktiRule,
    VIBHAKTI_SUFFIXES,
    get_vibhakti_rules_sorted,
)
from marathi_shabda.morphology.stem_alternations import apply_stem_alternations


class TestVibhaktiRules:
    """Test vibhakti detection rules."""
    
    def test_rules_exist(self):
        """Test that vibhakti rules are defined."""
        assert len(VIBHAKTI_SUFFIXES) > 0
    
    def test_rules_have_required_fields(self):
        """Test that all rules have required fields."""
        for rule in VIBHAKTI_SUFFIXES:
            assert isinstance(rule.suffix, str)
            assert isinstance(rule.vibhakti_type, VibhaktiType)
            assert isinstance(rule.priority, int)
            assert len(rule.suffix) > 0
    
    def test_sorted_rules(self):
        """Test that rules are sorted correctly."""
        sorted_rules = get_vibhakti_rules_sorted()
        
        # Check that rules are sorted by priority, then length
        for i in range(len(sorted_rules) - 1):
            curr = sorted_rules[i]
            next_rule = sorted_rules[i + 1]
            
            # If same priority, longer suffix should come first
            if curr.priority == next_rule.priority:
                assert len(curr.suffix) >= len(next_rule.suffix)
    
    def test_common_vibhaktis_present(self):
        """Test that common vibhaktis are in the rules."""
        suffixes = [rule.suffix for rule in VIBHAKTI_SUFFIXES]
        
        # Check for common vibhaktis
        assert "ने" in suffixes  # तृतीया
        assert "ला" in suffixes  # चतुर्थी
        assert "वर" in suffixes  # सप्तमी
        assert "मध्ये" in suffixes  # सप्तमी


class TestStemAlternations:
    """Test stem alternation rules."""
    
    def test_basic_alternation(self):
        """Test basic stem alternations."""
        candidates = apply_stem_alternations("पाण्य")
        
        # Should include original
        assert "पाण्य" in candidates
        
        # Should have multiple candidates
        assert len(candidates) > 1
    
    def test_no_alternation_needed(self):
        """Test words that don't need alternation."""
        candidates = apply_stem_alternations("पाणी")
        
        # Should at least include original
        assert "पाणी" in candidates
    
    def test_empty_input(self):
        """Test with empty input."""
        candidates = apply_stem_alternations("")
        assert "" in candidates
    
    def test_oblique_forms(self):
        """Test oblique form alternations."""
        # Test removal of oblique markers
        candidates = apply_stem_alternations("मुला")
        assert "मुला" in candidates
        
        # Should generate alternations
        assert len(candidates) >= 1

    
    def test_mulacha_stems(self):
        """Test specific stems for मुलाचा problem."""
        candidates = apply_stem_alternations("मुलासाठी")
        print(candidates)
        assert "मुलगा" in candidates
        assert "मूल" in candidates


# Note: Full lemmatizer tests require a real database
# These will be integration tests once database is provided
class TestLemmatizerStub:
    """Stub tests for lemmatizer (requires database)."""
    
    def test_placeholder(self):
        """Placeholder test."""
        # TODO: Add integration tests once database is provided
        assert True
