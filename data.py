# add possible actions None
import numpy as np
import torch
import torch.nn.functional as F

import random

from mtg.settings import *


Transition = namedtuple('Transition', 
    ('state', 'state_phase', 'action', 
    'next_state', 'next_state_phase', 'reward', 'possible_actions'))

# state: [feat1, feat2, feat3,...]
# feat: {"phase":phase, "player":player_feat, "opponent":player_feat}
# player_feat: {BOC, numerical..}
# =>
# 2 * numerical feat tensor : 1(batch_size) * length * feat_dim 
#   player's, opponent's 
# 5 * BOWs feat tensor : 1(batch_size) * length * MAX_NUM
#   player's bf, gy, hand, opponent's bf, gy
# 
#  action:
#  cast: id
#  attack: [id1, id2,...] # to pad
#  block: 
#
#  possible_actions
#

class ReplayMemory(object):
    def __init__(self, capacity, max_c = 20, max_h = 10, max_g = 60, pad_id = 0):
        '''
        max_c : max len(battle_field.creatures)
        max_h : max len(hand)
        max_g : max len(graveyard)
        '''
        self.capacity = capacity
        self.memory = []
        self.position = 0

        self.max_c = max_c
        self.max_h = max_h
        self.max_g = max_g
        self.pad_id = pad_id

    def push(self, state, state_phase, action, nextstate, 
                        nextstate_phase, reward, possible_actions):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        transition =self._fix_trainsition(state, state_phase, action, nextstate, 
                        nextstate_phase, reward, possible_actions)
        self.memory[self.position] = transition
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def _pad(self, cards, max_len):
        # to utils ?
        return cards + [self.pad_id] * (max_len - len(cards))

    def _pad_bf_creatures(self, creatures_data, max_len):
        # to utils ?
        l = len(creatures_data)
        creatures = [c[0] for c in creatures_data]
        tap_flg = [c[1] for c in creatures_data]
        sick_flg = [c[1] for c in creatures_data]
        pad_c = self._pad(creatures, max_len)
        pad_tap_flg = tap_flg + [0]*(max_len - l)
        pad_sick_flg = sick_flg + [0]*(max_len - l)

        return pad_c, pad_tap_flg, pad_sick_flg

    def _fix_action(self, action, phase):
        if phase in [MAIN1, MAIN2]:
            return torch.LongTensor([action])
        elif phase == ATTACK:
            return torch.LongTensor(self._pad(action, self.max_c))
        else: # block
            attackers = torch.LongTensor(self._pad(action["attackers"], self.max_c))
            blockers = torch.LongTensor(
                list(map(lambda x:self._pad(x, self.max_c), action["blockers"]))
            )
            return (attackers, blockers)

    def _fix_player_feat(self, feat):
        # TODO to utils?
        res = {}
        res["dense"] = [
                feat['lands'][0], feat['lands'][1],
                feat['n_hand'], feat['life'], feat['n_lib']
                ] 
        p_c, p_tf, p_sf = self._pad_bf_creatures(feat['creatures'], self.max_c) 
        res["creatures"] = p_c
        res["tap_flg"] = p_tf
        res["sick_flg"] = p_sf
        res["gy"] = self._pad(feat['gy'], self.max_g)
        if "hand" in feat:
            res["hand"] = self._pad(feat['hand'], self.max_h)

        return res

    def _player_state2tensor(self, dict_of_list):
        res = {}
        res["dense"] = torch.Tensor(res["player"]["dence"])
        res["creatures"] = torch.Tensor(res["player"][""])
        ###############

    def _fix_state(self, state):
        # TODO to utils?
        res = {
            "player":{"dense":[],"creatures":[],"tap_flg":[],"sick_flg":[],"gy":[],"hand":[]},
            "opponent":{"dense":[],"creatures":[],"tap_flg":[],"sick_flg":[],"gy":[]},
            "phase":[],
            "playing_idx":[]
            }
        for feat in state:
            p_feat = self._fix_player_feat(feat["player"])
            for k, v in p_feat.items():
                res["player"][k].append(v)
            o_feat = self._fix_player_feat(feat["opponent"])
            for k, v in o_feat.items():
                res["opponent"][k].append(v)
            res["phase"].append(feat["phase"])
            res["playing_idx"].append(feat["playing_idx"])

        return res
            
    def _fix_trainsition(self, state, state_phase, action, nextstate, 
                        nextstate_phase, reward, possible_actions):
        if state is not None:
            state = self._fix_state(state)
        if action is not None:
            action = self._fix_action(action, phase=state_phase)
        if nextstate is not None:
            nextstate = self._fix_state(nextstate)
        if possible_actions is not None:
            possible_actions = list(map(lambda x: self._fix_action(x, nextstate_phase), possible_actions))

        return Transition(state, state_phase, action, nextstate, 
                        nextstate_phase, reward, possible_actions)
  
    def __len__(self):
        return len(self.memory)


class ReplayController(object):
    def __init__(self, capacity, max_c = 20, max_h = 10, max_g = 60, pad_id = 0):
        self.cast_memory = ReplayMemory(capacity, max_c, max_h, max_g, pad_id)
        self.attack_memory = ReplayMemory(capacity, max_c, max_h, max_g, pad_id)
        self.block_memory = ReplayMemory(capacity, max_c, max_h, max_g, pad_id)

    def push(self, *args):
        state_phase = args[1]
        if state_phase in [MAIN1, MAIN2]:
            self.cast_memory.push(*args)
        elif state_phase == ATTACK:
            self.attack_memory.push(*args)
        else:
            self.block_memory.push(*args)

    def sample(self, phase, batch_size):
        if phase in [MAIN1, MAIN2]:
            return self.cast_memory.sample(batch_size)
        elif phase == ATTACK:
            return self.attack_memory.sample(batch_size)
        else:
            return self.block_memory.sample(batch_size)
