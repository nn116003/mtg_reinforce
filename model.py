import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


def _sumemb_bf_creatures(card_embedding, p_feat):
    embed_p_bf_c = card_embedding(
        p_feat['creatures']) # bs, phase_len, max_c -> bs, phase_len, max_c, card_emb_dim

    p_tap_flg = p_feat['tap_flg'].unsqueeze(-1)   # bs, phase_len, max_c, 1
    p_sick_flg = p_feat['sick_flg'].unsqueeze(-1) # bs, phase_len, max_c, 1
    embed_p_tap = (emebed_p_bf_c * p_tap_flg).sum(dim=2) # bs, phase_len, card_emb_dim
    embed_p_untap = (emebed_p_bf_c * (1-p_tap_flg)).sum(dim=2) # bs, phase_len, card_emb_dim
    embed_p_sick = (embed_p_bf_c * p_sick_flg).sum(dim=2) # bs, phase_len, card_emb_dim

    return embed_p_tap, embed_p_untap, embed_p_sick

def _fc_block(in_d, out_d, n_layer, nch):
    layers = []
    for i in range(n_layer):
        tmp_in = tmp_out = nch
        if i == 0:
            tmp_in = in_d
        if i == n_layer-1:
            tmp_out = out_d

        layers.append(nn.Linear(tmp_in, tmp_out))

        if i < n_layer - 1:
            layers.append(nn.ReLU())
        
    return nn.Sequential(*layers)


class FCGameEncoder(nn.Module):
    def __init__(self, out_d, 
        card_embedding=None, card_num=None, card_emb_dim=12, card_pad_idx=0,
        phase_embedding=None, phase_emb_dim=4, phase_pad_idx=0,
        dense_feat_dim=5, 
        phase_len=3, n_layer=2, nch=24):
        super(FCGameEncoder, self).__init__()

        self.out_d = out_d

        if card_embedding is None:
            self.card_embedding = nn.Embedding(
                                    card_num + 2, card_emb_dim, padding_idx=card_pad_idx) # Null card + padding idx
        else:
            self.card_embedding = card_embedding

        if phase_embedding is None:
            self.phase_embedding = nn.Embedding(
                                    8 + 1, phase_emb_dim, padding_idx=phase_pad_idx)
        else:
            self.phase_embedding = card_embedding

        first_input_dim = (dense_feat_dim * 2 
            # creatures*(tap, untap, summon sick)
            + (card_emb_dim * 2)*3 
            # gy, hand
            + (card_emb_dim) * 3 
            # phase, playing_idx
            + phase_emb_dim +1 ) * phase_len

        self.nn = _fc_block(first_input_dim, out_d, n_layer, nch)

    def forward(self, feat_dict):
        p_feat = feat_dict['player'] # bs, phase_len, dence_dim
        o_feat = feat_dict['opponent']

        # dence feature
        # bs, phase_len, dense_dim
        p_dense = p_feat['dense'] 
        o_dense = o_feat['dense'] 

        # creatures on bf
        # bs, phase_len, card_emb_dim
        embed_p_bf, emebd_p_tap, embed_p_untap = _sumemb_bf_creatures(self.card_embedding, p_feat)
        embed_o_bf, emebd_o_tap, embed_o_untap = _sumemb_bf_creatures(self.card_embedding, o_feat)

        # gy, hand
        # bs, phase_len, max_len, card_emb_dim -> bs, phase_len, card_emb_dim
        embed_p_gy = self.card_embedding(p_feat['gy']).sum(dim=2)
        embed_o_gy = self.card_embedding(o_feat['gy']).sum(dim=2)

        embed_p_hand = self.card_embedding(p_feat['hand']).sum(sim=2)

        # phase
        # bs, phase_len, phase_emb_dim
        embed_phase = self.phase_embedding(feat_dict['phase'])

        # playing_idx
        # bs, phase_len, 1
        playing_idx = feat_dict['playing_idx'].unsqueeze(-1)
    
        input2fc = torch.cat([p_dense, o_dense, 
                            embed_p_bf, emebd_p_tap, embed_p_untap,
                            embed_o_bf, emebd_o_tap, embed_o_untap,
                            embed_p_gy, embed_o_gy, embed_p_hand,
                            embed_phase, playing_idx], dim=2) # bs, phase_len, first_input_dim

        return self.nn(input2fc.view(p_dense.shape[0],-1)) # bs, out_d

class CastModule(nn.Module):
    def __init__(self, card_embedding, game_embedding, n_layer=2, nch=12):
        super(CastModule, self).__init__()
        self.card_embedding = card_embedding
        self.game_embedding = game_embedding
        self.nn = _fc_block(self.game_embedding.out_d + self.card_embedding.embedding_dim,
                             1, n_layer, nch)

    def forward(self, state, card_ids):
        embed_game = self.game_embedding(state) # bs, game_embedding.out_d
        embed_card = self.card_embedding(card_ids) # bs -> bs,card_emb_dim
        return self.nn(torch.cat([embed_game, embed_card]), dim=1) # bs, 1

class AttackModule(nn.Module):
    def __init__(self, card_embedding, game_embedding, n_layer=2, nch=12):
        super(AttackModule, self).__init__()
        self.card_embedding = card_embedding
        self.game_embedding = game_embedding
        self.gamesp2cardsp = nn.Linear(game_embedding.out_d, card_embedding.embedding_dim)
        self.nn = _fc_block(card_embedding.embedding_dim, 1, n_layer, nch)

    def forward(self, 
                state, # dict
                attackers # bs, max_c
                ):
        embed_game = self.game_embedding(state) # bs, out_d
        fix_embed_game = self.gamesp2cardsp(F.ReLU(emebd_game)) # bs, card_emb_dim
        embed_attackers = self.card_embedding(attackers) # bs, max_c, card_emb_dim
        pre_attentions = (fix_embed_game.unsqueeze(1) * embed_attackers).sum(dim=-1, keepdim=True) #bs, max_c, 1
        attentions = F.sigmoid(attentions)
        vector = (embed_attackers * attentions).sum(dim=1) # bs, card_emb_dim
        return self.nn(vector)

class BlockModule(nn.Module):
    def __init__(self, card_embedding, game_embedding, n_layer=2, nch=12):
        super(BlockModule, self).__init__()
        self.card_embedding = card_embedding
        self.game_embedding = game_embedding
        self.gamesp2cardsp = nn.Linear(game_embedding.out_d, card_embedding.embedding_dim)
        self.nn = _fc_block(card_embedding.embedding_dim, 1, n_layer, nch)

    def forward(self, 
                state, #dict
                attackers, # bs, max_c
                blockers, # bs, max_c(att), max_c(block)
                ):
        embed_game = self.game_embedding(state) # bs, out_d
        fix_embed_game = self.gamesp2cardsp(F.ReLU(emebd_game)) # bs, card_emb_dim
        embed_attackers = self.card_embedding(attackers) # bs, max_c, card_emb_dim
        embed_blockers = self.card_embedding(blockers) # bs, max_c, max_c, card_emb_dim
        # (emb(a_i), emb(b_i,j))
        pre_attention2blocker = (embed_attackers.unsqueeze(2) * embed_blockers).sum(dim=-1, keepdim=True) # bs, max_c, max_c, 1
        attention2blocker = F.sigmoid(pre_attention2blocker)
        embed_battle = (attention2blocker * embed_blockers).sum(dim=2) # bs, max_c, card_emb_dim
        
        pre_attention2battle = (fix_emebed_game.unsqueeze(1) * embed_battle).sum(dim=-1, keepdim=True) # bs, max_c, 1
        attention2battle = F.sigmoid(pre_attention2battle) 
        vector = (embed_battle * attention2battle).sum(dim=1) # bs, card_emb_dim
        return self.nn(vector)