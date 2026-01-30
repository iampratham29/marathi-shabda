# marathi-shabda

**Deterministic, offline Marathi word analysis library**

[![PyPI version](https://badge.fury.io/py/marathi-shabda.svg)](https://badge.fury.io/py/marathi-shabda)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is marathi-shabda?

`marathi-shabda` is a production-quality Python library for analyzing Marathi words. It provides:

1. **Lemma (stem) extraction** from inflected Marathi words
2. **Dictionary lookup** (Marathi ↔ English) with meanings
3. **Morphological analysis** (रूप परिचय) including POS, vibhakti, and kāl detection

### Why "pratham" (प्रथम)?

*Pratham* means "first" in Marathi. This library provides the **first step** in Marathi text analysis: understanding individual words before tackling sentences or documents.

---

## Motivation

Marathi language tooling lags behind other Indian languages. Existing solutions either:
- Require network access (API-based)
- Hallucinate meanings (LLM-based)
- Lack linguistic grounding (pure ML)

**marathi-shabda** is different:
- ✅ **Offline-first**: No network, no API keys
- ✅ **Dictionary-backed**: Authoritative meanings, no hallucinations
- ✅ **Explainable**: Shows reasoning for every decision
- ✅ **Honest about limitations**: Surfaces ambiguity instead of hiding it

---

## What It Does

### ✅ Supported Features

- **Lemma extraction**: `पाण्यावर` → `पाणी` (water)
- **Vibhakti detection**: Identifies case markers (तृतीया, सप्तमी, संबंध, etc.)
- **Dictionary lookup**: Marathi → English meanings
- **POS tagging**: Conservative noun/verb/adjective classification
- **Kāl inference**: Basic tense detection for verbs
- **Roman input**: Accepts romanized Marathi (e.g., `pani` → `पाणी`)
- **Stem alternations**: Handles oblique forms (`पाण्य` → `पाणी`)

### ❌ Explicit Non-Goals

This library **does NOT**:
- Parse sentences or multi-word phrases
- Claim grammatical correctness in all contexts
- Infer semantics beyond dictionary meanings
- Require network access
- Use machine learning (v0.1.0)

---

## Installation

```bash
pip install marathi-shabda
```

**Requirements**: Python 3.8+, no external dependencies

---

## Quick Start

### 1. Lemma Extraction

```python
from marathi_shabda import get_lemma

result = get_lemma("पाण्यावर")
print(result.lemma)              # पाणी
print(result.confidence)         # 0.9
print(result.detected_vibhakti)  # VibhaktiType.SAPTAMI (सप्तमी)
print(result.explanation)        # "Detected सप्तमी vibhakti"
```

### 2. Dictionary Lookup

```python
from marathi_shabda import lookup_word

result = lookup_word("पाणी")
print(result.english_meanings)   # ['water']
print(result.found)              # True

# Also works with Roman input
result = lookup_word("pani")
print(result.lemma)              # पाणी
```

### 3. Morphological Analysis

```python
from marathi_shabda import analyze_word

result = analyze_word("मुलाने")
print(result.lemma)      # मुल
print(result.pos)        # POSTag.NOUN
print(result.vibhakti)   # VibhaktiType.TRUTIYA (तृतीया)
print(result.confidence) # 0.9
print(result.explanation)
# "Detected तृतीया vibhakti; Inferred noun"
```

---

## How It Works

### Architecture

```
Input Word
   ↓
Normalization (Roman → Devanagari)
   ↓
Dictionary Check (exact match?)
   ↓
Vibhakti Detection (longest-first)
   ↓
Stem Alternations (पाण्य → पाणी)
   ↓
Dictionary Validation (lemma exists?)
   ↓
POS & Kāl Inference
   ↓
Result with Confidence
```

### Key Principles

1. **Dictionary-first validation**: Rules generate candidates, dictionary decides truth
2. **Longest-match-first**: Detects `मध्ये` before `ये`
3. **Conservative inference**: Returns `UNKNOWN` when uncertain
4. **Explainable decisions**: Every result includes reasoning

---

## Confidence & Ambiguity

### Confidence Scores

- **1.0**: Exact dictionary match
- **0.9**: Vibhakti detected, lemma validated
- **0.7**: Ambiguous (multiple possible lemmas)
- **0.0**: Word not in dictionary

### Handling Ambiguity

```python
result = get_lemma("घरात")
if result.ambiguous:
    print(f"Multiple interpretations: {result.candidates}")
    # ['घर', 'घरात']  # Could be noun or compound
```

**Philosophy**: We surface ambiguity instead of making false claims.

---

## Offline Guarantee

**marathi-shabda** works completely offline:
- ✅ No network requests
- ✅ No API keys
- ✅ No telemetry
- ✅ Bundled SQLite database
- ✅ Pure Python (stdlib only)

Perfect for:
- Privacy-sensitive applications
- Offline environments
- Embedded systems
- Research reproducibility

---

## Limitations

### Current Limitations (v0.1.0)

- **Single words only**: No sentence parsing
- **Conservative POS tagging**: Limited to obvious cases
- **Basic kāl detection**: Only common verb patterns
- **No semantic analysis**: Dictionary meanings only
- **Limited verb conjugation**: Focus on nouns/vibhakti

### Known Edge Cases

- Compound words may not split correctly
- Rare vibhaktis may not be detected
- Ambiguous forms return multiple candidates
- Roman transliteration is approximate

**We document limitations honestly.** If you encounter issues, please report them!

---

## Future Roadmap

### v0.2.0 (Planned)
- [ ] Extended database schema (POS, gender, number)
- [ ] Improved verb conjugation analysis
- [ ] Compound word splitting
- [ ] Performance optimizations

### v0.3.0 (Planned)
- [ ] Optional SLM integration for ambiguity resolution
- [ ] Sentence-level analysis (experimental)
- [ ] Batch processing API

### Long-term
- [ ] Hybrid rule-based + ML approach
- [ ] Community-contributed dictionary expansions
- [ ] Web API (optional deployment)

---

## Command-Line Interface

```bash
# Extract lemma
marathi-shabda lemma पाण्यावर

# Dictionary lookup
marathi-shabda lookup पाणी

# Full analysis
marathi-shabda analyze मुलाने
```

---

## Contributing

We welcome your feedback and suggestions! While the core codebase is maintained by the project owners, we encourage the community to:

### How You Can Help

- **Use the library** in your projects and applications
- **Report issues** if you encounter bugs or unexpected behavior
- **Suggest enhancements** for vibhakti rules, transliteration, or new features
- **Share use cases** to help us understand real-world applications
- **Provide linguistic feedback** on Marathi grammar rules and edge cases

### Suggesting Improvements

If you have ideas for improvement:

1. **Open an issue** on GitHub describing your suggestion
2. **Provide examples** of words or patterns that should be handled better
3. **Share linguistic references** if applicable (grammar rules, scholarly sources)

We review all suggestions and incorporate valuable feedback into future releases.

### Usage Terms

This library is freely available for use under the MIT License. You can:
- ✅ Use it in personal and commercial projects
- ✅ Modify it for your own needs
- ✅ Distribute it with your applications

The project maintainers reserve the right to manage contributions and maintain ownership of the core codebase.

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

### Free for Educational & Training Use

This software is licensed under **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International) for non-commercial use.

**You can freely use this library for:**
- ✅ Educational institutions and training programs
- ✅ Academic research and publications  
- ✅ Personal learning and experimentation
- ✅ Non-profit organizations
- ✅ Student projects and assignments

**You cannot use it for:**
- ❌ Commercial software products or services
- ❌ Business applications or internal tools
- ❌ Selling or monetizing the software
- ❌ SaaS or API services for profit

### Commercial Licensing

For commercial use, please contact us for a commercial license:

- **Email**: choudhariprathmesh001@gmail.com
- **GitHub**: [@iampratham29](https://github.com/iampratham29)
- **Subject**: "marathi-shabda Commercial License Inquiry"

We offer flexible commercial licensing options for businesses and enterprises.

See [LICENSE](LICENSE) for full legal details.

---

## Contributors

- **Prathmesh Santosh Choudhari** ([@iampratham29](https://github.com/iampratham29))
- **Vedangi Deepak Deshpande**
- **Siddhant Akash Bobde**

---

## Acknowledgments

- **[@vinodnimbalkar](https://github.com/vinodnimbalkar)** - For valuable open-source contributions to the Marathi language ecosystem
- Marathi language scholars and grammarians
- Open-source NLP community
- All contributors and testers

---

## Citation

If you use marathi-shabda in research, please cite:

```bibtex
@software{marathi_shabda,
  title = {marathi-shabda: Deterministic Marathi Word Analysis},
  author = {Choudhari, Prathmesh Santosh and Deshpande, Vedangi Deepak and Bobde, Siddhant Akash},
  year = {2026},
  url = {https://github.com/iampratham29/marathi-shabda}
}
```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/iampratham29/marathi-shabda/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iampratham29/marathi-shabda/discussions)
- **GitHub**: [@iampratham29](https://github.com/iampratham29)

---

**Philosophy**: *When unsure, defer. When confident, explain why.*

Built with respect for the Marathi language and its speakers. 🙏
