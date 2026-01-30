# PyPI Deployment Guide for marathi-shabda

## ✅ Build Complete

Successfully built distribution packages:
- **Source distribution**: `marathi_shabda-0.1.0.tar.gz`
- **Wheel distribution**: `marathi_shabda-0.1.0-py3-none-any.whl`

---

## Prerequisites for PyPI Upload

### 1. PyPI Account
- Create account at: https://pypi.org/account/register/
- Verify your email address

### 2. API Token
1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `marathi-shabda-upload`
4. Scope: "Entire account" (or specific to this project after first upload)
5. Copy the token (starts with `pypi-`)

### 3. Install Twine
```bash
pip install twine
```

---

## Upload to PyPI

### Option 1: Using API Token (Recommended)

```bash
# Set environment variable (Windows PowerShell)
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR_TOKEN_HERE"

# Upload to PyPI
twine upload dist/*
```

### Option 2: Interactive Upload

```bash
twine upload dist/*
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

---

## Test Upload (Recommended First)

Before uploading to the real PyPI, test with TestPyPI:

### 1. Create TestPyPI Account
- Register at: https://test.pypi.org/account/register/

### 2. Get TestPyPI Token
- Go to: https://test.pypi.org/manage/account/token/

### 3. Upload to TestPyPI
```bash
twine upload --repository testpypi dist/*
```

### 4. Test Installation
```bash
pip install --index-url https://test.pypi.org/simple/ marathi-shabda
```

---

## Verification After Upload

### 1. Check PyPI Page
- Visit: https://pypi.org/project/marathi-shabda/

### 2. Test Installation
```bash
# Create fresh virtual environment
python -m venv test_env
test_env\Scripts\activate

# Install from PyPI
pip install marathi-shabda

# Test it works
python -c "from marathi_shabda import lookup_word; print(lookup_word('पाणी').english_meanings)"


```

---

## Important Notes

### Package Size
- The database file (`dictionary.db`) is included in the package
- Check the final package size in `dist/` folder
- PyPI has a 100 MB limit per file

### Version Management
- Current version: **0.1.0**
- To release updates, increment version in `pyproject.toml`
- Rebuild with `python -m build`
- Upload new version

### Security
- **NEVER** commit API tokens to git
- Store tokens securely (password manager)
- Use project-scoped tokens when possible

---

## Troubleshooting

### Error: "File already exists"
- You cannot re-upload the same version
- Increment version number in `pyproject.toml`
- Rebuild and upload again

### Error: "Invalid credentials"
- Check token is correct (starts with `pypi-`)
- Username must be `__token__` (with double underscores)
- Token must not have expired

### Error: "Package name already taken"
- The name `marathi-shabda` must be available
- Check: https://pypi.org/project/marathi-shabda/
- If taken, choose a different name

---

## Post-Publication Checklist

- [ ] Verify package page on PyPI
- [ ] Test installation in clean environment
- [ ] Update README with PyPI badge
- [ ] Create GitHub release (if using GitHub)
- [ ] Announce on relevant forums/communities

---

## PyPI Badge for README

After publication, add this to your README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/marathi-shabda.svg)](https://badge.fury.io/py/marathi-shabda)
[![Downloads](https://pepy.tech/badge/marathi-shabda)](https://pepy.tech/project/marathi-shabda)
```

---

**Status**: Ready for PyPI upload
**Next Step**: Get PyPI API token and run `twine upload dist/*`
