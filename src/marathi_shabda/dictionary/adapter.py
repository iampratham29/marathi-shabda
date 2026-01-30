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
        
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        
        # Verify database exists
        if not self.db_path.exists():
            raise DatabaseError(
                f"Dictionary database not found at {self.db_path}. "
                "Please ensure the database file is properly installed."
            )
    
    @contextmanager
    def _get_connection(self):
        """Get database connection (context manager for thread safety)."""
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
                SELECT Key, Meaning1, Meaning2, Meaning3, Meaning4
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
                if row[col] and row[col].strip()
            ]
            
            return DictionaryEntry(
                roman_key=row["Key"],
                devanagari=row["Meaning1"],
                english_meanings=meanings,
                marathi_definition=None,  # Not in current schema
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
                SELECT Key, Meaning1, Meaning2, Meaning3, Meaning4
                FROM MarathiEnglish
                WHERE Meaning1 = ?
                """,
                (word,)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                meanings = [
                    row[col] for col in ["Meaning2", "Meaning3", "Meaning4"]
                    if row[col] and row[col].strip()
                ]
                
                results.append(DictionaryEntry(
                    roman_key=row["Key"],
                    devanagari=row["Meaning1"],
                    english_meanings=meanings,
                    marathi_definition=None,
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
