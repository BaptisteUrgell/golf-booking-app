#############################################################################################################################################################
#                                                                                                                                                           #
#    /$$$$$$   /$$$$$$  /$$       /$$$$$$$$      /$$$$$$$   /$$$$$$   /$$$$$$  /$$   /$$ /$$$$$$ /$$   /$$  /$$$$$$           /$$$$$$  /$$$$$$$  /$$$$$$$   #
#   /$$__  $$ /$$__  $$| $$      | $$_____/     | $$__  $$ /$$__  $$ /$$__  $$| $$  /$$/|_  $$_/| $$$ | $$ /$$__  $$         /$$__  $$| $$__  $$| $$__  $$  #
#  | $$  \__/| $$  \ $$| $$      | $$           | $$  \ $$| $$  \ $$| $$  \ $$| $$ /$$/   | $$  | $$$$| $$| $$  \__/        | $$  \ $$| $$  \ $$| $$  \ $$  #
#  | $$ /$$$$| $$  | $$| $$      | $$$$$ /$$$$$$| $$$$$$$ | $$  | $$| $$  | $$| $$$$$/    | $$  | $$ $$ $$| $$ /$$$$ /$$$$$$| $$$$$$$$| $$$$$$$/| $$$$$$$/  #
#  | $$|_  $$| $$  | $$| $$      | $$__/|______/| $$__  $$| $$  | $$| $$  | $$| $$  $$    | $$  | $$  $$$$| $$|_  $$|______/| $$__  $$| $$____/ | $$____/   #
#  | $$  \ $$| $$  | $$| $$      | $$           | $$  \ $$| $$  | $$| $$  | $$| $$\  $$   | $$  | $$\  $$$| $$  \ $$        | $$  | $$| $$      | $$        #
#  |  $$$$$$/|  $$$$$$/| $$$$$$$$| $$           | $$$$$$$/|  $$$$$$/|  $$$$$$/| $$ \  $$ /$$$$$$| $$ \  $$|  $$$$$$/        | $$  | $$| $$      | $$        #
#   \______/  \______/ |________/|__/           |_______/  \______/  \______/ |__/  \__/|______/|__/  \__/ \______/         |__/  |__/|__/      |__/        #
#                                                                                                                                                           #
#############################################################################################################################################################
                                                                                                                                                       

import os

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

from fastapi_jwt_auth import AuthJWT

from .core.config import get_api_settings
from .routes.receptionist import Receptionist
from .routes.credit import Credit
from .routes.login import OAuth2
from .classes.sqlite import SQLite


settings = get_api_settings()
TITLE = settings.title
CONTACTS = settings.contacts
URL_DOC = settings.redoc_url
URL_SWAGGER = settings.docs_url
STATICS_DIR = settings.static_dir
TEMPLATES_DIR = settings.templates_dir
DATABASE = settings.database
DATABASE_SHEMA = settings.database_shema

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def init_db():
    if not os.path.exists(DATABASE):
        print("not ok")
        with SQLite(DATABASE) as db:
            with open(DATABASE_SHEMA, mode='r') as f:
                db.executescript(f.read())

app = FastAPI(
    title = TITLE,
    contacts = CONTACTS,
    redoc_url = URL_DOC,
    docs_url = URL_SWAGGER
)

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")

app.include_router(OAuth2)
app.include_router(Receptionist)
app.include_router(Credit)


@app.get('/', response_class=HTMLResponse)
async def check_connexion(request: Request, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return templates.TemplateResponse("index.html", context={'request': request})
    except Exception as e:
        return templates.TemplateResponse("login.html", context={'request': request})
    


@app.get('/info')
async def about() -> dict[str, str]:
    """Give information about the API.

    Returns:
        dict[str, str]: With shape :
    `
    {"app_title": <TITLE>, "app_contacts": <CONTACTS>, "api_url_doc": <URL_DOC>, "api_url_swagger": <URL_SWAGGER>}
    `
    """
    return {
        "app_title": TITLE,
        "app_contacts": CONTACTS,
        "api_url_doc": URL_DOC,
        "api_url_swagger": URL_SWAGGER
    }
