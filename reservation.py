from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from typing import List
import time
import sys
import os
from ast import literal_eval
from argparse import ArgumentParser


sys.path.append(os.path.abspath('.'))

from config import Config
config = Config()

mois=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']

def compare_starts(best_start: WebElement, start_container: WebElement):
    time_str = str(start_container.find_element_by_xpath("div[1]").get_attribute("textContent")).replace(" ","").replace("\n","")
    start_horaire = datetime.strptime(time_str, "%H:%M")
    time_str = str(best_start.find_element_by_xpath("div[1]").get_attribute("textContent")).replace(" ","").replace("\n","")
    best_start_horaire = datetime.strptime(time_str, "%H:%M")
    
    if start_horaire.time() >= HORAIRE_DEB.time():
        if start_horaire.time() <= HORAIRE_FIN.time():
            if len(start_container.find_elements_by_xpath("div[2]/teesheet-slots/div/div")) >= 2 * NB_JOUEUR:
                best_time_delta = abs(datetime.combine(datetime.min.date(), best_start_horaire.time()) - datetime.combine(datetime.min.date(), HORAIRE.time()))
                time_delta = abs(datetime.combine(datetime.min.date(), start_horaire.time()) - datetime.combine(datetime.min.date(), HORAIRE.time()))
                if time_delta < best_time_delta:
                    best_start = start_container
    return best_start


#Expemple: python reservation.py --email 'cabotja@wanadoo.fr' --password '3Uslychien4' --golf 'UGOLF Toulouse La Ramée' --date '30-03-2022' --time_start '11:00' --time '12:00' --time_end '14:00' --players 'Regine #T CABOT' 'Player name'
"""Parse arguments."""
if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("--email", type=str, required=True, dest = "email", help = "Email de connexion.")
    parser.add_argument("--password", type=str, required=True, dest="password", help = "Mot de passe de connexion")
    parser.add_argument("--golf", type=str, required=True, dest="golf", help="Nom du parcours")
    parser.add_argument("--date", type=str, required=True, dest="date", help="Date de réservation")
    parser.add_argument("--time_start", type=str, required=True, dest="time_start", help="Horaire minimale de réservation")
    parser.add_argument("--time", type=str, required=True, dest="time", help="Horaire idéale de réservation")
    parser.add_argument("--time_end", type=str, required=True, dest="time_end", help="Horaire maximale de réservation")
    parser.add_argument("--players", nargs="*", type=str, required=False, default="[]", dest="players", help="Joueurs supplémentaires")
    args = parser.parse_args()

EMAIL = args.email
PASSWORD = args.password
GOLF = args.golf
DATE = datetime.strptime(args.date,"%d-%m-%Y")
HORAIRE = datetime.strptime(args.time, "%H:%M")
HORAIRE_DEB = datetime.strptime(args.time_start, "%H:%M")
HORAIRE_FIN = datetime.strptime(args.time_end, "%H:%M")
LISTE_JOUEURS = args.players
NB_JOUEUR = len(LISTE_JOUEURS) + 1


#Driver pour système d'exploitation à changer dans le fichier config.py
#Pour Linux 'geckodriver-v0.30.0-linux64/geckodriver'
#Pour Windows 'geckodriver-v0.30.0-win64/geckodriver.exe'
driver = Firefox(executable_path=config.DRIVER)

#Url du site
driver.get("https://www.chronogolf.fr/")

#Passer la page des cookies
driver.find_element_by_xpath("/html/body/cookie-law-banner/div/p/a[1]").click()

#Ouvrir la popup de connexion
driver.find_element_by_xpath('//*[@id="loginLink"]').click()

#Compléter et valider les informations de connexion
driver.find_element_by_xpath('//*[@id="sessionEmail"]').send_keys(EMAIL)
driver.find_element_by_xpath('//*[@id="sessionPassword"]').send_keys(PASSWORD)
driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/ng-switch/session-login/form/div[4]/input').click()

#Appuyer sur une nouvelle réservation
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div[1]/div[2]/button"))).click()

#Ouvrir la popup pour sélectionner le golf pour la nouvelle réservation
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div/affiliations-line/div/div[2]/div/button[1]"))).click()

#Mettre le nom du Golf dans la bar de recherche des golfs
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/club-selector-modal/div/app-page-body/app-search-input/input"))).send_keys(GOLF)

#Sélectionner le premier golf de la liste proposée suite à la recherche
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/club-selector-modal/div/div/div/organization-list-row/organization-logo/div/span"))).click()

#Ouvrir la popup du date picker 
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[1]/span"))).click()

#Ouvrir la sélection des mois du date picker
driver.find_element_by_xpath('/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/thead/tr[1]/th[2]/button').click()

#Ouvrir la sélection des années du date picker
driver.find_element_by_xpath('/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/thead/tr[1]/th[2]/button').click()

#Obtenir la liste de plusieurs années
years: List[WebElement] = driver.find_element_by_xpath('/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements_by_tag_name("span")

#Sélection de l'année
for year in years:
    if year.get_attribute('innerHTML') == str(DATE.year):
        year.click()
        break

#Obtenir la liste des mois de l'année
months: List[WebElement] = driver.find_element_by_xpath('/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements_by_tag_name("span")

#Sélection du mois
for month in months:
    if month.get_attribute('innerHTML') == mois[DATE.month-1]:
        month.click()
        break

#Obtenir la liste des jours du mois
days: List[WebElement] = driver.find_element_by_xpath('/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/teesheet-header/div/div/div/div[2]/ul/li/div/table/tbody').find_elements_by_tag_name("span")

#Sélection du jour
for day in days:
    if day.get_attribute('innerHTML') == str(DATE.strftime("%d")):
        day.click()
        break


#Chemin du tableau de réservation
path = '/html/body/div[2]/ui-view/div/div[2]/div[2]/club-teesheet/teesheet/div/teesheet-body/div[1]/div/teesheet-teetime/div'

#Attente jusqu'à la fin du chargement du tableau
WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,path)))
time.sleep(0.5)

#Le tableau se chargeant en le parcourant, je récupère ma liste, je scroll jusqu'à la fin de celle-ci, 
#je récupère de nouveau ma liste et je compare le dernier élément des deux listes, je réitère tant que les deux dernier éléments ne sont pas égaux
starts_containers: List[WebElement] = driver.find_elements_by_xpath(path)
old_starts_containers = [starts_containers[0]]
best_start = starts_containers[0]
    
while not starts_containers[-1] == old_starts_containers[-1]:
    j = len(old_starts_containers)
    for i in range(j,len(starts_containers)):
        driver.execute_script("arguments[0].scrollIntoView();", starts_containers[i])
        time.sleep(0.2)
        best_start = compare_starts(best_start, starts_containers[i])
    old_starts_containers = starts_containers.copy()
    starts_containers: List[WebElement] = driver.find_elements_by_xpath(path)

driver.execute_script("arguments[0].scrollIntoView();", best_start)
if config.DRY:
    print(str(best_start.find_element_by_xpath("div[1]").get_attribute("textContent")).replace(" ","").replace("\n",""))
path = f"div[2]/teesheet-slots/div/div[{NB_JOUEUR * 2 - 1}]"
best_start.find_element_by_xpath(path).click()

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/div/div/div/div[7]/div/div/button"))).click()

for i in range(len(LISTE_JOUEURS)):
    #Sélectionne la sous fenêtre pour inviter un golfeur
    path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/ul/li[{i+2}]/a/uib-tab-heading/div/span"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()
    #Entre le nom du golfeur pour le chercher dans la liste des golfeurs du site
    path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/input[1]"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).send_keys(LISTE_JOUEURS[i][:-1])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).send_keys(LISTE_JOUEURS[i][-1])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).send_keys(Keys.RETURN)
    #Appuie sur le nom du premier golfeur de la liste
    #path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div/div/ul/li/div[3]/a"
    #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,path))).click()
    path = f"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/editable-booking-rounds/div/div/div/div[{i+2}]/div/div/div/div[2]/div/div/div[2]/button"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,path))).click()

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[1]/reservation-review-terms/label/div/input"))).click()

if not config.DRY:
    driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div/div/div/div/div/div[1]/booking-confirmation/div/form/div[2]/div[2]/reservation-review-submit-button/button").click()

