###[ Imports ]##################################################################

import os  # basic os functions
import re  # regex
import requests  # REST calls

# browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


###[ Configuration ]############################################################

filename_credentials = "credentials.py"
url_cas_api = "https://commonchemistry.cas.org/api/detail?cas_rn="
url_dueperthal_base = "https://app.dueperthal-connect.com"
debug = False
browser_size = [1280, 1280]  # windows size in pixels
browser_wait = 3  # seconds
cas_number_regex = "[\d]+-[\d]+-[\d]+"


###[ Constatns ]################################################################

# cas test numbers
cas_number = "67-64-1"  # valid cas number, but exists already
# cas_number = "64-17-5" # valid cas number, not existing yet
# cas_number = "67-64-2" # valid pattern but does not exist
# cas_number = "abc"     # invalid pattern

###[ Functions ]################################################################


def get_dueperthal_credentials():
    if not os.path.isfile(filename_credentials):
        print("Düpertal-Connect App Credentials")
        print("================================")
        login = input("E-Mail: ")
        password = input("Password: ")

        lines = ['login = "' + login + '"', 'password = "' + password + '"']
        with open(filename_credentials, "w") as file:
            for line in lines:
                file.write(line)
                file.write("\n")
    import credentials  # has to be basename of the credential file without file extension

    return credentials


def get_cas_number():

    # if cas_number is already defined as a global variable in script
    # use that one and don't ask for another
    try:
        cas_number_local = cas_number
    except:
        cas_number_local = "none"

    if cas_number_local != "none":
        if re.fullmatch(cas_number_regex, cas_number_local):
            return cas_number_local
        else:
            print('Error: "' + cas_number_local + '"', "is no valid cas number.")
            cas_number_valid = False
    else:
        cas_number_valid = False

    while not cas_number_valid:
        cas_number_local = input("CAS-Number: ")

        # check if cas number has a valid pattern
        if re.fullmatch(cas_number_regex, cas_number_local):
            return cas_number_local
        else:
            print('Error: "' + cas_number_local + '"', "is no valid cas number.")


def get_data(cas_number_local):
    response = requests.get(url_cas_api + cas_number_local)

    if debug:
        print(response)

    while response.status_code != 200:
        print('\nCAS number "' + cas_number_local + '" not found via API.')
        global cas_number
        del cas_number
        cas_number_local = get_cas_number()
        response = requests.get(url_cas_api + cas_number_local)

    response = response.json()

    name = response["name"]
    molecular_formula = re.sub("</?sub>", "", response["molecularFormula"])
    molecular_mass = re.search("^[0-9.-]*", response["molecularMass"]).group()
    boiling_point = re.search(
        "^[0-9.-]*", response["experimentalProperties"][0]["property"]
    ).group()
    melting_point = re.search(
        "^[0-9.-]*", response["experimentalProperties"][1]["property"]
    ).group()
    density = re.search(
        "^[0-9.-]*", response["experimentalProperties"][2]["property"]
    ).group()
    synonyms = response["synonyms"]

    # Determine phisycal state
    roomTemperature = 20  # Degree Celsius
    if float(melting_point) > roomTemperature:
        physical_state = "Solid"
    if float(boiling_point) < roomTemperature:
        physical_state = "Gas"
    if (
        float(melting_point) < roomTemperature
        and float(boiling_point) > roomTemperature
    ):
        physical_state = "Liquid"

    data = {
        "cas_number": cas_number_local,
        "name": name,
        "molecular_formula": molecular_formula,
        "molecular_mass": molecular_mass,
        "boiling_point": boiling_point,
        "melting_point": melting_point,
        "physical_state": physical_state,
        "density": density,
        "synonyms": synonyms,
    }

    if debug:
        print(data)

    return data


def browser(data):

    # Browser Config
    options = Options()
    if debug:
        options.add_argument("log-level=2")
    else:
        options.add_argument("log-level=3")
    browser_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browser_driver.set_window_size(browser_size[0], browser_size[1])
    browser_driver.implicitly_wait(browser_wait)  # seconds

    # Login
    browser_driver.get(url_dueperthal_base + "/login")
    browser_driver.find_element(By.XPATH, "//input[@type='email']").send_keys(
        credentials.login
    )
    browser_driver.find_element(By.XPATH, "//input[@type='password']").send_keys(
        credentials.password
    )
    browser_driver.find_element(By.XPATH, "//button[@type='submit']").click()
    browser_driver.find_element(By.XPATH, "//h1")

    # Item Catalog
    browser_driver.get(url_dueperthal_base + "/en/substances/list")
    browser_driver.find_element(By.XPATH, "//input").send_keys(data["name"])

    # Test if item already exists
    number_items = len(
        browser_driver.find_elements(By.XPATH, "//button//mat-icon[text()='delete']")
    )
    if number_items != 0:
        input("\nItem already exists.\nPress <ENTER> to exit.\n")
        quit()

    # Create Item
    browser_driver.find_element(By.XPATH, "//button[@color='primary']").click()
    browser_driver.find_element(By.XPATH, "//input[@formcontrolname='cas']").send_keys(
        data["cas_number"]
    )
    browser_driver.find_element(By.XPATH, "//input[@formcontrolname='name']").send_keys(
        data["name"]
    )
    browser_driver.find_element(
        By.XPATH, "//input[@formcontrolname='alias']"
    ).send_keys(data["synonyms"][0])
    browser_driver.find_element(
        By.XPATH, "//input[@formcontrolname='molecularWeight']"
    ).send_keys(data["molecular_mass"])
    browser_driver.find_element(
        By.XPATH, "//input[@formcontrolname='specificWeight']"
    ).send_keys(data["density"])
    browser_driver.find_element(
        By.XPATH, "//input[@value='" + data["physical_state"] + "']/.."
    ).click()

    input("\nTime to do some manual stuff. If you' re done press <ENTER>\n")

    browser_driver.close()


###[ Script ]###################################################################

script_dir = os.path.dirname(__file__)
os.chdir(script_dir)

credentials = get_dueperthal_credentials()
cas_number = get_cas_number()
data = get_data(cas_number)
browser(data)
