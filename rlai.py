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
# Module to create Environments for your AI agent to train in
import RLAI
# Even if it's unused, you need to keep it here to create your custom gym environment
import numpy as np
import random
import pandas as pd
from bokeh.palettes import Spectral11
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import row
output_file('temp.html')

class Reinforcement:

    def __init__(self, filename, debug=True):

        self.colordict = []  # Dictionary to store the values of colors parsed from a txt/csv file
        self.filename = filename
        self.debug = debug  # Debug set by default to True to print all messages. Setting to debug to False causes
        # significant performance improvements

    def parse_file(self):
        """
        Function to parse text file to read in color values
        """

        try:
            fp = open(self.filename, 'r')
        except FileNotFoundError:
            print("Cannot open or find file {} in {}", format(self.filename, os.curdir))
            sys.exit()

        with fp:
            for linenumber, line in enumerate(fp):
                line = line.strip('\n')
                self.colordict.append(line)

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

        # creating the Q-table using numpy
        Q = np.zeros([env.observation_space.n, env.action_space.n])
        #  number of rows and columns is based on (number of states) X (number of actions)

        epochs = 0
        penalties, reward = 0, 0
        plots = []

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
            if episode % 500 == 0:  # display info every 50th episode
                print('Episode {} Total Reward: {}'.format(episode, G))
                print(info)  # Ignore unreferenced warning? Since it will never be called before it goes int while loop
                print('Q table: {}'.format(Q))
                plots += [self.graph_q(Q, episode)]
            if episode == 5000:
                show(row(plots))
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
        #     # Put each rendered frame into the dictionary for animation
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
        toy_df = pd.DataFrame(data=Q, columns = ('bright', 'dark'), index = range(0,10))   

        numlines=len(toy_df.columns)
        # mypalette=Spectral11[0:numlines]

        p = figure(width=500, height=300, title = "Episode " + str(episode) + ": Q-Table", x_axis_label="Data #", y_axis_label="Confidence Level") 
        p.multi_line(xs=[toy_df.index.values]*numlines,
                        ys=[toy_df[name].values for name in toy_df],
                        line_color=['#000000', '#FF0000'],
                        line_width=5)
        return p

    # def graph_data(self, colordict):
    #     """
    #     Graphs current data values on layered line graph.
    #     """
    #     toy_df = pd.DataFrame(data=colordict, columns = ('humidity', 'temperature', 'pressure'), index = range(1,7765))   

    #     numlines=len(toy_df.columns)
    #     mypalette=Spectral11[0:numlines]

    #     p = figure(width=500, height=300) 
    #     p.multi_line(xs=[toy_df.index.values]*numlines,
    #                     ys=[toy_df[name].values for name in toy_df],
    #                     line_color=mypalette,
    #                     line_width=5)
    #     show(p)


r = Reinforcement("fakevalues.txt", False)  # pass file name which contains color values and a debug parameter
r.parse_file()
r.q_learning()
