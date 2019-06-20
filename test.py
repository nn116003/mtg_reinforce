from mtg import game, player, utils
import pandas as pd 
import numpy as np 


np.random.seed(2)

deck1 = utils.random_deck_from_list(36, './mtg/cards.csv')
deck2 = utils.random_deck_from_list(36, './mtg/cards.csv')

p1 = player.Stupid_Player(deck1)
p2 = player.Stupid_Player(deck2)

random_game = game.Game([p1, p2])

random_game.main()


