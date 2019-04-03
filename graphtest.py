import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import time
import os
from datetime import datetime
import timestring
from rlai import Reinforcement
import csv

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

"""def get_sensor_original_file():
    Get the file names from dataset folder to display in drop down
    sensor_files = list()
    path1 = os.path.join(app.config['DATA_FOLDER'])
    os.chdir(path1)
    try:
        file_list = os.listdir(path='.')
    except (TypeError, FileNotFoundError):
        print("Invalid directory path")
        exit()
    for file_name in file_list:
        filedict = dict()
        if file_name.endswith("Data.csv"):
            filedict["label"] = file_name.split('.')[0]
            filedict["value"] = file_name
            sensor_files.append(filedict)
    return sensor_files"""
#filename = get_sensor_original_file()

#Code to read sensor data for the date selected
def read_sensor_file(selected_date):
    print(selected_date)

r=Reinforcement(False)
sen_files = r.get_sensor_original_file()
r.parse_file(sen_files)
#Get dictionary with key as file name and 
#value as time of that day when there were max people with humidity value of that time
out =r.q_learning()
out_key =[]
for keys,value in out.items():
    out_key.append(keys)
sensor_files = list()
#Create the dict with label value key to display dropdown
for file_name in out_key:
        filedict = dict()
        if file_name.endswith("Data.csv"):
            filedict["label"] = file_name.split('.')[0]
            filedict["value"] = file_name
            sensor_files.append(filedict)

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

#Get current date to set calender max date
current_date = datetime.now()

app.layout = html.Div([
    html.H1('RLAI Weather'),
    dcc.Dropdown(
        id='my-dropdown',
        options=sensor_files
    ),
    dcc.DatePickerSingle(
        id='my-date-picker',
        min_date_allowed=datetime(2018, 12, 6),
        max_date_allowed=datetime(current_date.year, current_date.month, current_date.day),
    ),
    html.Div([
    html.Div([dcc.Graph(id='temp-graph')], className="six columns"),
    html.Div([dcc.Graph(id='humidity-graph')], className="six columns"),
    html.Div([dcc.Graph(id='pressure-graph')], className="six columns"),
    ], className="row")
], className="container")

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(Output('temp-graph', 'figure'),
              [Input('my-dropdown', 'value'),
              Input('my-date-picker', 'date')])

def update_graph(selected_dropdown_value, selcted_date):
    #file_name=read_sensor_file(selcted_date)
    df = pd.read_csv(selected_dropdown_value, sep=',', parse_dates=['Time'])
    
    return {
        'data': [{
            'x': df.Time,
            'y': df.Temperature,
            'line': {
                'width': 1,
                'shape': 'spline'
            }
        }
        
        ],
        'layout': {
            'title':'Temperature'

            
        }
    }

@app.callback(Output('humidity-graph', 'figure'),
              [Input('my-dropdown', 'value'),
              Input('my-date-picker', 'date')])

def update_graph(selected_dropdown_value, selcted_date):
    #file_name=read_sensor_file(selcted_date)
    df = pd.read_csv(selected_dropdown_value, sep=',', parse_dates=['Time'])
       
    return {
        'data': [{
            'x': df.Time,
            'y': df.Humidity,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'title':'Humidity'
        }
    }


@app.callback(Output('pressure-graph', 'figure'),
              [Input('my-dropdown', 'value'),
              Input('my-date-picker', 'date')])

def update_pressure_graph(selected_dropdown_value, selcted_date):
    #file_name=read_sensor_file(selcted_date)
    df = pd.read_csv(selected_dropdown_value, sep=',', parse_dates=['Time'])
    return {
        'data': [{
            'x': df.Time,
            'y': df.Pressure,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }
        
        ],
        'layout': {
            'title':'Pressure'
        }
    }

if __name__ == '__main__':
    app.run_server()
