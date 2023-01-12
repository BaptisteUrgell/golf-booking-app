import datetime as dt

from passlib.hash import bcrypt

from app.classes.sqlite import SQLite
from app.classes.user import User
from app.classes.book import Book

from app.core.config import get_api_settings
settings = get_api_settings()

FERNET = settings.fernet

class AccountExist(Exception):
    pass

class AccountNotExist(Exception):
    pass

class WrongPassword(Exception):
    pass

async def get_account(email: str) -> User:
    async with SQLite() as cursor:
        await cursor.execute(f"SELECT id, email, hashed_password, credit, timestamp FROM Account WHERE email='{email}' AND disabled=False")
        account_info = await cursor.fetchone()
    if not account_info:
        raise AccountNotExist
    
    user = User(
        id=account_info[0],
        email=account_info[1],
        hashed_password=account_info[2],
        credit=account_info[3],
        timestamp=dt.datetime.strptime(account_info[4], "%Y-%m-%d %H:%M:%S"))
    return user

async def account_exist(email: str) -> bool:
    list_email = []
    async with SQLite() as cursor:
        await cursor.execute(f"SELECT email FROM Account WHERE email='{email}'")
        list_email = await cursor.fetchall()
    return bool(list_email)

async def create_account(email: str, password: str) -> bool:
    if await account_exist(email):
        raise AccountExist
    hashed_password = bcrypt.hash(password)

    async with SQLite() as cursor:
        await cursor.execute("INSERT INTO Account(email, hashed_password) VALUES(?, ?)", (email, hashed_password))
    return True

async def get_books(id: int):
    list_books = []
    async with SQLite() as cursor:
        await cursor.execute(f"SELECT id, user_id, email, password, golf, date, start_time, ideal_time, end_time, player2, player3, player4 FROM Book WHERE user_id='{id}' AND executed=False AND disabled=False")
        list_books_bd = await cursor.fetchall()
    for book in list_books_bd:
        list_books.append(Book(
            id         = book[0],
            user_id    = book[1],
            email      = book[2],
            password   = book[3],
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

async def book_exist(id: int):
    list_book = []
    async with SQLite() as cursor:
        await cursor.execute(f"SELECT id FROM Book WHERE id='{id}'")
        list_book = await cursor.fetchall()
    return bool(list_book)

async def insert_book(book: Book):
    id = None
    # try:
    async with SQLite() as cursor:
        await cursor.execute(
            f"INSERT INTO Book(user_id, email, password, golf, date, start_time, ideal_time, end_time, player2, player3, player4) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (book.user_id,
            book.email, 
            FERNET.encrypt(bytes(book.password, encoding='utf-8')),
            book.golf, 
            book.date.strftime("%Y-%m-%d"), 
            book.start_time.strftime("%H:%M:%S"),
            book.ideal_time.strftime("%H:%M:%S"),
            book.end_time.strftime("%H:%M:%S"),
            book.player2,
            book.player3, 
            book.player4))
    return True
    # except Exception as e:
    #     return False

async def disable_book(id: int):
    async with SQLite() as cursor:
        await cursor.execute(f"UPDATE Book SET disabled=True WHERE id='{id}' AND executed=False")
    return True

async def add_credit(id: int, credit: int):
    async with SQLite() as cursor:
        await cursor.execute(f"UPDATE Account SET credit=credit + {credit} WHERE id='{id}'")
    return True