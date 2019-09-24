# env cast_action(game,....)
# possible action -> agent?

from model import CastModule, AttackModule, BlockModule, FCGameEncoder
from mtg.player import Player

import logging

class AgentLearner(Player):
    def __init__(self, id, deck, cast_module, attack_module, block_module, 
        logger=logging):
        super(Agent, self).__init__(id, deck ,logger)
        self.cast_module = cast_module
        self.attack_module = attack_module
        self.block_module = block_module

    def train(self):
        self.cast_module.train()
        self.attack_module.train()
        self.block_module.train()

    def eval(self):
        self.cast_module.eval()
        self.attack_module.eval()
        self.block_module.eval()

    def _select_cast_action(self, state_tensor, card_ids):
        pass

    def cast_action(self, state, card_ids):
        pass

class AgentFromPlayer(Player):
    def __init__(self, id, deck, logger=logging):
        super(Agent, self).__init__(id, deck ,logger)

    def cast_action(self, env, *args):
        state = env.get_state()
        cast_card = self._pick_cast_card(env, *args)
        return state, utils.card2action(cast_card)
        
