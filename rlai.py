"""
Program to implement a Reinforcement learning based Q-learning algorithm to perform functions such as Sorting and
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
# Even if it's unused, you need to keep it here to create your custom gym environment
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
from numpy import genfromtxt
from datetime import datetime
from collections import defaultdict


class Reinforcement:

    def __init__(self, debug=True):

        self.humiditydict = defaultdict(dict)  # Dictionary to store the values of colors parsed from a txt/csv file
        self.debug = debug  # Debug set by default to True to print all messages. Setting to debug to False causes
        self.output = {}
        # significant performance improvements

    def get_sensor_original_file(self):
        sensor_files = list()
        path1 = os.getcwd() + '/dataset/'
        if(not os.getcwd().endswith("dataset")):
            os.chdir(path1)
        try:
            file_list = os.listdir(path='.')
        except (TypeError, FileNotFoundError):
            print("Invalid directory path")
            exit()
        else:
            for file_name in file_list:
                if file_name.endswith("Data.csv"):
                    sensor_files.append(file_name)
                    self.output[str(file_name)] = []
        return sensor_files

    def parse_file(self, sensor_files):
        """
        Function to parse text file to read in color values
        """

        for sensor_file in sensor_files:
            try:
                # REad csv file seperated by , and parse the time column as date object
                f = open(sensor_file)
                lines = f.readlines()
                for line in lines[1::]:
                    try:
                        num_date, humidity_temp_pressure = line.split()
                    except ValueError:
                        continue
                    number, date = num_date.split(",")
                    time, humidity, temperature, pressure = humidity_temp_pressure.split(",")
                    self.humiditydict[sensor_file][date+" "+time] = humidity

            except FileNotFoundError:
                print("Cannot open or find file {} in {}", format(sensor_file, os.curdir))
                sys.exit()

    def store_qtable(self, q_Table):
        """
        Store the Q-table as a text file to use it as a "memory" or database
        """

        # should_store = self.check_if_store("Qmemory.csv", q_Table)

        os.chdir(os.getcwd())
        try:
            with open('Qmemory.csv', 'w+', newline='') as csvfile:
                writerObj = csv.writer(csvfile)
                for value in q_Table:
                    writerObj.writerow([str(value[0]), str(value[1]), str(value[2]), str(value[3]), str(value[4]), str(value[5]), str(value[6]), str(value[7]), str(value[8]), str(value[9]), str(value[10]), str(value[11]), str(value[12]), str(value[13]), str(value[14]), str(value[15]), str(value[16]), str(value[17]), str(value[18]), str(value[19]), str(value[20]), str(value[21]), str(value[22]), str(value[23])])
        except IOError:
            print("Cannot create or open Qmemory.csv in path {}", format(os.curdir))
            sys.exit()

    def calc_peak_time(self, sensorvalues):

        max_time = None
        max_humidity = None

        for time, humidity in sensorvalues.items():
            time = datetime.strptime(time, "%m/%d/%y %H:%M")
            lasttime = None
            if time.hour > 22:
                continue
            if time.minute != 0 and lasttime:
                if (time - lasttime).seconds < 3600:
                    continue
            else:
                lasttime = time
                if not max_humidity:
                    max_humidity = humidity
                else:
                    if humidity > max_humidity:
                        max_humidity = humidity
                        max_time = time

        return max_humidity, max_time

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
        alpha = 0.7 # mathematical value of pi or something
        gamma = 0.618  # decay value ?
        epsilon = 1  # exploration vs exploitation
        max_epsilon = 1
        min_epsilon = 0.01
        decay_rate = 0.01
        G = 0

        """
           alpha α: (the learning rate) should decrease as you continue to gain a larger and larger knowledge base.
           gamma γ: as you get closer and closer to the deadline, your preference for near-term reward should increase,
              as you won't be around long enough to get the long-term reward, which means your gamma should decrease
           epsilon ϵ: as we develop our strategy, we have less need of exploration and more exploitation to get more 
              utility from our policy, so as trials increase, epsilon should decrease.
        """

        # Creating the env
        env = gym.make("rlai-v001")  # create our custom environment using Gym
        max_time = []
        max_humidity = []
        output = dict

        for sensor_file in self.humiditydict:
            maxHumidity, maxTime = self.calc_peak_time(self.humiditydict[sensor_file])
            max_time.append(maxTime)
            max_humidity.append(maxHumidity)



        env.sensorValue(self.humiditydict, max_time)  # send our color dictionary to our environment function

        # creating the Q-table using numpy
        # create Q table with zeros if there is no memory. If there is, read from file
        if os.path.isfile("Qmemory.csv"):
            Q = genfromtxt('Qmemory.csv', delimiter=',')
        else:
            Q = np.zeros([env.observation_space.n, env.action_space.n])
        #  number of rows and columns is based on (number of states) X (number of actions)

        epochs = 0
        penalties, reward = 0, 0

        for episode in range(1, 1001):  # how many episodes you want to train your agent, the longer the better always
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

                # next_max = np.max(Q[next_state])

                Q[state, action] = round((old_value + alpha * (reward - old_value)), 2)

                # alternative: alpha *(reward + np.max(Q[next_state]) - Q[state, action])

                G += reward
                if reward == -10:  # if agent keeps getting negative rewards, incur a penalty
                    penalties += 1
                state = next_state
            if episode % 50 == 0:  # display info every 50th episode
                print('Episode {} Total Reward: {}'.format(episode, G))
                print(info)  # Ignore unreferenced warning? Since it will never be called before it goes int while loop
                print('Q table: {}'.format(Q))

            epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate*episode)

        self.store_qtable(Q)
        for offset, file in enumerate(self.output):
            self.output[file].append(info[offset])
            self.output[file].append(max_humidity[offset])
        return self.output


r = Reinforcement(False)  # pass file name which contains color values and a debug parameter
sen_files = r.get_sensor_original_file()
r.parse_file(sen_files)
out = r.q_learning()
print(out)
