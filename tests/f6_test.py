import pytest
from library_service import (
    get_patron_status_report
)
from database import init_database, add_sample_data
from os import remove

init_database()
add_sample_data()

def test_patron_status_valid_input():
    """Test searching for a patron with a valid id input."""
    result = get_patron_status_report("123456")

    assert isinstance(result, dict)

def test_patron_status_invalid_id():
    """Test searching for a patron with an invalid id input"""
    result = get_patron_status_report("1234567890123")

    assert result == {}

def test_patron_status_valid_input_no_match():
    """Test searching for a patron with a valid id input format but id not assigned to a patron."""
    result = get_patron_status_report("789010")

    assert result["borrowing_history"] == []

def test_patron_status_valid_input_no_output():
    """Test searching for a patron with a valid id input but no results due to patron never borrowing a book."""
    result = get_patron_status_report("654321")

    assert result["currently_borrowed"] == []

remove("library.db")