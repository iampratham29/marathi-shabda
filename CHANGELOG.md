# Changelog

All notable changes to marathi-shabda will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.2.0
- Extended database schema with POS, gender, number columns
- Improved verb conjugation analysis
- Compound word splitting (experimental)
- Performance optimizations

## [0.1.3] - 2026-02-03

### Added
- **Irregular Word Handling**: Added exception mapping for words like "मुली" (muli) which now correctly map to "मुलगी" (mulgi) instead of "मूल" (mul).
- **Stem Alternations**: Added rules for oblique-to-direct conversions (e.g., "मुला" -> "मुलगा") and vowel lengthening (short 'u' to long 'uu').

### Fixed
- **Irregular Word Handling**: Added exception mapping for words like "मुली" (muli) which now correctly map to "मुलगी" (mulgi) instead of "मूल" (mul).
- **Stem Alternations**: Added rules for oblique-to-direct conversions (e.g., "मुला" -> "मुलगा") and vowel lengthening (short 'u' to long 'uu').

### Documentation
- Replaced confusing "mulane" example with "jagane" in `README.md` and docstrings.

## [0.1.2] - 2026-01-30

### Changed
- Updated license to CC BY-NC-SA 4.0 (Non-Commercial)
- Added contributors and acknowledgment section
- Updated documentation with dual licensing strategy

## [0.1.0] - 2026-01-28

### Added
- **Core Features**
  - Lemma extraction from inflected Marathi words
  - Dictionary lookup (Marathi → English)
  - Morphological analysis (रूप परिचय)
  - Vibhakti detection (30+ patterns)
  - POS tagging (conservative heuristics)
  - Kāl inference for verbs (basic patterns)

- **Normalization**
  - Script detection (Devanagari vs Roman)
  - Roman → Devanagari transliteration
  - Unicode normalization (NFC)
  - Zero-width character removal

- **Architecture**
  - Dictionary adapter with SQLite backend
  - Rule-based morphology engine
  - Confidence scoring system
  - Ambiguity handling
  - Structured output models (dataclasses)

- **Developer Experience**
  - Command-line interface (CLI)
  - Comprehensive documentation
  - Unit test suite
  - Type hints throughout
  - Zero runtime dependencies

- **Documentation**
  - Professional README with examples
  - CONTRIBUTING guide
  - API reference in docstrings
  - Honest limitations documented

### Philosophy
- Dictionary-first validation
- Conservative inference
- Explainable results
- Offline-first design
- "When unsure, defer. When confident, explain why."

### Known Limitations
- Single words only (no sentence parsing)
- Conservative POS tagging (limited patterns)
- Basic kāl detection (common verbs only)
- No semantic analysis beyond dictionary
- Limited verb conjugation support

### Technical Details
- Python 3.8+ required
- Pure Python (stdlib only)
- SQLite database bundled
- Deterministic behavior
- Thread-safe dictionary access

---

## Release Notes

### v0.1.0 - Initial Release

This is the first public release of marathi-shabda. The library provides foundational Marathi word analysis capabilities with a focus on correctness, explainability, and offline operation.

**Target Users**:
- Marathi language researchers
- NLP developers
- Educational applications
- Privacy-sensitive systems

**Not Recommended For**:
- Production sentence parsing (not supported)
- Real-time applications requiring ML accuracy
- Systems needing semantic understanding

**Next Steps**:
1. Gather community feedback
2. Expand vibhakti rules based on real-world usage
3. Improve transliteration accuracy
4. Plan database schema extensions

---

[Unreleased]: https://github.com/yourusername/marathi-shabda/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/marathi-shabda/releases/tag/v0.1.0
