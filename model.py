import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class FCGameEncoder(nn.Module):
    def __init__(self, out_d, 
        card_embedding=None, card_num=None, card_emb_dim=12, card_pad_idx=0,
        phase_embedding=None, phase_emb_dim=4, phase, pad_idx=0
        dense_feat_dim=5, 
        phase_len=3, n_layer=2, nch=24):
        super(FCGameEncoder, self).__init__()

        if card_embedding is None:
            self.card_embedding = nn.Embedding(card_num + 2, card_emb_dim) # Null card + padding idx
        else:
            self.card_embedding = card_embedding

        if phase_embedding is None:
            self.phase_embedding = nn.Embedding(8 + 1, phase_emb_dim)
        else:
            self.phase_embedding = card_embedding

        # phase emb
        # playing idx
        # fix _fix_state

        layers = []
        first_input_dim = (dense_feat_dim * 2 
            # creatures*(tap, untap, summon sick)
            + (card_emb_dim * 2)*3 
            # gy, hand
            + (card_emb_dim) * 3 
            # phase, playing_idx
            + 2 ) * phase_len


        for i in range(n_layer):
            tmp_in = tmp_out = nch
            if i == 0:
                tmp_in = first_input_dim
            if i == n_layer-1:
                tmp_out = out_d

            layers.append(nn.Linear(tmp_in, tmp_out))

            if i < n_layer - 1:
                layers.append(nn.ReLU())
        
        self.nn = nn.Sequential(*layers)    

    def forward(self, feat_dict):
        p_feat = feat_dict['player'] # bs, phase_len, dence_dim
        o_feat = feat_dict['opponent']
        dence = torch.cat([p_feat, o_feat], dim=1) # bs, 2*phase_len, dence_dim

        embed_p_bf_c = self.card_embedding(
            p_feat['creatures']) # bs, phase_len, max_c

    
        
