#!/usr/bin/env python3

import sys
import re
from unidecode import unidecode
from collections import OrderedDict

import subprocess

RM_CHARS = '¶'
REPL_CHARS = {
    '»': '"',
    '«': '"',
    '„': '"',
    '“': '"',
    '”': '"',
    '’': "'",
    '–': "-",
}

RE = re.compile(r'<verse osisID="([^"]+)">(.*)</verse>')
TAG_RE = re.compile(r'<[^<>]+>')
SPACE_RE = re.compile(r' +')

# def load_osis_str(inp, toascii=False):
#     inp = inp.split('\n')
#     dic = OrderedDict()
#     for i, line in enumerate(inp):
#         line = line.strip()
#         if not line or line.startswith('$'):
#             continue
#         r = RE.match(line)
#         #assert r, line
#         if not r:
#             continue
#         key = r.group(1)
#         v = r.group(2).strip()
#         for c in RM_CHARS:
#             v = v.replace(c, '')
#         for r, t in REPL_CHARS.items():
#             v = v.replace(r, t)

#         v = TAG_RE.sub(' ', v.strip())
#         v = SPACE_RE.sub(' ', v)
#         v = v.lower()
#         if toascii:
#             v = unidecode(v)
#         dic[key] = v
#     return dic

def load_osis_str( inp, toascii=False, lower=True ):
    key = "root"
    dic = OrderedDict()
    for line in inp.split('\n'):
        line = line.strip()

        if line.startswith( "$$$" ):
            key = line[3:].strip()
        else:
            v = line
            for c in RM_CHARS:
                v = v.replace( c, '' )
            for r, t in REPL_CHARS.items():
                v = v.replace( r, t )
            v = TAG_RE.sub( ' ', v.strip() )
            v = SPACE_RE.sub( ' ', v )
            if lower: 
                v = v.lower()
            if toascii:
                v = unidecode( v )
            v = v.strip()
            if v:
                dic[key] = v
    return dic

            




def load_osis_file(fname, **kwargs):
    with open(fname) as f:
        data = f.read()
    return load_osis_str(data, **kwargs)


def load_osis_module(modname, **kwargs):
    r = subprocess.run(['mod2imp', modname, '-r', 'OSIS'], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       encoding='utf-8')
    return load_osis_str(r.stdout, **kwargs)


def normalize_reference( ref ):

    return ref

def gen_trans(src, tgt, include_key=False, module_name=None):
    missing_keys = []

    for target_key in tgt:
        key = normalize_reference(target_key)
        if key in src:
            if include_key:
                yield key, src[key], tgt[key]
            else:
                yield src[key], tgt[key]
        else:
            whitelist_book_names = [
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', 'I Samuel', 
            'II Samuel', 'I Kings', 'II Kings', 'I Chronicles', 'II Chronicles', 'Ezra', 'Nehemiah', 
            'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 
            'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel','Amos', 'Obadiah', 'Jonah','Micah', 
            'Nahum',  'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 
            
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', 'I Corinthians', 'II Corinthians','Galatians',
            'Ephesians', 'Philippians', 'Colossians', 'I Thessalonians', 'II Thessalonians', 'I Timothy', 'II Timothy', 
            'Titus', 'Philemon', 'Hebrews', 'James', 'I Peter', 'II Peter', 'I John', 'II John', 'III John', 'Jude', 'Revelation of John']

         
            blacklist_book_names = [ 'Tobit', 'Judith', 'Esther (Greek)', 'Wisdom', 'Sirach', 'Baruch', 'Prayer of Azariah', 
                                    'Susanna', 'Bel and the Dragon', 'I Maccabees', 'II Maccabees', 'Prayer of Manasses',
                                    'I Esdras', 'Epistle of Jeremiah', 'III Maccabees', 'II Esdras',
                                    'Additional Psalm', 'Laodiceans']

            bookname_match = re.match( r'(^[0-9]*\s*[^0-9]+)', key )
            if bookname_match:
                bookname = bookname_match.group(1).strip()
                if bookname in whitelist_book_names:
                    print( "whitelist book: " + str(key) + " module: " + str(module_name) )
                elif bookname in blacklist_book_names:
                    print( "blacklist book: " + str(key) + " module: " + str(module_name) )
                else:
                    print( "missing from target: " + str(key) + " module: " + str(module_name) )
                    if bookname not in missing_keys:
                        missing_keys.append( bookname )


    if missing_keys: 
        print( "The missing books are in the source: " + repr(missing_keys) )


def split_at_key(split_key, od):
    lo = OrderedDict()
    hi = OrderedDict()
    tgt = lo
    for key, v in od.items():
        if key.startswith(split_key):
            tgt = hi
        tgt[key] = v
    return lo, hi


def main():
    TAG = sys.argv[1].upper()
    SRC_OSIS = sys.argv[2]
    TGT_OSIS = sys.argv[3]
    OUT_SRC = sys.argv[4]
    OUT_TGT = sys.argv[5]

    src = load_osis_file(SRC_OSIS, toascii=True)
    tgt = load_osis_file(TGT_OSIS)

    with open(OUT_SRC, 'w') as out_src:
        with open(OUT_TGT, 'w') as out_tgt:
            for srcv, tgtv in gen_trans(src, tgt):
                print('TGT_'+TAG + ' ' + srcv, file=out_src)
                print(tgtv, file=out_tgt)


if __name__ == '__main__':
    main()
