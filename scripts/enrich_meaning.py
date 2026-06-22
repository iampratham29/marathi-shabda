"""
enrich_meaning.py — Phase 4: Backfill English meanings for DB entries that have none.
Queries the DB for rows with empty Meaning2, then fetches definitions using the
MediaWiki Action API (batch of 50 words per call) — much more efficient and
resilient than the per-word REST summary API.

Usage:
    python scripts/enrich_meaning.py
    python scripts/enrich_meaning.py --limit 500
    python scripts/enrich_meaning.py --limit 500 --resume
"""

import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import argparse
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add src/ to python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from marathi_shabda.dictionary import DictionaryAdapter

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
USER_AGENT = "MarathiShabdaPipeline/1.0 (github.com/iampratham29/marathi-shabda)"
CHECKPOINT_FILE = Path("data/raw/enrich_meaning_progress.json")
API_BATCH_SIZE = 50      # words per API call
INTER_BATCH_SLEEP = 1.5  # seconds between calls
CHECKPOINT_EVERY = 200   # checkpoint after this many words


def load_checkpoint() -> set:
    if not CHECKPOINT_FILE.exists():
        return set()
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f).get("done", []))


def save_checkpoint(done: set) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"done": sorted(done)}, f, ensure_ascii=False)


def parse_gloss_from_wikitext(wikitext: str) -> str:
    """Extract the first English gloss from the ==Marathi== section."""
    lines = wikitext.splitlines()
    in_marathi = False
    for line in lines:
        if re.match(r"^==\s*Marathi\s*==$", line.strip()):
            in_marathi = True
            continue
        if in_marathi and re.match(r"^==\s*\w", line) and not re.match(r"^===", line):
            break
        if in_marathi and re.match(r"^#[^*:#]", line):
            gloss = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", line[1:])
            gloss = re.sub(r"\{\{[^}]*\}\}", "", gloss)
            gloss = re.sub(r"'{2,}", "", gloss)
            return gloss.strip().lstrip("#").strip()[:200]
    return ""


def api_request(params: dict, retries: int = 3) -> dict:
    """MediaWiki API GET with 429 Retry-After handling."""
    url = WIKTIONARY_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_exc: Exception = RuntimeError("Unknown error")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", 15))
                print(f"\n  429 — sleeping {wait}s (attempt {attempt+1}/{retries})")
                time.sleep(wait + 1)
                last_exc = e
            else:
                raise
        except Exception as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise last_exc


def fetch_glosses_batch(devanagari_words: list[str]) -> dict[str, str]:
    """
    Fetch wikitext for a batch of Devanagari words and extract Marathi glosses.
    Returns {devanagari_word: gloss}.
    """
    params = {
        "action": "query",
        "titles": "|".join(devanagari_words),
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "formatversion": "2",
    }
    result: dict[str, str] = {}
    try:
        data = api_request(params)
        pages = data.get("query", {}).get("pages", [])
        for page in pages:
            title = page.get("title", "").strip()
            revisions = page.get("revisions", [])
            if revisions:
                content = revisions[0].get("slots", {}).get("main", {}).get("content", "")
                gloss = parse_gloss_from_wikitext(content)
                if gloss:
                    result[title] = gloss
    except Exception as exc:
        print(f"\n  Warning: batch fetch failed: {exc}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4: Backfill English meanings for DB entries missing Meaning2."
    )
    parser.add_argument("--limit", type=int, default=500,
                        help="Max words to enrich per run (default: 500)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip words already attempted in a previous run")
    args = parser.parse_args()

    adapter = DictionaryAdapter()
    done = load_checkpoint() if args.resume else set()

    # Get all words with empty English meaning
    missing = adapter.get_words_missing_english()
    pending = [dv for dv in missing if dv not in done]
    batch = pending[: args.limit]

    print(f"Words missing meaning in DB     : {len(missing)}")
    print(f"Already attempted (checkpoint)  : {len(done)}")
    print(f"This run                        : {len(batch)}")
    api_calls = (len(batch) + API_BATCH_SIZE - 1) // API_BATCH_SIZE
    print(f"API calls needed (~{API_BATCH_SIZE}/call)      : {api_calls}")

    if not batch:
        print("Nothing to enrich.")
        return

    enriched = 0
    not_found = 0

    for start in range(0, len(batch), API_BATCH_SIZE):
        sub = batch[start: start + API_BATCH_SIZE]
        devanagari_list = sub

        glosses = fetch_glosses_batch(devanagari_list)

        with adapter._get_connection() as conn:
            for dv in sub:
                gloss = glosses.get(dv, "")
                done.add(dv)

                if gloss:
                    try:
                        conn.execute(
                            "UPDATE MarathiEnglish SET Meaning2 = ? WHERE devanagari = ? OR Meaning1 = ?",
                            (gloss, dv, dv),
                        )
                        enriched += 1
                    except Exception as exc:
                        print(f"\n  DB error for '{dv}': {exc}")
                else:
                    not_found += 1
            conn.commit()
        done_count = start + len(sub)
        pct = done_count / len(batch) * 100
        print(f"\r  [{done_count}/{len(batch)} ({pct:.0f}%)] enriched: {enriched} | not found: {not_found}",
              end="", flush=True)

        if done_count % CHECKPOINT_EVERY < API_BATCH_SIZE:
            save_checkpoint(done)

        time.sleep(INTER_BATCH_SLEEP)

    save_checkpoint(done)

    still_missing = len(adapter.get_words_missing_english())
    print(f"\n\n=== Phase 4 Enrichment Complete ===")
    print(f"Enriched this run   : {enriched}")
    print(f"No gloss found      : {not_found}")
    print(f"Still missing in DB : {still_missing}")

    if still_missing > 0:
        print(f"\nResume command:")
        print(f"  python scripts/enrich_meaning.py --limit {args.limit} --resume")


if __name__ == "__main__":
    main()
