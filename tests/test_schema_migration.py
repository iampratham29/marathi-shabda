import sqlite3
import shutil
import tempfile
from pathlib import Path
import pytest
from scripts.migrate_schema import migrate

def test_migration_on_test_db():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = Path(temp_dir) / "test_dictionary.db"
        
        # Create a database with the original schema
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE MarathiEnglish (
                Key TEXT,
                Meaning1 TEXT,
                Meaning2 TEXT,
                Meaning3 TEXT,
                Meaning4 TEXT,
                user_id INTEGER
            );
        """)
        # Insert sample data
        cursor.execute("INSERT INTO MarathiEnglish (Key, Meaning1, Meaning2) VALUES ('pani', 'पाणी ', 'water');")
        conn.commit()
        conn.close()
        
        # Run migration 1st time
        migrate(temp_db_path)
        
        # Verify schema and backfill
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(MarathiEnglish);")
        columns = [row[1] for row in cursor.fetchall()]
        
        assert "devanagari" in columns
        assert "pos" in columns
        assert "definition_mr" in columns
        assert "source" in columns
        assert "is_stem" in columns
        
        # Verify backfill (TRIM applied, source set to 'original')
        cursor.execute("SELECT devanagari, source, is_stem FROM MarathiEnglish WHERE Key = 'pani';")
        row = cursor.fetchone()
        assert row[0] == "पाणी"
        assert row[1] == "original"
        assert row[2] == 1
        
        conn.close()
        
        # Run migration 2nd time (idempotency check)
        migrate(temp_db_path)
        
        # Verify again
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM MarathiEnglish;")
        assert cursor.fetchone()[0] == 1
        conn.close()
