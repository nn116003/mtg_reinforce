from mtg import game, player, utils
from mtg.settings import *
from mtg.cards import Land, Creature, WrathG
from mtg.fields import Hand

from environment import Env

import unittest
import numpy as np 
import copy


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        np.random.seed(2)
        self.deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
        self.deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

        self.p1 = player.Stupid_Player(1, self.deck1)
        self.p2 =  player.Stupid_Player(2, self.deck2)
        self.cardid2idx = {"None":0,1:1,2:2,3:3,99:4}
        self.phase2idx = {UPLEEP:0, DRAW:1, MAIN1:2, MAIN2:2, ATTACK:3, BLOCK:4, ASSIGN:5 DAMAGE:6}
        self.env = Env(self.p1, self.p2, self.cardid2idx, self.phase2idx, feat_length=2)

    def test_possible_actions_cast(self):
        self.env.phase = MAIN1
        # no castable cards
        self.p1.hand = Hand(
            [Creature(1,1,1,1,1),Creature(2,2,2,2,2),Creature(3,3,3,3,3)]
        )
        pas = self.env.possible_actions(self.p1)
        self.assertEqual(len(pas), 0)

        # land is castable
        self.p1.battlefield.lands.extend(
            [Land(99, ''), Land(99,''), Land(99, '')])
        self.p1.battlefield.lands[0].tap()
        self.p1.hand = Hand(
            [Creature(1,1,1,1,1),Creature(2,2,2,2,2),Creature(3,3,3,3,3),Land(99,'')]
        )
        pas = self.env.possible_actions(self.p1)
        self.assertSetEqual(set(pas), 
            {self.cardid2idx[1], self.cardid2idx[2], self.cardid2idx[99], self.cardid2idx['None']})

        # land is not castable
        self.p1.n_played_lands = 1
        pas = self.env.possible_actions(self.p1)
        self.assertSetEqual(set(pas), 
            {self.cardid2idx[1], self.cardid2idx[2], self.cardid2idx['None']})


    def test_possible_actions_attack(self):
        self.env.phase = ATTACK
        
        # no attackable creatures
        creatures = [Creature(1,1,1,1,1),Creature(2,2,2,2,2)]
        creatures[0].summon_sick = True
        creatures[0].untap()
        creatures[1].summon_sick = False
        creatures[1].tap()
        self.b1.battlefield.creatures = creatures
        pas = self.env.possible_actions(self.p1)
        self.assertEqual(len(pas), 0)

        # there is attackable creatures
        creatures.append([Creatures(3,3,3,3,3)])


    

    def test_possible_actions_block(self):
        pass


