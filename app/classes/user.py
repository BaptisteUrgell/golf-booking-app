from pydantic import BaseModel
import datetime as dt

class User(BaseModel):
    id: int
    email: str
    hashed_password: str
    credit: int
    timestamp: dt.datetime