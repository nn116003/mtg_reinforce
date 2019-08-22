from mtg import game, player, utils
from mtg.settings import *
from mtg.cards import Land, Creature, WrathG
from mtg.fields import Hand

import unittest
import numpy as np 
import copy


class TestGane(unittest.TestCase):
    def setUp(self):
        np.random.seed(2)
        self.deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
        self.deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

        self.p1 = player.Stupid_Player(1, self.deck1)
        self.p2 =  player.Stupid_Player(2, self.deck2)
        self.game = game.Game([self.p1, self.p2])

    def test_reset(self):
        pass

    def test_burial_corpses(self):
        pass

    def test_end_turn(self):
        pass

    def test_upkeep(self):
        pass

    def test_draw(self):
        pass

    def test_main(self):
        pass

    def test_damage(self):
        pass
