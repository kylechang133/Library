"""
This file will contain all the database query request handle functions
"""
from connection import connect_db
from datetime import datetime, timedelta, date
from utilities import *

def view_profile(user):
    print("\n============================================")
    print("Viewing profile")
    conn = connect_db()
    cur = conn.cursor()
    email = user[0]

    #print personal informtion
    cur.execute("SELECT name, email, byear FROM members WHERE email = ?", (email, ))   
    info = cur.fetchone() 
    print("Name: " + info[0] + " | Email: " + info[1] + " | Birth year: " + str(info[2]) + "\n")

    #fetch and print borrowed and returned books
    cur.execute("SELECT count(bid) FROM borrowings WHERE member = ? AND end_date IS NOT NULL GROUP BY member", (email, ))
    returned_books = cur.fetchone()

    if(returned_books is None):
        print("You have previous borrowed 0 books")
    else:
        print("You have previous borrowed " + str(returned_books[0]) + " books")

    #fetch and return currently borrowing books
    cur.execute("SELECT count(bid) FROM borrowings WHERE member = ? AND end_date IS NULL GROUP BY member", (email, ))
    returned_books = cur.fetchone()
    
    if(returned_books is None):
        print("You are currently borrowing 0 books...")
    else:
        print("You are currently borrowing " + str(returned_books[0]) + " books...")

        #fetch and find overdue borrowings
        cur.execute("SELECT start_date, count(bid) FROM borrowings WHERE member = ? AND end_date IS NULL GROUP BY member, start_date", (email, ))
        returned_books = cur.fetchall()

        overdue_count = 0
        #add all the books that are overdue, calculate their sum
        for x in returned_books:
            borrowed_date = datetime.strptime(x[0],'%Y-%m-%d')
            if is_overdue(borrowed_date):
                overdue_count += x[1]

        print("Which has " + str(overdue_count) + " overdues \n")

    cur.execute("SELECT count(pid), sum(amount), sum(paid_amount) FROM penalties, borrowings WHERE penalties.bid = borrowings.bid AND borrowings.member = ? AND (paid_amount < amount OR paid_amount IS NULL) GROUP BY member", (email, ))
    penalty_data = cur.fetchone()
    if(penalty_data is None):
        print("You currently have no unpaid penalties")
    else:
        print(f"You currently have: {penalty_data[0]} unpaid penalties. Your unpaid amount is ${penalty_data[1] - penalty_data[2]}.")

    conn.close()

    input("Press Enter to return to menu...")

def return_book(user):
    print("\n============================================")
    print("Book Return\n")
    conn = connect_db()
    cur = conn.cursor()
    email = user[0]
    r_flag = False

    cur.execute('''SELECT b1.bid, b2.title, b1.start_date, b2.book_id
                FROM borrowings b1, books b2
                WHERE b1.book_id = b2.book_id 
                AND b1.member = ?
                AND b1.end_date IS NULL''', (email, ))
    borrowing_list = cur.fetchall()

    if(not borrowing_list):
        input("You are not currently borrowing any books, press ENTER to return to main menu...\n")
    else:
        #main loop- only broken by finished execution or return command
        while True:
            print("You are currently Borrowing: ")

            for x in borrowing_list:
                deadline = date_to_string((string_to_date(x[2])) + timedelta(days = 20))
                print(f"Borrowing id: {str(x[0])} | Title: {x[1]} | Borrowing date: {x[2]} | Return deadline: {deadline}")

            #extract the column of bid from the query results
            bid = extract_column(borrowing_list, 0)
            book_index = 0
            return_choice = input("\nPlease enter the borrowing id of the book to return and press ENTER (enter E to exit to main menu): ")

            if return_choice.lower() == "e": 
                break
            else:
                # bid input checking loop - breaks after input is valid
                while True:
                    try:
                        while not int(return_choice) in bid:
                            print("bid number does not exist")
                            return_choice = input("\nPlease enter the borrowing id of the book to return and press ENTER (enter E to exit to main menu): ")
                            if(return_choice.lower() == "e"):
                                r_flag = True
                                break
                        book_index = bid.index(int(return_choice))
                        break
                    except:
                        print("Invalid input - please enter a digit")
                        return_choice = input("\nPlease enter the borrowing id of the book to return and press ENTER (enter E to exit to main menu): ")
                        if(return_choice.lower() == "e"):
                            r_flag = True
                            break
                if(r_flag == True):
                    break

                # return the book by updating borrowings
                cur.execute("UPDATE borrowings SET end_date = ? WHERE bid = ?", (date_to_string(datetime.today()), int(return_choice)))

                borrowing_date = string_to_date(borrowing_list[book_index][2])

                if(is_overdue(borrowing_date)):
                    charge = (datetime.today() - (borrowing_date + timedelta(days = 20))).days
                    
                    cur.execute("SELECT MAX(pid) from penalties")
                    penalty_index = cur.fetchone()[0] + 1
                    
                    cur.execute("INSERT into penalties VALUES(?, ?, ?, ?)", (penalty_index, return_choice, charge, 0))
                    print("Return successful - you will be charged " + str(charge) + "$ due to overdue penalty.\n\n")
                else:
                    print("Return successful!\n\n")
                
                # review choice checking loop - broken if choice is Y/N
                while True:
                    review_choice = input("Would you wish to give a review to this book? (Y/N)\n")
                    review_rating = 0
                    if (review_choice.lower() == "n"):
                        break
                    elif (review_choice.lower() == "y"):

                        # rating checking loop - broken if rating is an int from 1 to 5
                        while True:
                            review_rating = input("On a scale of 1 to 5, how would you rate this book?\n")
                            try:
                                if(int(review_rating) < 1 or int(review_rating) > 5):
                                    print("Please provide the rating in the given range.")
                                else:
                                    break
                            except:
                                print("Please provide an integer number.")
                        review_text = input("If possible, please justify your rating with a brief description.\n")
                        if not review_text:
                            review_text = "No Review Text"
                        
                        cur.execute("SELECT MAX(rid) from reviews")
                        review_index = cur.fetchone()[0] + 1
                        
                        cur.execute("INSERT into reviews VALUES(?, ?, ?, ?, ?, ?)", (review_index, borrowing_list[book_index][3], email, review_rating, review_text, date_to_string(datetime.today())))

                        print("Review submitted. \n\n")
                        break
                    else:
                        print("please input a valid choice.")

                conn.commit()
            
            # checks the updated borrowing list
            cur.execute('''SELECT b1.bid, b2.title, b1.start_date, b2.book_id
                FROM borrowings b1, books b2
                WHERE b1.book_id = b2.book_id 
                AND b1.member = ?
                AND b1.end_date IS NULL''', (email, ))
            borrowing_list = cur.fetchall()

            #if all have been returned, give message and return to main menu
            if(not borrowing_list):
                input("You are not currently borrowing any books, press ENTER to return to main menu...\n")
                break

    conn.close()

def ask_yes_no(question):
    """Asks a yes/no question and returns True for 'y' and False for 'n'. (Helper function)"""
    while True:
        response = input(question + " (y/n): ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def search_book(user):
    """Main function that handles user interaction with the program regarding book searching."""
    while True: # Outer most loop for the feature (exiting this loop means finishing the search function)
        keyword = input("\nEnter a keyword to search for books: ")
        page = 1
        continue_searching = True
        books_borrowed = False

        while continue_searching and not books_borrowed: # While loop that allows users to indefinitely search for books unless they decide not to
            books, total_count = book_search_engine(keyword, page)
            total_pages = max((total_count + 4) // 5, 1) # Math that decides what "page" it is currently displaying

            # No books available
            if not books:
                print("No more books found.")
                break

            # Display the books
            print(f"Displaying Page {page} of {total_pages}")
            book_ids_available = {book['book_id']: book['available'] for book in books}
            for book in books:
                print(f"Book ID: {book['book_id']} | Title: {book['title']} | Author: {book['author']} | Publish Year: {book['pyear']} | "
                      f"Rating: {book['avg_rating'] or 'N/A'} | Available: {'Yes' if book['available'] else 'No'}")

            # Functionality for asking users if they want to borrow a book from the search
            borrowing_option = ask_yes_no("Would you like to borrow a book from this list?")
            if borrowing_option:
                while True:
                    book_id_input = input("Enter the ID of the book you want to borrow, or 'E' to exit: ")
                    if book_id_input.upper() == 'E':
                        break

                    # Check if user enters a non-valid book_id
                    try:
                        book_id = int(book_id_input)
                    except ValueError:
                        print("Please enter a valid ID for the book you want to borrow.")
                        continue

                    # Check if user enters a book that isn't listed in the search results
                    if book_id not in book_ids_available:
                        print("The book you want to borrow does not exist in the books listed.")
                        continue
                    
                    # Check if user tries to borrow a book that is already being borrowed by someone else
                    if not book_ids_available[book_id]:
                        print("This book is not available for borrowing.")
                        continue

                    # Mark book as borrowed
                    borrow_book(user, book_id)
                    books_borrowed = True
                    break

            else:
                # Exit case for when there are no more books available to be shown from the search
                if page >= total_pages:
                    print("End of search results.")
                    continue_searching = False
                else:
                    # Prompts user if they want to see the next "page" of books from the search
                    if not ask_yes_no("Would you like to see more results?"):
                        continue_searching = False
                    else:
                        page += 1
        
        # Asks user if they want to search for another book
        if not ask_yes_no("Would you like to search for another book?"):
            break

def book_search_engine(keyword, page=1):
    """
    Helper function for search_book() function.
    """
    page_size = 5
    offset = (page - 1) * page_size # Calculates how many items should be skipped before starting to return results for the current page

    keyword = f'%{keyword}%'
    conn = connect_db()
    cur = conn.cursor()

    # Create and execute query
    query = """
    SELECT book_id, title, author, pyear,
        (SELECT AVG(rating) FROM reviews WHERE reviews.book_id = books.book_id) AS avg_rating,
        (SELECT COUNT(*) FROM borrowings WHERE borrowings.book_id = books.book_id AND end_date IS NULL) = 0 AS available,
        (SELECT COUNT(*) FROM books WHERE title LIKE ? OR author LIKE ?) AS total_count
    FROM books
    WHERE title LIKE ? OR author LIKE ?
    ORDER BY
        CASE WHEN title LIKE ? THEN 0 ELSE 1 END,
        CASE WHEN title LIKE ? THEN title ELSE author END
    LIMIT ? OFFSET ?
    """
    cur.execute(query, (keyword, keyword, keyword, keyword, keyword, keyword, page_size, offset))

    books = cur.fetchall()
    total_count = books[0]['total_count'] if books else 0
    conn.close()

    return books, total_count

def borrow_book(user, book_id):
    """
    Helper function for search_book() function.
    """
    conn = connect_db()
    cur = conn.cursor()

    # Check if the book is currently borrowed
    cur.execute("SELECT COUNT(*) FROM borrowings WHERE book_id = ? AND end_date IS NULL", (book_id,))
    if cur.fetchone()[0] > 0:
        print("This book is not availiable for borrowing.")
    else:
        # Proceed to borrow the book
        today = date.today().isoformat()  # Format current date as YYYY-MM-DD
        cur.execute("INSERT INTO borrowings (member, book_id, start_date) VALUES (?, ?, ?)", (user[0], book_id, today))
        conn.commit()
        print("You have successfully borrowed the book.")

    conn.close()

def pay_penalty(user):
     
    #connect to db
    conn = connect_db()
    cur = conn.cursor()
    email = user[0]
    # if paid_amount is NULL, updates it to Zero
    cur.execute("UPDATE penalties SET paid_amount = 0 WHERE paid_amount IS NULL")
    conn.commit()
    
    # Get and show unpaid penalties from User
    cur.execute("SELECT pid, amount, paid_amount FROM penalties WHERE bid IN (SELECT bid FROM borrowings WHERE member = ?) AND paid_amount < amount", (email,))
    penalties = cur.fetchall()

    if not penalties:
        print("No unpaid penalties")
    else: 
        
        #ask user to pay, still in else statement
        x = 0
        while x == 0:
            print("List of unpaid penalties")
            for penalty in penalties:
                print(f"Penalty ID: {penalty[0]} | Amount: ${penalty[1]} | Paid Amount: ${penalty[2]}")
            penalty_select = input("Enter penalty ID or 'exit' to exit: ").lower()

            if penalty_select == "exit":
                print("No payment made")
                break
            else:
                
                try:
                    penalty_select = int(penalty_select)
                    # Get relavant data for the selected ID
                    penalty = next((p for p in penalties if p[0] == penalty_select), None)
                    # make sure penalty belongs to given user
                    cur.execute("SELECT COUNT(*) FROM penalties WHERE pid = ? AND bid IN (SELECT bid FROM borrowings WHERE member = ?)", (penalty_select, email))
                    # Checks if the penality is real
                    penalty_exists = cur.fetchone()[0] > 0

                    if penalty is not None:
                        while x == 0:
                            # Enter pay amount
                            payment_amount = float(input("Enter the payment amount: $"))

                            if payment_amount <= 0:
                                print("enter a positive number")
                            elif payment_amount > penalty[1] - penalty[2]:
                            # Update the penalty information
                                print("Do not exceed remaining payment")
                            else:
                                cur.execute("UPDATE penalties SET paid_amount = paid_amount + ? WHERE pid = ?", (payment_amount, penalty_select))
                                conn.commit()
                                print("Payment successful.")
                                x = 1
                    else:
                        print("Invalid Penalty ID. Please try again.")
                except ValueError:
                        print("Invalid input. Please enter a valid Penalty ID.")
    conn.close()   
    
