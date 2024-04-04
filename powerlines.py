from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import pymongo
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGODB_URI)
db = client['power_track']

df = pd.DataFrame(db.gridlines.find())
del df['metadata']
del df['_id']

plots = {
    "Power Generation": ['Peak Generation (MW)', 'Off-Peak Generation (MW)'],
    "Energy": ['Energy Generated (MWh)', 'Energy Sent Out (MWh)']
}

units = {
    "Power Generation": "MW",
    "Energy": "MWh"
}

for plot, columns in plots.items():
    ys = {i:i.replace(f' ({units[plot]})', '') for i in columns}
    df.rename(columns=ys, inplace=True, errors="raise")
    plots[plot] = list(ys.values())
df.rename(columns={"date": "Date"}, inplace=True, errors="raise")
# Create line plots
figures = []
for plot in plots:
    value = units[plot]
    figures.append(
        px.line(df, x='Date', y=plots[plot], labels={'value': value, 'variable': 'Legend has it that:'}, title=f'{plot} Trend', markers=True)
    )


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Powerlines', style={'textAlign': 'center', 'font-family': 'sans-serif'}),
    html.H3(children='A view of the Nigerian grid\'s performance through lines (read time).', style={'textAlign': 'center', 'font-family': 'sans-serif'}),
    html.Div(children=[
        dcc.Graph(id="graph1", figure=figures[0], style={'display': 'inline-block'}),
        dcc.Graph(id="graph2", figure=figures[1], style={'display': 'inline-block'})
    ]),
    # html.Div([dcc.Dropdown(list(plots.keys()), 'Power Generation', id='dropdown-selection')], style={"width": "15%"}),
    # dcc.Graph(id='graph-content'),
]
)

# @callback(
#     Output('graph-content', 'figure'),
#     Input('dropdown-selection', 'value')
# )
# def update_graph(plot):
#     value = units[plot]
#     fig = px.line(df, x='date', y=plots[plot], labels={'value': value, 'variable': 'Legend has it that:'}, title=f'{plot} Trend', markers=True)
#     return fig

if __name__ == '__main__':
    app.run(debug=True)