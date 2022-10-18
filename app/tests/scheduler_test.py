import sys, os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
sys.path.append(SCRIPT_DIR)
from core.config import get_api_settings

settings = get_api_settings()
DRIVER = settings.driver

EMAIL = "cabotja@wanadoo.fr"

PASSWORD = "3Uslychien4"

GOLF = "UGOLF Toulouse La Ramée"

DATE = "2022-10-25"

HORAIRE = "12:00"

HORAIRE_DEB = "11:00"

HORAIRE_FIN = "13:00"

LISTE_JOUEURS = ["Regine #T CABOT"]

def test_page():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(service=FirefoxService(DRIVER), options=firefox_options)

    driver.get("http://127.0.0.1:8000/")

    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(EMAIL)

    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(PASSWORD)

    driver.find_element(By.XPATH, '//*[@id="golf"]').send_keys(GOLF)

    driver.find_element(By.XPATH, '//*[@id="date"]').send_keys(DATE)

    driver.find_element(By.XPATH, '//*[@id="time_start"]').send_keys(HORAIRE_DEB)

    driver.find_element(By.XPATH, '//*[@id="time"]').send_keys(HORAIRE)

    driver.find_element(By.XPATH, '//*[@id="time_end"]').send_keys(HORAIRE_FIN)

    driver.find_element(By.XPATH, '//*[@id="player_2"]').send_keys(LISTE_JOUEURS[0])

    submit = driver.find_element(By.XPATH, '//*[@id="submit"]')

    driver.execute_script("arguments[0].scrollIntoView();", submit)

    submit.click()

    driver.close()

if __name__ == "__main__":
    test_page()
