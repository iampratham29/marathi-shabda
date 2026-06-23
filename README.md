# marathi-shabda (मराठी-शब्द)

**खात्रीशीर आणि पूर्णपणे ऑफलाइन चालणारी मराठी शब्द विश्लेषण लायब्ररी**

[![PyPI version](https://badge.fury.io/py/marathi-shabda.svg)](https://badge.fury.io/py/marathi-shabda)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---


## 🚩 परिचय (Introduction)

`marathi-shabda` ही मराठी शब्दांचे व्याकरणिक विश्लेषण करण्यासाठी बनवलेली एक प्रोफेशनल **Python Library** आहे.

हे प्रामुख्याने खालील गोष्टी करते:
1. **मूळ शब्द शोधणे (Lemma Extraction)**: `पाण्यावर` → `पाणी`
2. **शब्दकोश (Dictionary Lookup)**: मराठी शब्दांचे इंग्रजी अर्थ
3. **रूप परिचय (Morphology)**: शब्दाची जात (POS), विभक्ती आणि काळ ओळखणे.

हे पूर्णपणे **ऑफलाइन** चालते. याला इंटरनेटची गरज नाही.

---

## 📜 वापराचे नियम आणि परवाना (License & Guidelines)

हे प्रोजेक्ट **Dual Licensing** (दोन परवाने) मॉडेलवर चालते:

1. **Source Code (MIT)**: सॉफ्टवेअरचा कोड **MIT License** अंतर्गत आहे. 
   - ✅ तुम्ही कोड वापरू शकता, बदलू शकता (व्यावसायिक वापरासाठी सुद्धा).

2. **Data & Dictionary (CC BY-NC-SA 4.0)**: शब्दकोश आणि डेटा **Creative Commons Non-Commercial** आहे.
   - ❌ डेटाचा वापर पैसे कमावण्यासाठी (Commercial Use) करता येणार नाही.
   - ✅ शिक्षण आणि संशोधनासाठी डेटा मोफत आहे.

**व्यावसायिक वापरासाठी संपर्क (For Commercial Data Usage):**
- **Email**: choudhariprathmesh001@gmail.com
- **GitHub**: [@iampratham29](https://github.com/iampratham29)

---

## 🚀 इंस्टॉलेशन (Installation)

```bash
pip install marathi-shabda
```

**आवश्यकता**: Python 3.8 किंवा त्यापुढील व्हर्जन.

---

## ⚡ वापर कसा करावा (Quick Start)

### 1. मूळ शब्द शोधणे (Lemma Extraction)

```python
from marathi_shabda import get_lemma

result = get_lemma("पाण्यावर")
print(result.lemma)              # उत्तर: पाणी
print(result.detected_vibhakti)  # उत्तर: सप्तमी
print(result.explanation)        # उत्तर: "Detected सप्तमी vibhakti"
```

### 2. शब्दकोश (Meaning)

```python
from marathi_shabda import lookup_word

result = lookup_word("पाणी")
print(result.english_meanings)   # उत्तर: ['water']
```

---

## 🤝 योगदान (Contribution)

आम्ही तुमच्या योगदानाचे स्वागत करतो!
- तुम्हाला काही **चुका (Bugs)** आढळल्यास GitHub Issues वर कळवा.
- नवीन **विभक्ती नियम** किंवा **सुधारणा** सुचवायच्या असतील तर स्वागत आहे.
- **टीप**: मुख्य कोडची मालकी (Ownership) मूळ लेखकांकडे राखीव आहे.

अधिक माहितीसाठी [CONTRIBUTING.md](CONTRIBUTING.md) वाचा.

---
---

# 🇬🇧 English Description

## What is marathi-shabda?

`marathi-shabda` is a production-quality Python library for analyzing Marathi words. It provides:

1. **Lemma (stem) extraction** from inflected Marathi words
2. **Dictionary lookup** (Marathi ↔ English) with meanings
3. **Morphological analysis** (रूप परिचय) including POS, vibhakti, and kāl detection

It works completely **offline** with no internet dependency.

---

## License & Usage Guidelines

This project uses a **Split Licensing Model**:

### 1. Source Code (MIT License)
The Python code, algorithms, and API structure are licensed under the **MIT License**.
- ✅ You **CAN** use the code for commercial software.
- ✅ You **CAN** modify and distribute the code logic.

### 2. Data & Dictionary (CC BY-NC-SA 4.0)
The dictionary database (`dictionary.db`) and linguistic rules are licensed under **Creative Commons Non-Commercial**.
- ❌ You **CANNOT** sell the data or use it in commercial products without a license.
- ✅ Free for education, research, and non-profit use.

**For commercial data licensing:**
- **Email**: choudhariprathmesh001@gmail.com
- **GitHub**: [@iampratham29](https://github.com/iampratham29)

---

## Installation

```bash
pip install marathi-shabda
```

**Requirements**: Python 3.8+, no external dependencies.

---

## Quick Start

### 1. Lemma Extraction

```python
from marathi_shabda import get_lemma

result = get_lemma("पाण्यावर")
print(result.lemma)              # पाणी
print(result.confidence)         # 0.9
print(result.detected_vibhakti)  # VibhaktiType.SAPTAMI (सप्तमी)
```

### 2. Dictionary Lookup

```python
from marathi_shabda import lookup_word

result = lookup_word("पाणी")
print(result.english_meanings)   # ['water']
print(result.found)              # True
```

---

## Technical Details

### Architecture
- **Dictionary-backed**: Uses a built-in SQLite database containing over 46,000+ words (enriched from Wiktionary, Kaikki, and localized glossaries) for authoritative meanings.
- **Rule-based**: Uses linguistic rules for vibhakti and form handling.
- **Explanation**: Every result comes with a reason for why it was derived.

### Limitations (v0.1.5)
- **Single words only**: Does not parse full sentences.
- **Conservative**: Prefers to say "Unknown" rather than guessing wrong.
- **Transliteration**: Roman script support is approximate.

---

## Contributors

- **Prathmesh Santosh Choudhari** ([@iampratham29](https://github.com/iampratham29))
- **Vedangi Deepak Deshpande**
- **Siddhant Akash Bobde**

---

## Acknowledgments

- **Wiktionary (Wikimedia Foundation)**: For providing an open, collaborative dictionary. The dictionary data incorporated here is derived from the English and Marathi Wiktionary dumps, used solely for educational and non-commercial research purposes.
- **Kaikki.org**: For providing structured, machine-readable JSON extracts of Wiktionary data, which made parsing Marathi lemmas and definitions possible.
- **[@vinodnimbalkar](https://github.com/vinodnimbalkar)** - For valuable open-source contributions to the Marathi language ecosystem.
- Marathi language scholars and grammarians.
- Open-source NLP community.

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

---

**Philosophy**: *When unsure, defer. When confident, explain why.*

Built with respect for the Marathi language and its speakers. 🙏
