import pytest
from unittest.mock import patch, MagicMock
from scripts.fetch_dictionary import (
    fetch_wiktionary_lemmas,
    fetch_apertium_dix,
    parse_apertium_dix
)

def test_fetch_wiktionary_lemmas():
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"query": {"categorymembers": [{"pageid": 1, "ns": 0, "title": "\u092a\u093e\u0923\u0940"}]}}'
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_response
        lemmas = fetch_wiktionary_lemmas(limit=5)
        assert lemmas == ["पाणी"]

def test_parse_apertium_dix():
    dix_content = """<?xml version="1.0" encoding="utf-8"?>
    <dictionary>
        <section id="main" type="standard">
            <e><p><l>पाणी<s n="n"/></l><r>water<s n="n"/></r></p></e>
            <e><p><l>घर<s n="n"/></l><r>house<s n="n"/></r></p></e>
        </section>
    </dictionary>
    """
    entries = parse_apertium_dix(dix_content)
    assert len(entries) == 2
    assert entries[0]["devanagari"] == "पाणी"
    assert entries[0]["meaning2"] == "water"
    assert entries[0]["pos"] == "noun"
    assert entries[0]["source"] == "apertium_mr"
