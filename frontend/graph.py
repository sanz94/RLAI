import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask,render_template, request

app = Flask(__name__, static_url_path='/static')
#For no caching of the static folder
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

IMAGE_FOLDER = os.path.join('static')
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
        if file_name.endswith(".csv"):
            sensor_files.append(file_name)
    return sensor_files

def plot_graphs(sensor_file):
        """
        Function to read csv file selected in dropdown and plot the graphs for each day 
        and save the graph in static folder as test.png
        """
        try:
            #Read csv file seperated by , and parse the time column as date object
            data = pd.read_csv(sensor_file, sep=',', parse_dates=['Time'])
            #Create data to plot as per time and temperature
            temp_cols = ['Time', 'Temperature']
            temp_data = data[temp_cols]

            #Create data to plot as per time and humidity
            humidity_cols = ['Time', 'Humidity']
            hum_data = data[humidity_cols]

            #Create data to plot as per time and pressure
            pressure_cols = ['Time', 'Pressure']
            pressure_data = data[pressure_cols]
        except FileNotFoundError:
            print("Cannot open or find file {} in {}", format(sensor_file, os.curdir))
            sys.exit()
        #Create the subplot with 3 column to display 3 graph side by side
        fig2, ax2 = plt.subplots(nrows=1, ncols=3)
        fig2.set_size_inches(24, 8)
        plt.subplots_adjust(wspace=0.2)
            
        #Plot temperature graph in column 1
        temp_data.plot(x='Time', y='Temperature',ax=ax2[0])
        #Plot humidity graph in column 2
        hum_data.plot(x='Time', y='Humidity',ax=ax2[1])
        #Plot Pressure graph in column 3
        pressure_data.plot(x='Time', y='Pressure',ax=ax2[2])
        #Path of the static folder where image has to be saved
        path2 = os.path.join(app.root_path,app.config['UPLOAD_FOLDER'])
        
        #Remove the image if it exist as savefig do not overwrite the file if already exist
        if os.path.isfile(path2+"/test.png"):
            os.remove(path2+"/test.png") 
        #save the graph as image
        plt.savefig(path2+"/test.png")


@app.route('/test')
def Get_data():
    #display the dropdown with data files name 
    file_names = get_sensor_original_file()
    return render_template('test.html', file_names=file_names)

@app.route('/graph',methods=['Post'])
def plot_graph_html():
    #create graph as image and display in html
    plot_graphs(request.form.get("file_names"))
    #get the path where image is saved ie static folder
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'],'test.png')
    return render_template('graph.html',user_image = full_filename)

if __name__ == "__main__":
    app.run()   