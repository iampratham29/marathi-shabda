import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Add src/ to python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from marathi_shabda.dictionary import DictionaryAdapter

def call_sarvam_api(word, api_key):
    """Call Sarvam AI transliteration API for a single word."""
    url = "https://api.sarvam.ai/transliterate"
    payload = {
        "input": word,
        "source_language_code": "mr-IN",
        "target_language_code": "mr-IN",  # Devanagari to Roman as specified in prompt
        "spoken_form": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": api_key  # Standard header key for Sarvam AI
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            # Standard Sarvam AI response schema contains transliterated_text
            return res_data.get("transliterated_text", "")
    except urllib.error.HTTPError as e:
        print(f"API HTTP Error for '{word}': {e.code} - {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"API Error for '{word}': {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Enrich missing Roman transliterations in dictionary using Sarvam AI")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of words to process")
    parser.add_argument("--dry-run", action="store_true", help="Print operations without calling API or DB")
    args = parser.parse_args()
    
    checkpoint_path = Path("data/enrich_checkpoint.json")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: SARVAM_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)
        
    adapter = DictionaryAdapter()
    missing_words = adapter.get_words_missing_roman()
    
    print(f"Total words missing Roman in DB: {len(missing_words)}")
    
    # Load checkpoint
    checkpoint = {}
    if checkpoint_path.exists():
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            print(f"Loaded checkpoint with {len(checkpoint)} entries.")
        except Exception as e:
            print(f"Warning: Could not load checkpoint file: {e}", file=sys.stderr)
            
    # Filter words to process
    words_to_process = [w for w in missing_words if w not in checkpoint][:args.batch_size]
    print(f"Processing batch of {len(words_to_process)} words.")
    
    if not words_to_process:
        print("No new words to process in this batch.")
        return
        
    processed_count = 0
    success_count = 0
    error_count = 0
    total_chars = 0
    
    # Dry run
    if args.dry_run:
        print("\n--- Running in DRY-RUN Mode (no API calls or DB writes) ---")
        for word in words_to_process:
            total_chars += len(word)
            # Dummy transliteration: lowercase and keep alphanumeric
            dummy_roman = "".join(c for c in word if c.isalnum()).lower() or "translit"
            print(f"[Dry-run] Transliterate '{word}' -> '{dummy_roman}'")
            success_count += 1
            processed_count += 1
            
        print("\n=== Enrichment Complete (Dry-Run) ===")
        print(f"Words processed : {processed_count}")
        print(f"Successfully enriched: {success_count}")
        print(f"API errors      : {error_count}")
        print(f"Estimated tokens: ~{total_chars} chars")
        return
        
    # Regular run
    with adapter._get_connection() as conn:
        for word in words_to_process:
            total_chars += len(word)
            roman_result = call_sarvam_api(word, api_key)
            processed_count += 1
            
            if roman_result:
                # Update DB
                conn.execute(
                    "UPDATE MarathiEnglish SET Key = ? WHERE Meaning1 = ? OR devanagari = ?",
                    (roman_result, word, word)
                )
                conn.commit()
                
                # Update checkpoint
                checkpoint[word] = roman_result
                try:
                    with open(checkpoint_path, "w", encoding="utf-8") as f:
                        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Warning: Failed to save checkpoint: {e}", file=sys.stderr)
                    
                success_count += 1
                print(f"Enriched: {word} → {roman_result}")
            else:
                error_count += 1
                
    print("\n=== Enrichment Complete ===")
    print(f"Words processed : {processed_count}")
    print(f"Successfully enriched: {success_count}")
    print(f"API errors      : {error_count}")
    print(f"Estimated tokens: ~{total_chars} chars")

if __name__ == "__main__":
    main()
