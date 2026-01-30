# Contributing to marathi-shabda

Thank you for your interest in marathi-shabda! We welcome feedback, suggestions, and issue reports from the community.

---

## How You Can Contribute

While the core codebase is maintained by the project owners, there are many ways you can help improve this library:

### 1. Use the Library

The best way to contribute is to **use marathi-shabda** in your projects and share your experience!

### 2. Report Issues

Found a bug or unexpected behavior? Please report it!

**When reporting issues:**
- Use the [GitHub issue tracker](https://github.com/iampratham29/marathi-shabda/issues)
- Provide a clear description of the problem
- Include example Marathi words that demonstrate the issue
- Specify expected vs. actual behavior
- Mention your Python version and OS

**Example:**
```
Issue: get_lemma("घरात") returns confidence 0.0

Expected: Should detect "त" vibhakti and return lemma "घर"
Actual: Returns original word with no vibhakti detected

Python: 3.11, Windows 11
```

### 3. Suggest Enhancements

Have ideas for improvement? We'd love to hear them!

**Suggestions we're particularly interested in:**
- New vibhakti patterns that should be detected
- Improvements to Roman → Devanagari transliteration
- Edge cases in Marathi grammar we should handle
- Additional stem alternation rules
- Performance optimizations
- Documentation improvements

**When suggesting enhancements:**
1. Open a GitHub issue with the "enhancement" label
2. Provide specific examples of words or patterns
3. Explain the linguistic reasoning (if applicable)
4. Share references to grammar rules or scholarly sources

### 4. Share Use Cases

Tell us how you're using marathi-shabda! This helps us:
- Understand real-world applications
- Prioritize features
- Improve documentation
- Guide future development

### 5. Provide Linguistic Feedback

Are you a Marathi language expert? Your feedback is invaluable!

Help us with:
- Validating vibhakti detection rules
- Identifying missing grammar patterns
- Correcting linguistic inaccuracies
- Suggesting better terminology

---

## Contribution Process

### For Bug Reports & Suggestions

1. **Search existing issues** to avoid duplicates
2. **Open a new issue** with a descriptive title
3. **Provide details** as outlined above
4. **Engage in discussion** if maintainers have questions

We review all issues and incorporate valuable feedback into future releases.

### For Code Contributions

The project maintainers manage the core codebase directly. However, if you have:
- **Critical bug fixes**
- **Well-tested enhancements**
- **Documentation improvements**

Please open an issue first to discuss the proposed changes. We'll guide you on the best approach.

---

## Usage Terms

This library is freely available under the **CC BY-NC-SA 4.0 License** for non-commercial use.

### ✅ Permitted Uses (Free)

- Educational institutions and training programs
- Academic research and publications
- Personal learning and experimentation
- Non-profit organizations
- Student projects and assignments
- Open-source projects (non-commercial)

### ❌ Prohibited Uses (Requires Commercial License)

- Commercial software products or services
- Business applications or internal tools
- Selling or monetizing the software
- SaaS or API services for profit
- Consulting services using this software

### 💼 Commercial Licensing

For commercial use, please contact us:

- **Email**: prathmesh@example.com
- **GitHub**: [@iampratham29](https://github.com/iampratham29)
- **Subject**: "marathi-shabda Commercial License Inquiry"

We offer flexible commercial licensing options for businesses and enterprises.

**Note:** The project maintainers reserve the right to manage contributions and maintain ownership of the core codebase.

---

## Development Guidelines

If you're exploring the codebase or experimenting with modifications:

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and testable

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=marathi_shabda

# Run specific test
pytest tests/test_morphology.py -v
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/iampratham29/marathi-shabda.git
cd marathi-shabda

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

---

## Philosophy

Remember our core principle:

> **When unsure, defer. When confident, explain why.**

- Don't hallucinate meanings
- Surface ambiguity, don't hide it
- Conservative inference over aggressive guessing
- Dictionary-backed truth over heuristics

---

## Questions?

- **Issues**: [GitHub Issues](https://github.com/iampratham29/marathi-shabda/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iampratham29/marathi-shabda/discussions)

---

Thank you for helping improve Marathi language tooling! 🙏

**Your feedback makes this library better for everyone.**

