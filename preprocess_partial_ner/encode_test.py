import pickle
import argparse
import os
import random
import numpy as np
from tqdm import tqdm
import torch
import itertools
import functools

def read_corpus(lines):
    line_idx, features = list(), list()

    tmp_li, tmp_fl = list(), list()

    for line_num in range(0, len(lines)):
        line = lines[line_num]
        if not (line.isspace() or (len(line) > 10 and line[0:10] == '-DOCSTART-')):
            line = line.split()
            tmp_li.append(line_num)
            tmp_fl.append(line[0])
        elif len(tmp_fl) > 0:
            line_idx.append(tmp_li)
            features.append(tmp_fl)
            tmp_li, tmp_fl = list(), list()

    if len(tmp_fl) > 0:
        features.append(tmp_fl)
        line_idx.append(tmp_li)

    return line_idx, features

def encode_dataset(input_file, w_map, c_map):

    with open(input_file, 'r') as f:
        lines = f.readlines()

    line_idx, features = read_corpus(lines)

    w_st, w_unk, w_con, w_pad = w_map['<s>'], w_map['<unk>'], w_map['< >'], w_map['<\n>']
    c_st, c_unk, c_con, c_pad = c_map['<s>'], c_map['<unk>'], c_map['< >'], c_map['<\n>']

    dataset = list()

    for f_idx, f_l in zip(line_idx, features):
        tmp_w = [w_st, w_con]
        tmp_c = [c_st, c_con]
        tmp_mc = [0, 1]

        for i_f in f_l[1:-1]:
            tmp_w = tmp_w + [w_map.get(i_f.lower(), w_unk)] * len(i_f) + [w_con]
            tmp_c = tmp_c + [c_map.get(t, c_unk) for t in i_f] + [c_con]
            tmp_mc = tmp_mc + [0] * len(i_f) + [1]

        tmp_w.append(w_pad)
        tmp_c.append(c_pad)
        tmp_mc.append(0)

        tmp_idx = f_idx[1:]

        dataset.append([tmp_w, tmp_c, tmp_mc, tmp_idx])

    return dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data', default="./data/ner/eng.total.ck")
    parser.add_argument('--check_point', default="./checkpoint/ner_basic.model")
    parser.add_argument('--output_file', default="./data/target.pk")
    args = parser.parse_args()

    with open(args.check_point, 'rb') as f:
        pd = torch.load(f)
        w_map = pd['w_map']
        c_map = pd['c_map']

    target_dataset = encode_dataset(args.input_data, w_map, c_map)
    
    with open(args.output_file, 'wb') as f:
        pickle.dump(target_dataset, f)