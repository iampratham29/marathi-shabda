"""
Dictionary adapter for SQLite database access.

Philosophy: The dictionary answers "Does this word exist and what does it mean?"
It never answers "what form is this?"
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from marathi_shabda.models import DictionaryEntry, POSTag
from marathi_shabda.exceptions import DatabaseError


class DictionaryAdapter:
    """
    Encapsulates all SQLite database access.
    
    This adapter:
    - Opens SQLite DB from packaged resource
    - Provides read-only access
    - Hides schema details from rest of library
    - Can be extended without breaking existing code
    """
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize dictionary adapter.
        
        Args:
            db_path: Optional path to database file. If None, uses bundled database.
        
        Raises:
            DatabaseError: If database file not found or cannot be opened.
        """
        if db_path is None:
            # Use bundled database
            package_dir = Path(__file__).parent.parent
            db_path = package_dir / "data" / "dictionary.db"
        elif isinstance(db_path, str):
            db_path = Path(db_path)
        
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        
        # Verify database exists
        if str(self.db_path) != ":memory:" and not self.db_path.exists():
            raise DatabaseError(
                f"Dictionary database not found at {self.db_path}. "
                "Please ensure the database file is properly installed."
            )
    
    @contextmanager
    def _get_connection(self):
        """Get database connection (context manager for thread safety)."""
        is_memory = str(self.db_path) == ":memory:"
        if is_memory:
            if self._connection is None:
                self._connection = sqlite3.connect(":memory:")
                self._connection.row_factory = sqlite3.Row
                # Create schema for testing
                self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS MarathiEnglish (
                        Key TEXT,
                        Meaning1 TEXT,
                        Meaning2 TEXT,
                        Meaning3 TEXT,
                        Meaning4 TEXT,
                        user_id INTEGER,
                        devanagari TEXT,
                        pos TEXT,
                        definition_mr TEXT,
                        source TEXT,
                        is_stem INTEGER DEFAULT 1
                    );
                """)
                self._connection.commit()
            yield self._connection
            # Do not close connection for in-memory database to prevent data loss
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Access columns by name
            try:
                yield conn
            finally:
                conn.close()
    
    def lookup_by_roman(self, key: str) -> Optional[DictionaryEntry]:
        """
        Look up word by Roman key.
        
        Args:
            key: Roman Marathi word (as stored in DB)
        
        Returns:
            DictionaryEntry if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT *
                FROM MarathiEnglish
                WHERE Key = ? COLLATE NOCASE
                """,
                (key,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Extract English meanings (filter empty strings)
            meanings = [
                row[col] for col in ["Meaning2", "Meaning3", "Meaning4"]
                if col in row.keys() and row[col] and row[col].strip()
            ]
            
            pos_val = None
            if "pos" in row.keys() and row["pos"]:
                try:
                    pos_val = POSTag(row["pos"])
                except ValueError:
                    pos_val = POSTag.UNKNOWN
            
            marathi_definition = row["definition_mr"] if "definition_mr" in row.keys() else None
            source_val = row["source"] if "source" in row.keys() else None
            
            return DictionaryEntry(
                roman_key=row["Key"],
                devanagari=row["Meaning1"],
                english_meanings=meanings,
                marathi_definition=marathi_definition,
                pos=pos_val,
                source=source_val,
            )
    
    def lookup_by_devanagari(self, word: str) -> List[DictionaryEntry]:
        """
        Look up word by Devanagari text.
        
        Note: This requires scanning Meaning1 column. Not optimized for performance
        as English→Marathi lookup is not a priority use case.
        
        Args:
            word: Devanagari Marathi word
        
        Returns:
            List of matching DictionaryEntry objects (may be empty)
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT *
                FROM MarathiEnglish
                WHERE Meaning1 = ? OR (devanagari IS NOT NULL AND devanagari = ?)
                """,
                (word, word)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                meanings = [
                    row[col] for col in ["Meaning2", "Meaning3", "Meaning4"]
                    if col in row.keys() and row[col] and row[col].strip()
                ]
                
                pos_val = None
                if "pos" in row.keys() and row["pos"]:
                    try:
                        pos_val = POSTag(row["pos"])
                    except ValueError:
                        pos_val = POSTag.UNKNOWN
                
                marathi_definition = row["definition_mr"] if "definition_mr" in row.keys() else None
                source_val = row["source"] if "source" in row.keys() else None
                
                results.append(DictionaryEntry(
                    roman_key=row["Key"],
                    devanagari=row["Meaning1"],
                    english_meanings=meanings,
                    marathi_definition=marathi_definition,
                    pos=pos_val,
                    source=source_val,
                ))
            
            return results
    
    def exists(self, word: str) -> bool:
        """
        Check if word exists in dictionary (checks both Roman and Devanagari).
        
        Args:
            word: Word to check (Roman or Devanagari)
        
        Returns:
            True if word exists, False otherwise
        """
        # Try Roman lookup first (faster)
        if self.lookup_by_roman(word) is not None:
            return True
        
        # Try Devanagari lookup
        return len(self.lookup_by_devanagari(word)) > 0
        
    def insert_word(self, entry: dict) -> bool:
        """
        Insert a single word entry. Only inserts if the stem form doesn't already exist.
        entry = {
            "key": str,          # Roman transliteration (stem form)
            "devanagari": str,   # Devanagari stem form  ← REQUIRED
            "meaning2": str,     # English meaning
            "definition_mr": str,# Marathi definition (optional)
            "pos": str,          # part of speech (optional)
            "source": str,       # data source tag (optional)
        }
        Returns True if inserted, False if already exists (deduplication).
        """
        if not entry.get("devanagari"):
            raise ValueError("devanagari stem form is required")
            
        with self._get_connection() as conn:
            # Check duplicate by Devanagari (Meaning1 or devanagari column)
            cursor = conn.execute(
                "SELECT 1 FROM MarathiEnglish WHERE Meaning1 = ? OR devanagari = ?",
                (entry["devanagari"], entry["devanagari"])
            )
            if cursor.fetchone() is not None:
                return False
                
            columns = ["Meaning1", "devanagari"]
            values = [entry["devanagari"], entry["devanagari"]]
            
            if entry.get("key"):
                columns.append("Key")
                values.append(entry["key"])
            if entry.get("meaning2"):
                columns.append("Meaning2")
                values.append(entry["meaning2"])
            if "definition_mr" in entry:
                columns.append("definition_mr")
                values.append(entry["definition_mr"])
            if "pos" in entry:
                pos_val = entry["pos"]
                if hasattr(pos_val, "value"):
                    pos_val = pos_val.value
                columns.append("pos")
                values.append(pos_val)
            if "source" in entry:
                columns.append("source")
                values.append(entry["source"])
            if "is_stem" in entry:
                columns.append("is_stem")
                values.append(entry["is_stem"])
                
            query = f"INSERT INTO MarathiEnglish ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(values))})"
            conn.execute(query, values)
            conn.commit()
            return True

    def bulk_insert(self, entries: list[dict], skip_duplicates: bool = True) -> dict:
        """
        Insert multiple entries. Returns {"inserted": N, "skipped": N, "errors": N}.
        Applies lemma extraction before insert to ensure only stem forms are stored:
        - Run get_lemma(entry["devanagari"]) 
        - If lemma != devanagari, store lemma as the key, log the original as skipped inflection
        """
        from marathi_shabda.api import get_lemma
        import logging
        
        logger = logging.getLogger(__name__)
        stats = {"inserted": 0, "skipped": 0, "errors": 0}
        
        with self._get_connection() as conn:
            for entry in entries:
                try:
                    devanagari = entry.get("devanagari")
                    if not devanagari:
                        stats["errors"] += 1
                        continue
                    
                    # Run get_lemma to check for inflection
                    lemma_res = get_lemma(devanagari)
                    lemma = lemma_res.lemma
                    
                    # Copy entry to avoid mutating original
                    entry_to_insert = entry.copy()
                    
                    if lemma != devanagari:
                        logger.warning(
                            f"Skipping inflection and storing lemma: "
                            f"'{devanagari}' -> '{lemma}'"
                        )
                        entry_to_insert["devanagari"] = lemma
                        entry_to_insert["key"] = None  # Clear Roman key for inflected form
                    
                    # Try to insert
                    # Check duplicate
                    cursor = conn.execute(
                        "SELECT 1 FROM MarathiEnglish WHERE Meaning1 = ? OR devanagari = ?",
                        (entry_to_insert["devanagari"], entry_to_insert["devanagari"])
                    )
                    if cursor.fetchone() is not None:
                        if skip_duplicates:
                            stats["skipped"] += 1
                            continue
                    
                    # Perform insert
                    columns = ["Meaning1", "devanagari"]
                    values = [entry_to_insert["devanagari"], entry_to_insert["devanagari"]]
                    
                    if entry_to_insert.get("key"):
                        columns.append("Key")
                        values.append(entry_to_insert["key"])
                    
                    if entry_to_insert.get("meaning2"):
                        columns.append("Meaning2")
                        values.append(entry_to_insert["meaning2"])
                        
                    if "definition_mr" in entry_to_insert:
                        columns.append("definition_mr")
                        values.append(entry_to_insert["definition_mr"])
                        
                    if "pos" in entry_to_insert:
                        pos_val = entry_to_insert["pos"]
                        if hasattr(pos_val, "value"):
                            pos_val = pos_val.value
                        columns.append("pos")
                        values.append(pos_val)
                        
                    if "source" in entry_to_insert:
                        columns.append("source")
                        values.append(entry_to_insert["source"])
                        
                    if "is_stem" in entry_to_insert:
                        columns.append("is_stem")
                        values.append(entry_to_insert["is_stem"])
                    
                    query = f"INSERT INTO MarathiEnglish ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(values))})"
                    conn.execute(query, values)
                    stats["inserted"] += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting entry {entry}: {e}")
                    stats["errors"] += 1
            
            conn.commit()
            
        return stats

    def export_sql(self, output_path: str) -> None:
        """Export entire DB as a portable .sql dump file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")

    def get_words_missing_roman(self) -> list[str]:
        """Return Devanagari words where Key (Roman) is NULL or empty."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT Meaning1 
                FROM MarathiEnglish 
                WHERE Key IS NULL OR TRIM(Key) = ''
                """
            )
            return [row[0] for row in cursor.fetchall() if row[0]]

    def get_words_missing_english(self) -> list[str]:
        """Return Devanagari words where Meaning2 (English) is NULL or empty."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT Meaning1 
                FROM MarathiEnglish 
                WHERE Meaning2 IS NULL OR TRIM(Meaning2) = ''
                """
            )
            return [row[0] for row in cursor.fetchall() if row[0]]
    
    def close(self) -> None:
        """Close database connection (if persistent connection used)."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
