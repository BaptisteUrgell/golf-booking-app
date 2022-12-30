import datetime as dt

from fastapi import Form, Depends, Header
from fastapi.routing import APIRouter
from fastapi.responses import PlainTextResponse

from fastapi_jwt_auth import AuthJWT

from app.core.config import get_api_settings
# from app.scripts.assignment import schedule_books
from app.scripts.sql_tools import insert_book, get_account, get_books, disable_book
# from app.classes.user import User
from app.classes.book import Book

settings = get_api_settings()
BOOK_DIR = settings.booking_dir
DRY = settings.dry

Receptionist = APIRouter()

@Receptionist.post('/book', response_class=PlainTextResponse)
async def create_book(
    Authorize: AuthJWT = Depends(),
    x_csrf_token: str = Header(),
    email: str = Form(), 
    password: str = Form(), 
    golf: str = Form(), 
    date: dt.date = Form(),
    time_start: dt.time = Form(),
    time: dt.time = Form(), 
    time_end: dt.time = Form(), 
    player_2: str = Form(None),
    player_3: str = Form(None),
    player_4: str = Form(None)):
    
    # if DRY:
    #     print(email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4)
    # try:
    Authorize.jwt_required()
    user = await get_account(Authorize.get_jwt_subject())

    book = Book(
        user_id = user.id,
        email = email,
        password = password, 
        golf = golf, 
        date = date, 
        start_time = time_start, 
        ideal_time = time, 
        end_time = time_end,
        player2 = player_2, 
        player3 = player_3, 
        player4 = player_4)

    await insert_book(book)
    user_message = "OK"
    # except Exception as e:
    #     print(e)
    #     user_message = "Une erreur est survenue veillez réessayer"
    return user_message

@Receptionist.get('/getbooks', response_model=list[Book])
async def retrieve_books(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user = await get_account(Authorize.get_jwt_subject())
    books = await get_books(user.id)
    return books

@Receptionist.post('/disablebook', response_class=PlainTextResponse)
async def disable_book_request(
    Authorize: AuthJWT = Depends(), 
    x_csrf_token: str = Header(),
    id: int = Form()):

    Authorize.jwt_required()
    if await disable_book(id):
        response = "OK"
    else:
        response = "ECHEC"
    return response