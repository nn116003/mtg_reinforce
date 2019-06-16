from settings import *
from cards import *

class BattleController():
    def __init__(self):
        # relations[i] = {'attacker':c,'blockers':[c1,c2],
        #                  'a2b':[damage, damage]}
        self.battles = {}
        

    def reset(self):
        self.battles = {}

    def add_attackers(self, creatures):
        for creature in creatures:
            self.append({'attacker':creature})
        
    def add_one_blockers(self, idx, blockers):
        self.battle[idx]['blockers'] = blockers

    def assign_damages(self, idx, damages):
        self.battle[idx]['a2b'] = damages

    def exec_damages(self):
        damages2players = []
        
        for battle in battles:
            if 'blockers' in battle:
                battle.attacker.damaged(
                    sum([c.power for c in battle['blockers']])
                )
                for c,d in zip(battle.blockers, battle.a2b):
                    c.damaged(d)
            else:
                damages2players.append((battle.attacker,
                                        battle.attacker.power))

        return damages2players
            

        

    
        
        
        
