import argparse
import json
import os
import urllib.request
import urllib.parse
import re
import sys
from pathlib import Path

# Static mock data for fallback/offline testing
MOCK_ENTRIES = [
    {"devanagari": "पाणी", "key": "pani", "meaning2": "water", "definition_mr": "जीवन", "pos": "noun", "source": "mock"},
    {"devanagari": "मुलगा", "key": "mulga", "meaning2": "boy", "definition_mr": "पुत्र", "pos": "noun", "source": "mock"},
    {"devanagari": "मुलगी", "key": "mulgi", "meaning2": "girl", "definition_mr": "कन्या", "pos": "noun", "source": "mock"},
    {"devanagari": "घर", "key": "ghar", "meaning2": "house", "definition_mr": "गृह", "pos": "noun", "source": "mock"},
    {"devanagari": "झाड", "key": "zhad", "meaning2": "tree", "definition_mr": "वृक्ष", "pos": "noun", "source": "mock"},
    {"devanagari": "फूल", "key": "phool", "meaning2": "flower", "definition_mr": "पुष्प", "pos": "noun", "source": "mock"},
    {"devanagari": "पुस्तक", "key": "pustak", "meaning2": "book", "definition_mr": "ग्रंथ", "pos": "noun", "source": "mock"},
    {"devanagari": "हात", "key": "haat", "meaning2": "hand", "definition_mr": "कर", "pos": "noun", "source": "mock"},
    {"devanagari": "पाय", "key": "paay", "meaning2": "leg", "definition_mr": "पाद", "pos": "noun", "source": "mock"},
    {"devanagari": "माणूस", "key": "manoos", "meaning2": "man", "definition_mr": "मानव", "pos": "noun", "source": "mock"},
]

def fetch_wiktionary_lemmas(limit=50):
    """Fetch Marathi lemmas from Wiktionary API."""
    url = "https://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Marathi_lemmas&cmlimit=100&format=json"
    headers = {"User-Agent": "MarathiShabdaPipeline/0.1 (http://github.com/iampratham29/marathi-shabda)"}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            members = data.get("query", {}).get("categorymembers", [])
            return [m["title"] for m in members if m["ns"] == 0][:limit]
    except Exception as e:
        print(f"Warning: Wiktionary API fetch failed ({e}). Using mock/fallback data.", file=sys.stderr)
        return None

def fetch_wiktionary_definition(title):
    """Fetch summary/definition for a specific Wiktionary title."""
    encoded_title = urllib.parse.quote(title)
    url = f"https://en.wiktionary.org/api/rest_v1/page/summary/{encoded_title}"
    headers = {"User-Agent": "MarathiShabdaPipeline/0.1"}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            extract = data.get("extract", "")
            return extract
    except Exception:
        return ""

def fetch_apertium_dix():
    """Fetch Apertium bilingual dictionary DIX file."""
    # Attempt master first, then main branch
    urls = [
        "https://raw.githubusercontent.com/apertium/apertium-mar-eng/master/apertium-mar-eng.mar-eng.dix",
        "https://raw.githubusercontent.com/apertium/apertium-mar-eng/main/apertium-mar-eng.mar-eng.dix"
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")
        except Exception:
            continue
    print("Warning: Apertium DIX fetch failed. Using mock/fallback data.", file=sys.stderr)
    return None

def parse_apertium_dix(dix_xml):
    """Parse XML to extract Devanagari, POS, and English meanings."""
    # Basic regex parsing of XML entries like:
    # <e><p><l>पाणी<s n="n"/></l><r>water<s n="n"/></r></p></e>
    pattern = r'<e[^>]*>\s*<p>\s*<l>([^<]+)<s\s+n="([^"]+)"/></l>\s*<r>([^<]+)<s\s+n="([^"]+)"/></r>\s*</p>\s*</e>'
    matches = re.findall(pattern, dix_xml)
    
    entries = []
    for match in matches:
        marathi, mar_pos, english, eng_pos = match
        # Clean up tags/pos
        pos_map = {
            "n": "noun",
            "vblex": "verb",
            "adj": "adjective",
            "adv": "adverb",
            "prn": "pronoun",
            "pr": "postposition",
            "cnjcoo": "conjunction",
            "cnjsub": "conjunction",
            "ij": "interjection",
        }
        pos = pos_map.get(mar_pos, "unknown")
        
        # Ensure only Devanagari word
        # (Exclude transliterated forms if they happen to be in the left side, though usually it's Devanagari)
        # Verify it has Devanagari characters
        is_dev = any(0x0900 <= ord(c) <= 0x097F for c in marathi)
        if not is_dev:
            continue
            
        entries.append({
            "devanagari": marathi.strip(),
            "key": "", # No transliteration from XML
            "meaning2": english.strip(),
            "definition_mr": "",
            "pos": pos,
            "source": "apertium_mr"
        })
    return entries

def main():
    parser = argparse.ArgumentParser(description="Fetch Marathi dictionary data from external sources")
    parser.add_argument("--source", required=True, choices=["wiktionary", "apertium", "mock"], help="Data source")
    parser.add_argument("--output", required=True, help="Path to save output JSON file")
    parser.add_argument("--resume", action="store_true", help="Resume from existing output file")
    args = parser.parse_args()
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    existing_entries = []
    fetched_words = set()
    
    if args.resume and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_entries = json.load(f)
                fetched_words = {e["devanagari"] for e in existing_entries if "devanagari" in e}
            print(f"Resuming fetch. Loaded {len(existing_entries)} existing entries.")
        except Exception as e:
            print(f"Warning: Could not load existing output for resume: {e}", file=sys.stderr)
            
    normalized_entries = list(existing_entries)
    
    if args.source == "mock":
        # Use mock entries
        for entry in MOCK_ENTRIES:
            if entry["devanagari"] not in fetched_words:
                normalized_entries.append(entry)
                
    elif args.source == "wiktionary":
        titles = fetch_wiktionary_lemmas()
        if titles is None:
            # Fallback to mock
            print("Using mock data as fallback for wiktionary.")
            for entry in MOCK_ENTRIES:
                if entry["devanagari"] not in fetched_words:
                    normalized_entries.append(entry)
        else:
            for idx, title in enumerate(titles):
                if title in fetched_words:
                    continue
                # Clean/validate title is Devanagari
                is_dev = any(0x0900 <= ord(c) <= 0x097F for c in title)
                if not is_dev:
                    continue
                    
                # Fetch definition (optional, rate limited, so we do it nicely)
                definition = fetch_wiktionary_definition(title)
                
                # Guess POS from definition/title or leave empty
                pos = "noun" # Default
                
                entry = {
                    "devanagari": title,
                    "key": "", # No transliteration yet
                    "meaning2": definition[:100] if definition else "Wiktionary entry",
                    "definition_mr": "",
                    "pos": pos,
                    "source": "wiktionary_mr"
                }
                normalized_entries.append(entry)
                
                if (idx + 1) % 10 == 0 or idx == len(titles) - 1:
                    print(f"[{idx + 1}/{len(titles)}] Fetched: {title} → {entry['meaning2']}")
                    
    elif args.source == "apertium":
        xml_data = fetch_apertium_dix()
        if xml_data is None:
            # Fallback to mock
            print("Using mock data as fallback for apertium.")
            for entry in MOCK_ENTRIES:
                if entry["devanagari"] not in fetched_words:
                    normalized_entries.append(entry)
        else:
            entries = parse_apertium_dix(xml_data)
            for entry in entries:
                if entry["devanagari"] not in fetched_words:
                    normalized_entries.append(entry)
                    
    # Deduplicate and save
    final_entries = []
    seen = set()
    for e in normalized_entries:
        if e["devanagari"] not in seen:
            seen.add(e["devanagari"])
            final_entries.append(e)
            
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_entries, f, ensure_ascii=False, indent=2)
        
    total_fetched = len(final_entries)
    missing_roman = sum(1 for e in final_entries if not e.get("key"))
    missing_english = sum(1 for e in final_entries if not e.get("meaning2"))
    
    print("\n=== Fetch Complete ===")
    print(f"Total fetched  : {total_fetched}")
    print(f"Missing roman  : {missing_roman}")
    print(f"Missing english: {missing_english}")
    print(f"Saved to       : {output_path}")

if __name__ == "__main__":
    main()
