import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import re
import random
from db_setup import *

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

write_to_mongo(str(date.today() - timedelta(days=1)), get_data(curr))
write_to_mongo(str(date.today() - timedelta(days=2)), get_data(prev))

# Use selenium for this bit.

# ((power, frequency),
#  (highest_frequency, lowest_frequency),
#  (highest_voltage, lowest_voltage)) = [i.text.strip().split("\n") for i in soup.find_all("p", attrs={"class": "py-0 m-0 size12"})]


# def extractor(before, after, input):
#     output = re.search(rf'(?<={before})[\d,]+(?:\.\d+)?(?={after})', input)
#     output = output.group(0)
#     output = output.replace(',', '')
#     output = float(output)
#     return output

# today_data = {
#     'date': datetime.strptime(str(date.today()), '%Y-%m-%d'),
#     'metadata': {'source': 'power.gov.ng'},
#     'Grid @ 06:00 (MW)': extractor("Generation: ", "MW", power),
#     'Frequency @ 06:00 (Hz)': extractor("Frequency: ", "Hz", frequency),
# }