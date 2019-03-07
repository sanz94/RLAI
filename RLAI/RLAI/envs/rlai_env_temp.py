"""
Custom Environment for our AI agent to train to sort colors and find anamolies in given data sets
@author(s): Sanjeev Rajasekaran
Start date: 02/22/2019
End date: 02/28/2019
Version - 0.0.2
"""


import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random

# define globals
DARK = "dark"
BRIGHT = "bright"
RED = "red"
BLACK = "black"


class rlaiEnv_temp(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, options=2):

        self.n = options
        self.input = dict()  # input which will be set to the values we read from the file
        self.state = [None, None, None] # state aka current guesses by our AI
        self.actions = ["valid","invalid"]  # available actions for our AI (Valid or invalid sensor)
        self.reward = 0
        self.done = 0
        self.counter = 0
        self.action_space = spaces.Discrete(self.n)  # actions = self.n = 2 (RED/BLACK)
        self.observation_space = spaces.Discrete(3)  # states aka observations = 3 (3 sensor files)
        self.perfect = True  # if the AI agent gets everything right, it gets a huge +10 reward points

    def sensorValue(self, input_sensor):
        """
        Function to set self.input to whatever Sensor SD we read in from the file specified
        :param inputcolors: Dicitonary containing sensors SD values
        :return: None
        """

        self.input = input_sensor

    def check(self):
        """
        Function to compare our AI guess and the correct answer
        :return: Boolean based on comparison
        """

        # check what's the correct value based on our input
        data = list(self.input)[self.counter]
        data = self.input.get(data)
        t = data.get("temperature")
        h = data.get("humidity")
        p = data.get("pressure")
        #check if the standard deviation is in 40 range for temp,humidity and pressure
        if (abs(t[0] - t[1]) < 40 and abs(h[0]-h[1]) < 40 and abs(p[0]-p[1]) < 40):
            correct = 'valid'
        else:
            correct = 'invalid'
        
        # check if the value our AI guessed is correct and return True or False
        if correct == self.state[self.counter]:
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
        if self.counter >= 3:
            self.done = 1
            if self.perfect:
                self.reward += 10  # if perfect, award a reward of 10 times the normal reward

        if self.done == 1:
            print("Episode completed")
            return [self.counter-1, self.reward, self.done, self.state]

        if self.actions[action] == 'valid':  # set state based on our systems guess
            self.state[self.counter] = "valid"
        else:
            self.state[self.counter] = 'invalid'

        res = self.check() # use check to compare guessed value and correct value
        if res: # if return value is True, give a positive reward
            self.reward += 1
        else:  # if return is False, give a negative reward and set perfect to False.
            self.reward -= 1
            self.perfect = False

        self.counter += 1

        # print("Current State: {} \n Reward: {} \n Done: {}".format(self.state, self.reward, self.done))
        return [self.counter-1, self.reward, self.done, self.state]


    def reset(self):
        """
        Reset used to set values back to default values
        :return: integer self.counter set to 0
        """

        self.counter = 0
        self.done = 0
        self.reward = 0
        self.perfect = True
        self.state = [None, None, None]
        return self.counter

    def render(self, mode='human', close=False):
        """
        This function is normally used in gym to render frames. But since our program is not graphic related, we are
        not using this for now atleast
        :return: None
        """
        print("Render over")
