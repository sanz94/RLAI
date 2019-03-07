"""
Program to implement a Reinforcement learning based Q-learning algorithm to 
perform functions such as Sorting and
finding anamolies in sensor data
@author(s): Sanjeev Rajasekaran, Kipsy Quevada, Suchita Dmello
Start date: 02/22/2019
End date: ~
Version - 0.0.1
"""

import os
import sys
import gym
import csv
# Module to create Environments for your AI agent to train in
import RLAI
# Even if it's unused, you need to keep it here to 
# #create your custom gym environment
import numpy as np
import random
import math
from numpy import genfromtxt
import pandas as pd
from bokeh.palettes import Spectral11
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import row
output_file('temp.html')
output_file('temp2.html')
output_file('temp3.html')

class Reinforcement:

    def __init__(self, debug=True):
        #dictionary to store the dictionary holding standard deviation of temperature,pressure,humidity 
        # for each sensor
        self.result = dict()
        # Debug set by default to True to print all messages. Setting to debug to False causes
        self.debug = debug
        # significant performance improvements
    
    #return all the sensor data files name from the directory
    def get_sensor_original_file(self):
        sensor_files = list()
        try:
            file_list = os.listdir(path='.')
        except (TypeError, FileNotFoundError):
            print("Invalid directory path")
            exit()
        else:
            for file_name in file_list:
                if file_name.startswith("sensorData"):
                    sensor_files.append(file_name)
        print(sensor_files)
        return sensor_files
    
    #Calculate the standard deviation for list of data passed
    def calculate_SD(self, data):
        mean = sum(data)/len(data)
        a = list()
        for x in data:
            a.append(pow(abs(x-mean), 2))
        sd = math.sqrt(sum(a)/(len(a)-1))
        negative_sd_3 = round(mean - (sd*3), 3)
        positive_sd_3 = round(mean + (sd*3), 3)
        return negative_sd_3, positive_sd_3

    def store_qtable(self, q_Table):
        """
        Store the Q-table as a text file to use it as a "memory" or database
        """

        # should_store = self.check_if_store("Qmemory.csv", q_Table)

        try:
            with open('Qmemory.csv', 'w+', newline='') as csvfile:
                writerObj = csv.writer(csvfile)
                for value in q_Table:
                    writerObj.writerow([str(value[0]), str(value[1])])
        except IOError:
            print("Cannot create or open Qmemory.csv in path {}", format(os.curdir))
            sys.exit()


    def parse_file(self, sensor_files):
        """
        Function to parse text file to read each sensor file
        """
        #get each sensor file name
        for sensor_file in sensor_files:
            humidityList = []
            temList = []
            pressureList = []
            self.plots = []
            try:
                fp = open(sensor_file, 'r')
            except FileNotFoundError:
                print("Cannot open or find file {} in {}", format(sensor_file, os.curdir))
                sys.exit()

            with fp:
                for linenumber, line in enumerate(fp):
                    line = line.strip('\n')
                    data = line.split('\t')
                    #List of humidity value of each sensor
                    humidityList.append(float(data[2]))
                    #List of temperature value of each sensor
                    temList.append(float(data[3]))
                    #List of pressure value of each sensor
                    pressureList.append(float(data[4]))
            #graph all three sensor data
            self.plots += [self.graph_humidity(humidityList), self.graph_temperature(temList), self.graph_pressure(pressureList)]
            show(row(self.plots))
            #calculate 3 Standard deviations for the temperature
            temp_sd = self.calculate_SD(temList)
            #calculate 3 Standard deviations for the pressure
            pressure_sd = self.calculate_SD(pressureList)
            #calculate 3 Standard deviations for the humidity
            humidity_sd = self.calculate_SD(humidityList)
            #add in result dictionary - key as file name 
            # and standard deviation as value
            self.result[sensor_file] = {'temperature': temp_sd, 'humidity': humidity_sd, 'pressure': pressure_sd}
        return self.result
                
    def q_learning(self):
        """
        Process goes like this:
        1. Initialize Q-table
        2.Choose an action
        3. Perform action
        4. Measure reward
        5. Update Q-table
        :return:
        """

        # Hyperparameters
        alpha = 0.618  # mathematical value of pi or something
        gamma = 0.6  # decay value ?
        epsilon = 0.4  # exploration vs exploitation
        G = 0

        """
           alpha α: (the learning rate) should decrease as you continue to gain a larger and larger knowledge base.
           gamma γ: as you get closer and closer to the deadline, your preference for near-term reward should increase,
              as you won't be around long enough to get the long-term reward, which means your gamma should decrease
           epsilon ϵ: as we develop our strategy, we have less need of exploration and more exploitation to get more 
              utility from our policy, so as trials increase, epsilon should decrease.
        """

        # Creating the env
        env = gym.make("rlai-v002")  # create our custom environment using Gym
        env.sensorValue(self.result)  # send our color dictionary to our environment function
        # creating the Q-table using numpy
        # create Q table with zeros if there is no memory. If there is, read from file
        if os.path.isfile("Qmemory.csv"):
            Q = genfromtxt('Qmemory.csv', delimiter=',')
        else:
            Q = np.zeros([env.observation_space.n, env.action_space.n])
        #  number of rows and columns is based on (number of states) X (number of actions)

        epochs = 0
        penalties, reward = 0, 0

        for episode in range(1, 5001):  # how many episodes you want to train your agent, the longer the better always
            done = False
            G, reward = 0, 0
            state = env.reset()  # reset environment variables to default at start
            while not done:

                if random.uniform(0, 1) < epsilon:
                    action = env.action_space.sample()  # Explore action space
                else:
                    action = np.argmax(Q[state])  # Exploit learned values
                if self.debug:
                    print("Current Action: {}".format(action))
                next_state, reward, done, info = env.step(action)  # Pass chosen action to our environment step function
                #  Step is the next 'step' or action the agent takes in our environment. Think of it as one iteration
                #  of a for loop
                if self.debug:
                    print("Steps taken: {}".format(next_state))
                    print("Current State: {}".format(info))

                # ---Uppercase = Normal state, and (&) = subscript, power of (^) = superscript
                # Formula used: Q&(t+1) (StAt) = Q&t (S&t, a&t) + alpha&t(S&t, a&t) * [ R&(t+1) +
                # Discount Factor MAX&a Q&t (S&(t+1), a&t) - Q&t(S&t, a&t)
                # First Q&t (S&t, a&t) = Old Value
                # Second alpha&t(S&t, a&t) is the learning rate defined above as 0.618 which is the value of pi
                # Third, [ R&(t+1) + Discount Factor MAX&a Q&t (S&(t+1), a&t) Together make the learned value of model
                # R is the reward
                # Max is used to choose the highest Q value from the table to determine which action gets the
                # optimal future reward

                old_value = Q[state, action]
                next_max = np.max(Q[next_state])

                Q[state, action] = round(((1 - alpha) * old_value + alpha * (reward + gamma * next_max)), 4)

                # alternative: alpha *(reward + np.max(Q[next_state]) - Q[state, action])

                G += reward
                if reward == -10:  # if agent keeps getting negative rewards, incur a penalty
                    penalties += 1
                state = next_state
            if episode % 50 == 0:  # display info every 50th episode
                print('Episode {} Total Reward: {}'.format(episode, G))
                print(info)  # Ignore unreferenced warning? Since it will never be called before it goes int while loop
                print('Q table: {}'.format(Q))
            # if episode == 5000:
                # show(self.graph_q(Q, episode))
        self.store_qtable(Q)

        """
        Below is implementation without using Q-learning using a completely random approach. Q learning is around
        50 times more efficient than below code
        """
        # while not done:
        #     action = env.action_space.sample()
        #     # print("Action chosen: {}".format(action))
        #     state, reward, done, info = env.step(action)
        #
        #     if reward == -10:
        #         penalties += 1
        #
        #     # clePut each rendered frame into the dictionary for animation
        #
        #     print("Current Action: {} \n Reward: {} \n Current State: {}".format(action, reward, state))
        #
        #     epochs += 1
        # print("Timesteps taken: {}".format(epochs))
        # print("Penalties incurred: {}".format(penalties))

        # Printing all the possible actions, states, rewards.

    def graph_q(self, Q, episode):
        """
        Graphs Q table values on layered line graph.
        """
        toy_df = pd.DataFrame(data=Q, columns = ('valid', 'invalid'), index = range(0,3))   

        numlines=len(toy_df.columns)
        # mypalette=Spectral11[0:numlines]

        p = figure(width=500, height=300, title = "Final Q-Table", x_axis_label="Data #", y_axis_label="Confidence Level") 
        p.multi_line(xs=[toy_df.index.values]*numlines,
                        ys=[toy_df[name].values for name in toy_df],
                        line_color=['#000000', '#FF0000'],
                        line_width=5)
        return p

    def graph_humidity(self, s_data):
        """
        Graphs current data values on layered line graph.
        """
        toy_df = pd.DataFrame(data=s_data, columns = ['humidity'], index = range(1,7765))   

        numlines=len(toy_df.columns)
        mypalette=Spectral11[0:numlines]

        p = figure(width=500, height=300, title = "Humidity Data Values", x_axis_label="Data #", y_axis_label="% Humidity") 
        p.multi_line(xs=[toy_df.index.values]*numlines,
                        ys=[toy_df[name].values for name in toy_df],
                        line_color=mypalette,
                        line_width=5)
        return p

    def graph_temperature(self, s_data):
        """
        Graphs current data values on layered line graph.
        """
        toy_df = pd.DataFrame(data=s_data, columns = ['temperature'], index = range(1,7765))   

        numlines=len(toy_df.columns)
        mypalette=Spectral11[0:numlines]

        p = figure(width=500, height=300, title = "Temperature Data Values", x_axis_label="Data #", y_axis_label="Degrees Fahrenheit") 
        p.multi_line(xs=[toy_df.index.values]*numlines,
                        ys=[toy_df[name].values for name in toy_df],
                        line_color=mypalette,
                        line_width=5)
        return p

    def graph_pressure(self, s_data):
        """
        Graphs current data values on layered line graph.
        """
        toy_df = pd.DataFrame(data=s_data, columns = ['pressure'], index = range(1,7765))   

        numlines=len(toy_df.columns)
        mypalette=Spectral11[0:numlines]

        p = figure(width=500, height=300, title = "Pressure Data Values", x_axis_label="Data #", y_axis_label="Atmospheric Pressure") 
        p.multi_line(xs=[toy_df.index.values]*numlines,
                        ys=[toy_df[name].values for name in toy_df],
                        line_color=mypalette,
                        line_width=5)
        return p

r = Reinforcement(True)
sensor_files = r.get_sensor_original_file()
result_dict = r.parse_file(sensor_files)
r.q_learning()