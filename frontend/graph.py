import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
from datetime import datetime

def get_sensor_original_file():
        sensor_files = list()
        path1 = os.getcwd()+'/frontend/dataset/'
        os.chdir(path1)
        try:
            file_list = os.listdir(path='.')
        except (TypeError, FileNotFoundError):
            print("Invalid directory path")
            exit()
        else:
            for file_name in file_list:
                if file_name.endswith(".csv"):
                    sensor_files.append(file_name)
        return sensor_files

def plot_graphs(sensor_files):
        """
        Function to read csv files and plot the graphs for each day
        """
        #get each sensor file name
        for sensor_file in sensor_files:
            try:
                #REad csv file seperated by , and parse the time column as date object
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
            
            plt.show()
            
file_names = get_sensor_original_file()
plot_graphs(file_names)
