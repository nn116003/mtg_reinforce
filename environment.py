from mtg.game import Game
from mtg.settings import *
import logging

class Env(Game):
    def __init__(self, learner, opponent, first=True, logging=logging):
        super(Env, self).__init__([learner, opponent], logging=logging)
        self.learner = learner
        self.opponent = opponent
        
        if not first:
            self.playing_idx = 1

        self.feature_memory = []

        self.prev_snapshot = {
            "self":{
                "c_ids":[],
                "land_num":0,
                "hand_num":0,
                "life":learner.life
            },
            "opponent":{
                "c_ids":[],
                "land_num":0,
                "hand_num":0,
                "life":opponent.life
            }
        }
    
    def reset(self, deck = None, opponent = None):
        self.learner.reset(deck)
        if opponent is not None:
            self.opponent = opponent
        else:
            self.opponent.reset()
        self.feature_memory = []

    def _snapshot(self):
        return {
            "self":{
                "c_ids":[c.id for c in self.learner.battlefield.creatures],
                "land_num":len(self.learner.battlefield.lands),
                "hand_num":len(self.learner.hand),
                "life":self.learner.life
            },
            "opponent":{
                "c_ids":[c.id for c in self.opponent.battlefield.creatures],
                "land_num":len(self.opponent.battlefield.lands),
                "hand_num":len(self.opponent.hand),
                "life":self.opponent.life
            }
        }
        

    def _get_features(self):
        pass

    def _reward(self, snapshot, alpha = 0.1, beta=0.1):
        prev_self_state = self.prev_snapshot["self"]
        prev_op_state = self.prev_snapshot["opponent"]
        self_state = snapshot["self"]
        op_state = snapshot["opponent"]
        
        card_add = len(self_state["c_ids"]) + self_state["land_num"] + beta * self_state["hand_num"] \
                   - len(prev_self_state["c_ids"]) - prev_self_state["land_num"] - beta * prev_self_state["hand_num"] \
                   - (len(op_state["c_ids"]) + op_state["land_num"] + beta * op_state["hand_num"] 
                   - len(prev_op_state["c_ids"]) - prev_op_state["land_num"] - beta * prev_op_state["hand_num"] )
                   
        life_diff = self_state['life'] - prev_self_state['life'] \
                    - (op_state['life'] - prev_op_state['life'])

        return card_add + alpha * life_diff

    def step(self, action):
        if self.phase == MAIN:
            pass


        
