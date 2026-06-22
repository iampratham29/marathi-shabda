"""
fetch_kaikki.py — Phase 1 bulk fetcher
Downloads the Kaikki.org dedicated Marathi JSON (Wiktextract extract from English Wiktionary)
and converts each entry to the normalized format consumed by import_dictionary.py.

Source URL: https://kaikki.org/dictionary/Marathi/kaikki.org-dictionary-Marathi.json
Est. size  : ~5 MB
Est. words : ~25,000 senses

Usage:
    python scripts/fetch_kaikki.py --output data/processed/kaikki_entries.json
    python scripts/fetch_kaikki.py --output data/processed/kaikki_entries.json --skip-download
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
KAIKKI_URL = (
    "https://kaikki.org/dictionary/Marathi/kaikki.org-dictionary-Marathi.jsonl"
)
RAW_PATH = Path("data/raw/kaikki_marathi.jsonl")

POS_MAP = {
    "noun": "noun",
    "verb": "verb",
    "adj": "adjective",
    "adjective": "adjective",
    "adv": "adverb",
    "adverb": "adverb",
    "pron": "pronoun",
    "pronoun": "pronoun",
    "prep": "postposition",
    "postposition": "postposition",
    "conj": "conjunction",
    "conjunction": "conjunction",
    "intj": "interjection",
    "interjection": "interjection",
    "particle": "particle",
    "num": "numeral",
    "numeral": "numeral",
}

DEVANAGARI_RANGE = (0x0900, 0x097F)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_devanagari(text: str) -> bool:
    """Return True if text contains at least one Devanagari codepoint."""
    return any(DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1] for c in text)


def normalize_pos(raw_pos: str) -> str:
    return POS_MAP.get(raw_pos.lower().strip(), "unknown")


def extract_gloss(entry: dict) -> str:
    """Pull the first English gloss from senses[]."""
    senses = entry.get("senses") or []
    for sense in senses:
        glosses = sense.get("glosses") or []
        if glosses:
            gloss = glosses[0].strip()
            if gloss:
                return gloss[:200]  # cap length
    return ""


def download_kaikki(raw_path: Path) -> None:
    """Download the Kaikki Marathi JSON to raw_path with progress display."""
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Kaikki Marathi JSON from:\n  {KAIKKI_URL}")
    print(f"Saving to: {raw_path}")

    req = urllib.request.Request(
        KAIKKI_URL,
        headers={"User-Agent": "MarathiShabdaPipeline/1.0 (github.com/iampratham29/marathi-shabda)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 65536  # 64 KB

            with open(raw_path, "wb") as f:
                while True:
                    data = response.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  {downloaded // 1024} KB / {total // 1024} KB ({pct:.1f}%)   ", end="", flush=True)

        print(f"\nDownload complete: {raw_path.stat().st_size // 1024} KB")
    except Exception as exc:
        print(f"\nERROR: Download failed — {exc}", file=sys.stderr)
        sys.exit(1)


def parse_kaikki(raw_path: Path) -> list[dict]:
    """
    Parse the Kaikki JSON file.
    The file is JSONL (one JSON object per line) or a JSON array —
    we handle both formats gracefully.
    """
    entries = []
    seen_devanagari: set[str] = set()

    with open(raw_path, "r", encoding="utf-8") as f:
        # Peek at first non-whitespace byte to decide format
        first_char = ""
        for line in f:
            stripped = line.strip()
            if stripped:
                first_char = stripped[0]
                break
        f.seek(0)

        if first_char == "[":
            # JSON array format
            try:
                records = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON array — {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # JSONL format (one object per line)
            records = []
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines silently
                    pass

    print(f"Parsed {len(records)} raw records from Kaikki file.")

    skipped_non_dev = 0
    skipped_dup = 0

    for record in records:
        word = (record.get("word") or "").strip()

        # Must contain Devanagari
        if not is_devanagari(word):
            skipped_non_dev += 1
            continue

        # Deduplicate by Devanagari word (first sense wins)
        if word in seen_devanagari:
            skipped_dup += 1
            continue
        seen_devanagari.add(word)

        raw_pos = record.get("pos") or "unknown"
        pos = normalize_pos(raw_pos)
        gloss = extract_gloss(record)

        entry = {
            "devanagari": word,
            "key": "",          # Roman transliteration — enriched later by enrich_roman.py
            "meaning2": gloss,
            "definition_mr": "",
            "pos": pos,
            "source": "kaikki_wiktionary",
        }
        entries.append(entry)

    print(f"  Devanagari entries kept : {len(entries)}")
    print(f"  Skipped (non-Devanagari): {skipped_non_dev}")
    print(f"  Skipped (duplicate)     : {skipped_dup}")
    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: Download and parse Kaikki Marathi dictionary data."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write normalized JSON output (e.g. data/processed/kaikki_entries.json)"
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Skip download if data/raw/kaikki_marathi.json already exists"
    )
    args = parser.parse_args()

    output_path = Path(args.output)

    # Step 1: Download
    if args.skip_download and RAW_PATH.exists():
        print(f"Skipping download (--skip-download). Using existing: {RAW_PATH}")
    else:
        download_kaikki(RAW_PATH)

    # Step 2: Parse
    print("\nParsing Kaikki JSON...")
    t0 = time.time()
    entries = parse_kaikki(RAW_PATH)
    elapsed = time.time() - t0
    print(f"Parse took {elapsed:.1f}s")

    # Step 3: Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    missing_meaning = sum(1 for e in entries if not e["meaning2"])
    print(f"\n=== Phase 1 Complete ===")
    print(f"Total entries written : {len(entries)}")
    print(f"Missing meaning2      : {missing_meaning} (will be enriched in Phase 4)")
    print(f"Output file           : {output_path}")
    print(f"\nNext step:")
    print(f"  python scripts/import_dictionary.py --input {output_path}")


if __name__ == "__main__":
    main()
