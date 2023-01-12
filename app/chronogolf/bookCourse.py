from threading import Thread
from time import sleep
import datetime as dt
from datetime import datetime
import os, sys

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

from app.classes.book import Book

class BookCourse(Thread):
    def __init__(self, dry, driver_path, book: Book):
        Thread.__init__(self)
        self.dry: bool = dry
        self.driver_path: str = driver_path
        self.email: str = book.email
        self.password: str = book.password
        self.golf: str = book.golf
        self.date: dt.date = book.date
        self.time_start: dt.time = book.start_time
        self.time_perfect: dt.time = book.ideal_time
        self.time_end: dt.time = book.end_time
        self.list_players: list[str] = [player for player in [book.player2, book.player3, book.player4] if player]
        self.nb_players: int = len(self.list_players) + 1
   
    def run(self):
        mois=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']

        def send_keys_delay(controller,keys):
            for key in keys:
                controller.send_keys(key)
                sleep(0.1)

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

        #Driver pour système d'exploitation à changer dans le fichier config.py
        #Pour Linux 'geckodriver-v0.30.0-linux64/geckodriver'
        #Pour Windows 'geckodriver-v0.30.0-win64/geckodriver.exe'
        firefox_options = Options()
        if not self.dry:
            firefox_options.add_argument("--headless")
        driver = Firefox(service=FirefoxService(self.driver_path), options=firefox_options)


        #Url du site
        driver.get("https://www.chronogolf.fr/")

        #Passer la page des cookies
        driver.find_element(By.XPATH, "/html/body/cookie-law-banner/div/p/a[1]").click()

        #Ouvrir la popup de connexion
        driver.find_element(By.XPATH, '//*[@id="loginLink"]').click()

        #Compléter et valider les informations de connexion
        driver.find_element(By.XPATH, '//*[@id="sessionEmail"]').send_keys(self.email)
        driver.find_element(By.XPATH, '//*[@id="sessionPassword"]').send_keys(self.password)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/ng-switch/session-login/form/div[4]/input').click()

        #Appuyer sur une nouvelle réservation
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div[1]/div[2]/button"))).click()

        #Ouvrir la popup pour sélectionner le golf pour la nouvelle réservation
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div/affiliations-line/div/div[2]/div/button[1]"))).click()

        #Mettre le nom du Golf dans la bar de recherche des golfs
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/club-selector-modal/div/app-page-body/app-search-input/input"))).send_keys(self.golf)

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
            if year.get_attribute('innerHTML') == str(self.date.year):
                year.click()
                break

        #Obtenir la liste des mois de l'année
        months: list[WebElement] = driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements(By.TAG_NAME, "span")

        #Sélection du mois
        for month in months:
            if month.get_attribute('innerHTML') == mois[self.date.month-1]:
                month.click()
                break

        #Obtenir la liste des jours du mois
        days: list[WebElement] = driver.find_element(By.XPATH, '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements(By.TAG_NAME, "span")

        #Sélection du jour
        for day in days:
            if day.get_attribute('innerHTML') == str(self.date.strftime("%d")):
                day.click()
                break


        #Chemin du tableau de réservation
        path = '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/div/teesheet-body/div[1]/div/teesheet-teetime/div'

        #Attente jusqu'à la fin du chargement du tableau
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, path)))
        sleep(0.5)

        #Le tableau se chargeant en le parcourant, je récupère ma liste, je scroll jusqu'à la fin de celle-ci, 
        #je récupère de nouveau ma liste et je compare le dernier élément des deux listes, je réitère tant que les deux dernier éléments ne sont pas égaux
        starts_containers: list[WebElement] = driver.find_elements(By.XPATH, path)
        old_starts_containers = [starts_containers[0]]
        best_start = None
            
        while not starts_containers[-1] == old_starts_containers[-1]:
            j = len(old_starts_containers)
            for i in range(j,len(starts_containers)):
                driver.execute_script("arguments[0].scrollIntoView();", starts_containers[i])
                sleep(0.2)
                best_start = compare_starts(best_start, starts_containers[i], self.time_start, self.time_end, self.time_perfect, self.nb_players)
            old_starts_containers = starts_containers.copy()
            starts_containers: list[WebElement] = driver.find_elements(By.XPATH, path)

        driver.execute_script("arguments[0].scrollIntoView();", best_start)
        if self.dry:
            print(str(best_start.find_element(By.XPATH, "div[1]").get_attribute("textContent")).replace(" ","").replace("\n",""))
        path = f"div[2]/teesheet-slots/div/div[{self.nb_players * 2 - 1}]"
        best_start.find_element(By.XPATH, path).click()

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/div/div/div/div[7]/div/div/button"))).click()

        for i in range(len(self.list_players)):
            #Sélectionne la sous fenêtre pour inviter un golfeur
            path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/ul/li[{i+2}]/a/uib-tab-heading/div/span"
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()
            #Entre le nom du golfeur pour le chercher dans la liste des golfeurs du site
            path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/input[1]"
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()
            send_keys_delay(WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))), self.list_players[i])
            sleep(5)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()

            # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).send_keys(Keys.RETURN)
            #Appuie sur le nom du premier golfeur de la liste
            path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/ul/li/div[3]/a"
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,path))).click()
            path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div[2]/div/div/div[2]/button"
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[1]/reservation-review-terms/label/div/input"))).click()

        if not self.dry:
            driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[2]/reservation-review-submit-button/button").click()
            driver.close()

