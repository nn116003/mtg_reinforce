from mtg.settings import *


class Card():
    def __init__(self, id, name):
        self.name = name
        self.id = id

        # id for individual card in game
        self.tmp_id = 0

    def is_playable(self, game, player):
        pass

    def __str__(self):
        return "%d_%d" % (self.tmp_id, self.id)

class Spell(Card):
    def __init__(self, id, name, cost, flash=False):
        super(Spell, self).__init__(id, name)
        self.cost = cost
        self.flash = flash

    def is_playable(self, game, player):
        if not self.flash:
            if game.is_turn(player) \
                and game.is_main() \
                and (player.mana_available() >= self.cost):
                return True
            else:
                return False
        else:
            return player.mana_available() >= self.cost

    def effect(self, game, player):
        pass

class WrathG(Spell):
    def __init__(self, id, cost):
        super(WrathG, self).__init__(id, "WrathOfGod", cost)

    def effect(self, game, player):
        op = game.get_opponent(player)
        player.graveyard.extend(player.battlefield.creatures)
        player.battlefield.creatures = []
        op.graveyard.extend(op.battlefield.creatures)
        op.battlefield.creatures = []

class Permanent(Card):
    def __init__(self, id, name):
        super(Permanent, self).__init__(id, name)
        self.state = UNTAP

    def __str__(self):
        return "%d_%d_%s" % (self.tmp_id, self.id, self.state)

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
        self.state = UNTAP

    def is_playable(self, game, player):
        if game.is_turn(player) \
           and game.is_main() \
           and player.n_played_lands < player.n_playable_lands:
            return True
        else:
            return False

    def add_mana(self, manapool):
        if not self.is_tapped():
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

        self.summon_sick = True

    def is_playable(self, game, player):
        if game.is_turn(player) \
           and game.is_main() \
           and (player.mana_available() >= self.cost):
            return True
        else:
            return False

    def __str__(self):
        return "%d_%d(%d/%d/%d)_%s%s" % (self.tmp_id, self.id, 
            self.cost, self.power, self.tmp_toughness, self.state, 
            "ss" if self.summon_sick else "")

    def fix_summon_sick(self):
        self.summon_sick = False

    def is_attackable(self):
        return (not self.summon_sick) and (not self.is_tapped())

    def damaged(self, n):
        self.tmp_toughness -= n

    def reset_damage(self):
        self.tmp_toughness = self.toughness

    def reset(self):
        self.state = UNTAP
        self.reset_damage()

    def is_dead(self):
        return self.tmp_toughness <= 0


        
            
