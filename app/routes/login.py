from datetime import timedelta

from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status, Form, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel

from fastapi_jwt_auth import AuthJWT

from app.core.config import get_api_settings
from app.scripts.sql_tools import get_account, create_account, AccountExist, AccountNotExist, WrongPassword
# from app.classes.user import User

from passlib.hash import bcrypt

settings = get_api_settings()
TEMPLATES_DIR = settings.templates_dir

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 120

OAuth2 = APIRouter()

class Settings(BaseModel):
    authjwt_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    authjwt_algorithm: str = 'HS256'
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    authjwt_cookie_samesite: str = 'lax'

@AuthJWT.load_config
def get_config():
    return Settings()

async def authenticate_user(email: str, password: str):
    user = await get_account(email)
    if not bcrypt.verify(password, user.hashed_password):
        raise WrongPassword
    return user


@OAuth2.post("/login", response_class=PlainTextResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), Authorize: AuthJWT = Depends(), token_expire: bool = Form(False)):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "JWT"},
        )

    access_token = Authorize.create_access_token(subject=user.email, expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    if token_expire:
        expires_time = None 
    else:
        expires_time = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = Authorize.create_refresh_token(subject=user.email, expires_time=expires_time)
    
    # Set the JWT and CSRF double submit cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    
    return "OK"


@OAuth2.post('/refresh', response_class=JSONResponse)
def refresh(Authorize: AuthJWT = Depends(), x_csrf_token: str = Header()):
    # print(x_csrf_token, type(x_csrf_token))
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    # Set the JWT and CSRF double submit cookies in the response
    Authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}


@OAuth2.delete('/logout', response_class=PlainTextResponse)
def logout(Authorize: AuthJWT = Depends(), x_csrf_token: str = Header()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookie in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return "OK"

@OAuth2.post('/signup', response_class=PlainTextResponse)
async def signup(
    email: str = Form(),
    password: str = Form(),
    ):

    try:
        if not await create_account(email=email, password=password):
            raise AccountNotExist
        response = "OK"
    except AccountExist as e:
        response = "L'adresse email est déjà utilisée."
    except AccountNotExist as e:
        response = "Le compte n'a pas été créé."
    return response
    # await create_account(email=email, password=password)
    # return 'ok'