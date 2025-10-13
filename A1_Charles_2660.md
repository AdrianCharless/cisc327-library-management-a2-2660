Adrian Charles
20352660
Group 1

| Function name                  | Implementation status  | What is missing                                         |
|--------------------------------|------------------------|---------------------------------------------------------|
| add_book_to_catalog            | complete               | N/A                                                     |
| borrow_book_by_patron          | complete               | N/A                                                     |
| return_book_by_patron          | partial                | Book return functionality and R4 is not yet implemented |
| calculate_late_fee_for_book    | partial                | Late fee calculation and R5 not implemented             |
| search_books_in_catalog        | partial                | Search for books in the catalog and R6 not implemented  |
| get_patron_status_report       | partial                | Get status report for a patron and R7 not implemented   |
|--------------------------------|------------------------|---------------------------------------------------------|

f1_test.py tests function add_book_to_catalog with
    - a valid input test
    - an invalid input with a short ISBN
    - an invalid input with no title
    - an invalid input with no author
    - an invalid input with a previously existing ISBN
    - an invalid input with a negative integer for the copies

f2_test.py tests function borrow_book_by_patron with
    - a valid input test
    - an invalid input with a too long patron ID
    - an invalid input with a book ISBN which doesn't exist
    - a invalid input because no copies available

f3_test.py tests function return_book_by_patron with
    - a valid input test
    - an invalid input with too long patron ID
    - an invalid input with a book ISBN which doesn't exist
    - an invalid input matching a book to a patron who didn't borrow it

f4_test.py tests function calculate_late_fee_for_book with
    - a valid input test with an book thats on time
    - a valid input test for a book that is overdue
    - an invalid input with a too long patron id
    - an invalid input for an isbn book id 

f5_test.py tests search_books_in_catalog with
    - a valid input test using isbn type
    - an invalid input with a type which isn't available
    - an invalid input with a too short ISBN 
    - an valid input test using author type 

f6_test.py tests function get_patron_status_report with
    - a valid input test
    - an invalid input with a too long patron id
    - an invalid input with correct patron id format but no patron tied to the id
    - an valid input with matching patron id but no result history