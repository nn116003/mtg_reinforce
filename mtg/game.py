from mtg.settings import *
from mtg.battle import *
from mtg.utils import assign_ids_in_game
import logging 
import itertools

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
        [player.init_draw() for player in self.players]

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


    def _upkeep(self, player):
        # fix summon sick
        player.battlefield.fix_summon_sick()

        # upkeep
        self.set_phase(UPKEEP)
        player.battlefield.untap_all()

        return 0

    def _draw(self, player):
        # draw
        win_flg = 0
        self.set_phase(DRAW)
        if self.n_turn > 0:
            win_flg = player.draw(1)
        return win_flg
            

    def _main(self, player):
        # main1
        self.set_phase(MAIN1)
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,
        return 0

    def _attack(self, player):
        # battle
        self.set_phase(ATTACK)
        player.attack_command(self)
        return 0

    def _block(self, blocking_player):
        self.set_phase(BLOCK)
        blocking_player.block_command(self)
        return 0

    def _assign(self, player):
        self.set_phase(ASSIGN, show_bf=False)
        player.assign_damages_command(self)
        return 0

    def _damage(self, player, opponent):
        self.set_phase(DAMAGE, show_bf=False)
        damages2opponent = self.battle_ctrl.exec_damages()
        total_damage = sum([x[1] for x in damages2opponent])
        opponent_win_flg = opponent.damaged(total_damage)

        self._burial_corpses(player)
        self._burial_corpses(opponent)

        self.battle_ctrl.reset()

        return -1 * opponent_win_flg

    def _main2(self, player):
        # main2
        self.set_phase(MAIN2)
        while True:
            if player.cast_command(self) == 0:
                break
            # there is no instant card yet,
        return 0

    def _end(self):
        self._end_turn()
        self.n_turn += 1
        return 0


    def _possible_actions(self, player):
        if self.phase in [MAIN1, MAIN2]:
            return [card.id for card in player.castable_card(self)["hand"]]

        elif self.phase == ATTACK:
            attackable_creatures = player.battlefield.get_attackable_creatures()
            ac_ids = [card.id for card in attackable_creatures]
            if len(ac_ids) > 0:
                comb = []
                for i in range(len(ac_ids)):
                    comb.extend(itertools.combinations(ac_ids, i+1))
                return comb
            else:
                return []

        elif self.phase == BLOCK:
            ac_num = len(self.battle_ctrl.battles )
            blockable_creatures = player.battlefield.get_untap_creatures()
            bc_ids = [card.id for card in blockable_creatures ]
            if ac_num  > 0 and len(bc_ids) > 0:
                block_targets = list(range(ac_num + 1)) # +1: not block
                block_patterns = itertools.product(
                    *([block_targets]*len(bc_ids))
                    )
                res = []
                for pattern in block_patterns:
                    block_list = [[] for i in range(ac_num)]
                    for bc_id, b_target in zip(bc_ids, pattern):
                        if b_target < ac_num:
                            block_list[b_target].append(bc_id)
                    res.append(block_list)
                return res
            else:
                return []
        
            
    def _turn(self):
        self.log_info("start ##############################")
        player = self.players[self.playing_idx]
        opponent = self.players[1 - self.playing_idx]
        
        # fix summon sick
        # upkeep
        _ = self._upkeep(player)

        # draw
        win_flg = self._draw(player)
        if win_flg != 0:
            return "LO", win_flg 


        # main1
        _ = self._main(player)

        # battle
        _ = self._attack(player)
        _ = self._block(opponent)
        _ = self._assign(player)
        win_flg = self._damage(player, opponent)
        if win_flg != 0:
            return "LL", win_flg
        
        # main2
        _ = self._main2(player)
        
        # end
        _ = self._end()

        return None, 0
        

    def main(self):
        [player.shuffle() for player in self.players]
        self._init_draw()

        #try:    
        nturn = 0
        while True:
            win_condition, win_flg = self._turn()
            if win_flg == 1:
                print("player %d WIN (%s)" % (self.playing_idx, win_condition))
                break 
            elif win_flg == -1:
                print("player %d WIN (%s)" % (1 - self.playing_idx, win_condition))
                break 
            self.playing_idx = 1 - self.playing_idx
            nturn += 1
        #except Exception as e:
        #    print(e)
        
        




        
