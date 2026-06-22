"""
tests/test_bulk_fetchers.py
Unit tests for the Phase 1 and Phase 2 bulk fetcher scripts.
Uses in-memory fixtures — no network calls.
"""

import json
import sys
import tempfile
from io import StringIO
from pathlib import Path
import pytest

# ---------------------------------------------------------------------------
# Import helpers from scripts/ without running main()
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import fetch_kaikki  # type: ignore
import fetch_glossaries  # type: ignore


# ===========================================================================
# Phase 1 — Kaikki parser tests
# ===========================================================================

KAIKKI_FIXTURE_JSONL = """\
{"word": "पाणी", "pos": "noun", "senses": [{"glosses": ["water"]}], "lang": "Marathi"}
{"word": "मुलगा", "pos": "noun", "senses": [{"glosses": ["boy", "son"]}], "lang": "Marathi"}
{"word": "hello", "pos": "noun", "senses": [{"glosses": ["greeting"]}], "lang": "Marathi"}
{"word": "पाणी", "pos": "noun", "senses": [{"glosses": ["duplicate entry"]}], "lang": "Marathi"}
{"word": "जाणे", "pos": "verb", "senses": [{"glosses": ["to go"]}], "lang": "Marathi"}
{"word": "सुंदर", "pos": "adj", "senses": [{"glosses": ["beautiful"]}], "lang": "Marathi"}
{"word": "", "pos": "noun", "senses": [], "lang": "Marathi"}
"""

KAIKKI_FIXTURE_ARRAY = json.dumps([
    {"word": "पाणी", "pos": "noun", "senses": [{"glosses": ["water"]}]},
    {"word": "मुलगा", "pos": "noun", "senses": [{"glosses": ["boy"]}]},
])


class TestKaikkiParser:
    """Tests for fetch_kaikki.parse_kaikki()"""

    def _write_fixture(self, content: str, suffix=".json") -> Path:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=suffix, delete=False
        ) as f:
            f.write(content)
            return Path(f.name)

    def test_parses_jsonl_devanagari(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        words = {e["devanagari"] for e in entries}
        assert "पाणी" in words
        assert "मुलगा" in words
        assert "जाणे" in words
        assert "सुंदर" in words
        raw.unlink()

    def test_filters_non_devanagari(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        words = [e["devanagari"] for e in entries]
        assert "hello" not in words
        raw.unlink()

    def test_deduplicates(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        words = [e["devanagari"] for e in entries]
        assert words.count("पाणी") == 1  # duplicate removed
        raw.unlink()

    def test_gloss_extracted(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        pani = next(e for e in entries if e["devanagari"] == "पाणी")
        assert pani["meaning2"] == "water"
        raw.unlink()

    def test_pos_normalized(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        jane = next(e for e in entries if e["devanagari"] == "जाणे")
        assert jane["pos"] == "verb"
        sundar = next(e for e in entries if e["devanagari"] == "सुंदर")
        assert sundar["pos"] == "adjective"
        raw.unlink()

    def test_source_tag(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        assert all(e["source"] == "kaikki_wiktionary" for e in entries)
        raw.unlink()

    def test_key_initially_empty(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        # Roman key is not set by the fetcher — left for enrich_roman.py
        assert all(e["key"] == "" for e in entries)
        raw.unlink()

    def test_parses_json_array_format(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_ARRAY)
        entries = fetch_kaikki.parse_kaikki(raw)
        words = {e["devanagari"] for e in entries}
        assert "पाणी" in words
        assert "मुलगा" in words
        raw.unlink()

    def test_empty_word_skipped(self):
        raw = self._write_fixture(KAIKKI_FIXTURE_JSONL)
        entries = fetch_kaikki.parse_kaikki(raw)
        assert not any(e["devanagari"] == "" for e in entries)
        raw.unlink()

    def test_normalize_pos_unknown(self):
        assert fetch_kaikki.normalize_pos("xyz_unknown") == "unknown"

    def test_normalize_pos_known_variants(self):
        assert fetch_kaikki.normalize_pos("adj") == "adjective"
        assert fetch_kaikki.normalize_pos("vblex") == "unknown"  # Kaikki uses 'verb'
        assert fetch_kaikki.normalize_pos("NOUN") == "noun"




# ===========================================================================
# is_devanagari helper tests (shared logic)
# ===========================================================================

class TestIsDevanagari:
    def test_pure_devanagari(self):
        assert fetch_kaikki.is_devanagari("पाणी") is True

    def test_pure_latin(self):
        assert fetch_kaikki.is_devanagari("hello") is False

    def test_mixed(self):
        assert fetch_kaikki.is_devanagari("pani पाणी") is True

    def test_empty(self):
        assert fetch_kaikki.is_devanagari("") is False

    def test_number_only(self):
        assert fetch_kaikki.is_devanagari("123") is False
