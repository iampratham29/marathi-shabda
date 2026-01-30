# Building for PyPI with Wheel-Only Distribution

## Overview

To protect the source code while allowing users to install and use the library, we distribute **only the wheel (.whl) file** to PyPI, not the source distribution (.tar.gz).

---

## Build Process

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
Remove-Item -Recurse -Force dist, build, src\marathi_shabda.egg-info -ErrorAction SilentlyContinue
```

### 2. Build Wheel Only

```bash
# Build ONLY the wheel (no source distribution)
python -m build --wheel
```

This creates:
- ✅ `dist/marathi_shabda-0.1.0-py3-none-any.whl` (wheel file)
- ❌ No `.tar.gz` source distribution

### 3. Verify Build

```bash
# Check what was built
Get-ChildItem dist\

# Verify wheel contents
python -m zipfile -l dist\marathi_shabda-0.1.0-py3-none-any.whl
```

### 4. Upload to PyPI

```bash
# Upload ONLY the wheel
python -m twine upload dist/*.whl

# Or with credentials
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR_TOKEN_HERE"
python -m twine upload dist/*.whl
```

---

## What Users Get

When users install via `pip install marathi-shabda`, they get:

1. **Compiled bytecode** (.pyc files) - not source code
2. **Full functionality** - library works perfectly
3. **No source access** - cannot easily view implementation

### User Installation

```bash
pip install marathi-shabda
```

Works exactly the same as any other package!

---

## Source Code Protection

### What's Protected

✅ **Algorithm implementation** - users can't see your logic  
✅ **Database queries** - SQL and data access patterns hidden  
✅ **Vibhakti rules** - rule definitions compiled to bytecode  
✅ **Stem alternations** - pattern matching logic protected  

### What's Visible

Users can still see:
- ❌ Function/class names (via `dir()`)
- ❌ Docstrings (via `help()`)
- ❌ Type hints (in .pyi stub files if included)

But they **cannot** easily see:
- ✅ Implementation details
- ✅ Algorithm logic
- ✅ Internal helper functions

---

## GitHub Repository Strategy

### Public Repository Contents

Your public GitHub repo should contain:

```
marathi-shabda/
├── README.md                    # Full documentation
├── LICENSE                      # CC BY-NC-SA 4.0
├── CONTRIBUTING.md              # How to report issues
├── CHANGELOG.md                 # Version history
├── pyproject.toml               # Package metadata
├── MANIFEST.in                  # Package data rules
├── .gitignore                   # Git ignore rules
├── examples/                    # Usage examples
│   ├── basic_usage.py
│   ├── lemma_extraction.py
│   └── dictionary_lookup.py
├── docs/                        # Documentation
│   ├── api_reference.md
│   ├── quickstart.md
│   └── faq.md
└── src/marathi_shabda/          # SOURCE CODE (YES, PUBLIC!)
    ├── __init__.py
    ├── api.py
    ├── cli.py
    ├── models.py
    ├── exceptions.py
    ├── dictionary/
    ├── morphology/
    ├── normalization/
    └── inference/
```

**Wait, source code is public?**

Yes! Here's why it's still protected:

1. **License Protection**: CC BY-NC-SA 4.0 prevents commercial use
2. **Legal Recourse**: You can sue if someone uses it commercially
3. **Community Trust**: Users can inspect code for security/quality
4. **Issue Reports**: Users can reference specific lines when reporting bugs
5. **Transparency**: Shows you have nothing to hide

**The protection comes from the LICENSE, not obscurity!**

---

## How Users Contribute (Public Repo)

### 1. Reporting Issues

Users can open GitHub Issues:

```
Title: "Lemma extraction fails for word 'घरांवर'"

Description:
When I call get_lemma("घरांवर"), I expect it to return "घर" 
but it returns the original word with confidence 0.0.

Code:
```python
from marathi_shabda import get_lemma
result = get_lemma("घरांवर")
print(result.lemma)  # Expected: घर, Actual: घरांवर
```

Environment:
- marathi-shabda version: 0.1.0
- Python: 3.11
- OS: Windows 11
```

### 2. Suggesting Enhancements

Users can suggest improvements:

```
Title: "Add support for 'कडे' vibhakti"

Description:
The vibhakti 'कडे' (towards) is commonly used but not detected.

Examples:
- मुलाकडे → मुल
- घराकडे → घर

Reference: Marathi grammar book, page 45
```

### 3. Contributing Test Cases

Users can submit test cases via issues or PRs:

```json
// test_cases/user_contributions.json
{
  "lemma_tests": [
    {"input": "पाण्यावर", "expected_lemma": "पाणी", "contributor": "@username"},
    {"input": "मुलांनी", "expected_lemma": "मुल", "contributor": "@username2"}
  ]
}
```

### 4. Documentation PRs

Users can submit pull requests for:
- README improvements
- Example code
- Tutorial content
- Translation corrections

You review and merge if acceptable.

---

## Enforcement Strategy

### If Someone Uses Commercially Without License

1. **Friendly Contact**: Email them about the license
2. **Offer License**: Provide commercial licensing options
3. **Legal Action**: If they refuse, you have legal grounds

### Detection

Monitor:
- GitHub stars/forks
- PyPI download stats
- Google searches for "marathi-shabda" + company names
- LinkedIn posts mentioning your library

---

## Revenue Model

### Commercial License Pricing (Example)

**Startup License** ($500/year)
- Up to 10 developers
- Email support
- Updates included

**Business License** ($2,000/year)
- Unlimited developers
- Priority support
- Custom features (negotiable)

**Enterprise License** (Custom pricing)
- On-premise deployment
- Custom SLA
- Dedicated support

---

## Summary

**Your Strategy**:
1. ✅ Public GitHub repository (full source code visible)
2. ✅ CC BY-NC-SA 4.0 license (non-commercial use only)
3. ✅ Wheel-only PyPI distribution (no source tarball)
4. ✅ Commercial licenses available for businesses
5. ✅ Community can report issues and suggest improvements

**Protection**:
- Legal protection via license (not code obscurity)
- Can enforce against commercial misuse
- Revenue from commercial licenses

**Community**:
- Users can inspect code (builds trust)
- Can report bugs with line numbers
- Can suggest improvements
- Transparent and collaborative

This is the **best of both worlds**: open collaboration + commercial protection!
