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
        #print(self.env.feature_holder.features)
        self.p1.hand = Hand([Creature(1,1,1,1,1), Land(99, '')])
        self.p1.battlefield.creatures = [Creature(2,2,2,2,2), Creature(3,3,3,3,3)]
        self.p1.battlefield.creatures[0].tap()
        self.p1.battlefield.creatures[0].summon_sick = False
        self.p1.battlefield.lands = [Land(99,''), Land(99, '')]
        self.p1.battlefield.lands[0].tap()
        
        self.p2.life = 4
        self.p2.graveyard = [Creature(1,1,1,1,1), Land(99, '')]
        self.p2.init_draw()

        self.env.phase = MAIN1
        self.env.playing_idx = 0

        ans = {
            "player":{
                "creatures":[
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx[2],0,1], [self.cardid2idx[3],1,0]]
                ],
                "lands":[[0,0], [0,0], [1,1]],
                "n_hand":[0,0,2],
                "life":[LIFE, LIFE, LIFE],
                "n_lib":[DECK_NUM, DECK_NUM, DECK_NUM],
                "gy":[[self.cardid2idx["None"]], 
                    [self.cardid2idx["None"]], [self.cardid2idx["None"]]],
                "hand":[
                    [self.cardid2idx["None"]], [self.cardid2idx["None"]], 
                    [self.cardid2idx[1], self.cardid2idx[99]]
                    ]
            },
            "opponent":{
                "creatures":[
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx["None"], 0, 0]]
                ],
                "lands":[[0,0], [0,0], [0,0]],
                "n_hand":[0, 0, INIT_DRAW],
                "life":[LIFE, LIFE, 4],
                "n_lib":[DECK_NUM, DECK_NUM, DECK_NUM - INIT_DRAW],
                "gy":[
                    [self.cardid2idx["None"]], [self.cardid2idx["None"]], 
                    [self.cardid2idx[1], self.cardid2idx[99]]
                ]
            },
            "phase":[self.phase2idx[UPKEEP], self.phase2idx[UPKEEP], self.phase2idx[MAIN1]],
            "playing_idx":[0, 0, 0]
        }
        self.env.feature_holder.push(self.env)
        print(ans)
        print("###########")
        print(self.env.feature_holder.features)
        self.assertEqual(ans, self.env.feature_holder.features)

        state = self.env.feature_holder.get_state()
        state_ans = {
            "player":{
                "creatures":[
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx[2],0,1], [self.cardid2idx[3],1,0]]
                ],
                "lands":[[0,0], [1,1]],
                "n_hand":[0,2],
                "life":[LIFE, LIFE],
                "n_lib":[DECK_NUM, DECK_NUM],
                "gy":[[self.cardid2idx["None"]], [self.cardid2idx["None"]]],
                "hand":[
                    [self.cardid2idx["None"]], 
                    [self.cardid2idx[1], self.cardid2idx[99]]
                    ]
            },
            "opponent":{
                "creatures":[
                    [[self.cardid2idx["None"], 0, 0]],
                    [[self.cardid2idx["None"], 0, 0]]
                ],
                "lands":[[0,0], [0,0]],
                "n_hand":[0, INIT_DRAW],
                "life":[LIFE, 4],
                "n_lib":[DECK_NUM, DECK_NUM - INIT_DRAW],
                "gy":[
                    [self.cardid2idx["None"]], 
                    [self.cardid2idx[1], self.cardid2idx[99]]
                ]
            },
            "phase":[self.phase2idx[UPKEEP], self.phase2idx[MAIN1]],
            "playing_idx":[0, 0]
        }
        self.assertEqual(state, state_ans)

    def test_replay_memory(self):
        pass

if __name__ == "__main__":
    unittest.main()

