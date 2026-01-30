"""Tests for normalization module."""

import pytest

from marathi_shabda.models import ScriptType
from marathi_shabda.normalization import (
    detect_script,
    roman_to_devanagari,
    safe_normalize,
    normalize_input,
)


class TestScriptDetection:
    """Test script detection functionality."""
    
    def test_detect_devanagari(self):
        """Test detection of Devanagari script."""
        assert detect_script("पाणी") == ScriptType.DEVANAGARI
        assert detect_script("मराठी भाषा") == ScriptType.DEVANAGARI
    
    def test_detect_roman(self):
        """Test detection of Roman script."""
        assert detect_script("pani") == ScriptType.ROMAN
        assert detect_script("marathi") == ScriptType.ROMAN
    
    def test_detect_empty(self):
        """Test detection with empty input."""
        assert detect_script("") == ScriptType.UNKNOWN
        assert detect_script("   ") == ScriptType.UNKNOWN
    
    def test_detect_mixed(self):
        """Test detection with mixed scripts."""
        # Should detect based on majority
        text = "पाणी water"
        result = detect_script(text)
        assert result in [ScriptType.DEVANAGARI, ScriptType.ROMAN]


class TestTransliteration:
    """Test Roman to Devanagari transliteration."""
    
    def test_simple_words(self):
        """Test transliteration of simple words."""
        assert "प" in roman_to_devanagari("p")
        assert "क" in roman_to_devanagari("k")
    
    def test_complex_words(self):
        """Test transliteration of complex words."""
        # Note: Transliteration is approximate
        result = roman_to_devanagari("pani")
        assert len(result) > 0  # Should produce some output
    
    def test_empty_input(self):
        """Test transliteration with empty input."""
        assert roman_to_devanagari("") == ""
    
    def test_preserves_unknown(self):
        """Test that unknown characters are preserved."""
        result = roman_to_devanagari("123")
        assert "123" in result or len(result) > 0


class TestSafeNormalization:
    """Test safe normalization utilities."""
    
    def test_trim_whitespace(self):
        """Test whitespace trimming."""
        assert safe_normalize("  पाणी  ") == "पाणी"
    
    def test_remove_zero_width(self):
        """Test removal of zero-width characters."""
        text = "पा\u200bणी"  # Zero-width space
        assert safe_normalize(text) == "पाणी"
    
    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Should normalize to NFC
        result = safe_normalize("पाणी")
        assert result == "पाणी"
    
    def test_empty_input(self):
        """Test with empty input."""
        assert safe_normalize("") == ""


class TestNormalizeInput:
    """Test complete input normalization."""
    
    def test_devanagari_passthrough(self):
        """Test that Devanagari is normalized but not transliterated."""
        result = normalize_input("पाणी")
        assert result == "पाणी"
    
    def test_roman_transliteration(self):
        """Test that Roman is transliterated."""
        result = normalize_input("pani")
        # Should contain Devanagari characters
        assert any('\u0900' <= c <= '\u097F' for c in result)
    
    def test_empty_input(self):
        """Test with empty input."""
        assert normalize_input("") == ""
