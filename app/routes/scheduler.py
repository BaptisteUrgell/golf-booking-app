import datetime as dt
from urllib.request import Request
from fastapi import Form, Request, BackgroundTasks
from fastapi.routing import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from core.config import get_api_settings
from scripts.assignment import schedule_books

settings = get_api_settings()
BOOK_DIR = settings.booking_dir
DRY = settings.dry
TEMPLATES_DIR = settings.templates_dir
SchedulerRouter = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


user_message = None
alert = None

@SchedulerRouter.post('/book', response_class=RedirectResponse)
async def schedule_task(
    background_tasks: BackgroundTasks,
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

    global user_message, alert
    user_message = None
    alert = None

    # task_name = f"booking_{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    # date_format = get_date_format()
    # book = form2book(email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4)
    # task_date = get_task_date(book['date'], date_format)
    # task_date = get_task_date(date, date_format)
    # task_path = create_task_path(book['date'])
    # task_action = create_task_action(email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4)
    # task_bat = create_task_bat(task_path, task_name, task_action)
    # task_bat = create_task_bat(BOOK_DIR, task_name, task_action)

    background_tasks.add_task(schedule_books, email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4)
    # task = f'schtasks /create /tn {task_name} /tr {task_bat} /sc once /sd {task_date} /st 08:00 /ru "STUDENT-LAPTOP\Administrator" /rp "igoov4JaKoow" /z /V1'
    
    if DRY:
        print(email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4)

    # os.system(task)
    user_message = "La réservation a été prise en compte."
    alert = True
    response = RedirectResponse(url="/")
    response.status_code = 302
    return response

@SchedulerRouter.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'user_message': user_message, 'alert': alert})
