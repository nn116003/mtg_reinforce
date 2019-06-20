from mtg.cards import Land, Creature
from mtg.settings import DECK_NUM
import pandas as pd 
import numpy as np 

def random_creatures_from_list(n, path):
    card_list = pd.read_csv(path)
    l = card_list.shape[0]
    tmp_idxes = np.arange(l*4)
    use_tmp_idxes = np.random.choice(tmp_idxes, n, replace=False) 

    creature_list = [Creature(
                        card_list.id[i%l],
                        card_list.name[i%l],
                        card_list.cost[i%l],
                        card_list.power[i%l],
                        card_list.toughness[i%l]) for i in use_tmp_idxes]

    return creature_list

def random_deck_from_list(creature_num, path):
    creatures = random_creatures_from_list(creature_num, path)
    lands = [Land(i, 'land') for i in range(DECK_NUM - creature_num)]
    return creatures + lands



