"""
Custom Environment for our AI agent to train to sort colors and find anamolies in given data sets
@author(s): Sanjeev Rajasekaran
Start date: 02/22/2019
End date: 02/28/2019
Version - 0.0.1
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


class rlaiEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, options=2):

        self.n = options
        self.input = None  # input which will be set to the values we read from the file
        self.state = [None, None, None, None, None, None, None, None, None, None] # state aka current guesses by our AI
        self.actions = ["RED", "BLACK"]  # available actions for our AI
        self.reward = 0
        self.done = 0
        self.counter = 0
        self.action_space = spaces.Discrete(self.n)  # actions = self.n = 2 (RED/BLACK)
        self.observation_space = spaces.Discrete(10)  # states aka observations = 10 (10 values in a file for now)
        self.perfect = True  # if the AI agent gets everything right, it gets a huge +10 reward points

    def colorvalues(self, inputcolors):
        """
        Function to set self.input to whatever colors we read in from the file specified
        :param inputcolors: Dicitonary containing color values
        :return: None
        """

        self.input = inputcolors

    def check(self):
        """
        Function to compare our AI guess and the correct answer
        :return: Boolean based on comparison
        """

        # correct = [DARK, DARK, DARK, DARK, DARK, BRIGHT, DARK, DARK, DARK, DARK]

        # check what's the correct value based on our input
        if self.input[self.counter] == 'RED':
            correct = 'bright'
        else:
            correct = 'dark'

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

        # If more than 9 episodes, we set done to 1 and check if it's perfect or not
        if self.counter >= 10:
            self.done = 1
            if self.perfect:
                self.reward += 10  # if perfect, award a reward of 10 times the normal reward

        if self.done == 1:
            print("Episode completed")
            return [self.counter-1, self.reward, self.done, self.state]

        if self.actions[action] == 'RED': # set state based on our systems guess
            self.state[self.counter] = BRIGHT
        else:
            self.state[self.counter] = DARK

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
        self.state = [None, None, None, None, None, None, None, None, None, None]
        return self.counter

    def render(self, mode='human', close=False):
        """
        This function is normally used in gym to render frames. But since our program is not graphic related, we are
        not using this for now atleast
        :return: None
        """
        print("Render over")
