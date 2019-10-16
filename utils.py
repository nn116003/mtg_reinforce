import numpy as np
import torch
import torch.nn.functional as F

def card2idxlist(cards, cardid2idx, 
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

def pad(indexes, pad_idx, max_len):
    return indexes + [pad_idx] * (max_len - len(indexes))

def _pad_bf_creatures(
        creatures_data, # phase_len, *, 3
        pad_idx, 
        max_len):
    pad_c = []
    pad_tap_flg = []
    pad_sick_flg = []
    for ss in creatures_data:
        ss_arr = np.array(ss).astype(int) # *, 3
        pad_c.append(pad(ss_arr[:,0], pad_idx, max_len))
        pad_tap_flg.append(pad(ss_arr[:,1], 0, max_len))
        pad_sick_flg.append(pad(ss_arr[:,2], 0, max_len))

    # (phase_len, max_len ) *3
    return torch.LongTensor(pad_c), torch.Tensor(pad_tap_flg), torch.Tensor(pad_sick_flg)

def _fix_player_feat(feat, pad_idx, max_c, max_g, max_h):
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
    p_c, p_tf, p_sf = _pad_bf_creatures(feat['creatures'], pad_idx, max_c) 
    res["creatures"] = p_c.unsqueeze(0)
    res["tap_flg"] = p_tf.unsqueeze(0)
    res["sick_flg"] = p_sf.unsqueeze(0)

    # 1, phase_len, max_g
    res["gy"] = torch.LongTensor(pad(feat['gy'], pad_idx, max_g)).unsqueeze(0)
    if "hand" in feat:
        # 1, phase_len, max_h
        res["hand"] = torch.LongTensor(pad(feat['hand'], pad_idx, max_h)).unsqueeze(0)

    return res

def fix_state(state, pad_idx, max_c, max_g, max_h):
    res = {}
    res["player"] = _fix_player_feat(state["player"], pad_idx, max_c, max_g, max_h)
    res["opponent"] = _fix_player_feat(state["player"], pad_idx, max_c, max_g, max_h)
    res["phase"] = torch.LongTensor(state["phase"]).unsqueeze(0)
    res["playing_idx"] = torch.Tensor(state["playing_idx"]).unsqueeze(0)

    return res

def cast_action2tensor(cardidx):
    return torch.LongTensor([cardidx])

def attack_action2tensor(action, pad_idx, max_c):
    return torch.LongTensor(pad(action, pad_idx, max_c))

def block_action2tensor(action, pad_idx, max_c):
    attackers = torch.LongTensor(
        utils.pad(action["attackers"], pad_idx, max_c) # max_c
        )
    blockers = torch.LongTensor(
        list(map(lambda x:pad(x, pad_idx, max_c), action["blockers"])) # max_c, max_c
        )
    return (attackers, blockers)


# potentialy, we dont have to use this fcn.
# we shuold use tmp_id instaed of id
def cardids2cards(cardids, card_list):
    id_order_dict = {}
    for i, card in enumerate(card_list):
        if card.id in id_order_dict:
            id_order_dict[card.id].append(i)
        else:
            id_order_dict[card.id] = []

    res = []
    for cardid in cardids:
        res.append( card_list[id_order_dict[cardid][0]] )
        del id_order_dict[cardid][0]

    return res
        