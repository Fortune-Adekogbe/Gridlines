import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
import random

url = "https://www.useragents.me/" # "https://www.useragentlist.net/"

try:
    request = requests.get(url)
    user_agents = []
    soup = BeautifulSoup(request.text, "html.parser")
    for user_agent in soup.select("textarea.form-control.ua-textarea"): # pre.wp-block-code 
        user_agents.append(user_agent.text)

    url = "https://power.gov.ng"
    headers = {
        'User-Agent': random.choice(user_agents)
    }
except:
    raise(ConnectionAbortedError("Problem with User Agents Website."))

print(headers)
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")

website_date = soup.find(
    "p", attrs={"class": "bold size18 mt-0 mb-5 letter-spacing-6 w3-center"}).text

((power, frequency),
 (highest_frequency, lowest_frequency),
 (highest_voltage, lowest_voltage)) = [i.text.strip().split("\n") for i in soup.find_all("p", attrs={"class": "py-0 m-0 size12"})]


def extractor(before, after, input):
    output = re.search(rf'(?<={before})[\d,]+(?:\.\d+)?(?={after})', input)
    output = output.group(0)
    output = output.replace(',', '')
    output = float(output)
    return output

today_data = {
    'date': datetime.strptime(str(date.today()), '%Y-%m-%d'),
    'metadata': {'source': 'power.gov.ng'},
    'Grid @ 06:00 (MW)': extractor("Generation: ", "MW", power),
    'Frequency @ 06:00 (Hz)': extractor("Frequency: ", "Hz", frequency),
}

((_, peak_gen, peak_time, _),
 (_, offpeak_gen, offpeak_time, *_),
 (_, energy_gen, *_),
 (_, energy_sent, *_)) = [i.text.strip().split("\n") for i in soup.find_all("div", attrs={"class": "col-12 col-sm-6 col-md-3"})]

yesterday_data = {
    'Peak Generation (MW)': extractor("", "MW", peak_gen),
    'Off-Peak Generation (MW)': extractor("", "MW", offpeak_gen),
    'Energy Generated (MWh)': extractor("", "MWh", energy_gen),
    'Energy Sent Out (MWh)': extractor("", "MWh", energy_sent),
    'Frequency @ Peak Generation (Hz)': extractor("Freq.: ", "Hz", peak_time),
    'Frequency @ Off-Peak Generation (Hz)': extractor("Freq.: ", "Hz", offpeak_time),
    'Peak Generation Hour': int(extractor("Time: ", "Hrs", peak_time)),
    'Off-Peak Generation Hour': int(extractor("Time: ", "Hrs", offpeak_time)),
    'Highest Frequency (Hz)': extractor("Highest: ", "Hz", highest_frequency),
    'Lowest Frequency (Hz)': extractor("Lowest: ", "Hz", lowest_frequency),
    'Hour @ Highest Frequency': int(extractor("@ ", "Hrs", highest_frequency)),
    'Hour @ Lowest Frequency': int(extractor("@ ", "Hrs", lowest_frequency)),
    'Highest Voltage': highest_voltage.replace("Highest: ", ""),
    'Lowest Voltage': lowest_voltage.replace("Lowest: ", "")
}

print(website_date)
print(today_data)
print(yesterday_data)