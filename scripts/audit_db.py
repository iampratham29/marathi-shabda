"""
audit_db.py — Phase 5: Deduplication & quality audit of dictionary.db.

Checks:
  1. Duplicate Roman keys (Key column) — keeps row with more filled fields
  2. Source breakdown — count rows by source column
  3. Entries with missing Meaning2 (English)
  4. Entries with missing devanagari column
  5. is_stem = 0 entries (should not exist if lemma-gate worked)
  6. Exports final SQL dump to data/marathi_dictionary.sql

Usage:
    python scripts/audit_db.py
    python scripts/audit_db.py --fix-duplicates
    python scripts/audit_db.py --export-sql data/marathi_dictionary.sql
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from marathi_shabda.dictionary import DictionaryAdapter


def audit(adapter: DictionaryAdapter, fix_duplicates: bool = False) -> dict:
    """Run all quality checks. Returns a summary dict."""
    with adapter._get_connection() as conn:
        # ------------------------------------------------------------------ #
        # 1. Total row count
        # ------------------------------------------------------------------ #
        total = conn.execute("SELECT COUNT(*) FROM MarathiEnglish").fetchone()[0]

        # ------------------------------------------------------------------ #
        # 2. Source breakdown
        # ------------------------------------------------------------------ #
        source_rows = conn.execute(
            "SELECT source, COUNT(*) as cnt FROM MarathiEnglish GROUP BY source ORDER BY cnt DESC"
        ).fetchall()
        source_counts = {row[0] or "NULL": row[1] for row in source_rows}

        # ------------------------------------------------------------------ #
        # 3. Missing Meaning2
        # ------------------------------------------------------------------ #
        missing_meaning = conn.execute(
            "SELECT COUNT(*) FROM MarathiEnglish WHERE Meaning2 IS NULL OR Meaning2 = ''"
        ).fetchone()[0]

        # ------------------------------------------------------------------ #
        # 4. Missing devanagari
        # ------------------------------------------------------------------ #
        missing_dev = conn.execute(
            "SELECT COUNT(*) FROM MarathiEnglish WHERE devanagari IS NULL OR devanagari = ''"
        ).fetchone()[0]

        # ------------------------------------------------------------------ #
        # 5. Non-stem entries (is_stem = 0)
        # ------------------------------------------------------------------ #
        non_stem = conn.execute(
            "SELECT COUNT(*) FROM MarathiEnglish WHERE is_stem = 0"
        ).fetchone()[0]

        # ------------------------------------------------------------------ #
        # 6. Duplicate Roman keys
        # ------------------------------------------------------------------ #
        dup_rows = conn.execute(
            """
            SELECT Key, COUNT(*) as cnt
            FROM MarathiEnglish
            WHERE Key IS NOT NULL AND Key != ''
            GROUP BY Key
            HAVING cnt > 1
            ORDER BY cnt DESC
            """
        ).fetchall()
        dup_keys = {row[0]: row[1] for row in dup_rows}

        # ------------------------------------------------------------------ #
        # 7. Optionally fix duplicates
        # ------------------------------------------------------------------ #
        fixed_duplicates = 0
        if fix_duplicates and dup_keys:
            print(f"\nFixing {len(dup_keys)} duplicate Roman keys ...")
            for key, count in dup_keys.items():
                # Fetch all rows with this key
                rows = conn.execute(
                    "SELECT rowid, Key, Meaning1, Meaning2, devanagari, pos, definition_mr, source FROM MarathiEnglish WHERE Key = ?",
                    (key,)
                ).fetchall()

                # Score each row: +1 for each non-null/non-empty field
                def score(row):
                    return sum(1 for v in row[2:] if v)  # skip rowid and Key

                scored = sorted(rows, key=score, reverse=True)
                # Keep the best, delete the rest
                keep_rowid = scored[0][0]
                delete_rowids = [r[0] for r in scored[1:]]
                for rid in delete_rowids:
                    conn.execute("DELETE FROM MarathiEnglish WHERE rowid = ?", (rid,))
                fixed_duplicates += len(delete_rowids)

            conn.commit()
            print(f"  Removed {fixed_duplicates} duplicate rows.")

        return {
            "total": total,
            "source_counts": source_counts,
            "missing_meaning": missing_meaning,
            "missing_devanagari": missing_dev,
            "non_stem": non_stem,
            "duplicate_keys": len(dup_keys),
            "fixed_duplicates": fixed_duplicates,
        }


def print_report(summary: dict, export_sql: str | None) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sep = "=" * 50

    print(f"\n{sep}")
    print(f" Dictionary Audit Report — {now}")
    print(sep)
    print(f"  Total rows          : {summary['total']:,}")
    print(f"  Duplicate Keys found: {summary['duplicate_keys']}")
    print(f"  Fixed (deleted)     : {summary['fixed_duplicates']}")
    print(f"  Missing Meaning2    : {summary['missing_meaning']:,}")
    print(f"  Missing Devanagari  : {summary['missing_devanagari']}")
    print(f"  Non-stem entries    : {summary['non_stem']}")

    print(f"\n  Rows by source:")
    for src, cnt in sorted(summary["source_counts"].items(), key=lambda x: -x[1]):
        print(f"    {src:<30} {cnt:>6,}")

    quality_pct = 0
    if summary["total"] > 0:
        quality_pct = (1 - summary["missing_meaning"] / summary["total"]) * 100
    print(f"\n  Meaning coverage    : {quality_pct:.1f}%")

    if export_sql:
        print(f"\n  SQL dump written to : {export_sql}")

    print(sep)

    # Recommendations
    if summary["missing_meaning"] > 0:
        print(f"\n  RECOMMENDATION: Run enrich_meaning.py to fill {summary['missing_meaning']:,} missing meanings.")
    if summary["non_stem"] > 0:
        print(f"  WARNING: {summary['non_stem']} non-stem entries detected. The lemma-gate may have been bypassed.")
    if summary["duplicate_keys"] > 0 and summary["fixed_duplicates"] == 0:
        print(f"  TIP: Re-run with --fix-duplicates to remove {summary['duplicate_keys']} duplicate Roman keys.")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5: Deduplication and quality audit of dictionary.db."
    )
    parser.add_argument("--fix-duplicates", action="store_true",
                        help="Automatically remove duplicate Roman key rows (keeps most-complete row)")
    parser.add_argument("--export-sql", default="data/marathi_dictionary.sql",
                        help="Path to export final SQL dump (default: data/marathi_dictionary.sql)")
    args = parser.parse_args()

    adapter = DictionaryAdapter()
    print(f"Database: {adapter.db_path}")

    summary = audit(adapter, fix_duplicates=args.fix_duplicates)

    # Export SQL dump
    sql_path = Path(args.export_sql)
    sql_path.parent.mkdir(parents=True, exist_ok=True)
    adapter.export_sql(str(sql_path))
    summary["export_sql"] = str(sql_path)

    print_report(summary, str(sql_path))

    print(f"\n=== Phase 5 Complete ===")
    print(f"Audit finished. Total words in DB: {summary['total']:,}")


if __name__ == "__main__":
    main()
