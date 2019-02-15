from datetime import datetime as dt, date as d
from io import BytesIO
import calendar as c
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import requests
from dateutil import parser
import plotly

# start up app
app = dash.Dash('scratch', external_stylesheets=[dbc.themes.SANDSTONE])
app.scripts.config.serve_locally=True

# collect data
r = requests.get('https://docs.google.com/spreadsheets/d/1pZp7xbIEVOrM8Jk6xVwovIBe2I4sdv8u2h9RTwmiMZE/export?format=xlsx')
raw_data = pd.ExcelFile(BytesIO(r.content))

catalog = pd.read_excel(raw_data, sheet_name='catalog')
launches = pd.read_excel(raw_data, sheet_name='launches')
logins = pd.read_excel(raw_data, sheet_name='logins')

catalog['createdOn']=pd.to_datetime(catalog.createdOn)
catalog['completedOn']=pd.to_datetime(catalog.completedOn)
catalog = catalog.sort_values(by=['createdOn'])
catalog['day'] = catalog.createdOn.dt.date

launches['createdOn']=pd.to_datetime(launches.createdOn)
launches = launches.sort_values(by=['createdOn'])
launches['day'] = launches.createdOn.dt.date

logins['createdOn']=pd.to_datetime(logins.createdOn)
catalog['createdOn'] = catalog.createdOn.dt.date
logins = logins.sort_values(by=['createdOn'])

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
                 dcc.DatePickerRange(
                     id='date-picker',
                     min_date_allowed=dt.today().replace(year=dt.today().year - 3),
                     max_date_allowed=dt.today(),
                     initial_visible_month=dt.today(),
                     start_date=prevmonthdate(dt.today()),
                     end_date=dt.today(),
                 ),
                 dcc.Graph(id='key_metrics')
             ]),
             html.Div([
                 html.H2('Site Usage'),
                 dcc.Graph(id='logins',
                           figure=go.Figure(
                               data=[go.Scatter(
                                   x=logins.createdOn,
                                   y=logins['count'])],
                               layout=go.Layout(
                                   title='Logins',
                                   xaxis={'title':'Date'},
                                   yaxis={'title':'Logins'}
                               )
                           )),
                 html.Table(id='site_activity'),
                 dcc.Graph(id='device_usage',
                           figure=go.Figure(
                               data=[go.Pie(labels=['Desktop', 'Mobile', 'Tablet'],
                                            values=['42344', '1864', '2390'])],
                               layout=go.Layout(
                                   title='Device Usage')
                           ))
             ])
             ])

@app.callback(  #update key metrics
    dash.dependencies.Output('key_metrics','figure'),
    [dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date')])
def update_catalog(start_date, end_date):
    start_date = dt.date(parser.parse(start_date))
    end_date = dt.date(parser.parse(end_date))
    catalog_filtered = catalog.loc[(catalog.day>start_date) & (catalog.day<end_date)]
    launches_filtered = launches.loc[(launches.day>start_date) & (launches.day<end_date)]
    fig = {
        'data': [
                go.Scatter(
                    x=catalog_filtered.day.unique(),
                    y=catalog_filtered.groupby(catalog.day).rand.count(),
                    name='Enrollments'
            ),
                go.Scatter(
                    x=catalog_filtered.day.unique(),
                    y=catalog_filtered.groupby(catalog.day).completedOn.count(),
                    name='Completions'
                ),
                go.Scatter(
                    x=launches_filtered.day.unique(),
                    y=launches_filtered.groupby(launches.day).createdOn.count(),
                    name='Launches'
                )
        ],
        'layout': go.Layout(
            xaxis={
                'title': 'Date',
            },
            yaxis={
                'title': 'Count'
            }
        )
    }

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)