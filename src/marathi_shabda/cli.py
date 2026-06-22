"""Command-line interface for marathi-shabda."""

import sys
import argparse
from pathlib import Path

from marathi_shabda import get_lemma, lookup_word, analyze_word, __version__
from marathi_shabda.exceptions import MarathiShabdaError
from marathi_shabda.dictionary import DictionaryAdapter


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Marathi word analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  marathi-pratham lemma पाण्यावर
  marathi-pratham lookup पाणी
  marathi-pratham analyze मुलाने
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"marathi-pratham {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Lemma extraction command
    lemma_parser = subparsers.add_parser("lemma", help="Extract lemma from word")
    lemma_parser.add_argument("word", help="Marathi word")
    
    # Dictionary lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up word in dictionary")
    lookup_parser.add_argument("word", help="Marathi word")
    
    # Morphological analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze word morphology")
    analyze_parser.add_argument("word", help="Marathi word")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "lemma":
            result = get_lemma(args.word)
            print(f"Original: {result.original}")
            print(f"Lemma: {result.lemma}")
            print(f"Confidence: {result.confidence:.2f}")
            if result.detected_vibhakti:
                print(f"Vibhakti: {result.detected_vibhakti.value}")
            if result.ambiguous:
                print(f"Ambiguous: {', '.join(result.candidates)}")
            print(f"Explanation: {result.explanation}")
        
        elif args.command == "lookup":
            result = lookup_word(args.word)
            print(f"Input: {result.input}")
            print(f"Lemma: {result.lemma}")
            print(f"Found: {result.found}")
            if result.found:
                print(f"Meanings: {', '.join(result.english_meanings)}")
        
        elif args.command == "analyze":
            result = analyze_word(args.word)
            print(f"Input: {result.input}")
            print(f"Lemma: {result.lemma}")
            print(f"POS: {result.pos.value}")
            if result.vibhakti:
                print(f"Vibhakti: {result.vibhakti.value}")
            if result.kaal:
                print(f"Kāl: {result.kaal.value}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Explanation: {result.explanation}")
        
        return 0
    
    except MarathiShabdaError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def dict_cli() -> int:
    """CLI for dictionary database operations."""
    parser = argparse.ArgumentParser(
        description="Marathi dictionary database management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up a word in the dictionary")
    lookup_parser.add_argument("word", help="Word to look up (Roman or Devanagari)")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import words from a fetched JSON file")
    import_parser.add_argument("input_path", help="Path to input JSON file")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export entire database as a portable .sql dump")
    export_parser.add_argument("output_path", help="Path to output SQL file")
    
    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    try:
        adapter = DictionaryAdapter()
        
        if args.command == "lookup":
            from marathi_shabda.normalization import detect_script
            from marathi_shabda.models import ScriptType
            
            word = args.word
            script = detect_script(word)
            
            if script == ScriptType.ROMAN:
                entry = adapter.lookup_by_roman(word)
                entries = [entry] if entry else []
            else:
                entries = adapter.lookup_by_devanagari(word)
                
            if not entries:
                print(f"Word '{word}' not found in dictionary.")
                return 1
                
            for entry in entries:
                meanings = ", ".join(entry.english_meanings)
                pos_str = entry.pos.value if entry.pos else "unknown"
                source_str = entry.source if entry.source else "unknown"
                print(f"{entry.devanagari.strip()} → {meanings} ({entry.roman_key}) [{pos_str}] [source: {source_str}]")
                
        elif args.command == "import":
            import subprocess
            script_path = Path(__file__).parent.parent.parent / "scripts" / "import_dictionary.py"
            cmd = [sys.executable, str(script_path), "--input", args.input_path]
            result = subprocess.run(cmd)
            return result.returncode
            
        elif args.command == "export":
            adapter.export_sql(args.output_path)
            print(f"Database exported successfully to {args.output_path}")
            
        elif args.command == "stats":
            with adapter._get_connection() as conn:
                # Total words
                cursor = conn.execute("SELECT COUNT(*) FROM MarathiEnglish;")
                total_words = cursor.fetchone()[0]
                
                # With Roman (Key is not null/empty)
                cursor = conn.execute("SELECT COUNT(*) FROM MarathiEnglish WHERE Key IS NOT NULL AND Key != '';")
                with_roman = cursor.fetchone()[0]
                
                # With English (Meaning2 is not null/empty)
                cursor = conn.execute("SELECT COUNT(*) FROM MarathiEnglish WHERE Meaning2 IS NOT NULL AND Meaning2 != '';")
                with_english = cursor.fetchone()[0]
                
                # With Marathi def
                cursor = conn.execute("PRAGMA table_info(MarathiEnglish);")
                cols = [c[1] for c in cursor.fetchall()]
                
                with_marathi_def = 0
                if "definition_mr" in cols:
                    cursor = conn.execute("SELECT COUNT(*) FROM MarathiEnglish WHERE definition_mr IS NOT NULL AND definition_mr != '';")
                    with_marathi_def = cursor.fetchone()[0]
                    
                print(f"Total words     : {total_words}")
                print(f"With Roman      : {with_roman}")
                print(f"With English    : {with_english}")
                print(f"With Marathi def: {with_marathi_def}")
                
        return 0
        
    except MarathiShabdaError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
