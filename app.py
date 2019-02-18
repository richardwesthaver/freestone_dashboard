from datetime import datetime as dt
from io import BytesIO
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import requests
from dateutil import parser
import os

# start up app
port = int(os.environ.get('PORT', 5000))
app = dash.Dash(__name__)
server = app.server
app.title = 'Freestone Dashboard Mockup'

# collect data
r = requests.get('https://docs.google.com/spreadsheets/d/1pZp7xbIEVOrM8Jk6xVwovIBe2I4sdv8u2h9RTwmiMZE/export?format=xlsx')
raw_data = pd.ExcelFile(BytesIO(r.content))

catalog = pd.read_excel(raw_data, sheet_name='catalog')
launches = pd.read_excel(raw_data, sheet_name='launches')
logins = pd.read_excel(raw_data, sheet_name='logins')
activity = pd.read_excel(raw_data,sheet_name='activity')

catalog['createdOn']=pd.to_datetime(catalog.createdOn)
catalog['completedOn']=pd.to_datetime(catalog.completedOn)
catalog = catalog.sort_values(by=['createdOn'])
catalog['day'] = catalog.createdOn.dt.date

launches['createdOn']=pd.to_datetime(launches.createdOn)
launches = launches.sort_values(by=['createdOn'])
launches['day'] = launches.createdOn.dt.date

logins['createdOn']=pd.to_datetime(logins.createdOn)
logins['createdOn'] = catalog.createdOn.dt.date
logins = logins.sort_values(by=['createdOn'])

# today -1 month
def prevmonthdate(date):
    try:
        prevmonthdate=date.replace(month=date.month-1)
    except ValueError:
        if date.month ==1:
            prevmonthdate = date.replace(year=date.year-1, month=12)
        elif date.day > prevmonthdate:
                prevmonthdate = date.replace(month=date.month-1, day=date.day-1)
    return prevmonthdate

# app layout
app.layout = html.Div([
    html.Div(id='fs_sidenav',
         className='sidenav',
         children=[
             html.A('Home', href='#'),
             html.A('Courses', href='#'),
             html.A('Content', href='#')
         ]),
    html.Div(id='container',
        className='container', style={'padding-left': '250px', 'transition': 'margin-left .5s'},
        children=[
            html.Div(id='summary', className='twelve columns', children=[
                html.H3('Summary', className='twelve columns'),
                html.Div(id='card_1', className='three columns card', children=[
                    html.Div(className='card_title', children=[
                        html.H4('47')
                    ]),
                    html.Div(className='card_content', children=[
                        html.Span('Total Courses', className='card_content')
                    ])
                    ]),
                html.Div(id='card_2', className='three columns card', children=[
                    html.Div(className='card_title', children=[
                        html.H4('24')
                    ]),
                    html.Div(className='card_content', children=[
                        html.Span('Published Courses', className='card_content')
                    ])
                ]),
                html.Div(id='card_3', className='three columns card', children=[
                    html.Div(className='card_title', children=[
                        html.H4('231')
                    ]),
                    html.Div(className='card_content', children=[
                        html.Span('Total Orders', className='card_content')
                    ])
                ]),
                html.Div(id='card_4', className='three columns card', children=[
                    html.Div(className='card_title', children=[
                        html.H4('5')
                    ]),
                    html.Div(className='card_content', children=[
                        html.Span('Orders Today', className='card_content')
                    ])
                ])
            ]),
            html.Div(className='twelve columns', children=[
                html.Div(className='twelve columns', children=[
                    html.H3('Key Metrics', className='twelve columns')
                ]),
                html.Div(className='eight columns', children=[
                    dcc.Graph(id='key_metrics')
                ]),
                html.Div(className='four columns', children=[
                                 dcc.DatePickerRange(
                                     id='date-picker',
                                     min_date_allowed=dt.today().replace(year=dt.today().year - 3),
                                     max_date_allowed=dt.today(),
                                     initial_visible_month=dt.today(),
                                     start_date=prevmonthdate(dt.today()),
                                     end_date=dt.today()
                                 ),
                    dcc.Dropdown(
                        options=[
                            {'label': 'role_1', 'value': 'r1'},
                            {'label': 'role_2', 'value': 'r2'},
                            {'label': 'role_3', 'value': 'r3'}
                        ],
                        multi=True,
                        value="",
                        placeholder='User Role',
                        style={'margin-bottom': '18px', 'margin-top': '40px', 'max-width': '318px'}
                    ),
                    dcc.Dropdown(
                        options=[
                            {'label': 'tag_1', 'value': 't1'},
                            {'label': 'tag_2', 'value': 't2'},
                            {'label': 'tag_3', 'value': 't3'}
                        ],
                        multi=True,
                        value="",
                        placeholder='Tags',
                        style={'margin-bottom': '18px', 'max-width': '318px'}
                    )
                ])

            ]),
            html.Div(className='twelve columns', children=[
                html.H3('Site Usage', className='twelve columns'),
                html.Div(className='twelve columns', children=[
                    html.Div(className='seven columns', children=[
                       dash_table.DataTable(
                           id='activity_table',
                           data=activity.head(10).to_dict('rows'),
                           columns=[{'id': c, 'name': c} for c in activity.columns]
                       )
                    ]),
                    html.Div(className='five columns', children=[
                        dcc.Graph(id='device_usage',
                                  figure=go.Figure(
                                      data=[go.Pie(
                                          labels=['Desktop', 'Mobile', 'Tablet'],
                                          values=['42344', '1864', '2390'])],
                                      layout=go.Layout(
                                          title='Device Usage',
                                          height=375
                                      )
                                  ))
                    ]),
                ]),
                html.Div(className='twelve columns', children=[
                    dcc.Graph(id='logins',
                              figure=go.Figure(
                                  data=[go.Scatter(
                                      x=logins.createdOn,
                                      y=logins['count'])],
                                  layout=go.Layout(
                                      title='Logins',
                                      xaxis={'title': 'Date'},
                                      yaxis={'title': 'Logins'}
                                  )
                              ))
                ])
            ])
        ])
])


@app.callback(  # update key metrics
    dash.dependencies.Output('key_metrics', 'figure'),
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
