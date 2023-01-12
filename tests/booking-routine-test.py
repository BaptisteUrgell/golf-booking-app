import sys, os
import datetime as dt


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from app.chronogolf.routine import get_books, get_users, job, SQLite
# from app.classes.sqlite import SQLite

from app.core.config import get_api_settings
settings = get_api_settings()

FERNET = settings.fernet
CHRONOGOLF_PASSWORD = settings.chronogolf_password

def add_fake_account():
    list_id = []
    with SQLite() as cursor:
        for i in range(3):
            cursor.execute("INSERT INTO Account(email, hashed_password, credit) VALUES(?, ?, ?)", (f"test{i}@gmail.com", i, 4))
            list_id.append(cursor.lastrowid)
    return list_id

def add_fake_book(date: dt.datetime, list_id):
    with SQLite() as cursor:
        for id in list_id:
            cursor.execute(
                f"INSERT INTO Book(user_id, email, password, golf, date, start_time, ideal_time, end_time, player2, player3, player4) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id,
                f"cabotja@wanadoo.fr", 
                FERNET.encrypt(bytes(CHRONOGOLF_PASSWORD, encoding='utf-8')),
                "UGOLF Toulouse La Ramée", 
                date.strftime("%Y-%m-%d"), 
                dt.time(11).strftime("%H:%M:%S"),
                dt.time(12).strftime("%H:%M:%S"),
                dt.time(13).strftime("%H:%M:%S"),
                "Regine #T CABOT",
                None, 
                None))

def delete_fake_book(list_id):
    with SQLite() as cursor:
        cursor.execute(f"DELETE FROM Book WHERE user_id IN {tuple(list_id)}")


def delete_fake_account(list_id):
    with SQLite() as cursor:
        cursor.execute(f"DELETE FROM Account WHERE id IN {tuple(list_id)}")

def start_routine():
    today = dt.datetime.today()
    list_id = add_fake_account()
    add_fake_book(today, list_id)

    list_book = get_books(today.date())
    list_user = get_users([book.user_id for book in list_book])
    
    print(list_book)
    print(list_user)

    delete_fake_book(list_id)
    delete_fake_account(list_id)

def check_routine():
    today = dt.datetime.today() + dt.timedelta(days=9)
    list_id = add_fake_account()
    add_fake_book(today, list_id)
    print("do job")
    job()
    print("job done")

    delete_fake_book(list_id)
    delete_fake_account(list_id)

if __name__ == "__main__":
    # start_routine()
    check_routine()