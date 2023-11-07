#!/usr/bin/env python3

# dumps the texts in a module that also exist in 2TGreek

REF = '2TGreek'

import osis_tran
import sys

def main():
    module = sys.argv[1]
    src = osis_tran.load_osis_module(module)
    ref = osis_tran.load_osis_module(REF)

    for k in ref:
        if k in src:
            print(src[k])
        else:
            print()


if __name__ == '__main__':
    main()
