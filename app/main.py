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
                                                                                                                                                       
                                                                                                                                                       

from typing import Dict
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .core.config import get_api_settings
from .routes.scheduler import SchedulerRouter

settings = get_api_settings()
TITLE = settings.title
CONTACTS = settings.contacts
URL_DOC = settings.redoc_url
URL_SWAGGER = settings.docs_url
STATICS_DIR = settings.static_dir


app = FastAPI(
    title = TITLE,
    contacts = CONTACTS,
    redoc_url = URL_DOC,
    docs_url = URL_SWAGGER
)

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
app.include_router(SchedulerRouter)

@app.get('/')
async def about() -> Dict[str, str]:
    """Give information about the API.

    Returns:
        Dict[str, str]: With shape :
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
