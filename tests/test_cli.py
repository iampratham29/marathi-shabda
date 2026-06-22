import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from marathi_shabda.cli import dict_cli

def test_dict_cli_stats():
    with patch("sys.argv", ["marathi-dict", "stats"]):
        with patch("marathi_shabda.cli.DictionaryAdapter") as MockAdapter:
            mock_adapter = MockAdapter.return_value
            mock_conn = mock_adapter._get_connection.return_value.__enter__.return_value
            
            # Mock cursor returns
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                (100,),  # total
                (90,),   # with roman
                (80,),   # with english
                (50,)    # with marathi def
            ]
            mock_conn.execute.return_value = mock_cursor
            
            assert dict_cli() == 0
            assert mock_conn.execute.call_count >= 4

def test_dict_cli_lookup():
    with patch("sys.argv", ["marathi-dict", "lookup", "पाणी"]):
        with patch("marathi_shabda.cli.DictionaryAdapter") as MockAdapter:
            mock_adapter = MockAdapter.return_value
            mock_entry = MagicMock()
            mock_entry.devanagari = "पाणी"
            mock_entry.english_meanings = ["water"]
            mock_entry.roman_key = "pani"
            mock_entry.pos = MagicMock(value="noun")
            mock_entry.source = "wiktionary"
            
            mock_adapter.lookup_by_devanagari.return_value = [mock_entry]
            
            assert dict_cli() == 0
            mock_adapter.lookup_by_devanagari.assert_called_once_with("पाणी")

def test_dict_cli_export():
    with tempfile.TemporaryDirectory() as temp_dir:
        sql_path = Path(temp_dir) / "output.sql"
        with patch("sys.argv", ["marathi-dict", "export", str(sql_path)]):
            with patch("marathi_shabda.cli.DictionaryAdapter") as MockAdapter:
                mock_adapter = MockAdapter.return_value
                
                assert dict_cli() == 0
                mock_adapter.export_sql.assert_called_once_with(str(sql_path))

def test_dict_cli_import():
    with patch("sys.argv", ["marathi-dict", "import", "data/fetched.json"]):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            assert dict_cli() == 0
            mock_run.assert_called_once()
