# tests/conftest.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import database

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_library.db"
    monkeypatch.setattr(database, "DATABASE", str(test_db))
    database.init_database()
    database.add_sample_data()
    yield