import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import time
import os

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')
app = flask.Flask(__name__, static_folder="../static/dist", template_folder="../static")
IMAGE_FOLDER = os.path.join('static','js')
DATA_FOLDER = os.path.join(app.root_path,'dataset')

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
def get_sensor_original_file():
    """Get the file names from dataset folder to display in drop down"""
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
    return sensor_files
filename = get_sensor_original_file()

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    html.H1('Weather'),
    dcc.Dropdown(
        id='my-dropdown',
        options=filename
    ),
    html.Div([]),
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
              [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
    df = pd.read_csv(selected_dropdown_value, sep=',', parse_dates=['Time'])
    return {
        'data': [{
            'x': df.Time,
            'y': df.Temperature,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'title':'Temperature',
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }

@app.callback(Output('humidity-graph', 'figure'),
              [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
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
            'title':'Humidity',
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }


@app.callback(Output('pressure-graph', 'figure'),
              [Input('my-dropdown', 'value')])

def update_pressure_graph(selected_dropdown_value):
    df = pd.read_csv(selected_dropdown_value, sep=',', parse_dates=['Time'])
   
    #dff = df[df['Stock'] == selected_dropdown_value]
    return {
        'data': [{
            'x': df.Time,
            'y': df.Pressure,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'title':'Pressure',
            'margin': {
                'l': 20,
                'r': 20,
                'b': 30,
                't': 20
            },
            'xaxis' : {
                
            }
        }
    }

if __name__ == '__main__':
    app.run_server()
