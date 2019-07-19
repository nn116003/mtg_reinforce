from mtg.game import Game
from mtg.settings import *
import logging

class Env(Game):
    def __init__(self, learner, opponent, logging=logging):
        super(Env, self).__init__([learner, opponent], logging=logging)
    
    def reset(self, opponent):
        pass

    def _snapshot(self):
        pass

    def _get_features(self):
        pass

    def step(self, action):
        if self.phase == MAIN:
            pass
