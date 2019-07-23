from mtg.settings import *
from mtg.battle import *
from mtg.utils import assign_ids_in_game
import logging 

class Game():
    def __init__(self, players, logging=logging ):
        self.players = players
        assign_ids_in_game(players[0].library, players[1].library) 

        self.phase = None
        self.battle_ctrl = BattleController()
        
        self.playing_idx = 0 # players[0] plays first

        self.logger = logging 
        
        self.n_turn = 0

    def reset(self, players):
        self.players = players
        assign_ids_in_game(players[0].library, players[1].library) 

        self.phase = None
        self.battle_ctrl = BattleController()
        
        self.playing_idx = 0 # players[0] plays first

        self.n_turn = 0

    def get_opponent(self, player):
        return list((set(self.players) - set([player])))[0]

    def log_info(self, mes):
        self.logger.info("Turn_%d P_%d " % 
                            (self.n_turn, self.playing_idx+1) + mes)

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
            
    def set_phase(self, phase, show_bf=True ):
        self.phase = phase 
        self.log_info("Phase:" + self.phase)

        if show_bf:
            self.log_info("Player_1 BattleField:%s" 
                        % str(self.players[0].battlefield) )
            self.log_info("Player_2 BattleField:%s" 
                        % str(self.players[1].battlefield) )

    def _turn(self):
        self.log_info("start ##############################")
        player = self.players[self.playing_idx]
        opponent = self.players[1 - self.playing_idx]
        
        # fix summon sick
        player.battlefield.fix_summon_sick()

        # upkeep
        self.set_phase(UPKEEP)
        player.battlefield.untap_all()

        # draw
        self.set_phase(DRAW)
        if self.n_turn > 0:
            player.draw(1)

        # main1
        self.set_phase(MAIN1)
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,

        # battle
        self.set_phase(ATTACK)
        player.attack_command(self)

        self.set_phase(BLOCK)
        opponent.block_command(self)

        self.set_phase(ASSIGN, show_bf=False)
        player.assign_damages_command(self)

        self.set_phase(DAMAGE, show_bf=False)
        damages2opponent = self.battle_ctrl.exec_damages()
        total_damage = sum([x[1] for x in damages2opponent])
        opponent.damaged(total_damage)

        self._burial_corpses(player)
        self._burial_corpses(opponent)

        self.battle_ctrl.reset()

        # main2
        self.set_phase(MAIN2)
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,

        # end
        self._end_turn()
        self.n_turn += 1
        

    def main(self):
        [player.shuffle() for player in self.players]
        self._init_draw()

        #try:    
        nturn = 0
        while True:
            self._turn()
            self.playing_idx = 1 - self.playing_idx
            nturn += 1
        #except Exception as e:
        #    print(e)
        
        




        
