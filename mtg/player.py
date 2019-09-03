from mtg.settings import *
from mtg.fields import *
from mtg.cards import *
from mtg.utils import show_creatures_list, to_all_decimal
import numpy as np
import logging

class Player():
    def __init__(self, id, deck, logger=logging):
        self.id = id

        self.life = LIFE
        self.deck = deck
        self.library = Library(deck)
        #self.shuffle()
        self.hand = Hand([])
        
        self.battlefield = BattleField()
        self.graveyard = Graveyard()
        self.exiled = Exiled()

        self.n_playable_lands = LANDS_PLAYABLE
        self.n_played_lands = 0

        self.logger = logger

    def reset(self, deck=None):
        self.life = LIFE
        if deck is None:
            self.library = Library(self.deck)
        else:
            self.deck = deck
            self.library = Library(deck)
            
        self.hand = Hand([])
        
        self.battlefield = BattleField()
        self.graveyard = Graveyard()
        self.exiled = Exiled()

        self.n_playable_lands = LANDS_PLAYABLE
        self.n_played_lands = 0

    def show_bf(self, as_op=False):
        if as_op:
            print("Opponent life:%d hand:%d Lib:%d" 
                % (self.life, len(self.hand), len(self.library)))
            self.battlefield.show_lands()
            self.battlefield.show_creatures("Opponent creatures")
        else:
            self.battlefield.show_creatures("Your creatures")
            self.battlefield.show_lands()
            print("Hand:" + str(self.hand))
            print("Your life:%d Lib:%d" % (self.life, len(self.library)))


    def log_info(self, mes):
        self.logger.info("Player_%d " % self.id + mes)

    def shuffle(self):
        self.log_info("shuffle")
        np.random.shuffle(self.library)

    def mana_available(self):
        return self.battlefield.mana_available()

    def castable_card(self, game):
        return {"hand":self.hand.playable(game, self)}

    def init_draw(self):
        self.draw(INIT_DRAW)
        
    def draw(self, n):
        win_flg = 0
        self.log_info("draw")
        drawed = self.library.pop_top(n)
        if len(drawed) > 0:
            self.hand.extend(drawed)
        else:
            win_flg = -1
            #raise Exception("Player%d loses, LO" % self.id)
        self.log_info("hand " + str(self.hand))
        return win_flg

    def damaged(self, n):
        self.life -= n
        self.log_info("damaged %d life %d" % (n, self.life))
        if self.life <= 0:
            return -1
        else:
            return 0

    def _cast_from_hand(self, card, game):
        # to be implemented in Game class ?
        self.hand.remove(card)
                
        if isinstance(card, Land):
            self.battlefield.lands.append(card)
            self.n_played_lands += 1
        elif isinstance(card, Creature):
            self.battlefield.use_mana(card.cost)
            self.battlefield.creatures.append(card)
        else:# spell
            self.battlefield.use_mana(card.cost)
            card.effect(game, self)
            self.graveyard.append(card)

    def end_turn(self):
        self.n_played_lands = 0

    def _discard(self, card):
        self.log_info("discard " + str(card))
        self.hand.remove(card)
        self.graveyard.append(card)

    def _attack(self, creatures, b_ctrl):
        b_ctrl.add_attackers(creatures)

    def _pick_cast_card(self, game,*args):
        return None  

    def _pick_attack_creatures(self, game,*args):
        return []

    def _assign_damage(self, attacker, blockers, game,*args):
        # Among creatures that can be killed, assign damage from the biggest toughness ones
        if len(blockers) > 0:
            damage = [0] * len(blockers)

            b_toughness = [(i, b.toughness) for i, b in enumerate(blockers)]
            sorted_list = sorted(b_toughness, key=lambda tmp: tmp[1] ,reverse=True)

            power = attacker.power
            for idx, toughness in sorted_list:
                if toughness <= attacker.power: # can kill
                    damage[idx] += min(toughness, power)
                    power -= toughness
                    if power <= 0:
                        break
            if power > 0: # there is no killable creature
                damage[-1] += power

            return damage
        return []


    def _pick_block_creatures(self, attackers, game, *args):
        return [[]]*len(attackers)

    def cast_command(self, game, *args):
        cast_card = self._pick_cast_card(game, *args)
        if cast_card is not None:
            self.log_info("cast_from_hand " + str(cast_card))
            self._cast_from_hand(cast_card, game)
            return 1
        else:
            return 0

    def attack_command(self, game, *args):
        attack_creatures = self._pick_attack_creatures(game, *args)
        self.log_info("attack " + "-".join([str(card) for card in attack_creatures]))
        self._attack(attack_creatures, game.battle_ctrl)
        return 0

    def block_command(self, game, *args):
        attackers = [battle['attacker'] for battle in game.battle_ctrl.battles]
        blocker_list = self._pick_block_creatures(attackers, game, *args)
        game.battle_ctrl.add_blockers(blocker_list)
        self.log_info("block " + game.battle_ctrl.log_str_ab())
        return 0

    def assign_damages_command(self, game, *args):
        #damage_list = self._assign_damages(game.battle_ctrl.battles, game)
        for battle in game.battle_ctrl.battles:
            battle['a2b'] = self._assign_damage(battle['attacker'],
                                                battle['blockers'], game,*args)
        self.log_info("assign_damages " + game.battle_ctrl.log_str_abd())
        return 0


class Stupid_Player(Player):
    def _pick_cast_card(self, game):

        if np.random.uniform() > 0.3:
            playable_cards = self.hand.playable(game, self)
            if len(playable_cards) > 0:
                card = np.random.choice(playable_cards)
                return card
            else:
                return None
        return None

    def _pick_attack_creatures(self, game):
        attackable_creatures = self.battlefield.get_attackable_creatures()
        l = len(attackable_creatures)
        if l > 0:
            attack_creatures = np.random.choice(
                attackable_creatures, size=np.random.randint(0, l+1), 
                replace=False)
            return attack_creatures
        else:
            return []

    def _pick_block_creatures(self, attackers, game):
        if len(attackers) == 0:
            return []

        untap_creatures = self.battlefield.get_untap_creatures()
        l = len(untap_creatures)
        if l > 0:
            block_creatures = np.random.choice(
                untap_creatures, size=np.random.randint(1, l+1), 
                replace=False)
        else:
            block_creatures = []
        
        block_list = [[]] * len(attackers)
        block_list[0] = block_creatures

        return block_list


            

class Cmd_Player(Player):
    def show_game(self, game):
        op = game.get_opponent(self)

        print("####################################")
        op.show_bf(as_op=True)
        self.show_bf()
        print("####################################")
    
    def _pick_cast_card(self, game):
        while True:
            castable_cards = self.castable_card(game)['hand']
            castable_dict = {card.tmp_id:card for card in castable_cards}

            if len(castable_cards) == 0:
                return None

            print("##### You can cast a card. #####")
            print("Your hand ...")
            print(str(self.hand))
            print("Type...")
            print("[tmp_id]: select cast card.")
            print("[bf]    : show battle field.")
            print("[skip]  : skip the phase.")

            choice = input().lower()
            if choice == "bf":
                self.show_game(game)
            elif choice == "skip":
                return None
            elif choice.isdecimal() and int(choice) in castable_dict:
                return castable_dict[int(choice)]
            else:
                print("Bad input.")

    def _pick_attack_creatures(self, game):
        attackable_creatures = self.battlefield.get_attackable_creatures()
        attackable_dict = {card.tmp_id:card for card in attackable_creatures}

        if len(attackable_creatures) == 0:
            return []
        
        while True:

            print("##### Choose attackers. ######")
            print("Type...")
            print("[tmp_id1|tmp_id2|..]: select attack card.")
            print("[bf]                : show battle field.")
            print("[skip]              : skip the phase.")

            choice = input().lower()
            if choice == "bf":
                self.show_game(game)
            elif choice == "skip":
                return []
            else:
                tmp_ids_str = choice.split("|")
                flg, tmp_ids = to_all_decimal(tmp_ids_str)
                if not flg or len(set(tmp_ids) - set(attackable_dict.keys()) ) > 0:
                    print("Bad input.")
                else:
                    return [attackable_dict[int(tmp_id)] for tmp_id in tmp_ids]

    def _pick_block_creatures(self, attackers, game):
        blockable_creatures = self.battlefield.get_untap_creatures()
        blockable_dict = {card.tmp_id:card for card in blockable_creatures}
        att_tmp_ids = [c.tmp_id for c in attackers]
        if len(attackers) == 0 or len(blockable_creatures) == 0:
            return []

        while True:
            show_creatures_list(attackers, 'opponent is attacking with ...')
            print("##### Choose blockers. #####")
            print("Type...")
            print("[a1(tmp_id):b1|a2:b2:b3|..] : select block creatures. (b1 blocks a1, b2 and b3 block a2)")
            print("[bf]                : show battle field.")
            print("[skip]              : skip the phase.")

            choice = input().lower()
            if choice == "bf":
                self.show_game(game)
            elif choice == "skip":
                return [[]] * len(attackers)
            else:
                battles_str = [b.split(':') for b in choice.split('|')]
                flg, battles = to_all_decimal(battles_str)
                tmp_att = [t[0] for t in battles]
                tmp_blo = [] 
                [tmp_blo.extend(t[1:]) for t in battles]
                
                if not flg or len(set(tmp_blo) - set(blockable_dict.keys()) ) > 0 \
                        or len(set(tmp_att) - set(att_tmp_ids)) > 0:
                    print("Bad input")
                else:
                    battles_dict = {tmp[0]:tmp[1:] for tmp in battles}
                    block_list = [[]] * len(attackers)
                    for i, att in enumerate(attackers):
                        if att.tmp_id in battles_dict:
                            blockers = [blockable_dict[i] for i 
                                            in battles_dict[att.tmp_id]]
                            block_list[i] = blockers
                    return block_list

#    def _assign_damage(self, attacker, blockers, game):
#        pass
            






            



