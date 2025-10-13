import pytest
from library_service import (
    search_books_in_catalog
)

def test_search_book_valid_input():
    """Test searching for a book with a valid ISBN input."""
    result = search_books_in_catalog("1234567890123", "isbn")

    assert any("1234567890123" in book["isbn"] for book in result)

def test_search_book_invalid_type():
    """Test searching for a book with an invalid type."""
    result = search_books_in_catalog("2004", "year")

    assert result == False

def test_search_book_invalid_invalid_isbn():
    """Test searching for a book with an invalid isbn, too short."""
    result = search_books_in_catalog("123456789", "isbn")

    assert result == False

def test_search_book_valid_input_title():
    """Test searching for a book with a valid title input."""
    result = search_books_in_catalog("Harry P", "title")

    assert any("Harry P" in book["title"] for book in result)

def test_search_book_valid_input_Author():
    """Test searching for a book with a valid author input."""
    result = search_books_in_catalog("JK R", "author")

    assert any("JK R" in book["author"] for book in result)


