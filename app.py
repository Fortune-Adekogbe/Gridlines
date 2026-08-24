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

# extract relevant columns for current dashboard
relevant_cols = ['date', 'Peak Generation (MW)', 'Off-Peak Generation (MW)', "Grid @ 06:00 (MW)", 'Energy Generated (MWh)', 'Energy Sent Out (MWh)']

df = df[relevant_cols]

# convert columns to numeric datatype and remove duplicates
for col in relevant_cols:
    if col != 'date':
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].astype("Float64")

df = df.groupby('date').max().reset_index()

# def fill_the_gap(the_date):
#     """
#     Uses date information to reproduce power generation data from gridmoments.
#     """
#     filter = {"date": the_date}
#     result = db.gridmoments.find_one(filter, {"_id": 0, "date": 1, "Hour Total": 1})

#     if not isinstance(result, dict):
#         return None

#     # print(result["date"])
#     hourly_values = list(result["Hour Total"].values())[:-1] # Drop Total
#     # print(hourly_values)
#     peak_generation = max(hourly_values)
#     off_peak_generation = min([i for i in hourly_values if i != '0.00'])
#     grid_at_0600 = result["Hour Total"]["06:00"]
#     return {"Peak Generation (MW)": float(peak_generation.replace(',','')), "Off-Peak Generation (MW)": float(off_peak_generation.replace(',','')), "Grid @ 06:00 (MW)": float(grid_at_0600.replace(',',''))}


def fill_the_gap_batch(missing_dates):
    """
    Uses date information to reproduce power generation data from gridmoments.
    """
    filter = {"date": {"$in": missing_dates}}
    result = list(db.gridmoments.find(filter, {"_id": 0, "date": 1, "Hour Total": 1}))

    if len(result) == 0:
        return None
    missing_data = []
    for doc in result:
        missing_row = {"date": doc["date"]}
        hourly_values = list(doc["Hour Total"].values())[:-1] # Drop Total
        # print(hourly_values)
        peak_generation = max(hourly_values)
        off_peak_generation = min([i for i in hourly_values if i != '0.00'])
        grid_at_0600 = doc["Hour Total"]["06:00"]
        missing_row["Peak Generation (MW)"] = float(peak_generation.replace(',',''))
        missing_row["Off-Peak Generation (MW)"] = float(off_peak_generation.replace(',',''))
        missing_row["Grid @ 06:00 (MW)"] = float(grid_at_0600.replace(',',''))
        missing_data.append(missing_row)
    return missing_data

# temporarily make the date column the index
df = df.set_index("date")

# create rows for missing dates
# TODO: this can technically start from 2017; Verify calculations before updating
df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D"))

# identify all rows with missing values
missing_dates = df.index[df.isna().any(axis=1)].strftime("%Y-%m-%d").tolist()
# dates = df.index[df.isna().any(axis=1)]

# call fill_the_gap_batch to get data for rows with missing cells
patch = (
    pd.DataFrame(fill_the_gap_batch(missing_dates))
    .assign(date=lambda x: pd.to_datetime(x["date"]))
    .set_index("date")
)
# patch = pd.DataFrame({
#     d: fill_the_gap(d.strftime("%Y-%m-%d"))
#     for d in dates
# }).T

# fill the cells and reset the index; existing values are untouched
df = df.fillna(patch).rename_axis("date").reset_index()

# Define plots and units
plots = {
    "Power Generation": ['Peak Generation (MW)', 'Off-Peak Generation (MW)', "Grid @ 06:00 (MW)"],
    #"Grid @ 06:00": ["Grid @ 06:00 (MW)"],
    "Energy": ['Energy Generated (MWh)', 'Energy Sent Out (MWh)']
}

units = {
    "Power Generation": "MW",
    "Grid @ 06:00": "MW",
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

for plot in plots.keys():
    value = units[plot]
    fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': ''}, title=f'{plot} Trend', markers=False) # removed markers
    fig.update_layout(
        title=dict(y=0.925, text=f'{plot} Trend', font=dict(size=25), automargin=True, yref='container')
    )

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.0,
        xanchor="center",
        x=0.5        
    ))

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            # rangeselector=dict(
            #     buttons=list([
            #         dict(count=7, label="1 week", step="day", stepmode="backward"),
            #         dict(count=1, label="1 month", step="month", stepmode="backward"),
            #         # dict(count=3, label="3 months", step="month", stepmode="backward"),
            #         dict(label="All", step="all"),
            #     ]),
            #     y=1.15,
            #     yanchor="bottom"
            # ),
            rangeslider=dict(
                visible=True
            ),
            type="date",
        ),

    )

    st.plotly_chart(fig, use_container_width=True)

# # SIDE BY SIDE PLOTS
# col1, col2 = st.columns(2)

# # Create line plots
# for col, plot in zip(st.columns(2), plots.keys()):
#     with col:
#         value = units[plot]
#         fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': ''}, title=f'{plot} Trend', markers=True)
#         fig.update_layout(
#             title=dict(y=0.9, text=f'{plot} Trend', font=dict(size=25), automargin=True, yref='container')
#         )

#         fig.update_layout(legend=dict(
#             orientation="h",
#             yanchor="top",
#             y=1.125,
#             xanchor="center",
#             x=0.5        
#         ))
#         st.plotly_chart(fig, use_container_width=True)

# # WEEKLY VIEW WITH BUTTONS FOR NAVIGATION
# plot = "Energy"
# value = units[plot]

# # Setup state for storing the current view range
# if 'current_week_start' not in st.session_state:
#     st.session_state.current_week_start = df['Date'].iloc[-7]

# # Function to update the week view
# def update_week(offset):
#     start_index = df.index[df['Date'] == st.session_state.current_week_start][0] + offset * 7
#     if start_index < 0:
#         start_index = 0  # Prevent index out of range
#     elif start_index >= len(df) - 7:
#         start_index = len(df) - 7  # Prevent index out of range
#     st.session_state.current_week_start = df['Date'].iloc[start_index]

# # Display the selected week's data using Plotly
# current_range = [st.session_state.current_week_start, st.session_state.current_week_start + pd.Timedelta(days=6)]

# fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': ''}, title=f'{plot} Trend', markers=True)
# fig.update_layout(xaxis_range=current_range)

# fig.update_layout(
#     title=dict(y=0.9, text=f'{plot} Trend', font=dict(size=25), automargin=True, yref='container')
# )

# fig.update_layout(legend=dict(
#     orientation="h",
#     yanchor="top",
#     y=1.125,
#     xanchor="center",
#     x=0.5        
# ))

# st.plotly_chart(fig, use_container_width=True)
# # Buttons for navigation
# col1, col2 = st.columns(2)
# with col1:
#     if st.button('Previous Week'):
#         update_week(-1)
# with col2:
#     if st.button('Next Week'):
#         update_week(1)