from mtg.settings import *
from mtg.cards import *

class BattleController():
    def __init__(self):
        # battles[i] = {'attacker':c,'blockers':[c1,c2],
        #                  'a2b':[damage, damage]}
        self.battles = []
        

    def reset(self):
        self.battles = []

    def add_attackers(self, creatures):
        for creature in creatures:
            self.battles.append({'attacker':creature})
        
    def add_blockers(self, blocker_list):
        # blocker_list[i] blocks self.battles[i]['attacker']
        
        for battle, blockers in zip(self.battles, blocker_list):
            battle['blockers'] = blockers
        

    #def assign_damages(self, damage_list):
    #    # damage_list[i] is for self.battles[i]['attacker']
    #    for battle, damages in zip(self.battles, damage_list):
    #        battle['a2b'] = damages
    

    def exec_damages(self):
        damages2players = []
        
        for battle in self.battles:
            if len(battle['blockers']) > 0:
                battle['attacker'].damaged(
                    sum([c.power for c in battle['blockers']])
                )
                for c,d in zip(battle['blockers'], battle['a2b']):
                    c.damaged(d)
            else:
                
                damages2players.append((battle['attacker'],
                                        battle['attacker'].power))

        return damages2players
            

        

    
        
        
        
