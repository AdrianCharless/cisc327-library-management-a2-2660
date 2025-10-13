import pytest
from library_service import (
    add_book_to_catalog
)

# Sample unit tests
def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

# My unit tests, I did 6 just in case you wanted 4-5 of my own, not including the samples
def test_add_book_invalid_no_title():
    """Test adding a book with no title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "Title is required." in message

def test_add_book_invalid_no_author():
    """Test adding a book with no author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "Title is required." in message

def test_add_book_invalid_already_existing_ISBN():
    """Test adding a book with an already existing ISBN."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "A book with this ISBN already exists." in message.lower()

def test_add_book_invalid_negative_integer_copies():
    """Test adding a book with a negative integer for copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)
    
    assert success == False
    assert "Total copies must be a positive integer." in message.lower()