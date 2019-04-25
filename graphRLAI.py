import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import time
import os
from datetime import datetime
import timestring
from rlai import Reinforcement

import csv
import base64
from urllib.parse import quote as urlquote

import re
import numpy as np

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

#Get current date to set calender max date
current_date = datetime.now()
app.title = 'RLAI'

app.layout = html.Div([
    html.H1('RLAI Weather'),
    html.H2("Upload Data File"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to browse for upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.Div(id='output'),
        html.Ul(id="file-list",style={'list-style-type': 'none'}),
        dcc.DatePickerSingle(
            id='my-date-picker',
            min_date_allowed=datetime(2018, 12, 6),
            max_date_allowed=datetime(current_date.year, current_date.month, current_date.day),
        ),
        html.H1(id='record-error'),
        dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Temperature', value='tab-1'),
        dcc.Tab(label='Humidity', value='tab-2'),
        dcc.Tab(label='Pressure', value='tab-3'),
        ]),
        html.Div(id='tabs-content')
    ], className="container")

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

# START KIPSY: Code to read sensor data for the date selected

# To get rid of error on update_output function
app.config['suppress_callback_exceptions']=True

CURRENT_DIRECTORY = os.getcwd()
UPLOAD_DIRECTORY = CURRENT_DIRECTORY + "/dataset/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)

def file_download_csv(selected_date):
    """Convert TSV to CSV file."""
    if selected_date != None:
        tsv_file_name = "sensorData.tsv"
        csv_file_name = selected_date + ".csv"
        tsv_file_path = UPLOAD_DIRECTORY + "\\" + tsv_file_name
        csv_file_path = UPLOAD_DIRECTORY + "\\" + csv_file_name
        if not os.path.isfile(csv_file_path):
            sensorData = pd.read_csv(tsv_file_path, sep='\t', header = None)
            sensorData.columns = ["No","Time","Humidity","Temperature","Pressure","NA"]
            selectedData = sensorData['Time'].str.contains(selected_date)
            sensorData1 = sensorData[selectedData]
            sensorData1['Humidity'] = pd.to_numeric(sensorData1['Humidity'],errors='coerce')
            sensorData1['Temperature'] = pd.to_numeric(sensorData1['Temperature'],errors='coerce')
            sensorData1['Pressure'] = pd.to_numeric(sensorData1['Pressure'],errors='coerce')
            formatTime= sensorData1['Time'].unique()
            
            formatedData = sensorData1.groupby(['Time']).mean()
            formatedData['Time'] = formatTime
            cols = ["No","Time","Humidity","Temperature","Pressure"]
            formatedData = formatedData[cols]
            formatedData.to_csv(csv_file_path, index = False)
        return csv_file_path

@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")])
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)
    files = uploaded_files()
    if len(files) != 0:
        return [html.Li("")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]

@app.callback(Output('output', 'children'), [Input('upload-data', 'filename')])
def message(filename):
    time.sleep(2)
    filename = ''.join(filename)
    return 'Uploaded ' + filename

# END KIPSY's Code


@app.callback(Output('record-error', 'children'),
                    [Input('my-date-picker', 'date')])
def sensor_data_error(selcted_date):
    file_name = file_download_csv(selcted_date)
    df = pd.read_csv(file_name, sep=',', parse_dates=['Time'])
    if df.empty:
        return "Sensor data not present"
    else:
        return ""

@app.callback(Output('graph-container', 'style'), [Input('my-date-picker', 'date')])
def hide_graph(selcted_date):
    file_name = file_download_csv(selcted_date)
    df = pd.read_csv(file_name, sep=',', parse_dates=['Time'])
    if not df.empty:
        return {'display':'block'}
    return {'display':'none'}

@app.callback(Output('tabs-content', 'children'),
              [Input('my-date-picker', 'date'),Input('tabs', 'value')])
#Data to create temperature graph
def update_temp_graph(selcted_date,tab):
    file_name = file_download_csv(selcted_date)
    df = pd.read_csv(file_name, sep=',', parse_dates=['Time'])
    df = df.sort_values(by='Time')
    r=Reinforcement(file_name,False)
    sen_files = r.get_sensor_original_file()
    result=r.parse_file(sen_files)
    if result:
        out =r.q_learning()
        time = selcted_date+" "+str(out) +":00:00"
        qdate = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        endtime = selcted_date+" "+str(int(out) + 1) +":00:00"
        endtime = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
        df1 = df[(df.Time > qdate) & (df.Time < endtime)]
        if tab == 'tab-1':
            return html.Div([
                dcc.Graph(
                    id='graph-1-tabs',
                    figure={
                        'data': [{
                            'x': df.Time,
                            'y': df.Temperature,
                            'scatter': {
                            'width': 1,
                            'shape': 'spline'
                            }
                        }]
                    }
                )
            ])
        elif tab == 'tab-2':
            return html.Div([
                dcc.Graph(
                    id='graph-2-tabs',
                    figure={
                    'data': [{
                        'x': df.Time,
                        'y': df.Humidity,
                        'name':'Humidity',
                        'scatter': {
                            'width': 1
                        }
                     },
                        {
                        'x': df1.Time,
                        'y': df1.Humidity,
                        'name':'Max people',
                        'scatter': {
                        'width': 1
                        }
                    }]
                }
                )
            ])
        elif tab == 'tab-3':
            return html.Div([
                dcc.Graph(
                    id='graph-1-tabs',
                    figure={
                    'data': [{
                        'x': df.Time,
                        'y': df.Pressure,
                        'line': {
                          'width': 1,
                         'shape': 'spline'
                         }
                        }]
                }
            )
            ])


if __name__ == '__main__':
    app.run_server()