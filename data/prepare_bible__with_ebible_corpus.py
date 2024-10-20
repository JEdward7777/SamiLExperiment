#This module will download a test bible which we do not have the old testament to give real world motion of translating into a Bible without an OT.
#data is downloaded from https://raw.githubusercontent.com/sil-ai/sil-microsoft-hackathon-2023/main/data/amo.json



import requests
import os
import json
from unidecode import unidecode

import prepare_bible

corpus_path = "/home/lansford/bible_token_models/samual_liedes_experiment_data/ebible"

def load_silnlp( vref, versedata, toascii ):
    result = {}
    with open( vref, "rt", encoding="utf-8" ) as vref_in:
        with open( versedata, "rt", encoding="utf-8" ) as versedata_in:
            for vref_line, versedata_line in zip(vref_in, versedata_in):
                vref_line = vref_line.strip()
                versedata_line = versedata_line.strip()
                if vref_line and versedata_line and versedata_line != "<range>":
                    if not toascii:
                        result[vref_line] = versedata_line.lower()
                    else:
                        result[vref_line] = unidecode(versedata_line).lower()

                if vref_line == "REV 22:21": break #truncate the books after revelations which not match up.
    return result


def list_ebible_modules():
    return [x[:-4] for x in os.listdir(os.path.join(corpus_path, "corpus")) if x.endswith(".txt")]

def main():

    ebible_module_names = list_ebible_modules()
    
    def ebible_loader( name, toascii ):
        if name in ebible_module_names:
            return load_silnlp( os.path.join( corpus_path, "metadata/vref.txt" ), os.path.join( corpus_path, "corpus", name + ".txt" ), toascii=toascii )
        raise Exception( "Unknown module: " + name )
        #return default_loader( name, toascii=toascii )


    #drop all english versions which start with "eng-"
    ebible_module_names_without_english = [x for x in ebible_module_names if not x.startswith("eng-")]

    #for debugging just truncated the list to the first 4
    # ebible_module_names_without_english = ebible_module_names_without_english[:4]
    # if "grc-grcbrent" not in ebible_module_names_without_english: ebible_module_names_without_english.append( "grc-grcbrent" )

    #add a * on the start of all of them.
    ebible_module_names_without_english = ["*"+x for x in ebible_module_names_without_english]

    prepare_bible.BIBLE_LOADER = ebible_loader
    #prepare_bible.MODULES.append( "AMO" )
    #prepare_bible.TARGETS.append( "AMO" )
    prepare_bible.MODULES = ebible_module_names_without_english + ["eng-englee"]
    prepare_bible.TARGETS = ["eng-englee"]


    prepare_bible.PREP = '/home/lansford/bible_token_models/samual_liedes_experiment_data/ebible_to_english/prep'
    prepare_bible.TMP = prepare_bible.PREP + '/tmp'
    prepare_bible.BPE_CODE = prepare_bible.PREP + '/code'
    prepare_bible.SRC = 'grc-grcbrent'
    prepare_bible.TRAIN_STARTS = {
        "eng-englee": 'MAT',
    }
    prepare_bible.main()

    
    return ebible_loader

if __name__ == '__main__':
    main()