import sqlite3
from pathlib import Path
import sys

def migrate(db_path=None):
    # Find database path relative to this script
    if db_path is None:
        base_dir = Path(__file__).parent.parent
        db_path = base_dir / "src" / "marathi_shabda" / "data" / "dictionary.db"
    
    print(f"Connecting to database at: {db_path}")
    if not db_path.exists():
        print(f"Error: Database file does not exist at {db_path}", file=sys.stderr)
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(MarathiEnglish);")
        columns = [row[1] for row in cursor.fetchall()]
        
        columns_to_add = [
            ("devanagari", "TEXT"),
            ("pos", "TEXT"),
            ("definition_mr", "TEXT"),
            ("source", "TEXT"),
            ("is_stem", "INTEGER DEFAULT 1")
        ]
        
        added_columns = []
        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE MarathiEnglish ADD COLUMN {col_name} {col_type};")
                added_columns.append(col_name)
                print(f"Added column: {col_name} ({col_type})")
        
        # Backfill devanagari
        cursor.execute("""
            UPDATE MarathiEnglish 
            SET devanagari = TRIM(Meaning1) 
            WHERE devanagari IS NULL AND Meaning1 IS NOT NULL;
        """)
        devanagari_updates = cursor.rowcount
        
        # Backfill source
        cursor.execute("""
            UPDATE MarathiEnglish 
            SET source = 'original' 
            WHERE source IS NULL;
        """)
        source_updates = cursor.rowcount
        
        conn.commit()
        
        print("\n=== Migration Summary ===")
        print(f"Columns added : {', '.join(added_columns) if added_columns else 'None'}")
        print(f"Rows updated (devanagari backfill) : {devanagari_updates}")
        print(f"Rows updated (source backfill)     : {source_updates}")
        print("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
