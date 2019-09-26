# env cast_action(game,....)
# possible action -> agent?

import utils
from model import CastModule, AttackModule, BlockModule, FCGameEncoder
from mtg.player import Player
from settings import *

import logging

def _expand_state_tensor(state_tensor_dict, l):
    res = {}
    res["player"] = {}
    for k, v in state_tensor_dict["player"].items():
        res["player"][k] = v.expand(l, *(v.shape[1:]))

    res["opponent"] = {}
    for k, v in state_tensor_dict["opponent"].items():
        res["opponent"][k] = v.expand(l, *(v.shape[1:]))

    res["phase"] = state_tensor_dict["phase"].expand(l, -1)
    res["playing_idx"] = state_tensor_dict["playing_idx"].expand(l, -1)

    return res

class Agent(Player):
    def __init__(self, id, deck, cast_module, attack_module, block_module, 
                max_c = 20, max_h = 10, max_g = 60, pad_id = 0,
                logger=logging):
        super(Agent, self).__init__(id, deck ,logger)
        self.cast_module = cast_module
        self.attack_module = attack_module
        self.block_module = block_module

        self.max_c = max_c
        self.max_h = max_h
        self.max_g = max_g
        self.pad_id = pad_id

    def train(self):
        self.cast_module.train()
        self.attack_module.train()
        self.block_module.train()

    def eval(self):
        self.cast_module.eval()
        self.attack_module.eval()
        self.block_module.eval()

    def _select_cast_action(self, 
        state_tensor, # dict of tensor (batch_size = 1)
        card_ids # list of tensor
        ):
        expanded_state_tensor = _expand_state_tensor(state_tensor, len(card_ids))
        Qs = self.cast_module(expanded_state_tensor, torch.cat(card_ids).view(-1,1)) # 1, len(card_ids)
        # TODO max
        max_q, max_idx = Qs.view(-1).max()
        # predict from tensor
        # return state, action, Q
        return card_ids[int(max_idx)], max_q

    def cast_action(self, env, state, card_ids):
        # to tensor
        state_tensor_dict = utils.fix_state(state, self.pad_id, self.max_c, self.max_g, self.max_h)
        # action_tensor = utils.fix_action(card_ids, )
        # select action
        # do action
        # return state, action
        pass

class DummyAgent(Player):
    pass


