#!/usr/bin/env python3

from split_pred import postprocess
import sys

for line in sys.stdin:
    line = postprocess(line.strip())
    print(line)
