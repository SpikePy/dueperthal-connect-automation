###[ Imports ]##################################################################

import re          # regex
import requests    # REST calls
import credentials # import login credentials

# browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



###[ Configuration ]############################################################

debug = False
browser_size = [1280,1280] # windows size in pixels
browser_wait = 7           # seconds


###[ Functions ]################################################################

def get_data(cas_number):
    response = requests.get('https://commonchemistry.cas.org/api/detail?cas_rn=' + cas_number).json()

    name              = response["name"]
    molecular_formula = re.sub("</?sub>", "", response["molecularFormula"])
    molecular_mass    = re.search("^[0-9.-]*", response["molecularMass"]).group()
    boiling_point     = re.search("^[0-9.-]*", response["experimentalProperties"][0]["property"]).group()
    melting_point     = re.search("^[0-9.-]*", response["experimentalProperties"][1]["property"]).group()
    density           = re.search("^[0-9.-]*", response["experimentalProperties"][2]["property"]).group()
    synonyms          = response["synonyms"]

    # Determine phisycal state
    roomTemperature = 20 # Degree Celsius
    if float(melting_point) > roomTemperature:
        physical_state = "Solid"
    if float(boiling_point) < roomTemperature:
        physical_state = "Gas"
    if float(melting_point) < roomTemperature and float(boiling_point) > roomTemperature:
        physical_state = "Liquid"

    data = {
        "cas_number": cas_number,
        "name": name,
        "molecular_formula": molecular_formula,
        "molecular_mass": molecular_mass,
        "boiling_point": boiling_point,
        "melting_point": melting_point,
        "physical_state": physical_state,
        "density": density,
        "synonyms": synonyms
    }

    if debug == True:
        print(data)

    return data

def browser(data):
    
    # Browser Config
    options = Options()
    if debug == True:
        options.add_argument("log-level=2")
    else:
        options.add_argument("log-level=3")
    browser_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser_driver.set_window_size(browser_size[0],browser_size[1])
    browser_driver.implicitly_wait(browser_wait) # seconds

    # Login
    browser_driver.get("https://app.dueperthal-connect.com/login")
    browser_driver.find_element(By.XPATH,"//input[@type='email']").send_keys(credentials.login)
    browser_driver.find_element(By.XPATH,"//input[@type='password']").send_keys(credentials.password)
    browser_driver.find_element(By.XPATH,"//button[@type='submit']").click()
    browser_driver.find_element(By.XPATH,"//h1")

    # Item Catalog
    browser_driver.get("https://app.dueperthal-connect.com/en/substances/list")
    browser_driver.find_element(By.XPATH,"//button[@color='primary']").click()

    # Create Item
    browser_driver.find_element(By.XPATH,"//input[@formcontrolname='cas']").send_keys(data['cas_number'])
    browser_driver.find_element(By.XPATH,"//input[@formcontrolname='name']").send_keys(data['name'])
    browser_driver.find_element(By.XPATH,"//input[@formcontrolname='alias']").send_keys(data['synonyms'][0])
    browser_driver.find_element(By.XPATH,"//input[@formcontrolname='molecularWeight']").send_keys(data['molecular_mass'])
    browser_driver.find_element(By.XPATH,"//input[@formcontrolname='specificWeight']").send_keys(data['density'])
    browser_driver.find_element(By.XPATH,"//input[@value='" + data['physical_state'] + "']/..").click()

    input("\nTime to do some manual stuff. If you' re done press <ENTER>\n")

    browser_driver.close()


###[ Logic ]####################################################################

# input cas number and check for valid pattern
#cas_number = "67-64-1"
cas_number = input("CAS-Number: ")
if not re.fullmatch("[\d-]*",cas_number):
    print('Error: "' + cas_number + '"',"is no valid cas number")
    exit()

data = get_data(cas_number)
browser(data)

