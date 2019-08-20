from mtg import game, player, utils
from mtg.settings import *
from mtg.cards import Land, Creature, WrathG

import unittest
import numpy as np 


class TestPlayer(unittest.TestCase):
    def setUp(self):
        np.random.seed(2)
        self.deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
        self.deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

        self.p1 = player.Stupid_Player(1, deck1)
        self.p2 =  player.Stupid_Player(2, deck2)
        self.game = game.Game([self.p1, self.p2])

    def test_reset(self):
        self.p1.life -= 10
        self.p1.hand = self.p1.library.pop_top(10)
        self.p1.battlefield.creatures.add(Creature(1,1,1,1,1))
        self.p1.graveyard.add(Creature(1,1,1,1,1))
        self.p1.battlefield.lands.add(Land(99,'land'))
        self.p1.n_played_lands += 1

        self.p1.reset()
        self.assertEqual(len(self.p1.library), len(self.deck1))
        self.assertEqual(self.p1.life, LIFE)
        self.assertIsNone(self.p1.hand)
        self.assertEqual(len(self.p1.battlefield.creatures), 0)
        self.assertEqual(len(self.p1.battlefield.lands), 0)
        self.assertEqual(len(self.p1.graveyard), 0)
        self.assertEqual(self.p1.n_playable_lands, 0)

    def test_mana_available(self):
        tap_land = Land(99,'Land')
        tap_land.tap()
        untap_land = Land(99,'Land')

        self.p1.battlefield.lands.extend([tap_land, untap_land])
        self.p1.battlefield.manapool += 2

        self.assertEqual(self.p1.mana_available(), 3)

    def test_castable_card(self):
        pass

