import os
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash import dash_table
from datetime import datetime 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


data = pd.read_csv('lesiones_pollos.csv')
data = data.astype({'fecha':'datetime64[ns]'}, errors='ignore')

lesi_drop_list = data['lesionTipo'].unique()
lesi_drop_list = np.insert(lesi_drop_list, 0, 'Todas', axis=0)
gran_drop_list = data['granja'].unique()
gran_drop_list =  np.insert(gran_drop_list, 0, 'Todas', axis=0)

first_date = data.fecha.min()
lasT_date = data.fecha.max()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

PAGESIZE = 33

app.layout = dbc.Container(
    [
        html.H1("Información Lesiones Pollos"),
        html.Hr(),
        dash_table.DataTable(id='table_grid', 
                            columns=[
                                {'name': i ,'id':i} for i in data.columns
                                ],
                                page_current= 0,
                                page_size=PAGESIZE,
                                page_action='custom'
                            ),
        dbc.FormGroup(
            [
                dbc.Label("Granja"),
                dcc.Dropdown(
                    id='dGranja',
                    value='Todas',
                    clearable=False,
                    multi=False,
                    disabled=False,
                    searchable=True,
                    persistence='string',
                    persistence_type='local',
                    options= [
                        {'label': i, 'value':i}
                        for i in gran_drop_list
                    ],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Lesión"),
                dcc.Dropdown(
                    id='dLesion',
                    value='Todas',
                    clearable=False,
                    multi=False,
                    disabled=False,
                    searchable=True,
                    persistence='string',
                    persistence_type='local',
                    options=[
 
                        {'label': i, 'value':i}
                        for i in lesi_drop_list
                    ],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Rango De Fechas"),
                dbc.FormGroup(
                    dcc.DatePickerRange(
                        id = 'date_range',
                        min_date_allowed=first_date,
                        max_date_allowed=lasT_date,
                        start_date=first_date,
                        end_date=lasT_date
                    )
                )
            ]
        ),
    ],
    fluid=True,
)

@app.callback(
    Output('table_grid', 'data'),
    [
        Input('table_grid', 'page_current'),
        Input('table_grid', 'page_size'),
        Input('dGranja', 'value'),
        Input('dLesion', 'value'),
        Input('date_range', 'start_date'),
        Input('date_range', 'end_date')
    ]
)

def update_table(page_current, page_size, granja, lesion, start_date, end_date):
    
    if lesion == 'Todas' and granja == 'Todas':
        consulta = data.loc[(data['fecha'] >= start_date) & (data['fecha'] <= end_date)]
        print(consulta.head(10))
    elif lesion == 'Todas' and granja != 'Todas':
        consulta = data.loc[(data['granja'] == granja) & (data['fecha'] >= start_date) & (data['fecha'] <= end_date)]
    elif lesion != 'Todas' and granja == 'Todas':
        consulta = data.loc[(data['lesionTipo'] == lesion)& (data['fecha'] >= start_date) & (data['fecha'] <= end_date)]
    else:
        consulta = data.loc[(data['granja'] == granja) & (data['lesionTipo'] == lesion) & (data['fecha'] >= start_date) & (data['fecha'] <= end_date)]
        
    consulta.reset_index(drop=True, inplace=True)
    consulta = consulta.iloc[page_current*page_size:(page_current+1)*page_size]

    

    return consulta.to_dict('records')
    
#app.run_server(mode='inline')
if __name__ == '__main__':
    app.run_server(debug=True)