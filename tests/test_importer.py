import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.import_dictionary import main

def test_importer_dry_run():
    # Setup temporary fetched JSON file
    sample_data = [
        {"devanagari": "पाणी", "meaning2": "water"},
        {"devanagari": "घर", "meaning2": "house"}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "fetched.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(sample_data, f)
            
        # Run main with arguments using patch sys.argv
        with patch("sys.argv", ["import_dictionary.py", "--input", str(input_file), "--dry-run"]):
            with patch("scripts.import_dictionary.DictionaryAdapter") as MockAdapter:
                mock_adapter_instance = MockAdapter.return_value
                # Assume both words are already present
                mock_adapter_instance.exists.return_value = True
                
                main()
                
                # Verify that adapter.exists was checked for the words
                assert mock_adapter_instance.exists.call_count == 2
                # bulk_insert should NOT be called in dry run
                mock_adapter_instance.bulk_insert.assert_not_called()

def test_importer_real_run():
    sample_data = [
        {"devanagari": "पाणी", "meaning2": "water"},
        {"devanagari": "घर", "meaning2": "house"}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "fetched.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(sample_data, f)
            
        with patch("sys.argv", ["import_dictionary.py", "--input", str(input_file)]):
            with patch("scripts.import_dictionary.DictionaryAdapter") as MockAdapter:
                mock_adapter_instance = MockAdapter.return_value
                mock_adapter_instance.bulk_insert.return_value = {"inserted": 2, "skipped": 0, "errors": 0}
                
                main()
                
                # Verify bulk_insert called with batch of entries
                mock_adapter_instance.bulk_insert.assert_called_once()
                # Verify SQL export called
                mock_adapter_instance.export_sql.assert_called_once()
