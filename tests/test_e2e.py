import re
from playwright.sync_api import Page, expect
import random

# def test_has_title(page: Page):
#     page.goto("http://localhost:5000/catalog")

#     # Expect a title "to contain" a substring.
#     expect(page).to_have_title(re.compile("Library Management System"))

# def test_get_started_link(page: Page):
#     page.goto("https://playwright.dev/")

#     # Click the get started link.
#     page.get_by_role("link", name="Get started").click()

#     # Expects page to have a heading with the name of Installation.
#     expect(page.get_by_role("heading", name="Installation")).to_be_visible()

def test_e2e_add_new_book(page: Page):
    page.goto("http://localhost:5000/add_book")

    # Make the data unique for this test run
    suffix = str(random.randint(1000, 9999))
    title = f"Adrian Charles Biography {suffix}"
    isbn = str(random.randint(10**12, 10**13 - 1))  # 13-digit random ISBN
    page.get_by_label("Title *").fill(title)

    page.get_by_label("Author *").fill("LeBron James")
    
    page.get_by_label("ISBN *").fill(isbn)

    page.get_by_label("Total Copies *").fill("6")

    page.get_by_role("button", name="Add Book to Catalog").click()

    locator = page.locator('.flash-success')
    expect(locator).to_contain_text(title)

    row = page.locator("tr", has_text=title)
    patron_id = str(random.randint(100000, 999999))

    row.get_by_placeholder("Patron ID (6 digits)").fill(patron_id)
    row.get_by_role("button", name="Borrow").click()

    title_message = f'Successfully borrowed "{title}"'
    expect(page.locator(".flash-success")).to_contain_text(title_message)



def test_e2e_borrow_book_and_return(page: Page):
    page.goto("http://localhost:5000/catalog")

    # Make the data unique for this test run
    title = "Test Book"

    row = page.locator("tr", has_text=title)
    row.get_by_placeholder("Patron ID (6 digits)").fill("123456")
    row.get_by_role("button", name="Borrow").click()

    title_message = f'Successfully borrowed "{title}"'
    expect(page.locator(".flash-success")).to_contain_text(title_message)

    page.goto("http://localhost:5000/return")

    page.get_by_label("Patron ID *").fill("123456")

    page.get_by_label("Book ID *").fill("1")
    page.get_by_role("button", name="Process Return").click()

    title_message = 'Returned book successfully with a late fee of $0.00.'
    expect(page.locator(".flash-success")).to_contain_text(title_message)











