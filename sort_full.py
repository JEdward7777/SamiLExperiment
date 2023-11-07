#!/usr/bin/env python3

import sys

sys.path.append('data')
import osis_tran
from split_full import postprocess

SRC_MOD = '2TGreek'

mod = osis_tran.load_osis_module(SRC_MOD)
keys = list(mod.keys())
key_len = max(len(x) for x in keys)

lines = [x.strip().split('\t', 1) for x in sys.stdin.readlines()]
lines = [(int(x[0]), x[1].strip()) for x in lines]
lines.sort()

for lineno, text in lines:
    k = keys[lineno]
    k += ' '*(key_len-len(k))
    print('{} {}'.format(k, postprocess(text)))

