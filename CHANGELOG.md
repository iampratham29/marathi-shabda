# Changelog

All notable changes to marathi-shabda will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-27

### Added
- **Pratham Transliteration Style** — a new, Marathi-first bidirectional Roman
  transliteration system built into `marathi_shabda.normalization`:
  - `dev_to_roman(text)` — deterministic Devanagari → Pratham Roman with full
    Marathi schwa deletion at word boundaries.
  - `roman_to_dev(roman)` — returns **all plausible Devanagari** candidates for
    a given Pratham Roman string, including both inherent-a and virama forms for
    bare-consonant-final words.
  - `transliterate`, `to_roman`, `to_devanagari` — convenient public aliases.
  - Mapping tables (`VOWEL_LETTERS`, `VOWEL_SIGNS`, `CONSONANTS`) exported as
    the single source of truth for the scheme.

- **Full Marathi character support**:
  - Retroflex consonants use **UPPERCASE** (T Th D Dh N L R) to distinguish
    from dental lowercase (t th d dh n).
  - Marathi `ळ` → `L`, eyelash ra `ऱ` → `R` (both absent from Hindi/Urdu schemes).
  - Loan consonants: `KH G z .D .Dh f q` via nukta mapping.
  - Chandrabindu `ँ` → `ñ` (U+00F1).
  - Anusvara assimilation by place of articulation: `ng ny N n m .n`.

- **49 comprehensive tests** across 12 transliteration categories in
  `tests/test_transliterator.py`, each with embedded `REQUIREMENT_PROMPT`
  documentation and a standalone `run_all()` runner.

### Changed
- Removed all references to the Rekhta transliteration scheme; the library now
  ships its own documented **Pratham Transliteration Style**.
- `roman_to_devanagari()` (legacy) is preserved unchanged for backward
  compatibility with `normalize_input`.

### Transliteration Key (Pratham Style)
| Category | Roman notation |
|---|---|
| Short vowels | `a  i  u  e  o` |
| Long vowels  | `aa  ii  uu` |
| Diphthongs   | `ai  au` |
| Retroflex    | `T  Th  D  Dh  N  L  R` |
| Dental       | `t  th  d  dh  n` |
| Aspirates    | `kh  gh  ch  chh  jh  ph  bh` |
| Loans        | `KH  G  z  .D  .Dh  f  q` |
| Chandrabindu | `ñ` |
| Anusvara     | `ng  ny  N  n  m  .n` |

## [0.1.5] - 2026-06-23

### Added
- **Pronoun Conjugations**: Fully added 94 irregular pronoun variations into the dictionary (forms of मी, तू, तो, ती, ते, स्वतः).
- **Pronoun POS Tagging**: Mapped pronouns carefully so they reliably return English meanings denoting their vibhakti case (e.g. "by me", "to him") and are tagged properly as `pronoun`.


## [0.1.4] - 2026-06-22

### Added
- **Massive Dictionary Expansion**: Enriched the built-in SQLite dictionary from ~2,500 words to **over 46,000+ words**!
- **Bulk Dictionary Fetchers**: Added new automated scripts to parse and merge data from Wiktionary, Kaikki.org, and various localized Marathi-English glossaries.
- **GitHub Actions (OIDC)**: Migrated PyPI deployments to use Trusted Publishing (OIDC) for passwordless, automated releases via GitHub Actions.

### Changed
- Updated documentation and README to reflect the 46k+ word count.
- Added data attribution for Wikimedia Foundation and Kaikki.org.

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
