from settings import *


class Card():
    def __init__(self, id, name):
        self.name = name
        self.id = id

    def is_playable(self, game, player):
        pass

class Permanent(Card):
    def __init__(self, id, name):
        super(Permanent, self).__init__(id, name)
        self.state = UNTAP

    def is_tapped(self):
        return self.state == TAP

    def tap(self):
        if self.is_tapped():
            return 0
        else:
            self.state = TAP
            return 1

    def untap(self):
        if self.is_tapped():
            self.state = UNTAP
            return 1
        else:
            return 0

class Land(Permanent):
    def __init__(self, id, name):
        super(Land, self).__init__(id, name)
        self.state = TAP

    def is_playable(self, game, player):
        if game.is_turn(player) \
           and game.is_main() \
           and player.n_played_lands < player.n_playable_lands:
            return True
        else:
            return False

    def add_mana(self, manapool):
        if not self.is_tapped:
            self.tap()
            manapool.add(1)
            return 1
        else:
            return 0

class Creature(Permanent):
    def __init__(self, id, name, cost, power, toughness):
        super(Creature, self).__init__(id, name)
        self.cost = cost
        self.power = power
        self.toughness = toughness

        self.tmp_toughness = toughness


    def is_playable(self, game, player):
        if game.is_turn(players) \
           and game.is_main() \
           and player.mana_available <= self.cost:
            return True
        else:
            return False

    def damaged(self, n):
        self.tmp_toughness -= n

    def reset_damage(self):
        self.tmp_toughness = self.toughness

    def reset(self):
        self.state = UNTAP
        self.reset_damage()

    def is_dead(self):
        return self.tmp_toughness < 0


        
            
