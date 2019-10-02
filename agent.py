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

    def select_cast_action(self, 
        state_tensor, # dict of tensor (batch_size = 1)
        card_indexes # list of tensor : possible actions
        ):
        expanded_state_tensor = _expand_state_tensor(state_tensor, len(card_indexes))
        Qs = self.cast_module(expanded_state_tensor, torch.cat(card_indexes).view(-1,1)) # 1, len(card_ids)
        max_q, max_idx = Qs.view(-1).max(0)
        return card_indexes[int(max_idx)], max_q

    def cast_action(self, env, state, card_indexes):
        # select action
        state_tensor_dict = utils.fix_state(state, self.pad_id, self.max_c, self.max_g, self.max_h)
        action_tensors = list(map(lambda x: utils.cast_action2tensor(x), card_indexes))
        card_idx, _ = self.select_cast_action(state_tensor_dict, action_tensors)

        # idx -> id -> card -> cast
        card_id = env.idx2cardid[int(card_idx)]
        castable_cards = self.castable_card(env)["hand"]
        cast_card = utils.cardids2cards([card_id], castable_cards)
        self._cast_from_hand(cast_card, env)

        return state, card_idx

    def select_attack_action(
        self,
        state_tensor, # dict of tensor (batch_size = 1)
        attackers_tensor_list # list of tensor (max_c): possible actions
    ):
        expanded_state_tensor = _expand_state_tensor(state_tensor, len(attackers_tensor_list))
        Qs = self.attack_module(expanded_state_tensor, torch.cat(attackers_tensor_list)) # len(card_ids), 1
        max_q, max_idx = Qs.view(-1).max(0)
        return attackers_tensor_list[int(max_idx)], max_q

    def attack_action(self, env, state, attackers_list):
        # select action
        state_tensor_dict = utils.fix_state(state, self.pad_id, self.max_c, self.max_g, self.max_h)
        action_tensors = list(map(lambda x: utils.attack_action2tensor(x), attackers_list))
        attackers_tensor, _ = self.select_attack_action(state_tensor_dict, action_tensors)

        # idx -> id -> card -> attack
        attacker_ids = []
        for card_idx in attackers_tensor.view(-1):
            card_id = env.idx2cardid[int(card_idx)]
            if card_id == self.pad_id:
                break
            else:
                attacker_ids.append(card_id)
        attackable_cards = self.battlefield.get_attackable_creatures()

        attack_card = utils.cardids2cards(attacker_ids, attackable_cards)
        self._attack(attack_card, env.battle_ctrl)

        return state, attack_card

# TODO check id/index of action

class DummyAgent(Player):
    pass


