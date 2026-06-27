"""Devanagari <-> Pratham Roman transliteration for Marathi.

Public API
----------
dev_to_roman(text)   -- Devanagari -> Pratham Roman (deterministic)
roman_to_dev(roman)  -- Pratham Roman -> list of plausible Devanagari strings
transliterate        -- alias for dev_to_roman
to_roman             -- alias for dev_to_roman
to_devanagari        -- alias for roman_to_dev

roman_to_devanagari(text) -- LEGACY simple one-shot transliterator kept for
                             backward-compatibility with normalize_input / safe_normalizer.

Pratham Transliteration Style
------------------------------
This module implements the Pratham Transliteration Style — a Marathi-first,
phonetically-accurate Roman scheme designed for the marathi-shabda library.

It extends the standard Roman transliteration conventions used for Devanagari
with full Marathi support:

Conventions
-----------
  Retroflex consonants use UPPERCASE: T  Th  D  Dh  N  L  R
  Dental/standard consonants: t  th  d  dh  n
  Long vowels: aa  ii  uu
  Diphthongs: ai  au
  Aspirates: kh  gh  ch  chh  jh  ph  bh  dh  th
  Loan consonants: KH  G  z  .D  .Dh  f  q
  Nasal/chandrabindu: ñ  (always for ँ)
  Anusvara assimilation: ng  ny  N  n  m  .n  (by place of articulation)
  Marathi ळ -> L  (retroflex lateral)
  Marathi ऱ -> R  (eyelash ra, U+0931)

Known lossiness (documented)
------------------------------
  - ष maps to 'Sh' (distinct from श -> 'sh'); round-trip works via 'kSh' token.
  - Anusvara: 'n' before dental / 'm' before labial treated as anusvara in
    roman_to_dev (not consonant cluster). Dot separator intended for disambiguation.
  - Word-final inherent 'a' is dropped (Marathi schwa deletion). roman_to_dev
    returns two candidates for bare-consonant-final words: with and without virama.
"""

from itertools import product as _iterproduct
from typing import Optional

# ---------------------------------------------------------------------------
# Unicode constants
# ---------------------------------------------------------------------------
VIRAMA       = '\u094D'   # ्  halant / virama
NUKTA        = '\u093C'   # ़  nukta
ANUSVARA     = '\u0902'   # ं  anusvara
CHANDRABINDU = '\u0901'   # ँ  chandrabindu
VISARGA      = '\u0903'   # ः  visarga

# ---------------------------------------------------------------------------
# MAPPING TABLES — single source of truth (Pratham Transliteration Style)
# ---------------------------------------------------------------------------

# Independent vowel letters (word-initial / standalone)
VOWEL_LETTERS: dict[str, str] = {
    'अ': 'a',   'आ': 'aa',  'इ': 'i',   'ई': 'ii',
    'उ': 'u',   'ऊ': 'uu',  'ए': 'e',   'ऐ': 'ai',
    'ओ': 'o',   'औ': 'au',  'ऋ': 'ri',  'ॠ': 'rii',
    'ऌ': 'li',
}

# Vowel signs / matras (attach to preceding consonant)
VOWEL_SIGNS: dict[str, str] = {
    '\u093E': 'aa',   # ा  long aa
    '\u093F': 'i',    # ि  short i
    '\u0940': 'ii',   # ी  long ii
    '\u0941': 'u',    # ु  short u
    '\u0942': 'uu',   # ू  long uu
    '\u0947': 'e',    # े  e
    '\u0948': 'ai',   # ै  ai
    '\u094B': 'o',    # ो  o
    '\u094C': 'au',   # ौ  au
    '\u0943': 'ri',   # ृ  vocalic r
    '\u0944': 'rii',  # ॄ  vocalic rr
}

# Consonant inventory (Pratham Transliteration Style).
# UPPERCASE = retroflex; lowercase = dental / standard.
CONSONANTS: dict[str, str] = {
    'क': 'k',    'ख': 'kh',  'ग': 'g',   'घ': 'gh',   'ङ': 'ng',
    'च': 'ch',   'छ': 'chh', 'ज': 'j',   'झ': 'jh',   'ञ': 'ny',
    'ट': 'T',    'ठ': 'Th',  'ड': 'D',   'ढ': 'Dh',   'ण': 'N',
    'त': 't',    'थ': 'th',  'द': 'd',   'ध': 'dh',   'न': 'n',
    'प': 'p',    'फ': 'ph',  'ब': 'b',   'भ': 'bh',   'म': 'm',
    'य': 'y',    'र': 'r',   'ल': 'l',   'व': 'v',
    'श': 'sh',
    'ष': 'Sh',              # retroflex sibilant; kept distinct from श → 'sh'
    'स': 's',    'ह': 'h',
    'ळ': 'L',               # Marathi retroflex lateral
    '\u0931': 'R',          # ऱ Marathi eyelash ra (U+0931)
}

# Nukta-modified consonants (loan consonants from Persian/Arabic/English)
NUKTA_CONSONANTS: dict[str, str] = {
    'ख' + NUKTA: 'KH',    # ख़
    'ग' + NUKTA: 'G',     # ग़
    'ज' + NUKTA: 'z',     # ज़
    'ड' + NUKTA: '.D',    # ड़
    'ढ' + NUKTA: '.Dh',   # ढ़
    'फ' + NUKTA: 'f',     # फ़
    'क' + NUKTA: 'q',     # क़
}

# ---------------------------------------------------------------------------
# Anusvara place-of-articulation sets (Pratham Transliteration Style)
# ---------------------------------------------------------------------------
_VELAR     = frozenset('कखगघङ')
_PALATAL   = frozenset('चछजझञ')
_RETROFLEX = frozenset('टठडढणळ\u0931')
_DENTAL    = frozenset('तथदधन')
_LABIAL    = frozenset('पफबभम')


def _anusvara_roman(next_char: Optional[str]) -> str:
    """Map anusvara (ं) to Pratham Roman based on place of articulation of following consonant.

    Pratham Transliteration Style anusvara rules:
      Before velar     → ng
      Before palatal   → ny
      Before retroflex → N
      Before dental    → n
      Before labial    → m
      Word-final / pre-vowel → .n
    """
    if next_char is None:
        return '.n'
    if next_char in _VELAR:
        return 'ng'
    if next_char in _PALATAL:
        return 'ny'
    if next_char in _RETROFLEX:
        return 'N'
    if next_char in _DENTAL:
        return 'n'
    if next_char in _LABIAL:
        return 'm'
    return '.n'


def _handle_modifiers(word: str, i: int, n: int, result: list) -> int:
    """Consume anusvara or chandrabindu that immediately follows a vowel."""
    if i < n:
        if word[i] == ANUSVARA:
            lookahead = word[i + 1] if i + 1 < n else None
            result.append(_anusvara_roman(lookahead))
            i += 1
        elif word[i] == CHANDRABINDU:
            result.append('\u00f1')   # ñ  (U+00F1)
            i += 1
    return i


def _word_to_roman(word: str) -> str:
    """Transliterate a single Devanagari word to Pratham Roman.

    Marathi schwa deletion: the inherent 'a' of a word-final consonant is
    NOT emitted. Every other position emits inherent 'a' unless an explicit
    vowel sign or virama is present.
    """
    result: list[str] = []
    i = 0
    n = len(word)

    while i < n:
        ch = word[i]

        # ── Independent vowel letter ─────────────────────────────────────
        if ch in VOWEL_LETTERS:
            result.append(VOWEL_LETTERS[ch])
            i += 1
            i = _handle_modifiers(word, i, n, result)

        # ── Consonant ────────────────────────────────────────────────────
        elif ch in CONSONANTS:
            # Nukta-modified consonant?
            if i + 1 < n and word[i + 1] == NUKTA:
                key = ch + NUKTA
                roman_con = NUKTA_CONSONANTS.get(key, CONSONANTS[ch])
                i += 2
            else:
                roman_con = CONSONANTS[ch]
                i += 1

            result.append(roman_con)

            if i >= n:
                # Word-final: Marathi schwa deletion — no inherent 'a'
                pass
            elif word[i] == VIRAMA:
                # Virama cancels inherent 'a'; conjunct follows
                i += 1
            elif word[i] in VOWEL_SIGNS:
                result.append(VOWEL_SIGNS[word[i]])
                i += 1
                i = _handle_modifiers(word, i, n, result)
            else:
                # Inherent 'a'
                result.append('a')
                i = _handle_modifiers(word, i, n, result)

        # ── Standalone anusvara ───────────────────────────────────────────
        elif ch == ANUSVARA:
            lookahead = word[i + 1] if i + 1 < n else None
            result.append(_anusvara_roman(lookahead))
            i += 1

        # ── Chandrabindu ─────────────────────────────────────────────────
        elif ch == CHANDRABINDU:
            result.append('\u00f1')
            i += 1

        # ── Visarga ──────────────────────────────────────────────────────
        elif ch == VISARGA:
            result.append('h')
            i += 1

        # ── Pass-through ─────────────────────────────────────────────────
        else:
            result.append(ch)
            i += 1

    return ''.join(result)


def dev_to_roman(text: str) -> str:
    """Convert Devanagari text to Pratham Roman transliteration.

    Implements the Pratham Transliteration Style with Marathi schwa deletion
    (word-final inherent 'a' omitted). Multi-word input is processed
    word-by-word (split on spaces).

    Args:
        text: Devanagari string.

    Returns:
        Pratham Roman string.

    Examples:
        >>> dev_to_roman("नमस्कार")
        'namaskaar'
        >>> dev_to_roman("संकट")
        'sangkaT'
        >>> dev_to_roman("काळ")
        'kaaL'
        >>> dev_to_roman("माँ")
        'maa\\u00f1'
    """
    if not text:
        return text
    return ' '.join(_word_to_roman(p) if p else '' for p in text.split(' '))


# Public aliases
transliterate = dev_to_roman
to_roman      = dev_to_roman


# ===========================================================================
# Roman → Devanagari  (returns list[str] of all plausible candidates)
# ===========================================================================

# Token table: (roman_pattern, type, dev_independent, dev_matra_sign)
#   type: 'C' = consonant  'V' = vowel  'AN' = anusvara  'CB' = chandrabindu
_ROMAN_TOKENS: list[tuple[str, str, str, str]] = [
    # ── Special markers ────────────────────────────────────────────────
    ('.n',  'AN', ANUSVARA,      ANUSVARA),
    ('\u00f1', 'CB', CHANDRABINDU, CHANDRABINDU),   # ñ
    # ── 3-char consonant / conjunct ────────────────────────────────────
    ('.Dh', 'C',  'ढ' + NUKTA,                  'ढ' + NUKTA),
    ('chh', 'C',  'छ',                            'छ'),
    ('kSh', 'C',  'क' + VIRAMA + 'ष',            'क' + VIRAMA + 'ष'),
    ('ksh', 'C',  'क' + VIRAMA + 'ष',            'क' + VIRAMA + 'ष'),
    # ── 2-char consonant ───────────────────────────────────────────────
    ('.D',  'C',  'ड' + NUKTA,  'ड' + NUKTA),
    ('KH',  'C',  'ख' + NUKTA,  'ख' + NUKTA),
    ('Th',  'C',  'ठ',          'ठ'),
    ('Dh',  'C',  'ढ',          'ढ'),
    ('Sh',  'C',  'ष',          'ष'),
    ('gh',  'C',  'घ',          'घ'),
    ('kh',  'C',  'ख',          'ख'),
    ('ch',  'C',  'च',          'च'),
    ('jh',  'C',  'झ',          'झ'),
    ('th',  'C',  'थ',          'थ'),
    ('dh',  'C',  'ध',          'ध'),
    ('ph',  'C',  'फ',          'फ'),
    ('bh',  'C',  'भ',          'भ'),
    ('sh',  'C',  'श',          'श'),
    ('ng',  'C',  'ङ',          'ङ'),
    ('ny',  'C',  'ञ',          'ञ'),
    ('G',   'C',  'ग' + NUKTA,  'ग' + NUKTA),
    # ── 2-char vowel ───────────────────────────────────────────────────
    ('aa',  'V',  'आ',  '\u093E'),
    ('ii',  'V',  'ई',  '\u0940'),
    ('uu',  'V',  'ऊ',  '\u0942'),
    ('ai',  'V',  'ऐ',  '\u0948'),
    ('au',  'V',  'औ',  '\u094C'),
    ('ri',  'V',  'ऋ',  '\u0943'),
    # ── 1-char consonant ───────────────────────────────────────────────
    ('T',   'C',  'ट',       'ट'),
    ('D',   'C',  'ड',       'ड'),
    ('N',   'C',  'ण',       'ण'),
    ('R',   'C',  '\u0931',  '\u0931'),
    ('L',   'C',  'ळ',       'ळ'),
    ('k',   'C',  'क',       'क'),
    ('g',   'C',  'ग',       'ग'),
    ('j',   'C',  'ज',       'ज'),
    ('n',   'C',  'न',       'न'),
    ('t',   'C',  'त',       'त'),
    ('d',   'C',  'द',       'द'),
    ('p',   'C',  'प',       'प'),
    ('b',   'C',  'ब',       'ब'),
    ('m',   'C',  'म',       'म'),
    ('y',   'C',  'य',       'य'),
    ('r',   'C',  'र',       'र'),
    ('l',   'C',  'ल',       'ल'),
    ('v',   'C',  'व',       'व'),
    ('s',   'C',  'स',       'स'),
    ('h',   'C',  'ह',       'ह'),
    ('f',   'C',  'फ' + NUKTA,  'फ' + NUKTA),
    ('z',   'C',  'ज' + NUKTA,  'ज' + NUKTA),
    ('q',   'C',  'क' + NUKTA,  'क' + NUKTA),
    # ── 1-char vowel (must come AFTER all consonants) ──────────────────
    ('a',   'V',  'अ',  ''),
    ('i',   'V',  'इ',  '\u093F'),
    ('u',   'V',  'उ',  '\u0941'),
    ('e',   'V',  'ए',  '\u0947'),
    ('o',   'V',  'ओ',  '\u094B'),
]

_MAX_ROMAN_TOKEN_LEN: int = max(len(r) for r, *_ in _ROMAN_TOKENS)

_NASAL_ANUSVARA: dict[str, frozenset] = {
    'ङ': _VELAR   | frozenset({'ख' + NUKTA, 'ग' + NUKTA}),
    'ञ': _PALATAL | frozenset({'ज' + NUKTA}),
    'ण': _RETROFLEX | frozenset({'ड' + NUKTA, 'ढ' + NUKTA}),
    'न': _DENTAL,
    'म': _LABIAL  | frozenset({'फ' + NUKTA}),
}


def _tokenize_roman_word(roman: str) -> list[tuple[str, str, str, str]]:
    """Longest-match scan: parse a Pratham Roman word into a token list."""
    tokens: list[tuple[str, str, str, str]] = []
    i = 0
    n = len(roman)
    while i < n:
        matched = False
        for pat_len in range(_MAX_ROMAN_TOKEN_LEN, 0, -1):
            if i + pat_len > n:
                continue
            sub = roman[i:i + pat_len]
            for entry in _ROMAN_TOKENS:
                if sub == entry[0]:
                    tokens.append(entry)
                    i += pat_len
                    matched = True
                    break
            if matched:
                break
        if not matched:
            ch = roman[i]
            tokens.append((ch, '?', ch, ch))
            i += 1
    return tokens


def _post_process_anusvara(
        tokens: list[tuple[str, str, str, str]]
) -> list[tuple[str, str, str, str]]:
    """Replace nasal-consonant tokens with anusvara when followed by same-POA consonant.

    Implements the inverse of anusvara assimilation for round-tripping.
    Lossiness: 'n' + dental and 'm' + labial are always read as anusvara.
    """
    result: list[tuple[str, str, str, str]] = []
    n = len(tokens)
    for i, tok in enumerate(tokens):
        dev = tok[2]
        if tok[1] == 'C' and dev in _NASAL_ANUSVARA:
            nxt = tokens[i + 1] if i + 1 < n else None
            if nxt and nxt[1] == 'C' and nxt[2] in _NASAL_ANUSVARA[dev]:
                result.append(('.n_auto', 'AN', ANUSVARA, ANUSVARA))
                continue
        result.append(tok)
    return result


def _build_devanagari(
        tokens: list[tuple[str, str, str, str]],
        word_final_virama: bool = False,
) -> str:
    """Assemble Devanagari from a token list."""
    result: list[str] = []
    prev_type: Optional[str] = None

    for tok in tokens:
        tok_type = tok[1]
        dev_init = tok[2]
        dev_sign = tok[3]

        if tok_type == 'C':
            if prev_type == 'C':
                result.append(VIRAMA)
            result.append(dev_init)
            prev_type = 'C'

        elif tok_type == 'V':
            if prev_type == 'C':
                if dev_sign:
                    result.append(dev_sign)
            else:
                result.append(dev_init)
            prev_type = 'V'

        elif tok_type == 'AN':
            result.append(ANUSVARA)
            prev_type = 'AN'

        elif tok_type == 'CB':
            result.append(CHANDRABINDU)
            prev_type = 'CB'

        else:
            result.append(dev_init)
            prev_type = '?'

    if word_final_virama and prev_type == 'C':
        result.append(VIRAMA)

    return ''.join(result)


def roman_to_dev(roman: str) -> list[str]:
    """Convert Pratham Roman to all plausible Devanagari forms.

    For a word ending in a bare consonant (no explicit vowel), two candidates
    are returned:
      1. No word-final virama  (Marathi inherent-a reading, e.g. वदन)
      2. With word-final virama (explicit halant form, e.g. वदन्)

    For multi-word input, returns the cross-product of per-word candidates.

    Args:
        roman: Pratham Roman string.

    Returns:
        List[str] of plausible Devanagari strings (at least one element).

    Examples:
        >>> roman_to_dev("vadan")
        ['वदन', 'वदन्']
        >>> "संकट" in roman_to_dev("sangkaT")
        True
    """
    if not roman:
        return [roman]

    per_word: list[list[str]] = []
    for word in roman.split(' '):
        if not word:
            per_word.append([''])
            continue
        tokens = _post_process_anusvara(_tokenize_roman_word(word))
        last_type = tokens[-1][1] if tokens else None
        if last_type == 'C':
            c1 = _build_devanagari(tokens, False)
            c2 = _build_devanagari(tokens, True)
            per_word.append([c1, c2] if c1 != c2 else [c1])
        else:
            per_word.append([_build_devanagari(tokens, False)])

    results: list[str] = []
    for combo in _iterproduct(*per_word):
        results.append(' '.join(combo))
    return results


# Public alias
to_devanagari = roman_to_dev


# ===========================================================================
# LEGACY — kept intact for backward-compatibility with normalize_input
# ===========================================================================

TRANSLITERATION_MAP: list[tuple[str, str]] = [
    ("ksh",  "क्ष"), ("dny",  "ज्ञ"), ("shr",  "श्र"), ("shch", "श्च"),
    ("kh",  "ख"),   ("gh",  "घ"),   ("ch",  "च"),   ("chh", "छ"),
    ("jh",  "झ"),   ("th",  "थ"),   ("dh",  "ध"),   ("ph",  "फ"),
    ("bh",  "भ"),   ("sh",  "श"),   ("ny",  "ञ"),   ("ng",  "ङ"),
    ("aa",  "आ"),   ("ee",  "ई"),   ("oo",  "ऊ"),   ("ai",  "ऐ"),
    ("au",  "औ"),   ("ri",  "ऋ"),
    ("a", "ा"), ("i", "ि"), ("u", "ु"), ("e", "े"), ("o", "ो"),
    ("k", "क"), ("g", "ग"), ("c", "च"), ("j", "ज"), ("t", "त"),
    ("d", "द"), ("n", "न"), ("p", "प"), ("b", "ब"), ("m", "म"),
    ("y", "य"), ("r", "र"), ("l", "ल"), ("v", "व"), ("w", "व"),
    ("s", "स"), ("h", "ह"), ("f", "फ"), ("z", "झ"),
    ("A", "अ"), ("I", "इ"), ("U", "उ"), ("E", "ए"), ("O", "ओ"),
]


def roman_to_devanagari(text: str) -> str:
    """
    Convert Roman Marathi to Devanagari (LEGACY function).

    This is a deterministic, conservative transliteration designed for
    dictionary key matching, not general-purpose transliteration.
    For the full Pratham Transliteration Style, use dev_to_roman / roman_to_dev.

    Args:
        text: Roman Marathi text

    Returns:
        Devanagari text (best effort)

    Examples:
        >>> roman_to_devanagari("pani")
        'पानी'
        >>> roman_to_devanagari("cha")
        'चा'
    """
    if not text:
        return text
    result = []
    i = 0
    while i < len(text):
        matched = False
        for pattern_len in range(4, 0, -1):
            if i + pattern_len > len(text):
                continue
            substring = text[i:i + pattern_len]
            for roman, devanagari in TRANSLITERATION_MAP:
                if substring.lower() == roman.lower():
                    result.append(devanagari)
                    i += pattern_len
                    matched = True
                    break
            if matched:
                break
        if not matched:
            result.append(text[i])
            i += 1
    return ''.join(result)
