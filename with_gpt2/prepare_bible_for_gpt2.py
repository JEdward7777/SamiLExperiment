#!/usr/bin/env python3

from subprocess import run
from threading import Thread
import os
import shutil
import sys

#Add ../data to python path.
sys.path.append('../data')

import osis_tran

SCRIPTS = '../data/mosesdecoder/scripts'
TOKENIZER = SCRIPTS + '../data/tokenizer/tokenizer.perl'
CLEAN = SCRIPTS + '../data/training/clean-corpus-n.perl'
BPEROOT = 'subword-nmt'

BPE_TOKENS = 30000
CLEAN_RATIO = 1.5

PREP = 'bible.prep'
BPE_CODE = PREP + '/code'

# starts with * --> unidecode
# MODULES = [
#     '*2TGreek', 'Afr1953', 'Alb', 'BasHautin', '*Bela', 'BretonNT', '*BulVeren',
#     '*CSlElizabeth', 'Chamorro', '*ChiNCVs', 'Cro', 'CzeCEP', 'DaOT1931NT1907',
#     '*Dari', 'DutSVV', 'ESV2011', 'Esperanto', 'Est', '*FarTPV', 'FrePGR',
#     'FinPR', 'GerNeUe', '*GreVamvas', 'Haitian', '*HebModern', '*HinERV',
#     'HunUj', 'ItaRive', 'Kekchi', '*KorHKJV', 'LtKBB', 'LvGluck8', 'ManxGaelic',
#     'Maori', 'Mg1865', 'Norsk', 'NorthernAzeri', '*Peshitta', 'PolUGdanska',
#     'PorAlmeida1911', 'PotLykins', 'RomCor', '*RusSynodal', 'ScotsGaelic',
#     'SloStritar', 'SomKQA', 'SpaRV', 'Swahili', 'SweFolk1998', 'TagAngBiblia',
#     'TurHADI', '*Ukrainian', 'Vulgate'
# ]

MODULES = [
    'NETfree',

    '*2TGreek', 'Afr1953', 'Alb', 'BasHautin', '*Bela', 'BretonNT', '*BulVeren',
    'CzeCEP',
    'DutSVV', 'Esperanto', 'FrePGR',
    'FinPR', 'GerNeUe', '*GreVamvas', 'Haitian', '*HebModern', '*HinERV',
    'HunUj', 'ItaRive', 'Kekchi', '*KorHKJV', 'ManxGaelic',
    'Maori', 'PolUGdanska',
    'PorAlmeida1911', 'PotLykins', 'RomCor', '*RusSynodal', 
    'SloStritar', 'SomKQA', 'SpaRV', 'Swahili', 'SweFolk1998', 'TagAngBiblia',
    'TurHADI', '*Ukrainian', 'Vulgate'
]

TRAIN_STARTS = {
    'NETfree': 'Matt',
    #'ESV2011': 'Matt',
    'FinPR': 'Exod',
    'GerNeUe': 'Exod'
}

SRC_TOKEN_EXTRA_WEIGHT = 2
TARGET_EXTRA_PASSES = 2
TARGETS = list(TRAIN_STARTS)

SRC='2TGreek'

GLOSSARIES = ['TGT_' + m.lstrip('*') for m in MODULES] + ['TGT_TEMPLATE']


def main():
    modnames = [x.lstrip('*') for x in MODULES]
    assert SRC in modnames
    assert not (set(TRAIN_STARTS) - set(modnames)), (set(TRAIN_STARTS) - set(modnames))
    assert not (set(TARGETS) - set(modnames)), (set(TARGETS) - set(modnames))

    shutil.rmtree(PREP, ignore_errors=True)
    os.mkdir(PREP)

    if not os.path.exists('../data/mosesdecoder'):
        print('ERROR: Directory "mosesdecoder" does not exist.', file=sys.stderr)
        print('Did you git clone without --recurse-submodules?', file=sys.stderr)
        sys.exit(1)

    train_mods = {}
    val_mods = {}
    print('Loading modules...')
    for m in MODULES:
        print(m, end=' ', flush=True)
        decode = False
        if m[0] == '*':
            decode = True
            m = m[1:]
        train_mod = osis_tran.load_osis_module(m, toascii=decode)
        if m in TRAIN_STARTS:
            val_mod, train_mod = osis_tran.split_at_key(TRAIN_STARTS[m], train_mod)
            val_mods[m] = val_mod
        train_mods[m] = train_mod
    print()

    src_mod = train_mods[SRC]
    del train_mods[SRC]


    train_data = []

    for tgt_mod in train_mods:
        passes = 1
        if tgt_mod in TARGETS:
            passes += TARGET_EXTRA_PASSES
        for i in range(passes):
            for src_line, tgt_line in osis_tran.gen_trans(src_mod, train_mods[tgt_mod]):
                combined_line = f"{src_line} TGT_{tgt_mod} {tgt_line}"
                train_data.append(combined_line)

    val_data = []
    for tgt_mod in val_mods:
        for src_line, tgt_line in osis_tran.gen_trans(src_mod, val_mods[tgt_mod]):
            val_data.append(f"{src_line} TGT_{tgt_mod} {tgt_line}")

    
    with open( PREP + '/train.txt', 'w') as f:
        for line in train_data:
            print(line, file=f)

    with open( PREP + '/valid.txt', 'w') as f:
        for line in val_data:
            print(line, file=f)


if __name__ == '__main__':
    main()
