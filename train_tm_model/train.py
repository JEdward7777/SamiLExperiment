from collections import OrderedDict
import itertools
import os, json, sys
from unidecode import unidecode
import codecs
from sentence_transmorgrifier.transmorgrify import Transmorgrifier


sys.path.append('../data' )
sys.path.append('../data/subword-nmt' )
import osis_tran
import apply_bpe


bpe_code_files = {}
def run_bpe( input_string, code_file, glossaries):
    if code_file not in bpe_code_files:
        codes = codecs.open(code_file, encoding='utf-8')
        bpe_code_files[code_file] = codes
    else:
        codes = bpe_code_files[code_file]
    bpe = apply_bpe.BPE(codes=codes, glossaries=glossaries)
    return bpe.segment( input_string.strip() )

def main():
    with open("train_tm_config.json") as fin:
         tm_config = json.load(fin)
    config = tm_config["configs"][tm_config["active_config"]]

    source_language = config["source_language"] if "source_language" in config else tm_config["active_config"]

    #now figure out where to find the language.
    if config["module_source"] == "osis_module":
        source_module = osis_tran.load_osis_module(source_language,lower=False)
    else:
        raise ValueError(f"Unknown module source {config['module_source']}")
    
    #now truncate the data if the key exists for it.
    if "truncate" in config and config["truncate"] > 0 and config["truncate"] < len(source_module):
        source_module = OrderedDict(itertools.islice(source_module.items(), config["truncate"])) 

    
    #Make a deep copy for the versions that we are going to do all the tranformations to.  (it is a dictionary)
    source_module_copy = source_module.copy()

    #now lower case everything if that is configured.
    if config["lower_case"]:
        source_module_copy = {k:v.lower() for k,v in source_module_copy.items()}

    #now unidecode everything if that is configured.
    if config["unidecode"]:
        source_module_copy = {k:unidecode(v) for k,v in source_module_copy.items()}

    #now run the tokenization if that is configured.
    if config["tokenize"]:
        source_module_copy = {k:run_bpe(v, code_file=config["code_file"], glossaries=[]) for k,v in source_module_copy.items()}

    keys = list( source_module.keys() )

    tm = Transmorgrifier()

    from_sentences = [source_module_copy[key] for key in keys]
    to_sentences   = [source_module     [key] for key in keys]
    tm.train( from_sentences=from_sentences, to_sentences=to_sentences, **config["tm_params"] )
    tm.save( config["output_dir"].format( lang=source_language ) )


    #some testing
    source_module_full = osis_tran.load_osis_module(source_language,lower=False)
    verse_right = source_module_full[list(source_module_full.keys())[-2]]
    verse_wrong = verse_right
    if config["lower_case"]: verse_wrong = verse_wrong.lower()
    if config["unidecode"]: verse_wrong = unidecode(verse_wrong)
    if config["tokenize"]: verse_wrong = run_bpe(verse_wrong, code_file=config["code_file"], glossaries=[])
    verse_fixed = list(tm.execute([verse_wrong]))[0]


    print( f"Target: {verse_right}")
    print( f"Source: {verse_wrong}" )
    print( f"Fixed: {verse_fixed}" )

    print( "done")


if __name__ == "__main__":
    main()