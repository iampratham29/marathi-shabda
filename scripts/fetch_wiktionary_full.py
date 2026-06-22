"""
fetch_wiktionary_full.py — Phase 3 bulk fetcher
Paginated crawl of the English Wiktionary "Marathi_lemmas" category.
Runs in short, resumable batches to avoid long-running sessions.

Strategy:
  - Phase A: Harvest all Marathi lemma titles via categorymembers API
              (~4,800 titles stored in data/raw/wiktionary_titles.txt)
  - Phase B: Fetch English definitions using the MediaWiki ACTION API
              (query + prop=extracts, 50 titles per request = ~96 calls total)
              Much more efficient than the REST summary API (1 call per word)

Rate limit handling:
  - 429 responses: read Retry-After header and sleep accordingly
  - Default inter-request sleep: 1.0 second between batches of 50

Usage:
    python scripts/fetch_wiktionary_full.py --output data/processed/wiktionary_full_entries.json

Resume:
    python scripts/fetch_wiktionary_full.py --output data/processed/wiktionary_full_entries.json --resume

Control definitions per run (default 1000):
    python scripts/fetch_wiktionary_full.py --output ... --resume --batch-size 500
"""

import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
CATEGORY = "Category:Marathi_lemmas"

TITLES_FILE = Path("data/raw/wiktionary_titles.txt")
PROGRESS_FILE = Path("data/raw/wiktionary_progress.json")

USER_AGENT = "MarathiShabdaPipeline/1.0 (github.com/iampratham29/marathi-shabda)"

# Batch fetch: 50 titles per API call (Wiktionary limit for extracts)
API_BATCH_SIZE = 50
INTER_BATCH_SLEEP = 1.0   # seconds between batch API calls
CHECKPOINT_EVERY = 250    # checkpoint after this many processed words

DEVANAGARI_RANGE = (0x0900, 0x097F)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_devanagari(text: str) -> bool:
    return any(DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1] for c in text)


def api_request(params: dict, retries: int = 3) -> dict:
    """
    Make a GET request to the Wiktionary Action API.
    Handles 429 Retry-After automatically with up to `retries` attempts.
    """
    url = WIKTIONARY_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_exc: Exception = RuntimeError("Unknown error")

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", 10))
                print(f"\n  429 rate limit — sleeping {retry_after}s (attempt {attempt+1}/{retries})")
                time.sleep(retry_after + 1)
                last_exc = e
            else:
                raise
        except Exception as exc:
            last_exc = exc
            time.sleep(2 ** attempt)

    raise last_exc


# ---------------------------------------------------------------------------
# Phase A: Harvest title list
# ---------------------------------------------------------------------------

def fetch_all_titles() -> list[str]:
    """Paginated categorymembers fetch. Returns all Devanagari titles."""
    print("Phase A: Harvesting Marathi lemma titles from en.wiktionary.org ...")
    titles: list[str] = []
    cmcontinue = None
    page = 0

    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": CATEGORY,
            "cmlimit": "500",
            "cmtype": "page",
            "cmnamespace": "0",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        try:
            data = api_request(params)
        except Exception as exc:
            print(f"\nERROR during title harvest (page {page}): {exc}", file=sys.stderr)
            break

        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            t = m.get("title", "").strip()
            if t and is_devanagari(t):
                titles.append(t)
        page += 1

        cont = data.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        print(f"\r  Pages: {page}  |  Devanagari titles: {len(titles)}", end="", flush=True)

        if not cmcontinue:
            break
        time.sleep(0.5)

    print(f"\nPhase A complete: {len(titles)} titles harvested.")
    return titles


def save_titles(titles: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(titles))


def load_titles(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


# ---------------------------------------------------------------------------
# Phase B: Batch definition fetch via Action API
# ---------------------------------------------------------------------------

def load_progress(path: Path) -> dict:
    if not path.exists():
        return {"processed": set(), "entries": []}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {"processed": set(raw.get("processed", [])), "entries": raw.get("entries", [])}


def save_progress(progress: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"processed": sorted(progress["processed"]), "entries": progress["entries"]},
            f, ensure_ascii=False, indent=2,
        )


def parse_gloss_from_wikitext(wikitext: str) -> str:
    """
    Extract the first English gloss from English Wiktionary wikitext for a Marathi word.
    Looks for the ==Marathi== section then the first # gloss line.
    """
    import re
    lines = wikitext.splitlines()
    in_marathi = False
    for line in lines:
        # Detect ==Marathi== section header
        if re.match(r"^==\s*Marathi\s*==$", line.strip()):
            in_marathi = True
            continue
        # Stop at next language section
        if in_marathi and re.match(r"^==\s*\w", line) and not re.match(r"^===", line):
            break
        # First gloss line: starts with # but not #* or #:
        if in_marathi and re.match(r"^#[^*:#]", line):
            # Strip wiki markup: [[...]], {{...}}, ''...''
            gloss = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", line[1:])
            gloss = re.sub(r"\{\{[^}]*\}\}", "", gloss)
            gloss = re.sub(r"'{2,}", "", gloss)
            gloss = gloss.strip().lstrip("#").strip()
            if gloss:
                return gloss[:200]
    return ""


def fetch_extracts_batch(titles: list[str]) -> dict[str, str]:
    """
    Fetch full wikitext for up to 50 titles and parse the first Marathi gloss.
    Returns {title: gloss_string}.
    Note: rvsection is NOT set — we need the full page to find ==Marathi== section.
    """
    params = {
        "action": "query",
        "titles": "|".join(titles),
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
                result[title] = gloss
    except Exception as exc:
        print(f"\n  Warning: batch wikitext fetch failed: {exc}")
    return result




# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Paginated Wiktionary batch crawl for Marathi lemmas."
    )
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint (skip Phase A if titles cached)")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="Max definitions to fetch per run (default: 1000)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- Phase A ----
    if args.resume and TITLES_FILE.exists():
        titles = load_titles(TITLES_FILE)
        print(f"Resumed: {len(titles)} titles from {TITLES_FILE}")
    else:
        titles = fetch_all_titles()
        if not titles:
            print("ERROR: No titles fetched.", file=sys.stderr)
            sys.exit(1)
        save_titles(titles, TITLES_FILE)

    # ---- Phase B ----
    progress = load_progress(PROGRESS_FILE)
    already_done: set[str] = progress["processed"]
    entries: list[dict] = progress["entries"]

    pending = [t for t in titles if t not in already_done]
    run_batch = pending[: args.batch_size]

    print(f"\nPhase B: Fetching definitions (batched, {API_BATCH_SIZE} words/call)")
    print(f"  Total titles    : {len(titles)}")
    print(f"  Already done    : {len(already_done)}")
    print(f"  Pending         : {len(pending)}")
    print(f"  This run target : {len(run_batch)}")
    print(f"  API calls needed: ~{(len(run_batch) + API_BATCH_SIZE - 1) // API_BATCH_SIZE}")

    if not run_batch:
        print("Nothing pending — all titles processed.")
    else:
        fetched = 0
        no_extract = 0
        api_call_num = 0

        # Process in sub-batches of API_BATCH_SIZE
        for start in range(0, len(run_batch), API_BATCH_SIZE):
            sub_batch = run_batch[start : start + API_BATCH_SIZE]
            api_call_num += 1

            extracts = fetch_extracts_batch(sub_batch)

            for title in sub_batch:
                definition = extracts.get(title, "")
                entries.append({
                    "devanagari": title,
                    "key": "",
                    "meaning2": definition,
                    "definition_mr": "",
                    "pos": "unknown",
                    "source": "wiktionary_en_lemmas",
                })
                already_done.add(title)
                if definition:
                    fetched += 1
                else:
                    no_extract += 1

            done_total = len(already_done)
            pct = done_total / len(titles) * 100
            print(f"\r  Call {api_call_num} | words done this run: {start + len(sub_batch)}/{len(run_batch)} "
                  f"| total: {done_total}/{len(titles)} ({pct:.1f}%)", end="", flush=True)

            # Checkpoint
            if api_call_num % (CHECKPOINT_EVERY // API_BATCH_SIZE) == 0:
                progress["processed"] = already_done
                progress["entries"] = entries
                save_progress(progress, PROGRESS_FILE)

            time.sleep(INTER_BATCH_SLEEP)

        # Final checkpoint
        progress["processed"] = already_done
        progress["entries"] = entries
        save_progress(progress, PROGRESS_FILE)

        print(f"\n\n  Got extracts     : {fetched}")
        print(f"  No extract found : {no_extract}")

    # ---- Write output JSON ----
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    remaining = len(titles) - len(already_done)
    missing = sum(1 for e in entries if not e["meaning2"])

    print(f"\n=== Phase 3 Batch Complete ===")
    print(f"Entries in JSON        : {len(entries)}")
    print(f"Missing meaning2       : {missing}")
    print(f"Titles remaining       : {remaining}")
    print(f"Output                 : {output_path}")
    print(f"Checkpoint             : {PROGRESS_FILE}")

    if remaining > 0:
        print(f"\nResume command:")
        print(f"  python scripts/fetch_wiktionary_full.py --output {output_path} --resume --batch-size {args.batch_size}")
    else:
        print(f"\nAll done! Import with:")
        print(f"  python scripts/import_dictionary.py --input {output_path}")


if __name__ == "__main__":
    main()
