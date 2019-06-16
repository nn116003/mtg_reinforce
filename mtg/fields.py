from settings import *


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

    def untap_all(self):
        [land.untap() for self.lands if land.is_tapped()]
        [creature.untap() for self.creatures if creature.is_tapped()]

    def get_untap_lands(self):
        return [land for self.lands if not land.is_tapped()]

    def get_untap_creatures(self):
        return [creature for self.creatures if not creature.is_tapped()]

    def mana_available(self):
        return len(self.get_untap_lands) + self.manapool.mana

    def _add_mana_to_pool(self, n):
        usable_lands = self.get_untap_lands
        if n > len(usable_lands):
            assert "you cant make mana"
        else:
            for land in usable_lands[:n]:
                land.add_mana(self.manapool)

    def _use_mana_from_pool(self, n):
        if n > self.manapool.mana:
            assert "you are using too many mana"
        else:
            self.manapool.use(n)

    def use_mana(self, n):
        if self.mana_available(self) < n:
            assert "you cant cat this card"
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
        return [card in self if card.is_playable(game, player)]

    def lands(self):
        return [card in self if "Land" in str(type(card))]

class Graveyard(list):
    pass

class Exiled(list):
    pass    
        
