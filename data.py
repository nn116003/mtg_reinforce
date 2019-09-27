# add possible actions None
import numpy as np
import torch
import torch.nn.functional as F

import random
from collections import namedtuple

from mtg.settings import *

import utils


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


# stock sequence of game-sanpshot{dict} as dict of list
# self.features["featurename"] = sequence of "featurename" (list)
# cardids are converted to idx by cardid2idx
#
# 1-phase in game -> FeatureHolder.push(...)
class FeatureHolder(object):
    def __init__(self, length, cardid2idx, phase2idx, first_play_idx):
        self.cardid2idx = cardid2idx 
        self.phase2idx = phase2idx

        self.length = length 
        self.features = {}
        self.reset(first_play_idx)

    def _empty_feats(self, hand=False):
        feats = {
                "creatures": utils.card2idxlist([], self.cardid2idx, True ),
                "lands":[0, 0],
                "n_hand":0,
                "life":LIFE ,
                "n_lib":DECK_NUM ,
                "gy":utils.card2idxlist([], self.cardid2idx, False),
            }
        if hand:
            feats['hand'] = utils.card2idxlist([], self.cardid2idx, False)
        return feats

    def _add_features(self, p_feat, o_feat, phase, playing_idx):
        for k in o_feat:
            if self.features['player'][k] is not None:
                self.features['player'][k].append(p_feat[k])
                self.features['opponent'][k].append(o_feat[k])
            else:
                self.features['player'][k] = [p_feat[k]]
                self.features['opponent'][k] = [o_feat[k]]
        if self.features['player']['hand'] is not None:
            self.features['player']['hand'].append(p_feat['hand'])
        else:
            self.features['player']['hand'] = [p_feat['hand']]
        self.features['phase'].append(self.phase2idx[phase])
        self.features['playing_idx'].append(playing_idx)

    def reset(self, first_play_idx):
        self.features = {
            "player":dict.fromkeys(["creatures","lands","n_hand","life", "n_lib", "gy","hand"]),
            "opponent":dict.fromkeys(["creatures","lands","n_hand","life", "n_lib", "gy"]),
            "phase":[],
            "playing_idx":[]
            }
        for i in range(self.length):
            p_default = self._empty_feats(True)
            o_default = self._empty_feats()
            self._add_features(p_default, o_default, 
                UPKEEP, first_play_idx)
        

    def _player_feats(self, player, hand=True):
        bf = player.battlefield
        n_lands = len(bf.lands)
        n_untap_lands = len(bf.get_untap_lands())
        feats = {
            "creatures": utils.card2idxlist(bf.creatures, self.cardid2idx, True ),
            "lands":[n_untap_lands, n_lands - n_untap_lands],
            "n_hand":len(player.hand),
            "life":player.life,
            "n_lib":len(player.library),
            "gy":utils.card2idxlist(player.graveyard, self.cardid2idx, False)
        }
        if hand:
            feats["hand"] = utils.card2idxlist(player.hand, self.cardid2idx, False )

        return feats

    def push(self, game):
        self._add_features(
            self._player_feats(game.learner, hand=True),
            self._player_feats(game.opponent, hand=False),
            game.phase,
            game.playing_idx)

    def get_state(self):
        res = {'player':{}, 'opponent':{}}
        for k in self.features['opponent']:
            res['player'][k] = self.features['player'][k][-self.length:]
            res['opponent'][k] = self.features['opponent'][k][-self.length:]
        res['player']['hand'] = self.features['player']['hand'][-self.length:]
        res['phase'] = self.features['phase'][-self.length:]
        res['playing_idx'] = self.features['playing_idx'][-self.length:]
            
        return res


# stock trainsitions (state, state_phase, action, nextstate, next_phase, reward, possible_actions)
# convert sequence of features to tensor
# ## state ##
# pad feature sequence in state and covert to tensor
# ## action ##
# pad and convert to tensor
#
# 1-action in game -> ReplayMemory.push(...)
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

    def _fix_action(self, action, phase):
        if state_phase in [MAIN1, MAIN2]:
            action = utils.cast_action2tensor(action)
        elif state_phase == ATTACK:
            action = utils.attack_action2tensor(action, self.pad_id, self.max_c)
        else:#block
            action = utils.block_action2tensor(action, self.pad_id, sekf.max_c)
        return action
            
    def _fix_trainsition(self, state, state_phase, action, nextstate, 
                        nextstate_phase, reward, possible_actions):
        if state is not None:
            state = utils.fix_state(state, self.pad_id, self.max_c, self.max_g, self.max_h)
        if action is not None:
            action = self._fix_action(action, state_phase)
        if nextstate is not None:
            nextstate = utils.fix_state(nextstate, self.pad_id, self.max_c, self.max_g, self.max_h)
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
