import datetime as dt

from fastapi import Form, Depends, Header
from fastapi.routing import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse

from fastapi_jwt_auth import AuthJWT

from app.core.config import get_api_settings
from app.scripts.sql_tools import get_account, get_books, add_credit

settings = get_api_settings()
BOOK_DIR = settings.booking_dir
DRY = settings.dry
TEMPLATES_DIR = settings.templates_dir

Credit = APIRouter()

@Credit.get('/getCredit', response_class=JSONResponse)
async def get_credit(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user = await get_account(Authorize.get_jwt_subject())
    books = await get_books(user.id)
    response = {
        "credit": user.credit,
        "book": len(books)
    }
    return JSONResponse(content=response)

@Credit.post('/credit', response_class=PlainTextResponse)
async def get_credit(
    Authorize: AuthJWT = Depends(),
    x_csrf_token: str = Header(),
    credit: int = Form()):

    Authorize.jwt_required()
    if credit > 0:
        user = await get_account(Authorize.get_jwt_subject())
        await add_credit(user.id, credit)
    return "OK"