from functools import lru_cache
from typing import List
import os

from cryptography.fernet import Fernet
from pydantic import BaseSettings

from app.core.security import Security

class APISettings(BaseSettings):
    
    ########################     Global information    ########################
    
    title: str = "golf-booking-api"
    contacts: str = "baptiste.u@gmail.com"

    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)

    ########################     Routes    ########################

    api_scheduler_route: str = "/api/scheduler"

    ########################     Security    ########################
    security = Security()
    fernet = security.fernet
    authjwt_secret_key: str = security.authjwt_secret_key
    authjwt_algorithm: str = security.authjwt_algorithm
    chronogolf_password: str = security.chronogolf_password
        
    ########################     path, driver, ...     ########################
    
    # driver = os.path.join(ROOT_DIR, 'geckodriver-v0.30.0-win64', 'geckodriver.exe')
    driver = os.path.join(ROOT_DIR, 'geckodriver-v0.32.0-macos', 'geckodriver')
    dry = True
    booking_dir = os.path.join(ROOT_DIR, 'bookings')
    templates_dir = os.path.join(ROOT_DIR, 'templates')
    static_dir = os.path.relpath(os.path.join(ROOT_DIR, 'static'), ROOT_DIR)

    ########################     Database     ########################

    database = os.path.join(ROOT_DIR, 'database', 'golf-booking-app.db')
    database_schema = os.path.join(ROOT_DIR, 'database', 'database.sql')

    ########################     Other params     ########################

    backend_cors_origins_str: str = ""  # Should be a comma-separated list of origins

    @property
    def backend_cors_origins(self) -> List[str]:
        return [x.strip() for x in self.backend_cors_origins_str.split(",") if x]


@lru_cache()
def get_api_settings() -> APISettings:
    """Init and return the API settings

    Returns:
        APISettings: The settings
    """
    return APISettings()  # reads variables from environment    