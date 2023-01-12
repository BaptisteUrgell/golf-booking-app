import asyncio
import datetime as dt
import time
from datetime import datetime, timedelta
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import get_api_settings

settings = get_api_settings()
DRY = settings.dry
DRIVER = settings.driver

mois=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']

def send_keys_delay(controller,keys):
    for key in keys:
        controller.send_keys(key)
        time.sleep(0.1)

def compare_starts(best_start: WebElement, start_container: WebElement, time_start: dt.time, time_end: dt.time, time_perfect: dt.time, nb_players: int):
    time_str = str(start_container.find_element(By.XPATH, "div[1]").get_attribute("textContent")).replace(" ","").replace("\n","")
    start_horaire = datetime.strptime(time_str, "%H:%M")
    test = None 
    if (start_horaire.time() >= time_start) and (start_horaire.time() <= time_end):
        test = start_container.get_attribute("class")
        if start_container.get_attribute("class") == 'teesheet-teetime ':
            if len(start_container.find_elements(By.XPATH, "div[2]/teesheet-slots/div/div")) >= 2 * nb_players:
                if best_start is None:
                    return start_container
                time_str = str(best_start.find_element(By.XPATH, "div[1]").get_attribute("textContent")).replace(" ","").replace("\n","")
                best_start_horaire = datetime.strptime(time_str, "%H:%M")
            
                best_time_delta = abs(datetime.combine(datetime.min.date(), best_start_horaire.time()) - datetime.combine(datetime.min.date(), time_perfect))
                time_delta = abs(datetime.combine(datetime.min.date(), start_horaire.time()) - datetime.combine(datetime.min.date(), time_perfect))
                if time_delta < best_time_delta:
                    best_start = start_container
    return best_start

async def make_book(email, password, golf, date, time_start, time_perfect, time_end, nb_players, list_players):
    #Driver pour système d'exploitation à changer dans le fichier config.py
    #Pour Linux 'geckodriver-v0.30.0-linux64/geckodriver'
    #Pour Windows 'geckodriver-v0.30.0-win64/geckodriver.exe'
    firefox_options = Options()
    if not DRY:
        firefox_options.add_argument("--headless")
    driver = Firefox(service=FirefoxService(DRIVER), options=firefox_options)


    #Url du site
    driver.get("https://www.chronogolf.fr/")

    #Passer la page des cookies
    driver.find_element(By.XPATH, "/html/body/cookie-law-banner/div/p/a[1]").click()

    #Ouvrir la popup de connexion
    driver.find_element(By.XPATH, '//*[@id="loginLink"]').click()

    #Compléter et valider les informations de connexion
    driver.find_element(By.XPATH, '//*[@id="sessionEmail"]').send_keys(email)
    driver.find_element(By.XPATH, '//*[@id="sessionPassword"]').send_keys(password)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/ng-switch/session-login/form/div[4]/input').click()

    #Appuyer sur une nouvelle réservation
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div[1]/div[2]/button"))).click()

    #Ouvrir la popup pour sélectionner le golf pour la nouvelle réservation
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div/affiliations-line/div/div[2]/div/button[1]"))).click()

    #Mettre le nom du Golf dans la bar de recherche des golfs
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/club-selector-modal/div/app-page-body/app-search-input/input"))).send_keys(golf)

    #Sélectionner le premier golf de la liste proposée suite à la recherche
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/club-selector-modal/div/div/div/organization-list-row/organization-logo/div/span"))).click()

    #Ouvrir la popup du date picker 
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[1]/span"))).click()

    #Ouvrir la sélection des mois du date picker
    driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/thead/tr[1]/th[2]/button').click()

    #Ouvrir la sélection des années du date picker
    driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/thead/tr[1]/th[2]/button').click()

    #Obtenir la liste de plusieurs années
    years: list[WebElement] = driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements(By.TAG_NAME, "span")

    #Sélection de l'année
    for year in years:
        if year.get_attribute('innerHTML') == str(date.year):
            year.click()
            break

    #Obtenir la liste des mois de l'année
    months: list[WebElement] = driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements(By.TAG_NAME, "span")

    #Sélection du mois
    for month in months:
        if month.get_attribute('innerHTML') == mois[date.month-1]:
            month.click()
            break

    #Obtenir la liste des jours du mois
    days: list[WebElement] = driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements(By.TAG_NAME, "span")

    #Sélection du jour
    for day in days:
        if day.get_attribute('innerHTML') == str(date.strftime("%d")):
            day.click()
            break


    #Chemin du tableau de réservation
    path = '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/div/teesheet-body/div[1]/div/teesheet-teetime/div'

    #Attente jusqu'à la fin du chargement du tableau
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, path)))
    await asyncio.sleep(0.5)

    #Le tableau se chargeant en le parcourant, je récupère ma liste, je scroll jusqu'à la fin de celle-ci, 
    #je récupère de nouveau ma liste et je compare le dernier élément des deux listes, je réitère tant que les deux dernier éléments ne sont pas égaux
    starts_containers: list[WebElement] = driver.find_elements(By.XPATH, path)
    old_starts_containers = [starts_containers[0]]
    best_start = None
        
    while not starts_containers[-1] == old_starts_containers[-1]:
        j = len(old_starts_containers)
        for i in range(j,len(starts_containers)):
            driver.execute_script("arguments[0].scrollIntoView();", starts_containers[i])
            await asyncio.sleep(0.2)
            best_start = compare_starts(best_start, starts_containers[i], time_start, time_end, time_perfect, nb_players)
        old_starts_containers = starts_containers.copy()
        starts_containers: list[WebElement] = driver.find_elements(By.XPATH, path)

    driver.execute_script("arguments[0].scrollIntoView();", best_start)
    if DRY:
        print(str(best_start.find_element(By.XPATH, "div[1]").get_attribute("textContent")).replace(" ","").replace("\n",""))
    path = f"div[2]/teesheet-slots/div/div[{nb_players * 2 - 1}]"
    best_start.find_element(By.XPATH, path).click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/div/div/div/div[7]/div/div/button"))).click()

    for i in range(len(list_players)):
        #Sélectionne la sous fenêtre pour inviter un golfeur
        path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/ul/li[{i+2}]/a/uib-tab-heading/div/span"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()
        #Entre le nom du golfeur pour le chercher dans la liste des golfeurs du site
        path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/input[1]"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()
        send_keys_delay(WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))), list_players[i])
        time.sleep(5)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()

        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).send_keys(Keys.RETURN)
        #Appuie sur le nom du premier golfeur de la liste
        path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/ul/li/div[3]/a"
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,path))).click()
        path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div[2]/div/div/div[2]/button"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[1]/reservation-review-terms/label/div/input"))).click()

    if not DRY:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[2]/reservation-review-submit-button/button").click()
        driver.close()




async def schedule_books(email, password, golf, date, time_start, time, time_end, player_2, player_3, player_4):
    date = datetime.combine(date, dt.time(8))
    waiting_time = date - timedelta(days=9) - datetime.now()

    if not DRY:
        await asyncio.sleep(waiting_time.total_seconds())
    list_players = [player for player in [player_2, player_3, player_4] if not player is None]
    nb_players = len(list_players) + 1
    await make_book(email, password, golf, date, time_start, time, time_end, nb_players, list_players)
    