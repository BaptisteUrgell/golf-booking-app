import schedule
import sys, os
import datetime as dt
import sqlite3

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

from app.chronogolf.bookCourse import BookCourse
# from app.classes.sqlite import SQLite
from app.classes.book import Book
from app.classes.user import User


from app.core.config import get_api_settings
settings = get_api_settings()
DATABASE = settings.database
FERNET = settings.fernet
DAY = 9
DRY = True
DRIVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'geckodriver-v0.32.0-macos', 'geckodriver')

class SQLite():
    def __init__(self, file=DATABASE):
        self.file=file
    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.cursor =  self.conn.cursor()
        self.conn.row_factory = sqlite3.Row
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

def get_books(date: dt.date) -> list[Book]:
    """import all book for a donnate date

    :param date: The date
    :type date: dt.date
    :return: List of book for the date
    :rtype: list[Book]
    """
    list_books = []
    with SQLite() as cursor:
        cursor.execute(f"SELECT id, user_id, email, password, golf, date, start_time, ideal_time, end_time, player2, player3, player4 FROM Book WHERE date='{date.strftime('%Y-%m-%d')}' AND disabled=False")
        list_books_bd = cursor.fetchall()

    for book in list_books_bd:
        list_books.append(Book(
            id         = book[0],
            user_id    = book[1],
            email      = book[2],
            password   = FERNET.decrypt(book[3]),
            golf       = book[4],
            date       = dt.datetime.strptime(book[5], "%Y-%m-%d").date(),
            start_time = dt.datetime.strptime(book[6], "%H:%M:%S").time(),
            ideal_time = dt.datetime.strptime(book[7], "%H:%M:%S").time(),
            end_time   = dt.datetime.strptime(book[8], "%H:%M:%S").time(),
            player2    = book[9],
            player3    = book[10],
            player4    = book[11]
        ))
    return list_books

def get_users(list_id: list[int]) -> list[User]:
    list_user = []

    with SQLite() as cursor:
        if not len(list_id) == 1:
            cursor.execute(f"SELECT id, email, hashed_password, credit, timestamp FROM Account WHERE id IN {tuple(list_id)} AND disabled=False")
        else:
            cursor.execute(f"SELECT id, email, hashed_password, credit, timestamp FROM Account WHERE id={list_id[0]} AND disabled=False")
        list_account = cursor.fetchall()
    
    for account_info in list_account:
        user = User(
            id=account_info[0],
            email=account_info[1],
            hashed_password=account_info[2],
            credit=account_info[3],
            timestamp=dt.datetime.strptime(account_info[4], "%Y-%m-%d %H:%M:%S"))

        list_user.append(user)

    return list_user

def job():
    list_book = get_books((dt.datetime.today() + dt.timedelta(days=DAY)).date())
    list_user = get_users([book.user_id for book in list_book])
    if DRY:
        print(list_book, list_user)
    threads = []
    for book in list_book:
        for user in list_user:
            if book.user_id == user.id:
                if user.credit > 0:
                    threads.append(BookCourse(DRY, DRIVER, book))
                    user.credit -= 1
                if user.credit < 0:
                    threads.append(BookCourse(DRY, DRIVER, book))
                break

    if DRY:
        print(threads)

    for t in threads:
        t.start()
    
    for t in threads:
        t.join()



if __name__ == "__main__":
    schedule.every().day.at("08:00").do(job)