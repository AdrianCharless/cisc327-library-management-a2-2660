import pytest
from library_service import (
    return_book_by_patron
)

def test_return_book_valid_input():
    """Test returning a book with valid input."""
    success, message = return_book_by_patron("123456", "123")
    
    assert success == True
    assert "successfully added" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("123456789", "123")
    
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message.lower()

def test_return_book_invalid_book_not_found():
    """Test returning a book which doesn't exist."""
    success, message = return_book_by_patron("123456", "456")
    
    assert success == False
    assert "Book not found." in message.lower()

def test_return_book_invalid_wrong_borrower():
    """Test returning a book which was borrowed by someone else."""
    success, message = return_book_by_patron("123456", "789")
    
    assert success == False
    assert "Book was not borrowed by patron ." in message.lower()