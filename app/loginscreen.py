"""
This file will contain all the funcitonality regarding the "Login Screen" of the program
"""

from connection import connect_db


def login(email, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM members WHERE lower(email) = ? AND passwd = ?",
        (email.lower(), password),
    )
    login_info = cur.fetchone()

    conn.close()
    return login_info


def signup(email, password, name, byear, faculty):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO members (email, passwd, name, byear, faculty) VALUES (?, ?, ?, ?, ?)",
        (email, password, name, byear, faculty),
    )
    conn.commit()
    conn.close()


def check_exists(email):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT email FROM members WHERE lower(email) = ?", (email.lower(),))
    if cur.fetchone():
        conn.close()
        return True
    return False
