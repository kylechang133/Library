"""
This file is the main file for the program. This file will run when we want the entire program to run.
"""

import getpass

from connection import valid_db
from loginscreen import check_exists, login, signup
from systemfunctionality import (pay_penalty, return_book, search_book,
                                 view_profile)


def login_screen():
    print("============================================")
    print("Library Database System")

    while True:

        print("1. Login")
        print("2. Sign up")
        print("3. Exit\n")

        choice = input("Enter choice: ")

        if choice == "1":  # Login
            email = input("Email: ")
            password = getpass.getpass("Password: ")
            user = login(email, password)

            if user:
                return user
            else:
                print("Invalid email or password\n")

        elif choice == "2":  # Signup
            email = input("Email: ")

            # Keep prompt for email until getting an unique one
            while check_exists(email):
                email = input(
                    "Email already in use, please use another email \nEmail: "
                )

            password = getpass.getpass("Password: ")
            name = input("Name: ")
            byear = input("Birth Year: ")
            faculty = input("Faculty: ")

            signup(email, password, name, byear, faculty)
            print("Signup successful. You can now login.\n")

        elif choice == "3":  # Exit
            return

        else:  # Other
            print("Please select option 1, 2, or 3\n")


def function_select(user):
    while True:
        print("============================================")
        print(f"Welcome back, {user['name']}!")
        print("Please choose your action to perform\n")

        print("1. View user profile")
        print("2. Return a book")
        print("3. Search for a book")
        print("4. Pay a penalty")
        print("5. Log off\n")

        choice = input("Enter choice number: ")
        if choice == "1":
            view_profile(user)
        elif choice == "2":
            return_book(user)
        elif choice == "3":
            search_book(user)
        elif choice == "4":
            pay_penalty(user)
        elif choice == "5":
            print("Logging off...\n")
            break
        else:
            print("Please select option 1, 2, 3, 4 or 5\n")
    return True


def main():
    user = None

    valid_db()

    while True:
        user = login_screen()

        if user is not None:  # Login attempt is successful
            while function_select(user):  # Return user to login screen if they logoff
                user = login_screen()
                if user is None:  # User exists the program
                    print("Exiting...\n")
                    return
            break

        elif user is None:  # User exists the program
            print("Exiting...\n")
            return


if __name__ == "__main__":
    main()
