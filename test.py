from mtg import game, player, utils
import pandas as pd 
import numpy as np 
import logging

logging.basicConfig(level=logging.DEBUG)

np.random.seed(2)

deck1 = utils.random_deck_from_list(36, './mtg/cards.csv')
deck2 = utils.random_deck_from_list(36, './mtg/cards.csv')

p1 = player.Stupid_Player(1, deck1)
p2 = player.Stupid_Player(2, deck2)

random_game = game.Game([p1, p2])

random_game.main()


