from mtg import game, player, utils
import pandas as pd 
import numpy as np 
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

np.random.seed(8)

deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

flg = sys.argv[1]

if flg == 'r':
    p1 = player.Stupid_Player(1, deck1)
    p2 =  player.Stupid_Player(2, deck2)
    random_game = game.Game([p1, p2])
    random_game.main()
else:
    p1 = player.Cmd_Player(1, deck1)
    p2 =  player.Stupid_Player(2, deck2)
    cui_game = game.Game([p1, p2])
    cui_game.main()



