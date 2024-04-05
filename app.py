import streamlit as st
import pandas as pd
import plotly.express as px
import pymongo
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables
load_dotenv(find_dotenv())

# MongoDB credentials
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

# MongoDB URI
MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGODB_URI)
db = client['power_track']

# Load data from MongoDB
df = pd.DataFrame(db.gridlines.find())
df['date'] = pd.to_datetime(df['date'])
df.sort_values(by="date", inplace=True)

del df['metadata']
del df['_id']

# Define plots and units
plots = {
    "Power Generation": ['Peak Generation (MW)', 'Off-Peak Generation (MW)'],
    "Energy": ['Energy Generated (MWh)', 'Energy Sent Out (MWh)']
}

units = {
    "Power Generation": "MW",
    "Energy": "MWh"
}

# Process data
for plot, columns in plots.items():
    ys = {i: i.replace(f' ({units[plot]})', '') for i in columns}
    df.rename(columns=ys, inplace=True, errors="raise")
    plots[plot] = list(ys.values())
df.rename(columns={"date": "Date"}, inplace=True, errors="raise")

st.set_page_config(layout="wide")

# Create Streamlit dashboard
st.markdown("<h1 style='text-align: center; color: white;'>Gridlines</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>A view of the Nigerian grid\'s performance through lines (read time).</h3>", unsafe_allow_html=True)

# Create layout for plots
col1, col2 = st.columns(2)

# Create line plots
with col1:
    plot = "Power Generation"
    value = units[plot]
    fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': 'Legend has it that:'}, title=f'{plot} Trend', markers=True)
    fig.update_layout(
        title=dict(text=f'{plot} Trend', font=dict(size=25), automargin=True, yref='paper')
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    plot = "Energy"
    value = units[plot]
    fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': 'Legend has it that:'}, title=f'{plot} Trend', markers=True)
    fig.update_layout(
        title=dict(text=f'{plot} Trend', font=dict(size=25), automargin=True, yref='paper')
    )
    st.plotly_chart(fig, use_container_width=True)

# # Create line plots
# for plot in plots:
#     value = units[plot]
#     fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': 'Legend has it that:'}, title=f'{plot} Trend', markers=True)
#     st.plotly_chart(fig, use_container_width=True)
