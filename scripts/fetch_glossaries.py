"""
fetch_glossaries.py — Phase 2 bulk fetcher
Harvests Marathi word entries from two complementary Wiktionary sources:

  Source A: mr.wiktionary.org  — allpages API (full Marathi Wiktionary title list)
            ~5,000–10,000 Devanagari page titles
  Source B: en.wiktionary.org  — categorymembers for POS-specific categories
            (Marathi_nouns, Marathi_verbs, etc.) for better POS tagging

Both sources produce word *titles* with no English meanings.
Meanings are added by Phase 3 (wiktionary full crawl) or Phase 4 (enrich_meaning.py).

Usage:
    python scripts/fetch_glossaries.py --output data/processed/glossary_entries.json
"""

import argparse
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

USER_AGENT = "MarathiShabdaPipeline/1.0 (github.com/iampratham29/marathi-shabda)"
DEVANAGARI_RANGE = (0x0900, 0x097F)

MR_WIKI_API = "https://mr.wiktionary.org/w/api.php"
EN_WIKI_API = "https://en.wiktionary.org/w/api.php"

# POS-tagged categories on en.wiktionary.org
EN_POS_CATEGORIES = {
    "Category:Marathi_nouns":         "noun",
    "Category:Marathi_verbs":         "verb",
    "Category:Marathi_adjectives":    "adjective",
    "Category:Marathi_adverbs":       "adverb",
    "Category:Marathi_pronouns":      "pronoun",
    "Category:Marathi_conjunctions":  "conjunction",
    "Category:Marathi_interjections": "interjection",
    "Category:Marathi_postpositions": "postposition",
    "Category:Marathi_numerals":      "numeral",
    "Category:Marathi_particles":     "particle",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_devanagari(text: str) -> bool:
    return any(DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1] for c in text)


def api_get(base_url: str, params: dict) -> dict:
    """Make a GET request to a MediaWiki API, return parsed JSON."""
    url = base_url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Source A: mr.wiktionary.org — allpages
# ---------------------------------------------------------------------------

def fetch_mr_wiktionary_allpages() -> list[dict]:
    """
    Fetch ALL page titles in the main namespace of Marathi Wiktionary.
    Uses allpages API with pagination. Returns normalized entries (no meaning).
    """
    print("Source A: mr.wiktionary.org allpages ...")
    seen: set[str] = set()
    entries: list[dict] = []
    apcontinue = None
    page = 0

    while True:
        params: dict = {
            "action": "query",
            "list": "allpages",
            "apnamespace": "0",
            "aplimit": "500",
            "apfilterredir": "nonredirects",
            "format": "json",
        }
        if apcontinue:
            params["apcontinue"] = apcontinue

        try:
            data = api_get(MR_WIKI_API, params)
        except Exception as exc:
            print(f"\n  Warning: allpages API error (page {page}): {exc}")
            break

        pages = data.get("query", {}).get("allpages", [])
        for p in pages:
            title = p.get("title", "").strip()
            if title and title not in seen and is_devanagari(title):
                seen.add(title)
                entries.append({
                    "devanagari": title,
                    "key": "",
                    "meaning2": "",
                    "definition_mr": "",
                    "pos": "unknown",
                    "source": "mr_wiktionary_allpages",
                })
        page += 1

        cont = data.get("continue", {})
        apcontinue = cont.get("apcontinue")
        print(f"\r  Pages: {page}  |  Devanagari titles: {len(entries)}", end="", flush=True)

        if not apcontinue:
            break
        time.sleep(0.2)

    print(f"\nSource A done: {len(entries)} Devanagari titles")
    return entries


# ---------------------------------------------------------------------------
# Source B: en.wiktionary.org — POS-tagged categories
# ---------------------------------------------------------------------------

def fetch_en_wiktionary_pos_categories() -> list[dict]:
    """
    Fetch Marathi word titles from English Wiktionary POS categories.
    Returns entries with proper POS tags (noun/verb/adjective/etc.)
    and no meaning (to be enriched later).
    """
    print("\nSource B: en.wiktionary.org POS categories ...")
    seen: set[str] = set()
    entries: list[dict] = []

    for cat, pos in EN_POS_CATEGORIES.items():
        cmcontinue = None
        cat_count = 0

        while True:
            params: dict = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": cat,
                "cmlimit": "500",
                "cmtype": "page",
                "cmnamespace": "0",
                "format": "json",
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            try:
                data = api_get(EN_WIKI_API, params)
            except Exception as exc:
                print(f"  Warning: category fetch failed for {cat}: {exc}")
                break

            members = data.get("query", {}).get("categorymembers", [])
            for m in members:
                title = m.get("title", "").strip()
                if title and title not in seen and is_devanagari(title):
                    seen.add(title)
                    entries.append({
                        "devanagari": title,
                        "key": "",
                        "meaning2": "",
                        "definition_mr": "",
                        "pos": pos,
                        "source": f"en_wiktionary_{pos}",
                    })
                    cat_count += 1

            cont = data.get("continue", {})
            cmcontinue = cont.get("cmcontinue")
            if not cmcontinue:
                break
            time.sleep(0.2)

        # ASCII-safe print for Windows
        short_cat = cat.split(":")[-1]
        print(f"  {short_cat}: {cat_count} entries (pos={pos})")

    print(f"Source B done: {len(entries)} POS-tagged entries")
    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 2: Harvest Marathi word titles from Wiktionary (mr + en)."
    )
    parser.add_argument("--output", required=True,
                        help="Path to write normalized JSON output")
    parser.add_argument("--source-a-only", action="store_true",
                        help="Only run Source A (mr.wiktionary allpages)")
    parser.add_argument("--source-b-only", action="store_true",
                        help="Only run Source B (en.wiktionary POS categories)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_entries: list[dict] = []
    seen_global: set[str] = set()

    # Source A
    if not args.source_b_only:
        a_entries = fetch_mr_wiktionary_allpages()
        for e in a_entries:
            if e["devanagari"] not in seen_global:
                seen_global.add(e["devanagari"])
                all_entries.append(e)

    # Source B — adds POS tags to words already in A or fills in new ones
    if not args.source_a_only:
        b_entries = fetch_en_wiktionary_pos_categories()
        for e in b_entries:
            dv = e["devanagari"]
            if dv not in seen_global:
                seen_global.add(dv)
                all_entries.append(e)
            else:
                # Upgrade existing entry with POS if it was unknown
                for existing in all_entries:
                    if existing["devanagari"] == dv and existing["pos"] == "unknown":
                        existing["pos"] = e["pos"]
                        break

    if not all_entries:
        print("ERROR: No entries extracted.", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    by_source: dict[str, int] = {}
    for e in all_entries:
        by_source[e["source"]] = by_source.get(e["source"], 0) + 1

    print(f"\n=== Phase 2 Complete ===")
    print(f"Total entries written : {len(all_entries)}")
    print(f"Breakdown by source:")
    for src, cnt in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {src:<35} {cnt:>6,}")
    print(f"Output file          : {output_path}")
    print(f"\nNext step:")
    print(f"  python scripts/import_dictionary.py --input {output_path}")


if __name__ == "__main__":
    main()
