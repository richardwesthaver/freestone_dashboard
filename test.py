from io import BytesIO
import requests
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime as dt

# start up app
app = dash.Dash('test', external_stylesheets=[dbc.themes.SANDSTONE])

# collect data
r = requests.get('https://docs.google.com/spreadsheets/d/1pZp7xbIEVOrM8Jk6xVwovIBe2I4sdv8u2h9RTwmiMZE/export?format=xlsx')
raw_data = pd.ExcelFile(BytesIO(r.content))
data_set = pd.read_excel(raw_data, sheet_name=None)

# constants
today = dt.today()
# gen_graph(data_set['Enrollments'],'enrollments','enrollments','user_id')
# app layout
app.layout = html.Div([
    html.H1('Freestone Dashboard'),
    html.Div([
        html.H2('Summary')
    ]),
    html.Div([
        html.H2('Key Metrics'),
        dcc.Graph(id='Enrollments'),
        dcc.Graph(id='Launches'),
        dcc.Graph(id='Completions')
    ]),
    html.Div([
        html.H2('Site Usage'),
        dcc.Graph(id='Logins'),
        html.Table(id='site_activity'),
        dcc.Graph(id='device_usage')

    ])
]
)

#generate components
def gen_graph(dataframe,id,title,y):
    return dcc.Graph(
        id=id,
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=dataframe['time'],
                    y=dataframe[y]
                )
            ]
        )
    )

def gen_datePicker(id,min,max,):
    return dcc.DatePickerRange(
        id=id,
        min_date_allowed=min,
        max_date_allowed=max,
        initial_visible_month=dt.today()
    )

#if __name__ == "__main__":
app.run_server(debug=True)
