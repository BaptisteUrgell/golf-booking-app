from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

EMAIL = "cabotja@wanadoo.fr"

PASSWORD = "3Uslychien4"

GOLF = "UGOLF Toulouse La Ramée"

DATE = "2022-10-30"

HORAIRE = "12:00"

HORAIRE_DEB = "11:00"

HORAIRE_FIN = "13:00"

LISTE_JOUEURS = ["Regine #T CABOT"]

driver = Firefox(executable_path='geckodriver-v0.30.0-win64\geckodriver.exe')

driver.get("http://127.0.0.1:8080/")

driver.find_element_by_xpath('//*[@id="email"]').send_keys(EMAIL)

driver.find_element_by_xpath('//*[@id="password"]').send_keys(PASSWORD)

driver.find_element_by_xpath('//*[@id="golf"]').send_keys(GOLF)

driver.find_element_by_xpath('//*[@id="date"]').send_keys(DATE)

driver.find_element_by_xpath('//*[@id="time_start"]').send_keys(HORAIRE_DEB)

driver.find_element_by_xpath('//*[@id="time"]').send_keys(HORAIRE)

driver.find_element_by_xpath('//*[@id="time_end"]').send_keys(HORAIRE_FIN)

driver.find_element(By.XPATH,'//*[@id="nb_players"]').send_keys(Keys.ARROW_UP)

element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="input_player_2"]')))

submit = driver.find_element_by_xpath('//*[@id="submit"]')

driver.execute_script("arguments[0].scrollIntoView();", submit)

element.send_keys(LISTE_JOUEURS[0])

submit.click()

driver.close()

