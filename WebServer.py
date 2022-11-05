#!/usr/bin/env python

from setup import *
from graphData import *
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Check if Temp Sensor has errors - add to a list to print in warning
glabs = []
tlabs = ['Super', 'Brood', 'Outside', 'Roof']
tvars = ['temp1', 'temp2', 'temp3', 'temp4']
for f, l in zip(tvars, tlabs):
    if f in error_fields:
        glabs.append(l)

# Create Graphs

app = dash.Dash(__name__)
server = app.server

if len(glabs) > 0 :
    print(f"Error with Temp Readings: {', '.join(glabs)}")

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

    #Weight Sensors
    dcc.Checklist(
        id = 'checklist3', # How to choose group category
        options=[{'label': x, 'value': y}
                 for x,y in zip(weight_timegrp_lab, weight_timegrp)], # Loop through to choose Label/Value for Checkbox
        value = weight_timegrp, # Specify Starting Value
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='line-chart3'),
])

@app.callback(
     Output('line-chart1', 'figure'),
     [Input('checklist1', 'value')])

def update_line_chart(timegrp):
    mask = rdgs_plt.daygrp.isin(timegrp)
    tfig = px.line(rdgs_plt[mask],
                 x = 'datetime', y='reading', color='sensor_label',
                  labels={'datetime': "Date & Time of Reading",
                          'reading': "Sensor Value",
                          'sensor_label': "Sensor Location"},
                  title="Temperature")
    return tfig

@app.callback(
     Output('line-chart2', 'figure'),
     [Input('checklist2', 'value')])

def update_line_chart(humid_timegrp):
    mask = humid_plt.daygrp.isin(humid_timegrp)
    hfig = px.line(humid_plt[mask],
                 x = 'datetime', y='reading', color='sensor_label',
                  labels={'datetime': "Date & Time of Reading",
                          'reading': "Sensor Value",
                          'sensor_label': "Sensor Location"},
                  title="Humidity")
#     fig.update_layout(legend=dict(
#         orientation="h",
#         yanchor="bottom", y=1.02,
#         xanchor="right", x=1))
    return hfig

@app.callback(
     Output('line-chart3', 'figure'),
     [Input('checklist3', 'value')])

def update_line_chart(weight_timegrp):
    mask = weight_plt.daygrp.isin(weight_timegrp)
    wfig = px.scatter(weight_plt[mask],
                 x = 'datetime', y='reading', color='weightsensor', trendline="lowess", 
                  labels={'datetime': "Date & Time of Reading",
                          'reading': "Sensor Value"},
                  title="Weight (Kg)")
    wfig.update_traces(marker_symbol="circle-open")
    wfig.update_layout(showlegend=False) # Only 1 Reading so not needed
    return wfig

#app.run_server(debug=False, host='0.0.0.0', port=8050)

if __name__ == '__main__':
    app.run_server(debug=True)

