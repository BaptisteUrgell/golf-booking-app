from pydantic import BaseModel
import datetime as dt

class Book(BaseModel):
    id: int = None
    user_id: int
    email: str
    password: str
    golf: str 
    date: dt.date
    start_time: dt.time
    ideal_time: dt.time
    end_time: dt.time
    player2: str = None
    player3: str = None
    player4: str = None
    timestamp: dt.datetime = None

class Books(BaseModel):
    list_book: list[Book] = []