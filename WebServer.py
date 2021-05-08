#!/usr/bin/env python

from setup import *
from graphData import *
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    # Temp Sensors
    dcc.Checklist(
        id = 'checklist1', # How to choose group category
        options=[
            {'label': x, 'value': y}
                 for x,y in zip(timegrp_lab, timegrp)], # Loop through to choose Label/Value for Checkbox
        value = timegrp, # Specify Starting Value
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='line-chart1'),
    
    # Humid Sensors
    dcc.Checklist(
        id = 'checklist2', # How to choose group category
        options=[{'label': x, 'value': y}
                 for x,y in zip(humid_timegrp_lab, humid_timegrp)], # Loop through to choose Label/Value for Checkbox
        value = humid_timegrp, # Specify Starting Value
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='line-chart2'),
])

@app.callback(
     Output('line-chart1', 'figure'),
     [Input('checklist1', 'value')])

def update_line_chart(timegrp):
    mask = rdgs_plt.daygrp.isin(timegrp)
    fig = px.line(rdgs_plt[mask],
                 x = 'datetime', y='reading', color='tempsensor')
    return fig

@app.callback(
     Output('line-chart2', 'figure'),
     [Input('checklist2', 'value')])

def update_line_chart(timegrp):
    mask = humid_plt.daygrp.isin(humid_timegrp)
    fig = px.line(humid_plt[mask],
                 x = 'datetime', y='reading', color='humidsensor')
    return fig

#app.run_server(debug=False, host='0.0.0.0', port=8050)
if __name__ == '__main__':
    app.run_server(debug=True)