import pytest
from services.library_service import borrow_book_by_patron
from database import init_database, add_sample_data
from os import remove
from datetime import datetime, timedelta

init_database()
add_sample_data()

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", 2)
    expected_due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    assert success == True
    assert f'successfully borrowed "the great gatsby". due date: {expected_due_date}' in message.lower()

def test_borrow_book_invalid_patron_id():
    """Test borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("123456789", "123")
    
    assert success == False
    assert "invalid patron id. must be exactly 6 digits." in message.lower()

def test_borrow_book_invalid_book_not_found():
    """Test borrowing a book which doesn't exist."""
    success, message = borrow_book_by_patron("123456", "456")
    
    assert success == False
    assert "book not found." in message.lower()

def test_borrow_book_invalid_no_copies():
    """Test borrowing a book which exists, but there are no copies."""
    success, message = borrow_book_by_patron("123456", "789")
    
    assert success == False
    assert "book not found." in message.lower()

remove("library.db")