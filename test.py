from io import BytesIO
import requests
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# collect data
r = requests.get('https://docs.google.com/spreadsheets/d/1pZp7xbIEVOrM8Jk6xVwovIBe2I4sdv8u2h9RTwmiMZE/export?format=xlsx')
raw_data = pd.ExcelFile(BytesIO(r.content))
data_set = pd.read_excel(raw_data, sheet_name=None)
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

# start up app
app = dash.Dash('test', external_stylesheets=[dbc.themes.SANDSTONE])

app.layout = html.Div(gen_graph(data_set['Enrollments'],'enrollments','enrollments','user_id'))

#if __name__ == "__main__":
app.run_server(debug=True)
