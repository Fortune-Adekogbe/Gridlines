import pymongo
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, timedelta, date

load_dotenv(find_dotenv())

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGODB_URI)
db = client['power_track']

today_data = {
    'date': datetime.strptime(str(date.today()), '%Y-%m-%d'), 
    'metadata': {'source': 'power.gov.ng'},
    'Grid @ 06:00 (MW)': 4110.19,
    'Frequency @ 06:00 (Hz)': 50.17, 
}

yesterday_data = {
    'Peak Generation (MW)': 4303.0,
    'Off-Peak Generation (MW)': 3694.95,
    'Energy Generated (MWh)': 96131.84,
    'Energy Sent Out (MWh)': 94991.1,
    'Frequency @ Peak Generation (Hz)': 50.23,
    'Frequency @ Off-Peak Generation (Hz)': 50.62,
    'Peak Generation Hour': 17.0,
    'Off-Peak Generation Hour': 17.0,
    'Highest Frequency (Hz)': 50.76,
    'Lowest Frequency (Hz)': 49.08,
    'Hour @ Highest Frequency': 17.0,
    'Hour @ Lowest Frequency': 16.0,
    'Highest Voltage': '357.00kV @ Gwagwalada TS @ 14:00Hrs',
    'Lowest Voltage': '300.00kV @ Yola & Gombe TS @ 01:00 & 01:00Hrs'
}

# add data for today
result = db.gridlines.insert_one(today_data)
print(result)

# add to the data for yesterday
yesterday = date.today() - timedelta(days=1)
filter = {"date": datetime.strptime(str(yesterday), '%Y-%m-%d')}
update = {"$set": yesterday_data}
result = db.gridlines.update_one(filter, update)
print(result)