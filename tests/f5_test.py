import pytest
from library_service import (
    search_books_in_catalog
)
from database import init_database, add_sample_data
from os import remove

init_database()
add_sample_data()

def test_search_book_valid_input():
    """Test searching for a book with a valid ISBN input."""
    result = search_books_in_catalog("9780743273565", "isbn")

    assert any("9780743273565" in book["isbn"] for book in result)

def test_search_book_invalid_type():
    """Test searching for a book with an invalid type."""
    result = search_books_in_catalog("2004", "year")

    assert result == []

def test_search_book_invalid_invalid_isbn():
    """Test searching for a book with an invalid isbn, too short."""
    result = search_books_in_catalog("123456789", "isbn")

    assert result == []

def test_search_book_valid_input_title():
    """Test searching for a book with a valid title input."""
    result = search_books_in_catalog("The Great", "title")

    assert any("The Great" in book["title"] for book in result)

def test_search_book_valid_input_Author():
    """Test searching for a book with a valid author input."""
    result = search_books_in_catalog("Harp", "author")

    assert any("Harp" in book["author"] for book in result)

remove("library.db")
