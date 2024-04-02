import pandas as pd
import pymongo
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime

load_dotenv(find_dotenv())

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGODB_URI)
db = client['power_track']

store = [
    ["date", "Peak Generation (MW)", "Off-Peak Generation (MW)",
     "Energy Generated (MWh)", "Energy Sent Out (MWh)", "Frequency @ Peak Generation (Hz)",
     "Frequency @ Off-Peak Generation (Hz)", "Grid @ 06:00 (MW)", "Frequency @ 06:00 (Hz)"],
    ["2024-03-25", 4607.2, 4212.85, 106520.92, 105102.92, None,  None, None, None],
    ["2024-03-26", 4504.6, 4124.59, 104401.65, 103051.36, None,  None, None, None],
    ["2024-03-27", 4536.7, 4123.49, 102180.86, 100941.23, None,  None, None, None],
    ["2024-03-28", 4524.7, 21, 77046.06, 75955.28, None,  None, None, None],
    ["2024-03-29", 4389.5, 2690.46, 90292.02, 89151.36, None,  None, None, None],
    ["2024-03-30", 4518.4, 3685.61, 99892.91,
        98610.9, None,  None, 4518.46, 50.03],
    ["2024-03-31", 4303, 3694.95, 96131.84, 94991.1, 50.23, 50.62, 4110.19, 50.17],
    ["2024-04-01", None, None, None, None, None, None, 4106.83, 50.34]
]

store1 = [
    ["date", "Peak Generation Hour", "Off-Peak Generation Hour",
     "Highest Frequency (Hz)", "Lowest Frequency (Hz)",
     "Hour @ Highest Frequency", "Hour @ Lowest Frequency",
     "Highest Voltage", "Lowest Voltage"],
    ["2024-03-25", None, None, None, None, None, None, None, None],
    ["2024-03-26", None, None, None, None, None, None, None, None],
    ["2024-03-27", None, None, None, None, None, None, None, None],
    ["2024-03-28", None, None, None, None, None, None, None, None],
    ["2024-03-29", 1, 1, 51.19, 49.00, 3, 12, "355.00kV @ Gwagwalada T/S @ 22:00Hrs",
        "300.00kV @ Gombe & Yola T/S @ 04:00 & 16:00Hrs"],
    ["2024-03-30", 16, 16, 51.06, 49.00, 15, 11, "353.00kV @ Gwagwalada T.S @ 20:00Hrs",
        "300.00kV @ Yola & Gombe TS @ 07:00 & 07:00Hrs"],
    ["2024-03-31", 17, 17, 50.76, 49.08, 17, 16, "357.00kV @ Gwagwalada TS @ 14:00Hrs",
        "300.00kV @ Yola & Gombe TS @ 01:00 & 01:00Hrs"],
    ["2024-04-01", None, None, None, None, None, None, None, None]
]

df = pd.DataFrame(columns=store[0], data=store[1:])
sdf = pd.DataFrame(columns=store1[0], data=store1[1:])
df = df.merge(right=sdf, on='date')

documents = df.to_json(orient="records")
documents = json.loads(documents)

modified_docs = []

for document in documents:
    date = document["date"]
    del document["date"]
    modified_docs.append({"date": datetime.strptime(
        date, '%Y-%m-%d'), "metadata": {"source": "power.gov.ng"}, **document})

result = db.gridlines.insert_many(modified_docs)
print(result)
