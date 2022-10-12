import os

# SECRET_KEY = '6d3fe3baf328668440ccf6d3e51bb3fb9186ebd14272ed65161920655c01c0f3'

class Config:
    def __init__(self) -> None:
        pass
    
    DRIVER = os.path.abspath('geckodriver-v0.30.0-win64/geckodriver.exe')
    DRY = True
    PATH_TASK = os.path.abspath('bookings')