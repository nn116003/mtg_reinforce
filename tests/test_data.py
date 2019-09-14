from mtg import game, player, utils
from mtg.settings import *
from mtg.cards import Land, Creature, WrathG
from mtg.fields import Hand

from environment import Env

import unittest
import numpy as np 
import copy

class TestData(unittest.TestCase):
    def setUp(self):
        np.random.seed(2)
        self.deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
        self.deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

        self.p1 = player.Stupid_Player(1, self.deck1)
        self.p2 =  player.Stupid_Player(2, self.deck2)
        self.cardid2idx = {"None":0,1:1,2:2,3:3,4:4,99:5}
        self.phase2idx = {UPKEEP:0, DRAW:1, MAIN1:2, MAIN2:2, ATTACK:3, BLOCK:4, ASSIGN:5, DAMAGE:6}
        self.env = Env(self.p1, self.p2, self.cardid2idx, self.phase2idx, feat_length=2)

    def test_feature_holder(self):
        pass

if __name__ == "__main__":
    unittest.main()