# test
# winning state
# win to reward


from mtg.game import Game
from mtg.settings import *

import logging
import numpy as np
import itertools


def _card2idlist(cards, cardid2idx, battlefield=False):
    result = []
    if battlefield:
        if len(cards) == 0:
            result.append([cardid2idx["None"], 0, 0])
        else:
            for card in cards:
                tmp = [cardid2idx[card.id], 1-int(card.is_tapped()), int(card.summon_sick)]
                result.append(tmp)
    else:
        if len(cards) == 0:
            result.append(cardid2idx["None"])
        else:
            [result.append(cardid2idx[card.id]) for card in cards]

    return result 
        

class FeatureHolder(object):
    def __init__(self, length, cardid2idx):
        self.cardid2idx = cardid2idx 

        self.length = length 
        self.features = []
        self.reset()

    def reset(self):
        self.features = []
        for i in range(self.length):
            feats = {
                "creatures": _card2idlist([], self.cardid2idx, True ),
                "lands":[0, 0],
                "n_hand":0,
                "life":LIFE ,
                "n_lib":DECK_NUM ,
                "gy":_card2idlist([], self.cardid2idx, False),
                "hand":_card2idlist([], self.cardid2idx, False)
            }
            self.features.append({"player":feats, "opponent":feats})

    def _player_feats(self, player, hand=True):
        bf = player.battlefield
        n_lands = len(bf.lands)
        n_untap_lands = len(bf.get_untap_lands)
        feats = {
            "creatures": _card2idlist(bf.creatures, self.cardid2idx, True ),
            "lands":[n_untap_lands, n_lands - n_untap_lands],
            "n_hand":len(player.hand),
            "life":player.life,
            "n_lib":len(player.library),
            "gy":_card2idlist(player.graveyard, self.cardid2idx, False)
        }
        if hand:
            feats["hand"] = _card2idlist(player.hand, self.cardid2idx, False )

        return feats

    def push(self, game):
        feat = {
            "player":self._player_feats(game.learner, hand=True),
            "oppponent":self._player_feats(game.opponent, hand=False)
        }
        self.features.append(feat)

    def get_state(self):
        return self.features[-self.length:]

class Env(Game):
    def __init__(self, learner, opponent, cardid2idx, feat_length, 
        first=True, logging=logging, win_reward=20, lose_reward=-20):
        super(Env, self).__init__([learner, opponent], logging=logging)
        self.learner = learner
        self.opponent = opponent
        
        self.win_reward = win_reward
        self.lose_reward = lose_reward
        
        if not first:
            self.playing_idx = 1

        # to save past n turn features
        self.feature_holder = FeatureHolder(feat_length, cardid2idx )

        # sanpshot  of game(not = feat, use to calc reward)
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
        self.feature_holder.reset()

    def _possible_actions(self, player):
        if self.phase is in [MAIN, MAIN2]:
            return [card.id for card in player.castable_caard(self)["hand"]]

        elif self.phase == ATTACK:
            attackable_creatures = player.battlefield.get_attackable_creatures()
            ac_ids = [card.id for card in attackable_creatures]
            if len(ac_ids) > 0:
                comb = []
                for i in range(len(ac_ids)):
                    comb.extend(itertools.combinations(ac_ids, i+1))
                return comb
            else:
                return []

        elif self.phase == BLOCK:
            ac_num = len(self.battle_ctrl.battles )
            blockable_creatures = player.battlefield.get_untap_creatures()
            bc_ids = [card.id for card in blockable_creatures ]
            if ac_num  > 0 and len(bc_ids) > 0:
                block_targets = list(range(ac_num + 1)) # +1: not block
                block_patterns = itertools.product(
                    *([block_targts]*len(bc_ids))
                    )
                res = []
                for pattern in block_patterns:
                    block_list = [[] for i in range(ac_num)]
                    for bc_id, b_target in zip(bc_ids, pattern)
                        if b_target < ac_num:
                            block_list[b_target].append(bc_id)
                    res.append(block_list)
                return res
            else:
                return []


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


    def _prevNS_prevR(self):
        prev_nextstate = self.feature_holder.get_state()
        snapshot = self._snapshot()
        prev_reward = self._reward(snapshot)
        self.prev_snapshot = snapshot
        return prev_nextstate, prev_reward
        
        
    def main(self):
        """
        for state, action, next_state, reward, done in env.main():
            memory.push(state, action, next_state, reward)
            env.learner.update(memory)
        
        """
        # state, action, = learner
        # next state, reward = env
        # yield next_state, reward, done/not
        [player.shuffle() for player in self.players]
        self._init_draw()
        nturn = 0
        while True:
            if self.playing_idx == 0: # learner's turn
                # upkeep
                _ = self._upkeep(self.learner)
                win_flg = self._draw(self.learner)
                #################################
                if win_flg < 0: # lose (LO)
                    _, reward = self._prevNS_prevR()
                    reward += self.lose_reward
                    yield state, action, None, reward, None
                    break
                ##################################
                self.feature_holder.push(self)
                
                # main
                self.set_phase(MAIN)
                while True:
                    possible_actions = self._possible_actions(self.learner)
                    if len(possible_actions) > 0:
                        nextstate, reward = self._prevNS_prevR()
                        yield state, action, nextstate, reward, possible_actions

                        state = self.feature_holder.get_state()
                        action = self.learner.cast_action(state, possible_actions)
                        self.feature_holder.push(self)
                        if action is None:
                            break
                    else:
                        break
                        
                # attack
                self.set_phase(ATTACK)
                possible_actions = self._possible_actions(self.learner)
                if len(possible_actions) > 0:
                    nextstate, reward = self._prevNS_prevR()
                    yield state, action, nextstate, reward, possible_actions

                    state = self.feature_holder.get_state()
                    action = self.learner.attack_action(state, possible_actions)
                    self.feature_holder.push(self)

                    # block
                    _ = self._block(self.opponent, push_f=False)

                    # assign
                    _ = self._assign(self.learner, push_f=False)

                    # damage (learner to opponent)
                    win_flg = self._damage(self.learner, self.opponent, push_f=False)
                    self.feature_holder.push(self)

                # MAIN2
                self.set_phase(MAIN2)
                while True:
                    possible_actions = self._possible_actions(self.learner)
                    if len(possible_actions) > 0:
                        nextstate, reward = self._prevNS_prevR()
                        yield state, action, nextstate, reward, possible_actions

                        state = self.feature_holder.get_state()
                        action = self.learner.cast_action(state, possible_actions)
                        self.feature_holder.push(self)
                        if action is None:
                            break
                    else:
                        break
                
                self._end()
                    
            else: # opponent's turn
                self._upkeep(self.opponent, push_f=False)
                self._draw(self.opponent, push_f=False)
                self._main(self.opponent)
                self.feature_holder.push(self)

                # attack
                self._attack(self.opponent)
                self.feature_holder.push(self)

                # block
                self.set_phase(BLOCK)
                possible_actions = self._possible_action(self.learner)
                if len(possible_actions) > 0:
                    nextstate, reward = self._prevNS_prevR()
                    yield state, action, nextstate, reward, possible_actions

                    state = self.feature_holder.get_state()
                    action = self.learner.block_action(state, possible_actions)

                self._assign(self.opponent)
                self._damage(self.opponent, self.learner)
                self.feature_holder.push(self)


                self._main2(self.opponent)
                self.feature_holder.push(self)

                self._end()
                
            
            self.playing_idx = 1 - self.playing_idx
            nturn += 1
            
        
