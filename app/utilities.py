"""
This file is for utility functions
"""

from datetime import datetime, timedelta


def date_to_string(date):
    """Takes a datetime object and returns a formatted string of the date"""
    return date.strftime("%Y-%m-%d")


def string_to_date(date):
    """Takes a formatted string of a date and returns a datetime object"""
    return datetime.strptime(date, "%Y-%m-%d")


def is_overdue(date):
    """Takes a datetime object and returns true if it is more than 20 days from now (i.e. overdue)"""
    if datetime.today() - timedelta(days=20) > date:
        return True
    else:
        return False


def extract_column(array, column_index):
    """Takes in a matrix(2D list) and the column index to be extracted, and returns a list with the column values"""
    return [row[column_index] for row in array]


def insensitive_compare(string1, string2):
    return string1.lower() == string2.lower()
