from .cards import Land, Creature
from .settings import DECK_NUM
import pandas as pd 
import numpy as np 

def _random_creatures_from_list(n, path):
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
    creatures = _random_creatures_from_list(creature_num, path)
    lands = [Land(99, 'land') for i in range(DECK_NUM - creature_num)]
    return creatures + lands


def assign_ids_in_game(deck1, deck2):
    for i, card in enumerate(deck1):
        card.tmp_id = i

    l = len(deck1)
    for j, card in enumerate(deck2):
        card.tmp_id = l + j


def show_creatures_list(creatures, name):
    c_dict = {"tmp_id":[],"name":[],"cost":[],"power":[],"toughness":[],"state":[]}
    for c in creatures:
        c_dict["tmp_id"].append(c.tmp_id)
        c_dict["name"].append(c.name)
        c_dict["cost"].append(c.cost)        
        c_dict["power"].append(c.power)
        c_dict["toughness"].append(c.toughness)
        c_dict["state"].append(c.state)

    print("##### %s #####" % name)
    print(pd.DataFrame(c_dict))
    print("##########")

def to_all_decimal(str_arr):
    flg = True
    res = []
    for x in str_arr:
        if type(x) == list:
            f, r = to_all_decimal(x)
        else:
            f = x.isdecimal()
            r = int(x) if f else x
        flg = flg and f
        res.append(r)
    return flg, res


