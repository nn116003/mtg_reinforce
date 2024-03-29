from mtg import game, player, utils
from mtg.settings import *
from mtg.cards import Land, Creature, WrathG
from mtg.fields import Hand

import unittest
import numpy as np 
import copy


class TestPlayer(unittest.TestCase):
    def setUp(self):
        np.random.seed(2)
        self.deck1 = utils.random_deck_from_list(32, './mtg/cards.csv')
        self.deck2 = utils.random_deck_from_list(32, './mtg/cards.csv')

        self.p1 = player.Stupid_Player(1, self.deck1)
        self.p2 =  player.Stupid_Player(2, self.deck2)
        self.game = game.Game([self.p1, self.p2])

    def test_reset(self):
        self.p1.life -= 10
        self.p1.hand = self.p1.library.pop_top(10)
        self.p1.battlefield.creatures.append(Creature(1,1,1,1,1))
        self.p1.graveyard.append(Creature(1,1,1,1,1))
        self.p1.battlefield.lands.append(Land(99,'land'))
        self.p1.n_played_lands += 1

        self.p1.reset()
        self.assertEqual(len(self.p1.library), len(self.deck1))
        self.assertEqual(self.p1.life, LIFE)
        self.assertEqual(len(self.p1.hand), 0)
        self.assertEqual(len(self.p1.battlefield.creatures), 0)
        self.assertEqual(len(self.p1.battlefield.lands), 0)
        self.assertEqual(len(self.p1.graveyard), 0)
        self.assertEqual(self.p1.n_played_lands, 0)

    def test_mana_available(self):
        tap_land = Land(99,'Land')
        tap_land.tap()
        untap_land = Land(99,'Land')

        self.p1.battlefield.lands.extend([tap_land, untap_land])
        self.p1.battlefield.manapool.add(2)

        self.assertEqual(self.p1.mana_available(), 3)

    def test_castable_card(self):
        c1 = Creature(1,1,1,1,1)
        c2 = Creature(1,2,2,1,1)
        land_h = Land(99, 'land')
        land_b1 = Land(99, 'hand')
        land_b2 = Land(99, 'hand')

        self.p1.hand = Hand([c1,c2,land_h])
        self.p1.battlefield.lands.append(land_b1)
        self.p1.battlefield.lands.append(land_b2)
        land_b1.tap()

        self.game.phase = MAIN1
        self.game.playing_idx = 0
        playables = self.p1.castable_card(self.game)
        self.assertEqual(set(playables['hand']), set([c1, land_h]))

        self.p1.battlefield.lands.append(land_h)
        self.p1.hand.remove(land_h)
        self.p1.hand.append(Land(99,''))
        self.p1.n_played_lands += 1

        playables = self.p1.castable_card(self.game)
        self.assertEqual(set(playables['hand']), set([c1, c2]))

    def test_draw(self):
        n = 7
        lib = copy.deepcopy(self.p1.library)
        topn = self.p1.library[:n]
        flg = self.p1.draw(n)

        self.assertEqual(flg, 0)
        self.assertEqual(set(topn), set(self.p1.hand))
        self.assertEqual([c.id for c in self.p1.library], 
                        [c.id for c in lib[n:]])
        
        flg = self.p1.draw(99999999)
        self.assertEqual(flg, -1)

    def test_damaged(self):
        d = 3
        flg = self.p1.damaged(d)
        self.assertEqual(d, LIFE - self.p1.life)
        self.assertEqual(flg, 0)

        flg = self.p1.damaged(99999)
        self.assertEqual(flg, -1)

    def test_cast_from_hand_land(self):
        land = Land(99, '')
        self.p1.hand = Hand([land])
        self.p1._cast_from_hand(land, self.game)
        self.assertEqual(self.p1.battlefield.lands, [land])
        self.assertEqual(self.p1.n_played_lands, 1)
        self.assertNotIn(land, self.p1.hand)
        self.assertEqual(land.state, UNTAP)

    def test_cast_from_hand_creature(self):
        creature = Creature(2,2,2,2,2)#cost 2
        self.p1.hand = Hand([creature])
        self.p1.battlefield.lands.extend(
            [Land(99, ''), Land(99,''), Land(99, '')])
        self.p1._cast_from_hand(creature, self.game)

        self.assertIn(creature, self.p1.battlefield.creatures)
        self.assertNotIn(creature, self.p1.hand)
        self.assertEqual(self.p1.mana_available(), 1)
        self.assertTrue(creature.summon_sick)
        self.assertEqual(creature.state, UNTAP)

    def test_cast_from_hand_wrath(self):
        spell = WrathG(999,4)
        self.p1.hand = Hand([spell])
        self.p1.battlefield.lands.extend(
            [Land(99, ''), Land(99,''), Land(99, ''), Land(99, '')])
        self_cs = [Creature(1,1,1,1,1),Creature(2,1,1,1,1)]
        opponent_cs = [Creature(3,1,1,1,1),Creature(4,1,1,1,1)]
        self.p1.battlefield.creatures = self_cs
        self.p2.battlefield.creatures = opponent_cs

        self.p1._cast_from_hand(spell, self.game)

        self.assertNotIn(spell, self.p1.hand)
        self.assertEqual(self.p1.battlefield.creatures, [])
        self.assertEqual(self.p2.battlefield.creatures, [])
        self.assertEqual(set(self.p1.graveyard), set(self_cs + [spell]))
        self.assertEqual(set(self.p2.graveyard), set(opponent_cs))
        self.assertEqual(self.p1.mana_available(), 0)

    def test_attack(self):
        pass

    def test_cast_command(self):
        pass
    
    def test_battle(self):
        creatures1 = [Creature(4,4,4,4,4),Creature(2,2,2,2,2),Creature(3,3,3,3,3),Creature(1,1,1,1,1)]
        for c in creatures1:
            c.summon_sick = False 
        creatures2 = [Creature(1,1,1,1,1),Creature(2,2,2,2,2),Creature(3,3,3,3,3)]
        self.p1.battlefield.cratures = creatures1
        self.p2.battlefield.cratures = creatures2

        # attack creatures1[0~2],
        # creatures2[2] block creatures1[0]
        # creatures2[0~1] block creatures1[2]
        def a(_):
            return creatures1[:3]
        self.p1._pick_attack_creatures = a
        def b(_,__):
            return [
                [creatures2[2]],# 4/4 is blocked by 3/3
                [], # 2/2 not blocked
                [creatures2[0],creatures2[1]] # 3/3 is blocked by 1/1 and 2/2
                ]
        self.p2._pick_block_creatures = b

        # attack command
        self.p1.attack_command(self.game)
        self.assertTrue(creatures1[0].is_tapped())
        self.assertTrue(creatures1[1].is_tapped())
        self.assertTrue(creatures1[2].is_tapped())
        self.assertFalse(creatures1[3].is_tapped())
        att_set = set([battle['attacker'] for battle in self.game.battle_ctrl.battles])
        self.assertEqual(att_set, set(creatures1[:3]))

        # block command
        self.p2.block_command(self.game)
        self.assertEqual(3, len(self.game.battle_ctrl.battles))
        self.assertIn({"attacker":creatures1[0], 'blockers':[creatures2[2]]}, self.game.battle_ctrl.battles)
        self.assertIn({"attacker":creatures1[1], 'blockers':[]}, self.game.battle_ctrl.battles)
        self.assertIn({"attacker":creatures1[2], 'blockers':[creatures2[0], creatures2[1]]}, self.game.battle_ctrl.battles)

        # assign command
        self.p1.assign_damages_command(self.game)
        self.assertEqual(3, len(self.game.battle_ctrl.battles))
        self.assertIn({"attacker":creatures1[0], 'blockers':[creatures2[2]], 'a2b':[4]}, 
                        self.game.battle_ctrl.battles)
        self.assertIn({"attacker":creatures1[1], 'blockers':[], 'a2b':[]}, 
                        self.game.battle_ctrl.battles)
        self.assertIn({"attacker":creatures1[2], 'blockers':[creatures2[0], creatures2[1]], 'a2b':[1,2]}, 
                        self.game.battle_ctrl.battles)

        
if __name__ == "__main__":
    unittest.main()

