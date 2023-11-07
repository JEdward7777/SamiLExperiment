#!/usr/bin/env python3

import sys
import re

sys.path.append('data')
import osis_tran

SRC_MOD = '2TGreek'

# inclusive
RANGES = {
    'en': (0, 22874),
    'fi': (22875, 24405),
    'de': (24406, 25935)
}

RM_SPACE = re.compile(r" ([?.,!;':])")
APOS = re.compile(r' &apos; ')
QUOT = re.compile(r'&quot;')

def postprocess(s):
    s = APOS.sub("'", s)
    s = RM_SPACE.sub(r'\1', s)
    s = QUOT.sub('"', s)  # don't know which side to put it on...
    return s

def main():
    fname = sys.argv[1]

    mod = osis_tran.load_osis_module(SRC_MOD)
    keys = list(mod.keys())
    key_len = max(len(x) for x in keys)

    with open(fname) as inf:
        lines = inf.read().splitlines()

    lines = [x.split('\t') for x in lines]
    lines = [(int(num), txt) for num, txt in lines]
    lines.sort()

    fps = {}
    for lang in RANGES:
        fps[lang] = open(fname + '.' + lang, 'w')

    for lineno, text in lines:
        for lang, (start, end) in RANGES.items():
            if lineno >= start and lineno <= end:
                k = keys[lineno-start]
                k += ' '*(key_len-len(k))
                print('{} {}'.format(k, postprocess(text)), file=fps[lang])

    for lang in RANGES:
        fps[lang].close()


if __name__ == '__main__':
    main()
