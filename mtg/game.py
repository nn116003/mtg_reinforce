from mtg.settings import *
from mtg.battle import *


class Game():
    def __init__(self, players):
        self.players = players
        self.phase = None
        self.battle_ctrl = BattleController()
        
        self.playing_idx = 0 # players[0] plays first


    def _init_draw(self):
        [player.init_draw(INIT_DRAW) for player in self.players]

    def _burial_corpses(self, player):
        dead_creatures = [creature for
                          creature in player.battlefield.creatures
                          if creature.is_dead()]
        for dead_creature in dead_creatures:
            player.battlefield.creatures.remove(dead_creature)
            player.graveyard.append(dead_creature)

    def _reset_damages(self):
        [c.reset_damage() for c in self.players[0].battlefield.creatures]
        [c.reset_damage() for c in self.players[1].battlefield.creatures]

    def _end_turn(self):
        self._reset_damages()
        [player.end_turn() for player in self.players]
        

    def is_turn(self, player):
        return self.players[self.playing_idx] == player

    def is_main(self):
        return (self.phase in (MAIN1, MAIN2))
            

    def _turn(self, draw=True):
        player = self.players[self.playing_idx]
        opponent = self.players[1 - self.playing_idx]
        
        # upkeep
        self.phase = UPKEEP
        player.battlefield.untap_all()

        # draw
        self.phase = DRAW
        player.draw(1)

        # main1
        self.phase = MAIN1
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,

        # battle
        self.phase = ATTACK
        player.attack_command(self)

        self.phase = BLOCK
        opponent.block_command(self)

        self.phase = ASSIGN
        player.assign_damages_command(self)

        self.phase = DAMAGE
        damages2opponent = self.battle_ctrl.exec_damages()
        total_damage = sum([x[1] for x in damages2opponent])
        opponent.damaged(total_damage)

        self._burial_corpses(player)
        self._burial_corpses(opponent)

        self.battle_ctrl.reset()

        # main2
        self.phase = MAIN2
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,

        # end
        self._end_turn()
        

    def main(self):
        self._init_draw()

        nturn = 0
        while True:
            self._turn(draw = nturn>0 )
            #print(nturn, len(self.players[0].library))
            self.playing_idx = 1 - self.playing_idx
            nturn += 1
        
        




        
