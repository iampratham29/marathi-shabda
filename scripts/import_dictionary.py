import argparse
import json
import os
import sys
from pathlib import Path

# Add src/ to python path so we can import marathi_shabda
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from marathi_shabda.dictionary import DictionaryAdapter
from marathi_shabda import get_lemma

def main():
    parser = argparse.ArgumentParser(description="Import Marathi words from JSON into the dictionary database")
    parser.add_argument("--input", required=True, help="Path to fetched JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Print operations without updating the database")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist at {input_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except Exception as e:
        print(f"Error: Failed to read input JSON file: {e}", file=sys.stderr)
        sys.exit(1)
        
    adapter = DictionaryAdapter()
    print(f"Loaded {len(entries)} entries from {input_path}")
    print(f"Database path: {adapter.db_path}")
    
    if args.dry_run:
        print("\n--- Running in DRY-RUN Mode (no database writes) ---")
        inserted = 0
        skipped = 0
        errors = 0
        
        for entry in entries:
            try:
                devanagari = entry.get("devanagari")
                if not devanagari:
                    errors += 1
                    continue
                    
                lemma_res = get_lemma(devanagari)
                lemma = lemma_res.lemma
                
                # Check duplication by lemma
                if adapter.exists(lemma):
                    skipped += 1
                else:
                    if lemma != devanagari:
                        print(f"[Dry-run] Would convert inflected '{devanagari}' to lemma '{lemma}' and insert.")
                    else:
                        print(f"[Dry-run] Would insert: {devanagari} ({entry.get('meaning2')})")
                    inserted += 1
            except Exception as e:
                print(f"[Dry-run] Error processing {entry}: {e}")
                errors += 1
                
        print("\n=== Import Complete (Dry-Run) ===")
        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}  (already exists or inflected form)")
        print(f"Errors   : {errors}")
        print(f"DB path  : {adapter.db_path}")
        
    else:
        # Run bulk insert in batches of 100
        stats = {"inserted": 0, "skipped": 0, "errors": 0}
        batch_size = 100
        
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            batch_stats = adapter.bulk_insert(batch)
            stats["inserted"] += batch_stats["inserted"]
            stats["skipped"] += batch_stats["skipped"]
            stats["errors"] += batch_stats["errors"]
            
        print("\n=== Import Complete ===")
        print(f"Inserted : {stats['inserted']}")
        print(f"Skipped  : {stats['skipped']}  (already exists or inflected form)")
        print(f"Errors   : {stats['errors']}")
        print(f"DB path  : {adapter.db_path}")
        
        # Export a fresh .sql dump after import
        sql_dump_path = Path("data/marathi_dictionary.sql")
        sql_dump_path.parent.mkdir(parents=True, exist_ok=True)
        adapter.export_sql(str(sql_dump_path))
        print(f"Exported fresh SQL dump to: {sql_dump_path}")

if __name__ == "__main__":
    main()
