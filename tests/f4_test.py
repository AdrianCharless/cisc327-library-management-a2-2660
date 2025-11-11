import pytest
from services.library_service import (
    calculate_late_fee_for_book
)
from database import init_database, add_sample_data
from os import remove

init_database()
add_sample_data()

def test_calculate_book_late_fee_on_time_valid_input():
    """Test the fee for a book with valid input thats on time."""
    values = calculate_late_fee_for_book("123456", "123")
    
    assert values["days_overdue"] == 0

def test_calculate_book_late_fee_overdue_valid_input():
    """Test the fee for a book with valid input thats overdue."""
    values = calculate_late_fee_for_book("123456", 4)
    assert values["days_overdue"] > 0
    assert values["fee_amount"] > 0


def test_calculate_book_late_fee_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    values = calculate_late_fee_for_book("123456789", "123")
    
    assert values["status"] == "Invalid patron ID"


def test_calculate_book_late_fee_invalid_book_not_found():
    """Test returning a book which doesn't exist."""
    values = calculate_late_fee_for_book("123456", "789")
    
    assert values["status"] == "Invalid book ID"

remove("library.db")