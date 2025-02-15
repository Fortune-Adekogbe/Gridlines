import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import random
from db_setup import *
from selenium_setup import *

url = "https://www.useragents.me/" # "https://www.useragentlist.net/"

try:
    request = requests.get(url)
    user_agents = []
    soup = BeautifulSoup(request.text, "html.parser")
    for user_agent in soup.select("textarea.form-control.ua-textarea"): # pre.wp-block-code 
        user_agents.append(user_agent.text)

    headers = {
        'User-Agent': random.choice(user_agents)
    }
except:
    raise(ConnectionAbortedError("Problem with User Agents Website."))

print(headers)
url = "https://niggrid.org/Dashboard"
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")

website_date = soup.find("span", attrs={"id": "MainContent_lblCurrentDay"}).text

print(website_date)

(_, _, curr,_, prev, *_) = soup.select("div.row")

def get_data(object):
    data = {
        'Peak Generation (MW)': None,
        'Off-Peak Generation (MW)': None,
        'Energy Generated (MWh)': None,
        'Energy Sent Out (MWh)': None,
        'Frequency @ Peak Generation (Hz)': None,
        'Frequency @ Off-Peak Generation (Hz)': None,
        'Peak Generation Hour': None,
        'Off-Peak Generation Hour': None,
        # 'Highest Frequency (Hz)': None,
        # 'Lowest Frequency (Hz)': None,
        # 'Hour @ Highest Frequency': None,
        # 'Hour @ Lowest Frequency': None,
        # 'Highest Voltage': None,
        # 'Lowest Voltage': None
    }

    peak_gen, off_peak_gen, energy_gen, energy_sent = object.select("div.col-lg-3.col-md-6.col-sm-6")
    (data['Peak Generation (MW)'], 
     data['Peak Generation Hour'], 
     data['Frequency @ Peak Generation (Hz)'], *_) = [i.text.replace(',', '') for i in peak_gen.find_all('span', {'class': 'control-label'})]
    
    (data['Off-Peak Generation (MW)'], 
     data['Off-Peak Generation Hour'], 
     data['Frequency @ Off-Peak Generation (Hz)'], *_) = [i.text.replace(',', '') for i in off_peak_gen.find_all('span', {'class': 'control-label'})]
    
    (data['Energy Generated (MWh)'], *_) = [i.text.replace(',', '') for i in energy_gen.find_all('span', {'class': 'control-label'})]
    (data['Energy Sent Out (MWh)'], *_) = [i.text.replace(',', '') for i in energy_sent.find_all('span', {'class': 'control-label'})]

    return data

def write_to_mongo(the_date, data):
    filter = {"date": the_date}
    update = {"$set": data}
    result = db.gridlines.update_one(filter, update)
    # print(result.modified_count)
    if (result.matched_count) == 0:
        data = {
            "date": the_date,
            'metadata': {'source': 'niggrid.org'},
            **data
        }
        result = db.gridlines.insert_one(data)
    return result

# Use selenium for this bit.
driver.get(url)
# Click "get generation" button
button = driver.find_element(By.XPATH, '//*[@id="MainContent_lnkShowAdditionalData"]')
driver.execute_script("arguments[0].click();", button)

card = driver.find_element(By.CSS_SELECTOR, 'div[class="modal-content"]')
freq, morn = card.find_elements(By.CSS_SELECTOR, 'div[class="col-lg-6 col-md-12 col-sm-12"]')
voltage = card.find_element(By.CSS_SELECTOR, 'div[class="col-lg-8 col-md-12 col-sm-12"]')


highest_frequency, highest_freq_time, lowest_frequency, lowest_freq_time = freq.find_elements(By.CSS_SELECTOR, 'span[class="control-label"]')
power06, freq06, *_ = morn.find_elements(By.CSS_SELECTOR, 'span[class="control-label"]')
highest_voltage, _, lowest_voltage, _ = voltage.find_elements(By.CSS_SELECTOR, 'span[class="control-label"]')

today_data = {
    'date': str(date.today()),
    'metadata': {'source': 'niggrid.org'},
    'Grid @ 06:00 (MW)': power06.text.replace(',', ''),
    'Frequency @ 06:00 (Hz)': freq06.text
}

curr_data = get_data(curr)
curr_data['Highest Frequency (Hz)'] = highest_frequency.text
curr_data['Lowest Frequency (Hz)'] = lowest_frequency.text
curr_data['Hour @ Highest Frequency'] = highest_freq_time.text
curr_data['Hour @ Lowest Frequency'] = lowest_freq_time.text
curr_data['Highest Voltage'] = highest_voltage.text
curr_data['Lowest Voltage'] = lowest_voltage.text

# print(today_data)
# print(curr_data)

write_to_mongo(str(date.today()), today_data)
write_to_mongo(str(date.today() - timedelta(days=1)), curr_data)
write_to_mongo(str(date.today() - timedelta(days=2)), get_data(prev))