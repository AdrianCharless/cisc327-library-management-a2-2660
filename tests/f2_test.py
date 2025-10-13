import pytest
from library_service import (
    borrow_book_by_patron
)

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", "123")
    
    assert success == True
    assert "Successfully borrowed Test Book. Due date: 2026-05-01" in message.lower()

def test_borrow_book_invalid_patron_id():
    """Test borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("123456789", "123")
    
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message.lower()

def test_borrow_book_invalid_book_not_found():
    """Test borrowing a book which doesn't exist."""
    success, message = borrow_book_by_patron("123456", "456")
    
    assert success == False
    assert "Book not found." in message.lower()

def test_borrow_book_invalid_no_copies():
    """Test borrowing a book which exists, but there are no copies."""
    success, message = borrow_book_by_patron("123456", "789")
    
    assert success == False
    assert "This book is currently not available." in message.lower()