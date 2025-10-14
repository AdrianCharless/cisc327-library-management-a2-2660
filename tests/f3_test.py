import pytest
from library_service import (
    return_book_by_patron
)
from database import init_database, add_sample_data
from os import remove

init_database()
add_sample_data()

def test_return_book_valid_input():
    """Test returning a book with valid input."""
    success, message = return_book_by_patron("123456", 3)
    print("DEBUG:", message)
    assert success == True
    assert "returned book successfully with a late fee of $0.00." in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("123456789", "123")
    
    assert success == False
    assert "invalid patron id. must be exactly 6 digits." in message.lower()

def test_return_book_invalid_book_not_found():
    """Test returning a book which doesn't exist."""
    success, message = return_book_by_patron("123456", "456")
    
    assert success == False
    assert "invalid book id. must be a positive integer." in message.lower()

def test_return_book_invalid_wrong_borrower():
    """Test returning a book which was borrowed by someone else."""
    success, message = return_book_by_patron("123456", "789")
    
    assert success == False
    assert "invalid book id. must be a positive integer." in message.lower()

remove("library.db")