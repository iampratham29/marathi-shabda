"""Command-line interface for marathi-shabda."""

import sys
import argparse
from pathlib import Path

from marathi_shabda import get_lemma, lookup_word, analyze_word, __version__
from marathi_shabda.exceptions import MarathiPrathamError


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


if __name__ == "__main__":
    sys.exit(main())
