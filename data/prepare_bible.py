#!/usr/bin/env python3

from subprocess import run
from threading import Thread
import os
import shutil

import osis_tran

SCRIPTS = 'mosesdecoder/scripts'
TOKENIZER = SCRIPTS + '/tokenizer/tokenizer.perl'
CLEAN = SCRIPTS + '/training/clean-corpus-n.perl'
BPEROOT = 'subword-nmt'

BPE_TOKENS = 30000
CLEAN_RATIO = 1.5

PREP = 'bible.prep'
TMP = PREP + '/tmp'
BPE_CODE = PREP + '/code'

# starts with * --> unidecode
MODULES = [
    '*2TGreek', 'Afr1953', 'Alb', 'BasHautin', '*Bela', 'BretonNT', '*BulVeren',
    '*CSlElizabeth', 'Chamorro', '*ChiNCVs', 'Cro', 'CzeCEP', 'DaOT1931NT1907',
    '*Dari', 'DutSVV', 'ESV2011', 'Esperanto', 'Est', '*FarTPV', 'FrePGR',
    'FinPR', 'GerNeUe', '*GreVamvas', 'Haitian', '*HebModern', '*HinERV',
    'HunUj', 'ItaRive', 'Kekchi', '*KorHKJV', 'LtKBB', 'LvGluck8', 'ManxGaelic',
    'Maori', 'Mg1865', 'Norsk', 'NorthernAzeri', '*Peshitta', 'PolUGdanska',
    'PorAlmeida1911', 'PotLykins', 'RomCor', '*RusSynodal', 'ScotsGaelic',
    'SloStritar', 'SomKQA', 'SpaRV', 'Swahili', 'SweFolk1998', 'TagAngBiblia',
    'TurHADI', '*Ukrainian', 'Vulgate'
]

TRAIN_STARTS = {
    'ESV2011': 'Matt.',
    'FinPR': 'Exod.',
    'GerNeUe': 'Exod.'
}

SRC_TOKEN_EXTRA_WEIGHT = 2
TARGET_EXTRA_PASSES = 2
TARGETS = list(TRAIN_STARTS)

SRC='2TGreek'

GLOSSARIES = ['TGT_' + m.lstrip('*') for m in MODULES]

def apply_bpe(fname):
    with open(TMP + '/' + fname) as inf:
        with open(PREP + '/' + fname, 'w') as outf:
            CMD = (['python', BPEROOT+'/apply_bpe.py', '--glossaries'] + GLOSSARIES +
                   ['-c', BPE_CODE])
            run(CMD, stdin=inf, stdout=outf, check=True)


def main():
    modnames = [x.lstrip('*') for x in MODULES]
    assert SRC in modnames
    assert not (set(TRAIN_STARTS) - set(modnames)), (set(TRAIN_STARTS) - set(modnames))
    assert not (set(TARGETS) - set(modnames)), (set(TARGETS) - set(modnames))

    shutil.rmtree(PREP, ignore_errors=True)
    os.mkdir(PREP)
    os.mkdir(TMP)

    # if not os.path.exists('mosesdecoder'):
    #     run('git clone https://github.com/moses-smt/mosesdecoder.git', shell=True)
    # if not os.path.exists('subword-nmt'):
    #     run('git clone https://github.com/rsennrich/subword-nmt.git', shell=True)

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

    src_data = []
    tgt_data = []
    for tgt_mod in train_mods:
        passes = 1
        if tgt_mod in TARGETS:
            passes += TARGET_EXTRA_PASSES
        for i in range(passes):
            for src_line, tgt_line in osis_tran.gen_trans(src_mod, train_mods[tgt_mod]):
                src_data.append('TGT_' + tgt_mod + ' ' + src_line)
                tgt_data.append(tgt_line)

    val_src_data = []
    val_tgt_data = []
    for tgt_mod in val_mods:
        for src_line, tgt_line in osis_tran.gen_trans(src_mod, val_mods[tgt_mod]):
            val_src_data.append('TGT_' + tgt_mod + ' ' + src_line)
            val_tgt_data.append(tgt_line)

    print('Preprocessing train data...')
    with open(TMP + '/protect', 'w') as f:
        print('TGT_[a-zA-Z0-9]+', file=f)

    for data, fname in [(src_data, 'tok.src'), (tgt_data, 'tok.tgt'),
                        (val_src_data, 'val.src'), (val_tgt_data, 'val.tgt')]:
        CMD = ['perl', TOKENIZER, '-threads', '8', '-protected',
               TMP+'/protect', '-l', 'nosuchlanguage']
        with open(TMP + '/' + fname, 'w') as f:
            run(CMD, input='\n'.join(data), stdout=f, check=True, encoding='utf-8')

    for s, d in [('tok', 'train'), ('val', 'valid')]:
        CMD = ['perl', CLEAN, '-ratio', str(CLEAN_RATIO), TMP+'/'+s, 'src', 'tgt',
               TMP + '/' + d, '1', '175']
        run(CMD, check=True)

    # for BPE, learn source language only once
    with open(TMP + '/src-once', 'w') as f:
        for i in range(1+SRC_TOKEN_EXTRA_WEIGHT):
            print('\n'.join(src_mod.values()), file=f)

    run('cat {tmp}/src-once {tmp}/train.tgt >{tmp}/train.both'.format(tmp=TMP),
        shell=True, check=True)

    print('Learning BPE...')
    with open(TMP + '/train.both') as inf:
        with open(BPE_CODE, 'w') as outf:
            run(['python', BPEROOT + '/' + 'learn_bpe.py', '-s', str(BPE_TOKENS)],
                stdin=inf, stdout=outf, check=True)

    threads = []
    for l in ('src', 'tgt'):
        for s in ('train', 'valid'):
            fname = s + '.' + l
            print('apply_bpe.py to ' + fname + '...')
            th = Thread(target=apply_bpe, args=[fname])
            th.start()
            threads.append(th)

    for t in threads:
        t.join()

    # FIXME proper test set
    shutil.copy(PREP + '/valid.src', PREP + '/test.src')
    shutil.copy(PREP + '/valid.tgt', PREP + '/test.tgt')


if __name__ == '__main__':
    main()
