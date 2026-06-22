import pytest
import tempfile
from pathlib import Path
from marathi_shabda.dictionary import DictionaryAdapter
from marathi_shabda.models import POSTag

def test_dictionary_adapter_basic_operations():
    # Use in-memory DB (DictionaryAdapter special casing sets up schema)
    adapter = DictionaryAdapter(db_path=":memory:")
    
    # 1. Test insert_word
    entry1 = {
        "key": "ghar",
        "devanagari": "घर",
        "meaning2": "house",
        "definition_mr": "राहण्याचे ठिकाण",
        "pos": POSTag.NOUN,
        "source": "wiktionary"
    }
    
    assert adapter.insert_word(entry1) is True
    # Duplicate insert should return False
    assert adapter.insert_word(entry1) is False
    
    # 2. Test exists
    assert adapter.exists("घर") is True
    assert adapter.exists("ghar") is True
    assert adapter.exists("other") is False
    
    # 3. Test lookup_by_roman
    lookup1 = adapter.lookup_by_roman("ghar")
    assert lookup1 is not None
    assert lookup1.devanagari == "घर"
    assert lookup1.english_meanings == ["house"]
    assert lookup1.marathi_definition == "राहण्याचे ठिकाण"
    assert lookup1.pos == POSTag.NOUN
    
    # 4. Test lookup_by_devanagari
    lookup2 = adapter.lookup_by_devanagari("घर")
    assert len(lookup2) == 1
    assert lookup2[0].roman_key == "ghar"
    
    # 5. Test missing roman / english
    # Insert entry missing roman
    entry2 = {
        "key": "",
        "devanagari": "झाड",
        "meaning2": "tree"
    }
    assert adapter.insert_word(entry2) is True
    assert "झाड" in adapter.get_words_missing_roman()
    
    # Insert entry missing english
    entry3 = {
        "key": "फूल",
        "devanagari": "फूल",
        "meaning2": ""
    }
    assert adapter.insert_word(entry3) is True
    assert "फूल" in adapter.get_words_missing_english()

def test_dictionary_adapter_export_sql():
    adapter = DictionaryAdapter(db_path=":memory:")
    entry = {
        "key": "pani",
        "devanagari": "पाणी",
        "meaning2": "water"
    }
    adapter.insert_word(entry)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        sql_path = Path(temp_dir) / "dump.sql"
        adapter.export_sql(str(sql_path))
        
        assert sql_path.exists()
        content = sql_path.read_text(encoding="utf-8")
        assert "पाणी" in content
        assert "pani" in content
        assert "MarathiEnglish" in content
