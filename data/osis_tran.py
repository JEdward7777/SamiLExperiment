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
    '’': "'"
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

def load_osis_str( inp, toascii=False ):
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
            known_strange_verses = [
                'Genesis 31:51', 'Genesis 35:21',
                'Exodus 25:6', 'Exodus 28:24', 'Exodus 28:25', 'Exodus 28:26', 'Exodus 28:27',
                'Exodus 28:28', 'Exodus 32:9', 'Exodus 35:8','Exodus 35:15', 'Exodus 35:18',
                'Exodus 36:10','Exodus 36:11','Exodus 36:12','Exodus 36:13','Exodus 36:14',
                'Exodus 36:15','Exodus 36:16','Exodus 36:17','Exodus 36:18','Exodus 36:19',
                'Exodus 36:20','Exodus 36:21','Exodus 36:22','Exodus 36:23','Exodus 36:24',
                'Exodus 36:25','Exodus 36:26','Exodus 36:27','Exodus 36:28','Exodus 36:29',
                'Exodus 36:30','Exodus 36:31','Exodus 36:32','Exodus 36:33',
                'Exodus 37:4','Exodus 37:11', 'Exodus 37:12', 'Exodus 37:14', 'Exodus 37:20',
                'Exodus 37:22','Exodus 37:24','Exodus 37:25', 'Exodus 37:26', 'Exodus 37:27',
                'Exodus 37:28','Exodus 38:2','Exodus 38:5','Exodus 38:6', 'Exodus 38:7',
                'Exodus 39:35','Exodus 39:39','Exodus 40:7','Exodus 40:11','Exodus 40:28',
                'Exodus 40:31', 'Exodus 40:32',
                'Numbers 6:27','Numbers 10:34',
                'Deuteronomy 23:24',

                'Joshua 8:13','Joshua 8:26','Joshua 10:15','Joshua 10:43','Joshua 13:33','Joshua 20:4'
                'Joshua 20:5','Joshua 20:6','Joshua 6:4', 'Joshua 20:4', 'Joshua 20:5', 
                'I Samuel 17:12', 'I Samuel 17:13', 'I Samuel 17:14', 'I Samuel 17:15',
                'I Samuel 17:16', 'I Samuel 17:17', 'I Samuel 17:18', 'I Samuel 17:19',
                'I Samuel 17:20', 'I Samuel 17:21', 'I Samuel 17:22', 'I Samuel 17:23',
                'I Samuel 17:24', 'I Samuel 17:25', 'I Samuel 17:26', 'I Samuel 17:27',
                'I Samuel 17:28', 'I Samuel 17:29', 'I Samuel 17:30', 'I Samuel 17:31',
                'I Samuel 17:41','I Samuel 17:50','I Samuel 17:55','I Samuel 17:56',
                'I Samuel 17:57', 'I Samuel 17:58', 'I Samuel 18:1', 'I Samuel 18:2',
                'I Samuel 18:3', 'I Samuel 18:4', 'I Samuel 18:5', 'I Samuel 18:10',
                'I Samuel 18:11', 'I Samuel 18:17', 'I Samuel 18:18', 'I Samuel 18:19'
                'I Samuel 18:30', 'I Samuel 23:12','I Samuel 18:19', 'I Samuel 18:30', 
                'I Kings 4:20','I Kings 4:25','I Kings 4:26','I Kings 4:28','I Kings 5:17',
                'I Kings 6:11', 'I Kings 6:12', 'I Kings 6:13', 'I Kings 6:14',
                'I Kings 6:37','I Kings 6:38', 'I Kings 7:22', 'I Kings 7:31',
                'I Kings 8:12', 'I Kings 8:13', 'I Kings 9:16', 'I Kings 9:17', 'I Kings 9:18'
                'I Kings 9:19','I Kings 9:21', 'I Kings 9:23', 'I Kings 9:25', 'I Kings 11:3',
                'I Kings 11:23', 'I Kings 11:24', 'I Kings 4:21', 'I Kings 6:18', 'I Kings 9:18', 
                'I Kings 9:19', 'I Kings 11:24', 'I Kings 11:39', 'I Kings 12:2', 'I Kings 12:17', 
                'I Kings 13:27', 'I Kings 15:6', 'I Kings 15:32', 'I Kings 22:46', 'I Kings 22:47', 
                'I Kings 22:48', 'I Kings 22:49',
                 
                'I Chronicles 1:11', 'I Chronicles 1:12', 'I Chronicles 1:13', 'I Chronicles 1:14',
                'I Chronicles 1:15', 'I Chronicles 1:16', 'I Chronicles 1:18', 'I Chronicles 1:19', 
                'I Chronicles 1:20', 'I Chronicles 1:21', 'I Chronicles 1:22', 'I Chronicles 1:23', 
                'I Chronicles 16:24', 'II Chronicles 27:8',
                 
                'Nehemiah 3:7', 'Nehemiah 4:6', 'Nehemiah 11:16', 'Nehemiah 11:20', 
                'Nehemiah 11:21', 'Nehemiah 11:28', 'Nehemiah 11:29', 'Nehemiah 11:32', 
                'Nehemiah 11:33', 'Nehemiah 11:34', 'Nehemiah 11:35', 'Nehemiah 12:4', 
                'Nehemiah 12:5', 'Nehemiah 12:6', 
                
                'Esther 4:6', 'Esther 9:5', 'Esther 9:30', 
                
                'Job 23:14', 
                
                'Psalms 116:14', 
                
                'Proverbs 4:7', 'Proverbs 8:33', 'Proverbs 11:4', 'Proverbs 15:31', 'Proverbs 16:3', 
                'Proverbs 16:4', 'Proverbs 16:6', 'Proverbs 18:23', 'Proverbs 18:24', 
                'Proverbs 19:1', 'Proverbs 19:2', 'Proverbs 20:14', 'Proverbs 20:15',
                'Proverbs 20:16', 'Proverbs 20:17', 'Proverbs 20:18', 'Proverbs 20:19',
                'Proverbs 21:5', 'Proverbs 22:6', 'Proverbs 23:23', 
                    
                'Isaiah 2:22', 'Isaiah 56:12', 
                
                'Jeremiah 7:28', 'Jeremiah 8:11', 'Jeremiah 8:12', 'Jeremiah 10:6',
                'Jeremiah 10:7', 'Jeremiah 10:8', 'Jeremiah 10:10', 'Jeremiah 11:7', 
                'Jeremiah 25:14', 'Jeremiah 27:7', 'Jeremiah 27:13', 'Jeremiah 27:17', 
                'Jeremiah 27:21', 'Jeremiah 29:16', 'Jeremiah 29:17', 'Jeremiah 29:18',
                'Jeremiah 29:19', 'Jeremiah 29:20', 'Jeremiah 30:10', 'Jeremiah 30:11', 
                'Jeremiah 30:15', 'Jeremiah 30:22', 'Jeremiah 33:14', 'Jeremiah 33:15', 
                'Jeremiah 33:16', 'Jeremiah 33:17', 'Jeremiah 33:18', 'Jeremiah 33:19', 
                'Jeremiah 33:20', 'Jeremiah 33:21', 'Jeremiah 33:22', 'Jeremiah 33:23', 
                'Jeremiah 33:24', 'Jeremiah 33:25', 'Jeremiah 33:26', 'Jeremiah 39:4', 
                'Jeremiah 39:5', 'Jeremiah 39:6', 'Jeremiah 39:7', 'Jeremiah 39:8', 
                'Jeremiah 39:9', 'Jeremiah 39:10', 'Jeremiah 39:11', 'Jeremiah 39:12', 
                'Jeremiah 39:13', 'Jeremiah 46:26', 'Jeremiah 48:45', 'Jeremiah 48:46', 
                'Jeremiah 48:47', 'Jeremiah 49:6', 'Jeremiah 51:45', 'Jeremiah 51:46', 
                'Jeremiah 51:47', 'Jeremiah 51:48', 'Jeremiah 52:2', 'Jeremiah 52:3',
                'Jeremiah 52:15', 'Jeremiah 52:28', 'Jeremiah 52:29', 'Jeremiah 52:30',
                 
                'Lamentations 3:22', 'Lamentations 3:23', 'Lamentations 3:24', 'Lamentations 3:29',
                 
                'Ezekiel 1:14', 'Ezekiel 10:14', 'Ezekiel 27:31', 'Ezekiel 32:19', 
                'Ezekiel 33:26', 'Ezekiel 40:30',


                'Matthew 17:21', 'Matthew 18:11', 'Matthew 21:44', 'Matthew 23:14',
                'Mark 7:16', 'Mark 9:44', 'Mark 9:46', 'Mark 11:26', 'Mark 15:28',
                'Luke 17:36', 'Luke 23:17', 'Luke 24:12', 'Luke 24:40',
                'John 5:4', 'John 21:25',
                'Acts 8:37', 'Acts 15:34', 'Acts 24:7', 'Acts 28:29',
                'Romans 16:24',
                'II Corinthians 13:14'
            ]
            if not key in known_strange_verses:
                print( "missing from source: " + str(key) + " module: " + str(module_name) )
                missing_keys.append( key )

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
