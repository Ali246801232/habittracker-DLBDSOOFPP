import pytest
import sqlite3
import tempfile

from src.habittracker import db_handler

@pytest.fixture(autouse=True)
def use_temp_db():
    """Use a temporary database file for tests."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    original_path = db_handler.DB_PATH
    db_handler.DB_PATH = temp_file.name
    yield
    db_handler.DB_PATH = original_path

def test_initialize_database():
    """Test database initialization creates tables."""
    db_handler.initialize_database()
    conn = sqlite3.connect(db_handler.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # All tables present
    assert "habits" in tables
    assert "periods" in tables
    assert "completions" in tables
    conn.close()

def test_save_and_load_all():
    """Test saving and loading habits."""
    db_handler.initialize_database()

    # Create test data
    data = {
        "uuid-1": {
            "habit": {
                "name": "Test Habit",
                "periodicity_amount": 1,
                "periodicity_unit": "days",
                "notes": "Test notes",
                "start_date": "2023-01-01T00:00:00",
            },
            "periods": [
                {"start": "2023-01-01T00:00:00", "end": "2023-01-02T00:00:00"}
            ],
            "completions": ["2023-01-01T12:00:00"]
        }
    }

    db_handler.save_all(data)
    loaded = db_handler.load_all()

    # All data matches
    assert "uuid-1" in loaded
    assert loaded["uuid-1"]["habit"]["name"] == "Test Habit"
    assert len(loaded["uuid-1"]["periods"]) == 1
    assert len(loaded["uuid-1"]["completions"]) == 1