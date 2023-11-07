#!/usr/bin/env python3

import sys
import re

# inclusive
RANGES = {
    'en': (0, 18115),
    'fi': (18116, 19548),
    'de': (19549, 20826)
}

RM_SPACE = re.compile(r" ([?.,!;':])")
APOS = re.compile(r' &apos; ')
QUOT = re.compile(r'&quot;')

def postprocess(s):
    s = APOS.sub("'", s)
    s = RM_SPACE.sub(r'\1', s)
    s = QUOT.sub('"', s)  # don't know which side to put it on...
    return s

def parse_line(s):
    s = s.split('\t', 2)
    assert len(s) == 3, s
    num = int(s[0])
    txt = s[2]
    return (num, txt)

def main():
    fname = sys.argv[1]

    with open(fname) as inf:
        lines = inf.read().splitlines()

    lines = [x[2:] for x in lines if x.startswith('H-')]
    lines = [parse_line(x) for x in lines]
    lines.sort()

    fps = {}
    for lang in RANGES:
        fps[lang] = open(fname + '.' + lang, 'w')

    for lineno, text in lines:
        for lang, (start, end) in RANGES.items():
            if lineno >= start and lineno <= end:
                print(postprocess(text), file=fps[lang])

    for lang in RANGES:
        fps[lang].close()


if __name__ == '__main__':
    main()
