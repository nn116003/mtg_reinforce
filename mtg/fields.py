from .settings import *
from .utils import show_creatures_list


class Manapool():
    def __init__(self):
        self.mana = 0

    def add(self, n):
        self.mana += n

    def use(self, n):
        if self.mana < n:
            assert "you are to use mana more than that of in mana pool."
        self.mana -= n

    def reset(self):
        self.mana = 0


class BattleField():
    def __init__(self):
        self.lands = []
        self.creatures = []
        self.manapool = Manapool()

    def __str__(self):
        n_lands = len(self.lands)
        n_untap_lands = len(self.get_untap_lands())
        c_s = "|".join([str(card) for card in self.creatures ])
        return "Lands:T%d|U%d Creatures:%s" % (n_lands - n_untap_lands, n_untap_lands,
                                                c_s)

    def show_creatures(self, name):
        show_creatures_list(self.creatures, name)

    def show_lands(self):
        n_lands = len(self.lands)
        n_untap_lands = len(self.get_untap_lands())
        print("Lands:T%d|U%d" % (n_lands - n_untap_lands, n_untap_lands))

    def untap_all(self):
        [land.untap() for land in self.lands if land.is_tapped()]
        [creature.untap() for creature in self.creatures if creature.is_tapped()]

    def fix_summon_sick(self):
        [creature.fix_summon_sick() for creature in self.creatures]

    def get_untap_lands(self):
        return [land for land in self.lands if not land.is_tapped()]

    def get_untap_creatures(self):
        return [creature for creature in self.creatures if not creature.is_tapped()]

    def get_attackable_creatures(self):
        return [creature for creature in self.creatures if creature.is_attackable()]

    def mana_available(self):
        return len(self.get_untap_lands()) + self.manapool.mana

    def _add_mana_to_pool(self, n):
        usable_lands = self.get_untap_lands()
        if n > len(usable_lands):
            raise Exception("you cant make mana")
        else:
            for land in usable_lands[:n]:
                land.add_mana(self.manapool)

    def _use_mana_from_pool(self, n):
        if n > self.manapool.mana:
            raise Exception("you are using too many mana")
        else:
            self.manapool.use(n)

    def use_mana(self, n):
        if self.mana_available() < n:
            raise Exception("you cant cast this card")
        else:
            tmp = self.manapool.mana - n
            if tmp < 0:
                self._add_mana_to_pool(-tmp)
            self._use_mana_from_pool(n)

        
class Library(list):
    def pop_top(self, n):
        if len(self) < n:
            return []

        top = self[:n]
        del self[:n]
        
        return top

class Hand(list):

    def playable(self, game, player):
        return [card for card in self if card.is_playable(game, player)]

    def lands(self):
        return [card for card in self if "Land" in str(type(card))]

    def __str__(self):
        card_str = [str(card) for card in self]
        return "|".join(card_str)

class Graveyard(list):
    pass

class Exiled(list):
    pass    
        
