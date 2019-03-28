"""
Custom Environment for our AI agent to train to sort colors and find anamolies in given data sets
@author(s): Sanjeev Rajasekaran
Start date: 02/22/2019
End date: 03/23/2019
Version - 0.0.3
"""


import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random
from datetime import datetime

class rlaiEnv_temp(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, options=24):

        self.n = options
        self.input = dict()  # input which will be set to the values we read from the file
        self.state = [None, None] # state aka current guesses by our AI
        self.actions = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"]  # available actions for our AI (Valid or invalid sensor)
        self.reward = 0
        self.done = 0
        self.counter = 0
        self.action_space = spaces.Discrete(self.n)  # actions = self.n = 2 (RED/BLACK)
        self.observation_space = spaces.Discrete(2)  # states aka observations = 3 (3 sensor files)
        self.perfect = True  # if the AI agent gets everything right, it gets a huge +10 reward points

    def sensorValue(self, sensorinput, max_time):
        """
        Function to set self.input to whatever Sensor SD we read in from the file specified
        :param inputcolors: Dicitonary containing sensors SD values
        :return: None
        """

        self.input = sensorinput
        self.max_time = max_time

    def check(self, offset):
        """
        Function to compare our AI guess and the correct answer
        :return: Boolean based on comparison
        """

        # check if the value our AI guessed is correct and return True or False
        if int(self.state[self.counter]) == self.max_time[offset].hour:
            return True
        else:
            return False


    def step(self, action):
        """
        Function to perform the next step/iteration taken by our AI in the environment
        :param action: Integer from 0-1
        :return: [self.counter-1, self.reward, self.done, self.state]
        Self.counter is the current number of iterations taken
        We do (Self.counter)-1 because when our code runs we increment the counter before our return but in our return
        we want to return the first iteration as 0 and not 1.
        self.reward is the current reward
        self.done is if the system is done or not for the current episode
        self.state will be the info we print out containing our systems guesses
        """

        # If more than 3 episodes, we set done to 1 and check if it's perfect or not
        if self.counter >= 2:
            self.done = 1
            if self.perfect:
                self.reward += 10  # if perfect, award a reward of 10 times the normal reward

        if self.done == 1:
            print("Episode completed")
            return [self.counter-1, self.reward, self.done, self.state]

        if self.actions[action] == '0':
            self.state[self.counter] = "0"
        elif self.actions[action] == '1':
            self.state[self.counter] = "1"
        elif self.actions[action] == '2':
            self.state[self.counter] = "2"
        elif self.actions[action] == '3':
            self.state[self.counter] = "3"
        elif self.actions[action] == '4':
            self.state[self.counter] = "4"
        elif self.actions[action] == '5':
            self.state[self.counter] = "5"
        elif self.actions[action] == '6':
            self.state[self.counter] = "6"
        elif self.actions[action] == '7':
            self.state[self.counter] = "7"
        elif self.actions[action] == '8':
            self.state[self.counter] = "8"
        elif self.actions[action] == '9':
            self.state[self.counter] = "9"
        elif self.actions[action] == '10':
            self.state[self.counter] = "10"
        elif self.actions[action] == '11':
            self.state[self.counter] = "11"
        elif self.actions[action] == '12':
            self.state[self.counter] = "12"
        elif self.actions[action] == '13':
            self.state[self.counter] = "13"
        elif self.actions[action] == '14':
            self.state[self.counter] = "14"
        elif self.actions[action] == '15':
            self.state[self.counter] = "15"
        elif self.actions[action] == '16':
            self.state[self.counter] = "16"
        elif self.actions[action] == '17':
            self.state[self.counter] = "17"
        elif self.actions[action] == '18':
            self.state[self.counter] = "18"
        elif self.actions[action] == '19':
            self.state[self.counter] = "19"
        elif self.actions[action] == '20':
            self.state[self.counter] = "20"
        elif self.actions[action] == '21':
            self.state[self.counter] = "21"
        elif self.actions[action] == '22':
            self.state[self.counter] = "22"
        elif self.actions[action] == '23':
            self.state[self.counter] = "23"
        elif self.actions[action] == '24':
            self.state[self.counter] = "24"


        if self.counter < 2:
            res = self.check(self.counter) # use check to compare guessed value and correct value

 # if return value is True, give a positive reward
            if res == True:
                self.reward += 5
            else:
                self.reward -= 5
                self.perfect = False
 # if return is False, give a negative reward and set perfect to False.


        self.counter += 1
        if self.counter == 2:
            return [0, self.reward, self.done, self.state]

        # print("Current State: {} \n Reward: {} \n Done: {}".format(self.state, self.reward, self.done))
        return [self.counter, self.reward, self.done, self.state]


    def reset(self):
        """
        Reset used to set values back to default values
        :return: integer self.counter set to 0
        """

        self.counter = 0
        self.done = 0
        self.reward = 0
        self.perfect = True
        self.state = [None, None]
        return self.counter

    def render(self, mode='human', close=False):
        """
        This function is normally used in gym to render frames. But since our program is not graphic related, we are
        not using this for now atleast
        :return: None
        """
        print("Render over")
