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
    fig = px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': ''}, title=f'{plot} Trend', markers=True)
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