import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class FCGameEncoder(nn.Module):
    def __init__(self, out_d, 
        card_embedding=None, card_num=None, emb_dim=12,
        dense_feat_dim=5, phase_len=3, n_layer=2, nch=24):
        super(FCGameEncoder, self).__init__()

        if card_embedding is None:
            self.card_embedding = nn.Embedding(card_num + 2, emb_dim) # Null card + padding idx
        else:
            self.card_embedding = card_embedding

        layers = []
        first_input_dim = dense_feat_dim * phase_len * 2 + emb_dim * 5
        for i in range(n_layer):
            tmp_in = tmp_out = nch
            if i == 0:
                tmp_in = first_input_dim
            if i == n_layer-1:
                tmp_out = out_d

            layers.append(nn.linear(tmp_in, tmp_out))

            if i < n_layer - 1:
                layers.append(nn.ReLU())
        
        self.nn = nn.Sequential(*layers)    

    def forward(self, feat_dict):
        pass

    
        
