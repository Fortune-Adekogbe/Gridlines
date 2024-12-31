import pymongo
from dotenv import load_dotenv, find_dotenv
import os
from datetime import timedelta
from scraper import *

load_dotenv(find_dotenv())

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGODB_URI)
db = client['power_track']

# DATE ON WEBSITE
_, date_str = website_date.split(maxsplit=1)
date_str = date_str.replace("ST ", " ").replace("ND", "").replace("RD", "").replace("TH", "")
website_date = datetime.strptime(date_str, "%d %B, %Y").date()

# add to the data for yesterday depending on how updated the website is.
yesterday = date.today() - timedelta(days=1)

if website_date == yesterday:
    filter = {"date": datetime.strptime(str(yesterday), '%Y-%m-%d')}
    update = {"$set": yesterday_data}
    result = db.gridlines.update_one(filter, update)
    if (result.matched_count) == 0:
        yesterday_data = {
            "date": datetime.strptime(str(yesterday), '%Y-%m-%d'),
            'metadata': {'source': 'power.gov.ng'},
            **yesterday_data
        }
        result = db.gridlines.insert_one(yesterday_data)
    print(result)

    # add data for today if it doesn't already exist
    result = db.gridlines.insert_one(today_data)
    print(result)
print("Done.")
