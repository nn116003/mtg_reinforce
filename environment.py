from mtg.game import Game
from mtg.settings import *
import logging


class FeatureHolder(object):
    def __init__(length, creature_ids, land_id, wrath_id):
        pass

    def _extract_feats(player, opponent):
        pass

    def push(game):
        pass

    def get_state():
        pass

class Env(Game):
    def __init__(self, learner, opponent, first=True, logging=logging):
        super(Env, self).__init__([learner, opponent], logging=logging)
        self.learner = learner
        self.opponent = opponent
        
        if not first:
            self.playing_idx = 1

        # to save past n turn features
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


    def _prevNS_prevR(self):
        prev_nextstate = self.get_state()
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
                self._upkeep(self.learner, push_f=False) # push_=T to add feature
                self._draw(self.learner, push_f=False)
                
                # main
                self.set_phase(MAIN)
                while True:
                    possible_actions = self.possible_action(self.learner)
                    if possible_actions is not None:
                        nextstate, reward = self._prevNS_prevR()
                        yield state, action, nextstate, reward, possible_actions

                        state = self.get_state()
                        action = self.learner.cast_action(state, possible_actions)
                        if action is None:
                            break
                    else:
                        break
                        
                # attack
                self.set_phase(ATTACK)
                possible_actions = self.possible_action(self.learner)
                if possible_actions is not None:
                    nextstate, reward = self._prevNS_prevR()
                    yield state, action, nextstate, reward, possible_actions

                    state = self.get_state()
                    action = self.learner.attack_action(state, possible_actions)

                    # block
                    self._block(self.opponent, push_f=False)

                    # assign
                    self._assign(self.learner, push_f=False)

                    # damage
                    self._damage(self.learner, self.opponent, push_f=False)

                # MAIN2
                self.set_phase(MAIN2)
                while True:
                    possible_actions = self.possible_action(self.learner)
                    if possible_actions is not None:
                        nextstate, reward = self._prevNS_prevR()
                        yield state, action, nextstate, reward, possible_actions

                        state = self.get_state()
                        action = self.learner.cast_action(state, possible_actions)
                        if action is None:
                            break
                    else:
                        break

                self._end()
                    
            else: # opponent's turn
                self._upkeep(self.opponent, push_f=False)
                self._draw(self.opponent, push_f=False)
                self._main(self.opponent)

                # attack
                self._attack(self.opponet)

                # block
                possible_actions = self.possible_action(self.learner)
                if possible_actions is not None:
                    nextstate, reward = self._prevNS_prevR()
                    yield state, action, nextstate, reward, possible_actions

                    state = self.get_state()
                    action = self.learner.block_action(state, possible_actions)

                self._assign(self.opponent)
                self._damage(self.opponent, self.learner)
                self._main2(self.opponent)
                self._end()
                
            
            self.playing_idx = 1 - self.playing_idx
            nturn += 1
            
        
