from mtg.game import Game
from mtg.settings import *
import logging

class Env(Game):
    def __init__(self, learner, opponent, first=True, logging=logging):
        super(Env, self).__init__([learner, opponent], logging=logging)
        self.learner = learner
        self.opponent = opponent
        if not first:
            self.playing_idx = 1
    
    def reset(self, deck = None, opponent = None):
        self.learner.reset(deck)
        if opponent is not None:
            self.opponent = opponent
        else:
            self.opponent.reset()

    def _snapshot(self):
        # to calc re
        pass

    def _get_features(self):
        pass

    def _reward(self):
        pass

    def step(self, action):
        if self.phase == MAIN:
            pass
