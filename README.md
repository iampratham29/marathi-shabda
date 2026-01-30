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

हे सॉफ्टवेअर **CC BY-NC-SA 4.0** (Creative Commons Non-Commercial) परवान्याअंतर्गत उपलब्ध आहे.

### ✅ मोफत वापर (Free Use)
खालील कारणांसाठी तुम्ही हे मोफत वापरू शकता:
- 🎓 **शाळा/कॉलेजचे प्रकल्प आणि शिक्षण** (Education)
- 🔬 **संशोधन** (Research)
- 🏠 **वैयक्तिक अभ्यास** (Personal Use)
- 🤝 **विना-नफा संस्था** (Non-profit NGOs)

### ❌ व्यावसायिक वापर (Commercial Use)
खालील कारणांसाठी **परवानगी घेणे अनिवार्य** आहे:
- 💼 **व्यावसायिक सॉफ्टवेअर किंवा ॲप्स** (Business Apps)
- 💰 **पैसे कमावण्यासाठी केलेले प्रोजेक्ट्स** (For-profit Services)
- 🏢 **कंपनी अंतर्गत टूल्स** (Internal Company Tools)

**व्यावसायिक लायसन्ससाठी संपर्क करा:**
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

This software is licensed under **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International).

### ✅ Free for Educational & Training Use
You can freely use this library for:
- Educational institutions and training programs
- Academic research and publications
- Personal learning and experimentation
- Non-profit organizations
- Student projects and assignments

### ❌ Commercial Licensing Required
You **cannot** use it for the following without a commercial license:
- Commercial software products or services
- Business applications or internal tools
- Selling or monetizing the software
- SaaS or API services for profit

**For commercial inquiries:**
- **Email**: choudhariprathmesh001@gmail.com
- **GitHub**: [@iampratham29](https://github.com/iampratham29)
- **Subject**: "marathi-shabda Commercial License Inquiry"

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
- **Dictionary-backed**: Uses a built-in SQLite database for authoritative meanings.
- **Rule-based**: Uses linguistic rules for vibhakti and form handling.
- **Explanation**: Every result comes with a reason for why it was derived.

### Limitations (v0.1.2)
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
