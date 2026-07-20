from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# chrome_options = webdriver.ChromeOptions()    
# # Adding options to run in headless mode (old) and disable notifications.
# options = [
#    "--headless",
#    "--disable-notifications"
# ]

# for option in options:
#     chrome_options.add_argument(option)

# # creating driver
# driver = webdriver.Chrome(options = chrome_options)

def create_driver():
    chrome_options = webdriver.ChromeOptions()    
    # Adding options to run in headless mode (old) and disable notifications.
    options = [
    "--headless",
    "--disable-notifications"
    ]

    for option in options:
        chrome_options.add_argument(option)

    # creating driver
    driver = webdriver.Chrome(options = chrome_options)
    # driver.set_page_load_timeout(60)
    return driver
