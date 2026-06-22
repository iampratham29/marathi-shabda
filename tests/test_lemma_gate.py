from unittest.mock import patch
import pytest
from marathi_shabda.dictionary import DictionaryAdapter
from marathi_shabda.models import LemmaResult

def test_inflected_word_not_inserted():
    """Inserting पाण्यावर should store पाणी (lemma), not पाण्यावर."""
    adapter = DictionaryAdapter(db_path=":memory:")
    
    # Mock get_lemma to return "पाणी" for "पाण्यावर"
    with patch("marathi_shabda.api.get_lemma") as mock_get_lemma:
        mock_get_lemma.return_value = LemmaResult(
            original="पाण्यावर",
            lemma="पाणी",
            confidence=0.9,
            explanation="Mocked lemma"
        )
        
        adapter.bulk_insert([{"devanagari": "पाण्यावर", "meaning2": "on the water"}])
        
        assert not adapter.exists("पाण्यावर")  # inflected form must NOT be in DB
        assert adapter.exists("पाणी")          # only lemma stored
