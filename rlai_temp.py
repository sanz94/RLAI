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
# Module to create Environments for your AI agent to train in
import RLAI
# Even if it's unused, you need to keep it here to 
# #create your custom gym environment
import numpy as np
import random
import math



class Reinforcement:

    def __init__(self, debug=True):
        # Dictionary to store the values of colors parsed from a txt/csv file
        self.colordict = []

        self.result = dict()
        # Debug set by default to True to print all messages. Setting to debug to False causes
        self.debug = debug
        # significant performance improvements
    
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
    
    def calculate_SD(self, data):
        mean = sum(data)/len(data)
        #print(mean)
        a = list()
        for x in data:
            a.append(pow(abs(x-mean), 2))
        sd = math.sqrt(sum(a)/(len(a)-1))
        #print(sd)
        negative_sd_3 = round(mean - (sd*3), 3)
        positive_sd_3 = round(mean + (sd*3), 3)
        return negative_sd_3, positive_sd_3

    def parse_file(self, sensor_files):
        """
        Function to parse text file to read in color values
        """
        for sensor_file in sensor_files:
            humidityList = []
            temList = []
            pressureList = []
            try:
                fp = open(sensor_file, 'r')
            except FileNotFoundError:
                print("Cannot open or find file {} in {}", format(sensor_file, os.curdir))
                sys.exit()

            with fp:
                for linenumber, line in enumerate(fp):
                    line = line.strip('\n')
                    data = line.split('\t')
                    self.colordict.append(line)
                    humidityList.append(float(data[2]))
                    temList.append(float(data[3]))
                    pressureList.append(float(data[4]))
            temp_sd = self.calculate_SD(temList)
            pressure_sd = self.calculate_SD(pressureList)
            humidity_sd = self.calculate_SD(humidityList)
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
        epsilon = 0.1  # exploration vs exploitation
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
        env.colorvalues(self.colordict)  # send our color dictionary to our environment function
        env.state(self.temList)

        # creating the Q-table using numpy
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

r = Reinforcement(True)
sensor_files = r.get_sensor_original_file()
result_dict = r.parse_file(sensor_files)
print(result_dict)