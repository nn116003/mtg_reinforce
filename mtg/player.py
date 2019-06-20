from mtg.settings import *
from mtg.fields import *
from mtg.cards import *
import numpy as np
import logging

class Player():
    def __init__(self, id, deck, logger=logging):
        self.id = id

        self.life = LIFE
        self.library = Library(deck)
        #self.shuffle()
        
        self.battlefield = BattleField()
        self.graveyard = Graveyard()
        self.exiled = Exiled()

        self.n_playable_lands = LANDS_PLAYABLE
        self.n_played_lands = 0

        self.logger = logger

    def log_info(self, mes):
        self.logger.info("Player_%d " % self.id + mes)

    def shuffle(self):
        self.log_info("shuffle")
        np.random.shuffle(self.library)

    def mana_available(self):
        return self.battlefield.mana_available()

    def init_draw(self, n):
        self.log_info("init_draw")
        self.hand = Hand(self.library.pop_top(n))
        self.log_info("hand " + self.hand.log_str())
        
    def draw(self, n):
        self.log_info("draw")
        drawed = self.library.pop_top(n)
        if len(drawed) > 0:
            self.hand.extend(drawed)
        else:
            raise Exception("LO")
        self.log_info("hand " + self.hand.log_str())

    def damaged(self, n):
        self.log_info("damaged %d" % n)
        self.life -= n
        if self.life <= 0:
            raise Exception("you dead")

    def _cast_from_hand(self, card):
        
        self.hand.remove(card)
        tmp = str(type(card))
        
        if "Land" in tmp:
            self.battlefield.lands.append(card)
            self.n_played_lands += 1
        else:
            self.battlefield.use_mana(card.cost)
            self.battlefield.creatures.append(card)

    def end_turn(self):
        self.n_played_lands = 0

    def _discard(self, card):
        self.log_info("discard " + card.log_str())
        self.hand.remove(card)
        self.graveyard.append(card)

    def _attack(self, creatures, b_ctrl):
        b_ctrl.add_attackers(creatures)

    def _pick_cast_card(self, game):
        return None  

    def _pick_attack_creatures(self, game):
        return []

    #def _pick_block_creature(self, attacker, blockables, game):
    #    pass

    def _assign_damage(self, attacker, blockers, game):
        if len(blockers) > 0:
            damage = [0] * len(blockers)
            damage[0] = attacker.power
            return damage
        return []


    def _pick_block_creatures(self, attackers, game):
        return [[]]*len(attackers)

    def cast_command(self, game):
        cast_card = self._pick_cast_card(game)
        if cast_card is not None:
            self.log_info("cast_from_hand " + cast_card.log_str())
            self._cast_from_hand(cast_card)
            return 1
        else:
            return 0

    def attack_command(self, game):
        attack_creatures = self._pick_attack_creatures(game)
        self.log_info("attack " + "-".join([card.log_str() for card in attack_creatures]))
        self._attack(attack_creatures, game.battle_ctrl)
        return 0

    def block_command(self, game):
        attackers = [battle['attacker'] for battle in game.battle_ctrl.battles]
        blocker_list = self._pick_block_creatures(attackers, game)
        game.battle_ctrl.add_blockers(blocker_list)
        self.log_info("block " + game.battle_ctrl.log_str_ab())
        return 0

    def assign_damages_command(self, game):
        #damage_list = self._assign_damages(game.battle_ctrl.battles, game)
        for battle in game.battle_ctrl.battles:
            battle['a2b'] = self._assign_damage(battle['attacker'],
                                                battle['blockers'], game)
        self.log_info("assign_damages " + game.battle_ctrl.log_str_abd())
        return 0


class Stupid_Player(Player):
    def _pick_cast_card(self, game):

        if np.random.uniform() > 0.3:
            playable_cards = self.hand.playable(game, self)
            if len(playable_cards) > 0:
                card = np.random.choice(playable_cards)
                return card
            else:
                return None
        return None

    def _pick_attack_creatures(self, game):
        untap_creatures = self.battlefield.get_untap_creatures()
        l = len(untap_creatures)
        if l > 0:
            attack_creatures = np.random.choice(
                untap_creatures, size=np.random.randint(0, l+1), 
                replace=False)
            return attack_creatures
        else:
            return []

    def _pick_block_creatures(self, attackers, game):
        if len(attackers) == 0:
            return []

        untap_creatures = self.battlefield.get_untap_creatures()
        l = len(untap_creatures)
        if l > 0:
            block_creatures = np.random.choice(
                untap_creatures, size=np.random.randint(1, l+1), 
                replace=False)
        else:
            block_creatures = []
        
        block_list = [[]] * len(attackers)
        block_list[0].extend(block_creatures)

        return block_list


            








            



