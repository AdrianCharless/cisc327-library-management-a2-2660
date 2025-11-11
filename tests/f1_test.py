import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.library_service import (
    add_book_to_catalog
)
from database import init_database
from os import remove



init_database()
# Sample unit tests
def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Valid Book", "Test Author", "1234567890123", 1)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 1)
    
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
    assert "Author is required." in message

def test_add_book_invalid_already_existing_ISBN():
    """Test adding a book with an already existing ISBN."""
    success1, msg1 = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    assert success1 is True

    # 2nd insert with same ISBN must fail (duplicate)
    success2, msg2 = add_book_to_catalog("Another Title", "Another Author", "1234567890123", 3)
    
    assert success2 == False 
    assert "a book with this isbn already exists." in msg2.lower()

def test_add_book_invalid_negative_integer_copies():
    """Test adding a book with a negative integer for copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)
    
    assert success == False
    assert "total copies must be a positive integer." in message.lower()
    
    
remove("library.db")