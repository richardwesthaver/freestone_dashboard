from datetime import datetime as dt
from io import BytesIO
import calendar as c
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import requests

# start up app
app = dash.Dash('test', external_stylesheets=[dbc.themes.SANDSTONE])

# collect data
r = requests.get('https://docs.google.com/spreadsheets/d/1pZp7xbIEVOrM8Jk6xVwovIBe2I4sdv8u2h9RTwmiMZE/export?format=xlsx')
raw_data = pd.ExcelFile(BytesIO(r.content))

enrollments = pd.read_excel(raw_data, sheet_name='Enrollments')
launches = pd.read_excel(raw_data, sheet_name='Launches')
completions = pd.read_excel(raw_data, sheet_name='Completions')
logins = pd.read_excel(raw_data, sheet_name='Logins')

dataframes = [enrollments,launches,completions,logins]

for df in dataframes:
    df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y')
    df['day']=df['date'].apply(lambda x: '%d/%d/%d' % (x.month, x.day, x.year))

def prevmonthdate(date):
    try:
        prevmonthdate=date.replace(month=date.month-1)
    except ValueError:
        if date.month ==1:
            prevmonthdate = date.replace(year=date.year-1, month=12)
        elif date.day > prevmonthdate:
                prevmonthdate = date.replace(month=date.month-1, day=date.day-1)
    return prevmonthdate
# gen_graph(data_set['Enrollments'],'enrollments','enrollments','user_id')
# app layout
app.layout = html.Div(children=[html.H1('Freestone Dashboard'),
             html.Div(html.H2('Summary')),
             html.Div([
                 html.H2('Key Metrics'),
                 dcc.Graph(id='Enrollments',),
                 dcc.Graph(id='Launches'),
                 dcc.Graph(id='Completions'),
                 dcc.DatePickerRange(
                     id='date-picker',
                     min_date_allowed=dt.today().replace(year=dt.today().year-3),
                     max_date_allowed=dt.today(),
                     initial_visible_month=dt.today(),
                     start_date=prevmonthdate(dt.today()),
                     end_date=dt.today()
                 )
             ]),
             html.Div([
                 html.H2('Site Usage'),
                 dcc.Graph(id='Logins'),
                 html.Table(id='site_activity'),
                 dcc.Graph(id='device_usage')
             ])
             ])

@app.callback(
    dash.dependencies.Output('Enrollments','figure'),
    [dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date')])
def update_figure(start_date, end_date):
    enrollments_filtered = enrollments[(enrollments.date>start_date) & (enrollments.date<end_date)]
    return {
        'data': [go.Scatter(
            x=enrollments_filtered['day'].unique(),
            y=enrollments.groupby(enrollments.day).user_id.count(),
            mode='lines'
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'x',
                'autorange': 'reversed'
            },
            yaxis={
                'title': 'y'
            },
            hovermode='closest'
        )
    }

if __name__ == "__main__":
    app.run_server(debug=True)