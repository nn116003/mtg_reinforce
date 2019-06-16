from settings import *
from fields import *
from cards import *
import numpy as np

class Player():
    def __init__(self, deck):
        self.life = LIFE
        self.library = Library(deck)
        np.random.shuffle(self.library)
        
        self.battlefield = BattleField()
        self.graveyard = Graveyard()
        self.exiled = Exiled()

        self.n_playable_lands = LANDS_PLAYABLE
        self.n_played_lands = 0

    def mana_available(self):
        return self.battlefield.mana_available()

    def init_draw(self, n):
        self.hand = Hand(self.library.pop_top(n))

    def draw(self, n):
        drawed = self.library.pop_top(n)
        if len(drawed) > 0:
            hand.extend(drawed)
        else:
            assert "LO"

    def damaged(self, n):
        self.life -= n
        if self.life <= 0:
            assert "you dead"

    def _cast_from_hand(self, card):
        self.hand.remove(card)
        tmp = str(type(card))
        
        if "Land" in tmp:
            self.battlefield.lands.append(card)
            self.n_played_lands += 1
        else:
            self.battlefield.use_mana(card.cost)
            self.battlefield.creatures.append(card)

    def reset_in_game(self):
        self.n_played_lands = 0

    def _discard(self, card):
        self.hand.remove(card)
        self.graveyard.append(card)

    def _attack(self, creatures, b_ctrl):
        b_ctrl.add_attackers(creatures)

    def cast_command(self, game):
        return 0

    def attack_command(self, game):
        return 0

    def block_command(self, game):
        return 0

    def assign_damages_command(self, game):
        return 0


        
        


def Random_Player(Player):
    def _cast_command(self, game):
        # cast land
        lands = self.hand.land()
        if lands[0].is_playable(game, self):
            self._cast_from_hand(lands[0])

        # cast creature
        playable_cards = self.hand.playable(game, self)
        if len(playable_cards) > 0:
            card = np.random.choice(playable_cards)
            self._cast_from_hand(card)

    def _attack_command(self, game):
        if len(self.battlefield_creatures) > 0:
            
        
        











