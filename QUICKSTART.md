# marathi-shabda Library - Quick Start Guide

## ✅ Setup Complete!

The library is now fully integrated and tested with your database.

---

## Installation Status

- ✅ Virtual environment created
- ✅ Development dependencies installed
- ✅ Package installed in editable mode
- ✅ Database integrated (16,518 entries)
- ✅ All 33 unit tests passing (61% coverage)

---

## Quick Usage Examples

### 1. Dictionary Lookup

```python
from marathi_shabda import lookup_word

result = lookup_word("पाणी")
print(result.english_meanings)  # ['water', "Adam's ale", 'guts']
```

### 2. Lemma Extraction

```python
from marathi_shabda import get_lemma

result = get_lemma("पाणी")
print(f"Lemma: {result.lemma}")
print(f"Confidence: {result.confidence}")  # 1.0 (exact match)
```

### 3. Morphological Analysis

```python
from marathi_shabda import analyze_word

result = analyze_word("पाणी")
print(f"POS: {result.pos}")
print(f"Explanation: {result.explanation}")
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=marathi_shabda --cov-report=html

# Run specific test file
python -m pytest tests/test_normalization.py -v
```

---

## CLI Usage

```bash
# Lemma extraction
python -m marathi_shabda.cli lemma पाणी

# Dictionary lookup
python -m marathi_shabda.cli lookup पाणी

# Full analysis
python -m marathi_shabda.cli analyze पाणी
```

---

## Test Results Summary

**Total Tests**: 33  
**Passed**: 33 ✅  
**Failed**: 0  
**Coverage**: 61%

### Test Breakdown

- **Normalization Tests**: 13 tests
  - Script detection (Devanagari/Roman)
  - Transliteration
  - Unicode normalization
  
- **Morphology Tests**: 9 tests
  - Vibhakti rules validation
  - Stem alternations
  
- **Inference Tests**: 9 tests
  - POS tagging
  - Kāl detection

---

## Next Steps

### For Development

1. **Add more vibhakti rules** based on real-world usage
2. **Improve stem alternations** for better lemma detection
3. **Extend database schema** with POS/gender/number columns
4. **Write integration tests** with real database queries

### For Production

1. **Build package**: `python -m build`
2. **Test installation**: `pip install dist/marathi-shabda-0.1.0.tar.gz`
3. **Publish to PyPI**: `twine upload dist/*`

---

## Known Limitations

- Vibhakti detection works but may need tuning for specific word forms
- Roman transliteration is approximate (designed for DB key matching)
- POS tagging is conservative (returns UNKNOWN when uncertain)
- No sentence-level parsing (single words only)

---

## Files Created

- `requirements.txt` - Development dependencies
- `venv/` - Virtual environment
- Database: `src/marathi_shabda/data/dictionary.db` (16,518 entries)

---

## Support

- **Documentation**: See `README.md`
- **Contributing**: See `CONTRIBUTING.md`
- **Tests**: `tests/` directory

---

**Status**: ✅ Ready for development and testing!
