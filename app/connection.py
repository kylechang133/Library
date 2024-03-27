"""
This file assists the connection between any file and the database.
"""

import sqlite3
import sys

def valid_db():
    if len(sys.argv) < 2:
        print("Error: Too few command line arguments provided. Verify that a database was provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("Error: Too many command line arguments provided. Verify that only one database was provided")
        sys.exit(1)

def connect_db():
    database_name = sys.argv[1]
    conn = sqlite3.connect(database_name)
    conn.row_factory = sqlite3.Row # Makes it so that table entries can be accessed like a python dictionary
    return conn
