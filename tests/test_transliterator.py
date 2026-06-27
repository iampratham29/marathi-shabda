"""Comprehensive tests for the Pratham Roman <-> Devanagari transliterator.

Tests cover all 12 categories defined by the Pratham Transliteration Style
as used in the marathi-shabda library (v0.2.0+).

Pratham Transliteration Style conventions:
  Retroflex (uppercase): T  Th  D  Dh  N  L  R
  Dental (lowercase):    t  th  d  dh  n
  Long vowels: aa  ii  uu
  Aspirates:   kh  gh  ch  chh  jh  ph  bh  dh  th
  Loans:       KH  G  z  .D  .Dh  f  q
  Chandrabindu: ñ   Anusvara: ng  ny  N  n  m  .n

Run standalone:
    python tests/test_transliterator.py
Run with pytest:
    python -m pytest tests/test_transliterator.py -v
"""
# Force UTF-8 output on Windows so Devanagari characters print correctly
import os as _os
_os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

import sys
import os

# Ensure the package is importable when run as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from marathi_shabda.normalization.transliterator import dev_to_roman, roman_to_dev

# ñ character (U+00F1) used in Pratham style for chandrabindu ँ
_N_TILDE = '\u00f1'


# ===========================================================================
# Category 1 — Short vs Long vowels
# ===========================================================================

def test_cat1_short_long_a_vadan():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Short inherent 'a' and long 'aa' must produce distinct Roman output.
    Pratham Transliteration Style:
      अ / inherent a  → "a"   (English: bus, ado)
      आ / ा matra    → "aa"  (English: father, start)
    Fix: VOWEL_SIGNS["\\u093E"] must be "aa"; inherent vowel appended as "a" in FSM.
    File: transliterator.py  Tables: VOWEL_SIGNS, _word_to_roman (else branch → 'a')
    """
    assert dev_to_roman("वदन")  == "vadan",   REQUIREMENT_PROMPT + " | वदन → vadan"
    assert dev_to_roman("वादन") == "vaadan",  REQUIREMENT_PROMPT + " | वादन → vaadan"
    assert "वदन"  in roman_to_dev("vadan"),   REQUIREMENT_PROMPT + " | round-trip vadan"
    assert "वादन" in roman_to_dev("vaadan"),  REQUIREMENT_PROMPT + " | round-trip vaadan"


def test_cat1_short_long_i_dil():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Short 'i' (ि) → "i" and long 'ii' (ी) → "ii" must be distinct.
    Pratham style: इ/ि → "i" | ई/ी → "ii"
    Fix: VOWEL_SIGNS["\\u093F"] = "i", VOWEL_SIGNS["\\u0940"] = "ii"
    File: transliterator.py  Table: VOWEL_SIGNS
    """
    assert dev_to_roman("दिल")  == "dil",   REQUIREMENT_PROMPT + " | दिल → dil"
    assert dev_to_roman("दील")  == "diil",  REQUIREMENT_PROMPT + " | दील → diil"
    assert "दिल" in roman_to_dev("dil"),    REQUIREMENT_PROMPT + " | round-trip dil"
    assert "दील" in roman_to_dev("diil"),   REQUIREMENT_PROMPT + " | round-trip diil"


def test_cat1_short_long_u_pul():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Short 'u' (ु) → "u" and long 'uu' (ू) → "uu" must be distinct.
    Pratham style: उ/ु → "u" | ऊ/ू → "uu"
    Fix: VOWEL_SIGNS["\\u0941"] = "u", VOWEL_SIGNS["\\u0942"] = "uu"
    File: transliterator.py  Table: VOWEL_SIGNS
    """
    assert dev_to_roman("पुल")  == "pul",   REQUIREMENT_PROMPT + " | पुल → pul"
    assert dev_to_roman("पूल")  == "puul",  REQUIREMENT_PROMPT + " | पूल → puul"
    assert "पुल" in roman_to_dev("pul"),    REQUIREMENT_PROMPT + " | round-trip pul"
    assert "पूल" in roman_to_dev("puul"),   REQUIREMENT_PROMPT + " | round-trip puul"


def test_cat1_short_long_a_pairs():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Multiple a/aa minimal pairs to confirm the pattern is systematic.
    Pratham style: inherent a → "a" | ā matra → "aa"
    Fix: same as test_cat1_short_long_a_vadan
    """
    assert dev_to_roman("मन")  == "man",   REQUIREMENT_PROMPT
    assert dev_to_roman("मान") == "maan",  REQUIREMENT_PROMPT
    assert dev_to_roman("सन")  == "san",   REQUIREMENT_PROMPT
    assert dev_to_roman("सान") == "saan",  REQUIREMENT_PROMPT
    assert dev_to_roman("कन")  == "kan",   REQUIREMENT_PROMPT
    assert dev_to_roman("कान") == "kaan",  REQUIREMENT_PROMPT


# ===========================================================================
# Category 2 — Retroflex vs Dental minimal pairs
# ===========================================================================

def test_cat2_retroflex_dental_T_t():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Retroflex ट → "T" (uppercase) must be distinct from dental त → "t".
    Pratham style: ट → T  |  त → t
    Fix: CONSONANTS["ट"] = "T", CONSONANTS["त"] = "t"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("टन") == "Tan",  REQUIREMENT_PROMPT + " | टन → Tan"
    assert dev_to_roman("तन") == "tan",  REQUIREMENT_PROMPT + " | तन → tan"
    assert "टन" in roman_to_dev("Tan"),  REQUIREMENT_PROMPT + " | round-trip Tan"
    assert "तन" in roman_to_dev("tan"),  REQUIREMENT_PROMPT + " | round-trip tan"


def test_cat2_retroflex_dental_D_d():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Retroflex ड → "D" (uppercase) must be distinct from dental द → "d".
    Pratham style: ड → D  |  द → d
    Fix: CONSONANTS["ड"] = "D", CONSONANTS["द"] = "d"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("डाळ") == "DaaL", REQUIREMENT_PROMPT + " | डाळ → DaaL"
    assert dev_to_roman("दाळ") == "daaL", REQUIREMENT_PROMPT + " | दाळ → daaL"
    assert "डाळ" in roman_to_dev("DaaL"), REQUIREMENT_PROMPT + " | round-trip DaaL"
    assert "दाळ" in roman_to_dev("daaL"), REQUIREMENT_PROMPT + " | round-trip daaL"


def test_cat2_retroflex_dental_N_n():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Retroflex ण → "N" (uppercase) must be distinct from dental न → "n".
    Pratham style: ण → N  |  न → n
    Fix: CONSONANTS["ण"] = "N", CONSONANTS["न"] = "n"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("पण") == "paN", REQUIREMENT_PROMPT + " | पण → paN"
    assert dev_to_roman("पन") == "pan", REQUIREMENT_PROMPT + " | पन → pan"
    assert "पण" in roman_to_dev("paN"), REQUIREMENT_PROMPT + " | round-trip paN"
    assert "पन" in roman_to_dev("pan"), REQUIREMENT_PROMPT + " | round-trip pan"


def test_cat2_aspirate_retroflex():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Retroflex aspirates Th/Dh (uppercase) vs dental th/dh (lowercase).
    Pratham style: ठ → Th  ढ → Dh  |  थ → th  ध → dh
    Fix: CONSONANTS table with proper case.
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("ठाव")  == "Thaav",  REQUIREMENT_PROMPT + " | ठाव → Thaav"
    assert dev_to_roman("थाव")  == "thaav",  REQUIREMENT_PROMPT + " | थाव → thaav"
    assert dev_to_roman("ढाल")  == "Dhaal",  REQUIREMENT_PROMPT + " | ढाल → Dhaal"
    assert dev_to_roman("धाल")  == "dhaal",  REQUIREMENT_PROMPT + " | धाल → dhaal"


# ===========================================================================
# Category 3 — Aspirate vs Unaspirate minimal pairs
# ===========================================================================

def test_cat3_k_kh():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Unaspirate क → "k" vs aspirate ख → "kh".
    Pratham style: क → k  |  ख → kh
    Fix: CONSONANTS["क"] = "k", CONSONANTS["ख"] = "kh"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("काम") == "kaam",  REQUIREMENT_PROMPT
    assert dev_to_roman("खाम") == "khaam", REQUIREMENT_PROMPT


def test_cat3_g_gh():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: ग → "g" vs घ → "gh".
    Pratham style: ग → g  |  घ → gh
    Fix: CONSONANTS table.
    """
    assert dev_to_roman("गाय")  == "gaay",  REQUIREMENT_PROMPT
    assert dev_to_roman("घाय")  == "ghaay", REQUIREMENT_PROMPT


def test_cat3_p_ph_b_bh():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: प → "p" vs फ → "ph"; ब → "b" vs भ → "bh".
    Pratham style: प → p  फ → ph  ब → b  भ → bh
    Fix: CONSONANTS table.
    """
    assert dev_to_roman("पाल")  == "paal",  REQUIREMENT_PROMPT
    assert dev_to_roman("फाल")  == "phaal", REQUIREMENT_PROMPT
    assert dev_to_roman("बाल")  == "baal",  REQUIREMENT_PROMPT
    assert dev_to_roman("भाल")  == "bhaal", REQUIREMENT_PROMPT


def test_cat3_ch_chh():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: च → "ch" vs छ → "chh".
    Pratham style: च → ch  |  छ → chh
    Fix: CONSONANTS["च"] = "ch", CONSONANTS["छ"] = "chh"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("चाल")  == "chaal",  REQUIREMENT_PROMPT
    assert dev_to_roman("छाल")  == "chhaal", REQUIREMENT_PROMPT
    assert "चाल" in roman_to_dev("chaal"),   REQUIREMENT_PROMPT
    assert "छाल" in roman_to_dev("chhaal"),  REQUIREMENT_PROMPT


# ===========================================================================
# Category 4 — Conjuncts / Halant (virama)
# ===========================================================================

def test_cat4_conjunct_initial_pr():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Virama cancels inherent 'a'; conjunct प्र = p + r (no 'a' between).
    Pratham style: ् (virama) → consumed silently; p + r written as "pr".
    Fix: _word_to_roman must consume virama and NOT emit 'a' after consonant+virama.
    File: transliterator.py  Function: _word_to_roman (virama branch)
    """
    # प्रण: p + r (conjunct) + aN (word-final N, schwa-deleted)
    assert dev_to_roman("प्रण")    == "praN",    REQUIREMENT_PROMPT
    assert "प्रण" in roman_to_dev("praN"),       REQUIREMENT_PROMPT


def test_cat4_conjunct_medial_shabd():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Medial conjunct ब्द = b (virama) d; शब्द → "shabd".
    Fix: same as above — virama handling in _word_to_roman.
    """
    assert dev_to_roman("शब्द")   == "shabd",   REQUIREMENT_PROMPT
    assert "शब्द" in roman_to_dev("shabd"),     REQUIREMENT_PROMPT


def test_cat4_conjunct_namaskar():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: नमस्कार has medial virama (स्क); result is "namaskaar".
    The ā matra (0x93E) after क gives "kaa"; word-final र (schwa-deleted) → "r".
    Full breakdown: na-ma-s-kaa-r = "namaskaar".
    Fix: virama branch in _word_to_roman (consumes virama, no 'a' added).
    """
    assert dev_to_roman("नमस्कार") == "namaskaar",  REQUIREMENT_PROMPT
    assert "नमस्कार" in roman_to_dev("namaskaar"),  REQUIREMENT_PROMPT


def test_cat4_conjunct_ksha():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: क्ष (k + virama + ष) → "kSh"; ष → "Sh" (distinct from श → "sh").
    Pratham style: ष → Sh (retroflex sibilant).
    Fix: CONSONANTS["ष"] = "Sh"; roman_to_dev("kSh") must return क्ष.
    File: transliterator.py  Table: CONSONANTS; _ROMAN_TOKENS 'kSh' entry.
    """
    assert dev_to_roman("क्ष")   == "kSh",        REQUIREMENT_PROMPT
    assert "क्ष" in roman_to_dev("kSh"),           REQUIREMENT_PROMPT
    assert "क्ष" in roman_to_dev("ksh"),           REQUIREMENT_PROMPT   # legacy alias


def test_cat4_conjunct_tra():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: त्र (t + virama + r) → "tr" in conjunct; मित्र → "mitr".
    Fix: virama handling.
    """
    assert dev_to_roman("मित्र") == "mitr",        REQUIREMENT_PROMPT
    assert "मित्र" in roman_to_dev("mitr"),        REQUIREMENT_PROMPT


# ===========================================================================
# Category 5 — Anusvara assimilation (one per place of articulation)
# ===========================================================================

def test_cat5_anusvara_velar_sangkaT():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Anusvara before velar consonant → "ng".
    Pratham style: anusvara before velar (क ख ग घ ङ) → "ng".
    Fix: _anusvara_roman: if next_char in _VELAR → "ng"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("संकट")    == "sangkaT",   REQUIREMENT_PROMPT
    assert "संकट" in roman_to_dev("sangkaT"),      REQUIREMENT_PROMPT


def test_cat5_anusvara_palatal_sanych():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Anusvara before palatal consonant → "ny".
    Pratham style: anusvara before palatal (च छ ज झ ञ) → "ny".
    Fix: _anusvara_roman: if next_char in _PALATAL → "ny"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("संच")     == "sanych",    REQUIREMENT_PROMPT
    assert "संच" in roman_to_dev("sanych"),        REQUIREMENT_PROMPT


def test_cat5_anusvara_retroflex_saNT():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Anusvara before retroflex consonant → "N" (uppercase).
    Pratham style: anusvara before retroflex (ट ठ ड ढ ण) → "N".
    Fix: _anusvara_roman: if next_char in _RETROFLEX → "N"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("संट")     == "saNT",      REQUIREMENT_PROMPT
    assert "संट" in roman_to_dev("saNT"),          REQUIREMENT_PROMPT


def test_cat5_anusvara_dental_sant():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Anusvara before dental consonant → "n".
    Pratham style: anusvara before dental (त थ द ध न) → "n".
    Fix: _anusvara_roman: if next_char in _DENTAL → "n"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("संत")     == "sant",      REQUIREMENT_PROMPT
    assert "संत" in roman_to_dev("sant"),          REQUIREMENT_PROMPT


def test_cat5_anusvara_labial_samp():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Anusvara before labial consonant → "m".
    Pratham style: anusvara before labial (प फ ब भ म) → "m".
    Fix: _anusvara_roman: if next_char in _LABIAL → "m"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("संप")     == "samp",      REQUIREMENT_PROMPT
    assert "संप" in roman_to_dev("samp"),          REQUIREMENT_PROMPT


def test_cat5_anusvara_word_final_hun():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Word-final or pre-vowel anusvara → ".n".
    Pratham style: anusvara word-final → ".n"
    Fix: _anusvara_roman: if next_char is None → ".n"
    File: transliterator.py  Function: _anusvara_roman
    """
    assert dev_to_roman("हुं")     == "hu.n",       REQUIREMENT_PROMPT
    assert "हुं" in roman_to_dev("hu.n"),           REQUIREMENT_PROMPT


# ===========================================================================
# Category 6 — Chandrabindu / Nasalised vowels
# ===========================================================================

def test_cat6_chandrabindu_maan():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Chandrabindu ँ → ñ (n-tilde, U+00F1); always.
    Pratham style: ँ → ñ
    Fix: _handle_modifiers appends '\\u00f1' for CHANDRABINDU; _word_to_roman
         also handles standalone CHANDRABINDU.
    File: transliterator.py  Functions: _handle_modifiers, _word_to_roman
    """
    assert dev_to_roman("माँ")   == "maa" + _N_TILDE,   REQUIREMENT_PROMPT
    assert "माँ" in roman_to_dev("maa" + _N_TILDE),     REQUIREMENT_PROMPT


def test_cat6_chandrabindu_haan():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: हाँ (yes) → "haaÃ" using ñ for chandrabindu.
    Pratham style: ँ → ñ
    """
    assert dev_to_roman("हाँ")   == "haa" + _N_TILDE,  REQUIREMENT_PROMPT
    assert "हाँ" in roman_to_dev("haa" + _N_TILDE),    REQUIREMENT_PROMPT


def test_cat6_chandrabindu_aankh():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: आँख (eye) → independent vowel आ with chandrabindu + ख.
    Expected: "aa" + ñ + "kh"
    Pratham style: आ (independent) → "aa"; ँ → ñ; ख → "kh"
    """
    expected = "aa" + _N_TILDE + "kh"
    assert dev_to_roman("आँख")   == expected,          REQUIREMENT_PROMPT
    assert "आँख" in roman_to_dev(expected),            REQUIREMENT_PROMPT


def test_cat6_chandrabindu_yahaan():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: यहाँ (here) → "yahaa" + ñ (chandrabindu on ā).
    """
    expected = "yahaa" + _N_TILDE
    assert dev_to_roman("यहाँ")  == expected,          REQUIREMENT_PROMPT
    assert "यहाँ" in roman_to_dev(expected),           REQUIREMENT_PROMPT


# ===========================================================================
# Category 7 — Marathi-specific consonants
# ===========================================================================

def test_cat7_marathi_La_kaaL():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Marathi retroflex lateral ळ → "L" (uppercase).
    Pratham style adds this Marathi-specific consonant (not in standard Hindi/Urdu schemes).
    Fix: CONSONANTS["ळ"] = "L"
    File: transliterator.py  Table: CONSONANTS
    """
    assert dev_to_roman("काळ")   == "kaaL",   REQUIREMENT_PROMPT
    assert "काळ" in roman_to_dev("kaaL"),     REQUIREMENT_PROMPT


def test_cat7_marathi_La_shaala():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: शाळा (school) → "shaaLaa"; ळ → "L" (uppercase) in medial position.
    Pratham style Marathi extension: ळ → L (uppercase retroflex lateral).
    Fix: CONSONANTS["ळ"] = "L"
    """
    assert dev_to_roman("शाळा")  == "shaaLaa",  REQUIREMENT_PROMPT
    assert "शाळा" in roman_to_dev("shaaLaa"),   REQUIREMENT_PROMPT


def test_cat7_marathi_La_paalii():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: पाळी (raised / kept) → "paaLii"; ळ → "L" (uppercase), ी → "ii".
    Pratham style Marathi extension: ळ → L.
    """
    assert dev_to_roman("पाळी")  == "paaLii",  REQUIREMENT_PROMPT
    assert "पाळी" in roman_to_dev("paaLii"),   REQUIREMENT_PROMPT


def test_cat7_marathi_Ra_eyelash():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Marathi eyelash ra ऱ (U+0931) → "R" (uppercase).
    Fix: CONSONANTS["\\u0931"] = "R"
    File: transliterator.py  Table: CONSONANTS
    """
    # शेऱ्या: श + े + ऱ + ् + य + ा
    assert dev_to_roman("शेऱ्या") == "sheRyaa",  REQUIREMENT_PROMPT
    assert "शेऱ्या" in roman_to_dev("sheRyaa"),  REQUIREMENT_PROMPT


def test_cat7_marathi_Ra_baaryaa():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: बाऱ्या → "baaRyaa"; eyelash ra in medial conjunct with virama.
    """
    assert dev_to_roman("बाऱ्या") == "baaRyaa",  REQUIREMENT_PROMPT
    assert "बाऱ्या" in roman_to_dev("baaRyaa"),  REQUIREMENT_PROMPT


# ===========================================================================
# Category 8 — Nukta / Urdu loan consonants
# ===========================================================================

def test_cat8_nukta_KH():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: ख़ (ख + ़) → "KH" (uppercase KH).
    Pratham style: ख़ → KH
    Fix: NUKTA_CONSONANTS["ख" + NUKTA] = "KH"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    # ख़ + ा → "KHaa"
    word = "ख\u093Cा"   # ख + nukta + ā
    assert dev_to_roman(word)     == "KHaa",   REQUIREMENT_PROMPT
    assert word in roman_to_dev("KHaa"),       REQUIREMENT_PROMPT


def test_cat8_nukta_z():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: ज़ (ज + ़) → "z".
    Pratham style: ज़ → z
    Fix: NUKTA_CONSONANTS["ज" + NUKTA] = "z"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    word = "ज\u093Cा"   # ज + nukta + ā
    assert dev_to_roman(word)     == "zaa",    REQUIREMENT_PROMPT
    assert word in roman_to_dev("zaa"),        REQUIREMENT_PROMPT


def test_cat8_nukta_dotD():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: ड़ (ड + ़) → ".D".
    Pratham style: ड़ → .D
    Fix: NUKTA_CONSONANTS["ड" + NUKTA] = ".D"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    word = "ड\u093Cा"   # ड + nukta + ā
    assert dev_to_roman(word)     == ".Daa",   REQUIREMENT_PROMPT
    assert word in roman_to_dev(".Daa"),       REQUIREMENT_PROMPT


def test_cat8_nukta_f():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: फ़ (फ + ़) → "f".
    Pratham style: फ़ → f
    Fix: NUKTA_CONSONANTS["फ" + NUKTA] = "f"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    word = "फ\u093Cा"   # फ + nukta + ā
    assert dev_to_roman(word)     == "faa",    REQUIREMENT_PROMPT
    assert word in roman_to_dev("faa"),        REQUIREMENT_PROMPT


def test_cat8_nukta_G():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: ग़ (ग + ़) → "G" (uppercase).
    Pratham style: ग़ → G
    Fix: NUKTA_CONSONANTS["ग" + NUKTA] = "G"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    word = "ग\u093Cा"   # ग + nukta + ā
    assert dev_to_roman(word)     == "Gaa",    REQUIREMENT_PROMPT
    assert word in roman_to_dev("Gaa"),        REQUIREMENT_PROMPT


def test_cat8_nukta_q():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: क़ (क + ़) → "q".
    Pratham style: क़ → q
    Fix: NUKTA_CONSONANTS["क" + NUKTA] = "q"
    File: transliterator.py  Table: NUKTA_CONSONANTS
    """
    word = "क\u093Cा"   # क + nukta + ā
    assert dev_to_roman(word)     == "qaa",    REQUIREMENT_PROMPT
    assert word in roman_to_dev("qaa"),        REQUIREMENT_PROMPT


# ===========================================================================
# Category 9 — Independent vowel letters (word-initial)
# ===========================================================================

def test_cat9_independent_vowels():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Every independent vowel letter must map to its Pratham Roman form.
    Pratham style: अ→a  आ→aa  इ→i  ई→ii  उ→u  ऊ→uu  ए→e  ऐ→ai  ओ→o  औ→au  ऋ→ri
    Fix: VOWEL_LETTERS table.
    File: transliterator.py  Table: VOWEL_LETTERS
    """
    cases = [
        ("अ", "a"), ("आ", "aa"), ("इ", "i"), ("ई", "ii"),
        ("उ", "u"), ("ऊ", "uu"), ("ए", "e"), ("ऐ", "ai"),
        ("ओ", "o"), ("औ", "au"), ("ऋ", "ri"),
    ]
    for dev, roman in cases:
        assert dev_to_roman(dev) == roman, \
            REQUIREMENT_PROMPT + f" | {dev} → {roman}"
        assert dev in roman_to_dev(roman), \
            REQUIREMENT_PROMPT + f" | round-trip {roman} ∋ {dev}"


def test_cat9_independent_vowel_in_word():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Independent vowel आम (mango) → "aam"; एक (one) → "ek".
    Shows vowel letter at word start followed by consonant (schwa-deleted word-final).
    """
    assert dev_to_roman("आम") == "aam",  REQUIREMENT_PROMPT
    assert dev_to_roman("एक") == "ek",   REQUIREMENT_PROMPT
    assert "आम" in roman_to_dev("aam"),  REQUIREMENT_PROMPT
    assert "एक" in roman_to_dev("ek"),   REQUIREMENT_PROMPT


# ===========================================================================
# Category 10 — Round-trip identity
# ===========================================================================

_ROUND_TRIP_WORDS = [
    # Category 1
    "वदन", "वादन", "दिल", "दील", "पुल", "पूल", "मन", "मान",
    # Category 2
    "पण", "पन", "डाळ", "दाळ",
    # Category 3
    "काम", "खाम", "पाल", "फाल",
    # Category 4
    "शब्द", "नमस्कार", "मित्र",
    # Category 5
    "संकट", "संच", "संट", "संत", "संप",
    # Category 6
    "माँ", "हाँ",
    # Category 7
    "काळ", "शाळा", "शेऱ्या",
]


def test_cat10_round_trip_identity():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: For every word W: W ∈ roman_to_dev(dev_to_roman(W)).
    This verifies that dev_to_roman and roman_to_dev are inverses.
    Fix: any bug in either direction.
    File: transliterator.py  Functions: dev_to_roman, roman_to_dev
    """
    for word in _ROUND_TRIP_WORDS:
        roman = dev_to_roman(word)
        candidates = roman_to_dev(roman)
        assert word in candidates, \
            REQUIREMENT_PROMPT + f" | FAIL: {word} → {roman!r} → {candidates}"


# ===========================================================================
# Category 11 — roman_to_dev ambiguity (word-final implicit schwa)
# ===========================================================================

def test_cat11_ambiguity_vadan():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: roman_to_dev("vadan") must return BOTH:
      1. वदन  (Marathi: inherent-a reading, no word-final virama)
      2. वदन् (explicit halant form, used in Sanskrit/formal contexts)
    Fix: roman_to_dev generates two candidates when last token is a bare consonant.
    File: transliterator.py  Function: roman_to_dev
    """
    candidates = roman_to_dev("vadan")
    assert "वदन"  in candidates, REQUIREMENT_PROMPT + " | missing वदन"
    assert "वदन्" in candidates, REQUIREMENT_PROMPT + " | missing वदन्"


def test_cat11_ambiguity_san():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: roman_to_dev("san") must return both सन and सन्.
    Fix: same as test_cat11_ambiguity_vadan.
    """
    candidates = roman_to_dev("san")
    assert "सन"  in candidates, REQUIREMENT_PROMPT + " | missing सन"
    assert "सन्" in candidates, REQUIREMENT_PROMPT + " | missing सन्"


def test_cat11_ambiguity_no_double_when_vowel_final():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: roman_to_dev("vaadan") ends in vowel 'n' after 'aa', so the
    word-final token is NOT a bare consonant — only ONE candidate (वादन) needed.
    Actually 'n' IS a consonant token. Two candidates: वादन and वादन्.
    The key requirement: at minimum वादन is present.
    Fix: roman_to_dev candidate generation.
    """
    candidates = roman_to_dev("vaadan")
    assert "वादन" in candidates, REQUIREMENT_PROMPT


def test_cat11_ambiguity_vowel_terminal_no_virama_extra():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: roman_to_dev("mitraa") ends in vowel 'aa', prev_type='V',
    so NO word-final virama candidate — only one candidate मित्रा.
    Fix: roman_to_dev: virama candidate only added when last token type == 'C'.
    """
    candidates = roman_to_dev("mitraa")
    assert "मित्रा" in candidates, REQUIREMENT_PROMPT
    # Should NOT generate मित्रा· (virama after vowel)
    assert "मित्रा" + "\u094D" not in candidates, REQUIREMENT_PROMPT


# ===========================================================================
# Category 12 — Multi-word / phrase
# ===========================================================================

def test_cat12_multiword_namaskar():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: Multi-word input is split on spaces; each word processed independently.
    नमस्कार → "namaskaar" (ā matra on क gives long aa)
    मित्रा   → "mitraa"   (त्र conjunct + ā matra)
    Together: "namaskaar mitraa"
    Fix: dev_to_roman splits on ' ' and joins with ' '.
    File: transliterator.py  Function: dev_to_roman
    """
    assert dev_to_roman("नमस्कार मित्रा") == "namaskaar mitraa", REQUIREMENT_PROMPT
    assert "नमस्कार मित्रा" in roman_to_dev("namaskaar mitraa"), REQUIREMENT_PROMPT


def test_cat12_multiword_kaLa_shaLaa():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: "काळ शाळा" (black / school) → "kaaL shaaLaa"; spaces preserved.
    ळ → L (uppercase), ā matra → aa. Schwa-deleted word-final ळ gets no trailing a.
    """
    assert dev_to_roman("काळ शाळा")   == "kaaL shaaLaa",  REQUIREMENT_PROMPT
    assert "काळ शाळा" in roman_to_dev("kaaL shaaLaa"),    REQUIREMENT_PROMPT


def test_cat12_multiword_sangkaT_sant():
    REQUIREMENT_PROMPT = """
    REQUIREMENT: "संकट संत" → "sangkaT sant"; anusvara assimilation correct in both words.
    """
    assert dev_to_roman("संकट संत") == "sangkaT sant",    REQUIREMENT_PROMPT
    assert "संकट संत" in roman_to_dev("sangkaT sant"),    REQUIREMENT_PROMPT


# ===========================================================================
# Legacy backward-compat smoke test
# ===========================================================================

def test_legacy_roman_to_devanagari_still_works():
    """Verify the old roman_to_devanagari function is not broken by the new code."""
    from marathi_shabda.normalization.transliterator import roman_to_devanagari
    result = roman_to_devanagari("pani")
    assert len(result) > 0, "legacy roman_to_devanagari must still return non-empty string"
    # Must still contain Devanagari characters
    assert any('\u0900' <= c <= '\u097F' for c in result), \
        "legacy roman_to_devanagari must produce Devanagari"


# ===========================================================================
# run_all — standalone runner with ✓/✗ output
# ===========================================================================

def run_all():
    """Run every test function, printing ✓/✗ per test.
    Exits with code 1 if any test fails.
    """
    tests = [
        test_cat1_short_long_a_vadan,
        test_cat1_short_long_i_dil,
        test_cat1_short_long_u_pul,
        test_cat1_short_long_a_pairs,
        test_cat2_retroflex_dental_T_t,
        test_cat2_retroflex_dental_D_d,
        test_cat2_retroflex_dental_N_n,
        test_cat2_aspirate_retroflex,
        test_cat3_k_kh,
        test_cat3_g_gh,
        test_cat3_p_ph_b_bh,
        test_cat3_ch_chh,
        test_cat4_conjunct_initial_pr,
        test_cat4_conjunct_medial_shabd,
        test_cat4_conjunct_namaskar,
        test_cat4_conjunct_ksha,
        test_cat4_conjunct_tra,
        test_cat5_anusvara_velar_sangkaT,
        test_cat5_anusvara_palatal_sanych,
        test_cat5_anusvara_retroflex_saNT,
        test_cat5_anusvara_dental_sant,
        test_cat5_anusvara_labial_samp,
        test_cat5_anusvara_word_final_hun,
        test_cat6_chandrabindu_maan,
        test_cat6_chandrabindu_haan,
        test_cat6_chandrabindu_aankh,
        test_cat6_chandrabindu_yahaan,
        test_cat7_marathi_La_kaaL,
        test_cat7_marathi_La_shaala,
        test_cat7_marathi_La_paalii,
        test_cat7_marathi_Ra_eyelash,
        test_cat7_marathi_Ra_baaryaa,
        test_cat8_nukta_KH,
        test_cat8_nukta_z,
        test_cat8_nukta_dotD,
        test_cat8_nukta_f,
        test_cat8_nukta_G,
        test_cat8_nukta_q,
        test_cat9_independent_vowels,
        test_cat9_independent_vowel_in_word,
        test_cat10_round_trip_identity,
        test_cat11_ambiguity_vadan,
        test_cat11_ambiguity_san,
        test_cat11_ambiguity_no_double_when_vowel_final,
        test_cat11_ambiguity_vowel_terminal_no_virama_extra,
        test_cat12_multiword_namaskar,
        test_cat12_multiword_kaLa_shaLaa,
        test_cat12_multiword_sangkaT_sant,
        test_legacy_roman_to_devanagari_still_works,
    ]

    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  [PASS]  {fn.__name__}")
            passed += 1
        except AssertionError as exc:
            print(f"  [FAIL]  {fn.__name__}")
            msg = str(exc)
            # Truncate long REQUIREMENT_PROMPT messages for readability
            if len(msg) > 300:
                msg = msg[:300] + '...'
            print(f"          {msg}")
            failed += 1
        except Exception as exc:
            print(f"  [ERROR] {fn.__name__}")
            print(f"          {type(exc).__name__}: {exc}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"  {passed} passed   {failed} failed   (total {passed + failed})")
    print('='*60)
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    run_all()
