import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)
from database import init_database, add_sample_data, update_borrow_record_return_date, get_db_connection
from datetime import datetime, timedelta
from os import remove

# Initialize database for testing
init_database()
add_sample_data()

# ========== R1: ADD BOOK TO CATALOG TESTS ==========
def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Valid Book", "Test Author", "9991234567890", 1)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 1)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_no_title():
    """Test adding a book with no title."""
    success, message = add_book_to_catalog("", "Test Author", "9991234567891", 5)
    
    assert success == False
    assert "Title is required." in message

def test_add_book_invalid_no_author():
    """Test adding a book with no author."""
    success, message = add_book_to_catalog("Test Book", "", "9991234567892", 5)
    
    assert success == False
    assert "Author is required." in message

def test_add_book_invalid_already_existing_isbn():
    """Test adding a book with an already existing ISBN."""
    success1, msg1 = add_book_to_catalog("First Book", "First Author", "9991234567893", 5)
    assert success1 is True

    # 2nd insert with same ISBN must fail (duplicate)
    success2, msg2 = add_book_to_catalog("Another Title", "Another Author", "9991234567893", 3)
    
    assert success2 == False 
    assert "a book with this isbn already exists" in msg2.lower()

def test_add_book_invalid_negative_integer_copies():
    """Test adding a book with a negative integer for copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "9991234567894", -5)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_invalid_zero_copies():
    """Test adding a book with zero copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "9991234567895", 0)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_title_too_long():
    """Test adding a book with title exceeding 200 characters."""
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", "9991234567896", 1)
    
    assert success == False
    assert "200 characters" in message

def test_add_book_author_too_long():
    """Test adding a book with author exceeding 100 characters."""
    long_author = "A" * 101
    success, message = add_book_to_catalog("Test Book", long_author, "9991234567897", 1)
    
    assert success == False
    assert "100 characters" in message

# ========== R3: BORROW BOOK TESTS ==========
def test_borrow_book_valid():
    """Test borrowing a book with valid input."""
    # Add a book first
    add_book_to_catalog("Borrowable Book", "Test Author", "9992234567890", 3)
    
    # Get book ID (should be the last added)
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9992234567890",)).fetchone()
    conn.close()
    book_id = book['id']
    
    success, message = borrow_book_by_patron("100001", book_id)
    
    assert success == True
    assert "successfully borrowed" in message.lower()
    assert "due date" in message.lower()

def test_borrow_book_invalid_patron_id_too_short():
    """Test borrowing with patron ID too short."""
    success, message = borrow_book_by_patron("12345", 1)
    
    assert success == False
    assert "6 digits" in message

def test_borrow_book_invalid_patron_id_too_long():
    """Test borrowing with patron ID too long."""
    success, message = borrow_book_by_patron("1234567", 1)
    
    assert success == False
    assert "6 digits" in message

def test_borrow_book_invalid_patron_id_not_numeric():
    """Test borrowing with non-numeric patron ID."""
    success, message = borrow_book_by_patron("12345a", 1)
    
    assert success == False
    assert "6 digits" in message

def test_borrow_book_not_found():
    """Test borrowing a non-existent book."""
    success, message = borrow_book_by_patron("100002", 99999)
    
    assert success == False
    assert "book not found" in message.lower()

def test_borrow_book_not_available():
    """Test borrowing a book with no available copies."""
    # Book ID 3 (1984) has 0 available copies in sample data
    success, message = borrow_book_by_patron("100003", 3)
    
    assert success == False
    assert "not available" in message.lower()

def test_borrow_book_patron_limit_exceeded():
    """Test borrowing when patron has reached 5 book limit."""
    # Add multiple books
    for i in range(6):
        add_book_to_catalog(f"Book {i}", "Author", f"999323456789{i}", 2)
    
    # Get book IDs
    conn = get_db_connection()
    books = conn.execute("SELECT id FROM books WHERE isbn LIKE '999323456789%'").fetchall()
    conn.close()
    
    # Borrow 5 books (should succeed)
    patron_id = "100004"
    for i in range(5):
        success, _ = borrow_book_by_patron(patron_id, books[i]['id'])
        assert success == True
    
    # Try to borrow 6th book (should fail)
    success, message = borrow_book_by_patron(patron_id, books[5]['id'])
    
    assert success == False
    assert "maximum borrowing limit" in message.lower()
    assert "5 books" in message.lower()

# ========== R4: RETURN BOOK TESTS ==========
def test_return_book_valid():
    """Test returning a borrowed book."""
    # Add and borrow a book first
    add_book_to_catalog("Returnable Book", "Test Author", "9993234567890", 2)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9993234567890",)).fetchone()
    conn.close()
    book_id = book['id']
    
    patron_id = "200001"
    borrow_book_by_patron(patron_id, book_id)
    
    # Return the book
    success, message = return_book_by_patron(patron_id, book_id)
    
    assert success == True
    assert "returned" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning with invalid patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    assert "6 digits" in message

def test_return_book_invalid_book_id():
    """Test returning with invalid book ID."""
    success, message = return_book_by_patron("200002", -1)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_return_book_not_found():
    """Test returning a non-existent book."""
    success, message = return_book_by_patron("200003", 99999)
    
    assert success == False
    assert "book not found" in message.lower()

def test_return_book_not_borrowed():
    """Test returning a book that wasn't borrowed by patron."""
    success, message = return_book_by_patron("200004", 1)
    
    assert success == False
    assert "unable to be returned" in message.lower()

def test_return_book_with_late_fee():
    """Test returning a book late incurs fee."""
    # Add and borrow a book
    add_book_to_catalog("Late Book", "Test Author", "9994234567890", 2)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9994234567890",)).fetchone()
    book_id = book['id']
    
    patron_id = "200005"
    borrow_book_by_patron(patron_id, book_id)
    
    # Manually set due date to past (make it overdue by 3 days)
    past_due_date = (datetime.now() - timedelta(days=3)).isoformat()
    conn.execute("""
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (past_due_date, patron_id, book_id))
    conn.commit()
    conn.close()
    
    # Return the book
    success, message = return_book_by_patron(patron_id, book_id)
    
    assert success == True
    assert "late fee" in message.lower()
    assert "$1.50" in message  # 3 days * $0.50

# ========== R5: CALCULATE LATE FEE TESTS ==========
def test_calculate_late_fee_no_late():
    """Test fee calculation for on-time return."""
    # Setup a borrow record that's not late
    add_book_to_catalog("OnTime Book", "Author", "9995234567890", 1)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9995234567890",)).fetchone()
    book_id = book['id']
    conn.close()
    
    patron_id = "300001"
    borrow_book_by_patron(patron_id, book_id)
    
    result = calculate_late_fee_for_book(patron_id, book_id)
    
    assert result['fee_amount'] == 0
    assert result['days_overdue'] == 0
    assert "on time" in result['status'].lower()

def test_calculate_late_fee_first_week():
    """Test fee calculation for first 7 days ($.50/day)."""
    add_book_to_catalog("Late Week Book", "Author", "9996234567890", 1)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9996234567890",)).fetchone()
    book_id = book['id']
    
    patron_id = "300002"
    borrow_book_by_patron(patron_id, book_id)
    
    # Make it 5 days overdue
    past_due_date = (datetime.now() - timedelta(days=5)).isoformat()
    conn.execute("""
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (past_due_date, patron_id, book_id))
    conn.commit()
    conn.close()
    
    result = calculate_late_fee_for_book(patron_id, book_id)
    
    assert result['fee_amount'] == 2.50  # 5 days * $0.50
    assert result['days_overdue'] == 5

def test_calculate_late_fee_after_week():
    """Test fee calculation after 7 days ($1/day after first week)."""
    add_book_to_catalog("Very Late Book", "Author", "9997234567890", 1)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9997234567890",)).fetchone()
    book_id = book['id']
    
    patron_id = "300003"
    borrow_book_by_patron(patron_id, book_id)
    
    # Make it 10 days overdue
    past_due_date = (datetime.now() - timedelta(days=10)).isoformat()
    conn.execute("""
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (past_due_date, patron_id, book_id))
    conn.commit()
    conn.close()
    
    result = calculate_late_fee_for_book(patron_id, book_id)
    
    # First 7 days: 7 * $0.50 = $3.50
    # Days 8-10: 3 * $1.00 = $3.00
    # Total: $6.50
    assert result['fee_amount'] == 6.50
    assert result['days_overdue'] == 10

def test_calculate_late_fee_maximum():
    """Test fee calculation caps at $15."""
    add_book_to_catalog("Super Late Book", "Author", "9998234567890", 1)
    
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("9998234567890",)).fetchone()
    book_id = book['id']
    
    patron_id = "300004"
    borrow_book_by_patron(patron_id, book_id)
    
    # Make it 30 days overdue
    past_due_date = (datetime.now() - timedelta(days=30)).isoformat()
    conn.execute("""
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (past_due_date, patron_id, book_id))
    conn.commit()
    conn.close()
    
    result = calculate_late_fee_for_book(patron_id, book_id)
    
    assert result['fee_amount'] == 15.0  # Maximum cap
    assert result['days_overdue'] == 30

def test_calculate_late_fee_invalid_patron():
    """Test fee calculation with invalid patron ID."""
    result = calculate_late_fee_for_book("123", 1)
    
    assert result['fee_amount'] == 0
    assert result['days_overdue'] == 0
    assert "invalid patron" in result['status'].lower()

def test_calculate_late_fee_invalid_book():
    """Test fee calculation with invalid book ID."""
    result = calculate_late_fee_for_book("300005", -1)
    
    assert result['fee_amount'] == 0
    assert result['days_overdue'] == 0
    assert "invalid book" in result['status'].lower()

def test_calculate_late_fee_no_borrow_record():
    """Test fee calculation with no borrow record."""
    result = calculate_late_fee_for_book("300006", 1)
    
    assert result['fee_amount'] == 0
    assert result['days_overdue'] == 0
    assert "no borrow record" in result['status'].lower()

# ========== R6: SEARCH BOOKS TESTS ==========
def test_search_books_by_title():
    """Test searching books by title."""
    add_book_to_catalog("Unique Title XYZ", "Author", "9999234567890", 1)
    
    results = search_books_in_catalog("Unique Title", "title")
    
    assert len(results) > 0
    assert any("unique title xyz" in book['title'].lower() for book in results)

def test_search_books_by_author():
    """Test searching books by author."""
    add_book_to_catalog("Book", "Unique Author ABC", "9999234567891", 1)
    
    results = search_books_in_catalog("Unique Author", "author")
    
    assert len(results) > 0
    assert any("unique author abc" in book['author'].lower() for book in results)

def test_search_books_by_isbn():
    """Test searching books by ISBN."""
    add_book_to_catalog("Book", "Author", "9999234567892", 1)
    
    results = search_books_in_catalog("9999234567892", "isbn")
    
    assert len(results) == 1
    assert results[0]['isbn'] == "9999234567892"

def test_search_books_partial_match():
    """Test partial matching in search."""
    add_book_to_catalog("The Great Adventure", "John Smith", "9999234567893", 1)
    
    # Partial title search
    results = search_books_in_catalog("Great", "title")
    assert len(results) > 0
    
    # Partial author search
    results = search_books_in_catalog("Smith", "author")
    assert len(results) > 0

def test_search_books_empty_search_term():
    """Test search with empty search term."""
    results = search_books_in_catalog("", "title")
    
    assert results == []

def test_search_books_invalid_search_type():
    """Test search with invalid search type."""
    results = search_books_in_catalog("Test", "invalid_type")
    
    assert results == []

def test_search_books_no_results():
    """Test search that returns no results."""
    results = search_books_in_catalog("NonexistentBookXYZ123", "title")
    
    assert results == []

def test_search_books_case_insensitive():
    """Test case-insensitive search."""
    add_book_to_catalog("CaSe TeSt BoOk", "MiXeD CaSe AuThOr", "9999234567894", 1)
    
    # Search with different case
    results_title = search_books_in_catalog("case test", "title")
    results_author = search_books_in_catalog("mixed case", "author")
    
    assert len(results_title) > 0
    assert len(results_author) > 0

# ========== R7: PATRON STATUS REPORT TESTS ==========
def test_patron_status_report_valid():
    """Test getting patron status with borrowed books."""
    patron_id = "400001"
    
    # Add and borrow a book
    add_book_to_catalog("Status Book", "Author", "8881234567890", 1)
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("8881234567890",)).fetchone()
    conn.close()
    book_id = book['id']
    
    borrow_book_by_patron(patron_id, book_id)
    
    report = get_patron_status_report(patron_id)
    
    assert report['patron_id'] == patron_id
    assert report['borrow_count'] == 1
    assert len(report['currently_borrowed']) == 1
    assert report['total_late_fees'] == 0

def test_patron_status_report_with_late_fees():
    """Test patron status with overdue books and fees."""
    patron_id = "400002"
    
    # Add and borrow multiple books
    for i in range(2):
        add_book_to_catalog(f"Late Status Book {i}", "Author", f"888223456789{i}", 1)
        conn = get_db_connection()
        book = conn.execute("SELECT id FROM books WHERE isbn = ?", (f"888223456789{i}",)).fetchone()
        book_id = book['id']
        
        borrow_book_by_patron(patron_id, book_id)
        
        # Make first book 5 days overdue, second book 10 days overdue
        overdue_days = 5 if i == 0 else 10
        past_due_date = (datetime.now() - timedelta(days=overdue_days)).isoformat()
        conn.execute("""
            UPDATE borrow_records 
            SET due_date = ? 
            WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        """, (past_due_date, patron_id, book_id))
        conn.commit()
        conn.close()
    
    report = get_patron_status_report(patron_id)
    
    assert report['patron_id'] == patron_id
    assert report['borrow_count'] == 2
    # First book: 5 days * $0.50 = $2.50
    # Second book: 7 * $0.50 + 3 * $1.00 = $6.50
    # Total: $9.00
    assert report['total_late_fees'] == 9.00

def test_patron_status_report_no_books():
    """Test patron status with no borrowed books."""
    patron_id = "400003"
    
    report = get_patron_status_report(patron_id)
    
    assert report['patron_id'] == patron_id
    assert report['borrow_count'] == 0
    assert len(report['currently_borrowed']) == 0
    assert report['total_late_fees'] == 0

def test_patron_status_report_invalid_patron():
    """Test patron status with invalid patron ID."""
    report = get_patron_status_report("123")  # Invalid ID (not 6 digits)
    
    assert report == {}

def test_patron_status_report_history():
    """Test patron status includes borrowing history."""
    patron_id = "400004"
    
    # Add, borrow and return a book
    add_book_to_catalog("History Book", "Author", "8883234567890", 1)
    conn = get_db_connection()
    book = conn.execute("SELECT id FROM books WHERE isbn = ?", ("8883234567890",)).fetchone()
    conn.close()
    book_id = book['id']
    
    borrow_book_by_patron(patron_id, book_id)
    return_book_by_patron(patron_id, book_id)
    
    report = get_patron_status_report(patron_id)
    
    assert report['patron_id'] == patron_id
    assert len(report['borrowing_history']) > 0

# Clean up database after tests
def test_cleanup():
    """Clean up the test database."""
    remove("library.db")