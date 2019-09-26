import numpy as np
import torch
import torch.nn.functional as F

def card2idlist(cards, cardid2idx, 
                battlefield=False, add_none=False, empty2none=True):
    result = []
    if battlefield:
        if len(cards) == 0:
            result.append([cardid2idx["None"], 0, 0])
        else:
            for card in cards:
                tmp = [cardid2idx[card.id], 1-int(card.is_tapped()), 1-int(card.summon_sick)]
                result.append(tmp)
    else:
        if len(cards) == 0: 
            if empty2none:
                result.append(cardid2idx["None"])
        else:
            [result.append(cardid2idx[card.id]) for card in cards]
            if add_none:
                result.append(cardid2idx["None"])

    return result 

def pad(indexes, pad_id, max_len):
    return indexes + [pad_id] * (max_len - len(indexes))

def _pad_bf_creatures(
        creatures_data, # phase_len, *, 3
        pad_id, 
        max_len):
    pad_c = []
    pad_tap_flg = []
    pad_sick_flg = []
    for ss in creatures_data:
        ss_arr = np.array(ss).astype(int) # *, 3
        pad_c.append(pad(ss_arr[:,0], pad_id, max_len))
        pad_tap_flg.append(pad(ss_arr[:,1], 0, max_len))
        pad_sick_flg.append(pad(ss_arr[:,2], 0, max_len))

    # (phase_len, max_len ) *3
    return torch.LongTensor(pad_c), torch.Tensor(pad_tap_flg), torch.Tensor(pad_sick_flg)

def _fix_player_feat(feat, pad_id, max_c, max_g, max_h):
    res = {}

    # 1, phase_len, 5
    res["dense"] = torch.cat(
        [
            torch.Tensor(feat['lands']), # phase_len, 2
            torch.Tensor(feat['n_hand']).view(-1,1),
            torch.Tensor(feat['life']).view(-1,1),
            torch.Tensor(feat['n_lib']).view(-1,1),
        ],
        dim = 1
    ).unsqueeze(0)

    # (1, phase_len, max_len ) *3
    p_c, p_tf, p_sf = _pad_bf_creatures(feat['creatures'], pad_id, max_c) 
    res["creatures"] = p_c.unsqueeze(0)
    res["tap_flg"] = p_tf.unsqueeze(0)
    res["sick_flg"] = p_sf.unsqueeze(0)

    # 1, phase_len, max_g
    res["gy"] = torch.LongTensor(pad(feat['gy'], pad_id, max_g)).unsqueeze(0)
    if "hand" in feat:
        # 1, phase_len, max_h
        res["hand"] = torch.LongTensor(pad(feat['hand'], pad_id, max_h)).unsqueeze(0)

    return res

def fix_state(state, pad_id, max_c, max_g, max_h):
    res = {}
    res["player"] = _fix_player_feat(state["player"], pad_id, max_c, max_g, max_h)
    res["opponent"] = _fix_player_feat(state["player"], pad_id, max_c, max_g, max_h)
    res["phase"] = torch.LongTensor(state["phase"]).unsqueeze(0)
    res["playing_idx"] = torch.Tensor(state["playing_idx"]).unsqueeze(0)

    return res

