import os
import sys
import shlex
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
sys.path.append(os.path.abspath('.'))
from config import Config

config = Config()
app = Flask("Réservation golf")

book: dict = {
    "email" : "cabotja@wanadoo.fr",
    "password" : "3Uslychien4",
    "golf" : "UGOLF Toulouse La Ramée",
    "date" : datetime.strptime("04/03/2022","%d/%m/%Y"),
    "time" : datetime.strptime("12:00", "%H:%M"),
    "time_start" : datetime.strptime("11:00", "%H:%M"),
    "time_end" : datetime.strptime("17:00", "%H:%M"),
    "list_players" : ["Regine #T CABOT"]
}

def get_date_format()->str:
    date_format = "%Y-%m-%d"
    date_format = "%m/%d/%Y"
    return date_format

def form2book(form: dict)->dict:
    book = form.copy()
    book["date"] = datetime.strptime(form["date"],"%Y-%m-%d")
    book["time"] = datetime.strptime(form["time"], "%H:%M")
    book["time_start"] = datetime.strptime(form["time_start"], "%H:%M")
    book["time_end"] = datetime.strptime(form["time_end"], "%H:%M")
    
    book["list_players"] = []
    for i in range(2,int(form["nb_players"])+1):
        book["list_players"].append(form[f"player_{i}"])
    
    return book

def get_task_date(book_date: datetime, date_format: str)->str:
    date = book_date - timedelta(days=9)
    return date.strftime(date_format)

# def create_task_path(date: datetime)->str:
#     path = os.path.abspath("./reservations")
#     task_path = os.path.join(path, date.strftime('%Y'), date.strftime('%m'), date.strftime('%d'))
#     if not os.path.exists(task_path):
#         os.makedirs(task_path)
#     return task_path
        
def create_task_action(book: dict)->str:
    path = os.path.abspath("python-3.8.10-embed-amd64\python")
    email = shlex.quote(book['email'])
    password = shlex.quote(book['password'])
    golf = shlex.quote(book['golf'])
    date = shlex.quote(book['date'].strftime('%d-%m-%Y'))
    time = shlex.quote(book['time'].strftime('%H:%M'))
    time_start = shlex.quote(book['time_start'].strftime('%H:%M'))
    time_end = shlex.quote(book['time_end'].strftime('%H:%M'))
    players = " ".join([shlex.quote(player) for player in book['list_players']])
    script_path = os.path.abspath('reservation.py')
    
    action = f"{path} {script_path} --email {email} --password {password} --golf {golf} --date {date} --time {time} --time_start {time_start} --time_end {time_end} --players {players} "
    return action

def create_task_bat(directory: str, file: str, content: str)->str:
    file = os.path.join(directory, f"{file}.bat")
    
    with open(file, "w", encoding='utf-8') as f:
        f.write(content)
    
    return file

user_message = None
alert = None

@app.post('/book')
def schedule_task():
    global user_message, alert
    user_message = None
    alert = None
    
    #try:
    list_inputs = ["email","password","golf","date","time_start","time","time_end","nb_players"]
    form_completed = True
    
    for input in list_inputs:
        if not input in request.form:
            form_completed = False
            
    if form_completed:
        task_name = f"booking_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        date_format = get_date_format()
        book = form2book(request.form)
        task_date = get_task_date(book['date'], date_format)
        # task_path = create_task_path(book['date'])
        task_action = create_task_action(book)
        # task_bat = create_task_bat(task_path, task_name, task_action)
        task_bat = create_task_bat(config.PATH_TASK, task_name, task_action)
                
        task = f'schtasks /create /tn {task_name} /tr {task_bat} /sc once /sd {task_date} /st 08:00 /ru "STUDENT-LAPTOP\Administrator" /rp "igoov4JaKoow" /z /V1'
        
        if config.DRY:
            print(task)
        
        os.system(task)
        user_message = "La réservation a été prise en compte."
        alert = True
    else:
        user_message = "Formulaire incomplet, la réservation n'a pas été prise en compte."
        alert = False
    """except Exception as e:
        print(e)
        user_message = "Une erreur est survenue, la réservation n'a pas été prise en compte."
        alert = False"""
    return redirect("/")


@app.route('/')
def root():
    return render_template('index.html', user_message=user_message, alert=alert)

@app.post('/shutdown')
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running werkzeug')
    shutdown_func()
    return "Application éteinte. Bon golf !"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
