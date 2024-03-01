import requests
import os
import json

import prepare_bible
from unidecode import unidecode

def load_silnlp( vref, versedata ):
    result = {}
    with open( vref, "rt", encoding="utf-8" ) as vref_in:
        with open( versedata, "rt", encoding="utf-8" ) as versedata_in:
            for vref_line, versedata_line in zip(vref_in, versedata_in):
                vref_line = vref_line.strip()
                versedata_line = versedata_line.strip()
                if vref_line and versedata_line and versedata_line != "<range>":
                    result[vref_line] = versedata_line

                if vref_line == "REV 22:21": break #truncate the books after revelations which not match up.
    return result

def main( ):
    vref = "./vref.txt"
    file_paths = {
        "abc_lang": "./silnlp_content.txt",
    }

    loaded_modules = {}
    for key,file_path in file_paths.items():
        loaded_module = load_silnlp(vref,file_path)

        renamed_books = {}

        for ref,target in loaded_module.items():

            ref = (ref.replace( "GEN", "Genesis" )
            .replace( "EXO", "Exodus" )
            .replace( "LEV", "Leviticus" )
            .replace( "NUM", "Numbers" )
            .replace( "DEU", "Deuteronomy" )
            .replace( "JOS", "Joshua" )
            .replace( "JDG", "Judges" )
            .replace( "RUT", "Ruth" )
            .replace( "1SA", "I Samuel" )
            .replace( "2SA", "II Samuel" )
            .replace( "1KI", "I Kings" )
            .replace( "2KI", "II Kings" )
            .replace( "1CH", "I Chronicles" )
            .replace( "2CH", "II Chronicles" )
            .replace( "EZR", "Ezra" )
            .replace( "NEH", "Nehemiah" )
            .replace( "EST", "Esther" )
            .replace( "JOB", "Job" )
            .replace( "PSA", "Psalms" )
            .replace( "PRO", "Proverbs" )
            .replace( "ECC", "Ecclesiastes" )
            .replace( "SNG", "Song of Solomon" )
            .replace( "ISA", "Isaiah" )
            .replace( "JER", "Jeremiah" )
            .replace( "LAM", "Lamentations" )
            .replace( "EZK", "Ezekiel" )
            .replace( "DAN", "Daniel" )
            .replace( "HOS", "Hosea" )
            .replace( "JOL", "Joel" )
            .replace( "AMO", "Amos" )
            .replace( "OBA", "Obadiah" )
            .replace( "JON", "Jonah" )
            .replace( "MIC", "Micah" )
            .replace( "NAM", "Nahum" )
            .replace( "HAB", "Habakkuk" )
            .replace( "ZEP", "Zephaniah" )
            .replace( "HAG", "Haggai" )
            .replace( "ZEC", "Zechariah" )
            .replace( "MAL", "Malachi" )
            .replace( "MAT", "Matthew" )
            .replace( "MRK", "Mark" )
            .replace( "LUK", "Luke" )
            .replace( "JHN", "John" )
            .replace( "ACT", "Acts" )
            .replace( "ROM", "Romans" )
            .replace( "1CO", "I Corinthians" )
            .replace( "2CO", "II Corinthians" )
            .replace( "GAL", "Galatians" )
            .replace( "EPH", "Ephesians" )
            .replace( "PHP", "Philippians" )
            .replace( "COL", "Colossians" )
            .replace( "1TH", "I Thessalonians" )
            .replace( "2TH", "II Thessalonians" )
            .replace( "1TI", "I Timothy" )
            .replace( "2TI", "II Timothy" )
            .replace( "TIT", "Titus" )
            .replace( "PHM", "Philemon" )
            .replace( "HEB", "Hebrews" )
            .replace( "JAM", "James" ).replace( "JAS", "James" )
            .replace( "1PE", "I Peter" )
            .replace( "2PE", "II Peter" )
            .replace( "1JN", "I John" )
            .replace( "2JN", "II John" )
            .replace( "3JN", "III John" )
            .replace( "JUD", "Jude" )
            .replace( "REV", "Revelation of John" ) )
            
            #make sure we didn't miss one.
            assert( ref[3] != ' ' or ref[:3] == "Job" or ref[:3] == "III" )
            if target:
                renamed_books[ref] = target
        loaded_modules[key] = renamed_books 
    
    default_loader = prepare_bible.BIBLE_LOADER
    def loader_splicer( name, toascii ):
        if name in loaded_modules:
            asciied_mod = {}
            for k,v in loaded_modules[name].items():
                asciied_mod[k] = unidecode(v)
            return asciied_mod
        return default_loader( name, toascii=toascii )
    

    prepare_bible.BIBLE_LOADER = loader_splicer

    for key in file_paths.keys():
        prepare_bible.MODULES.insert( 0, "*" + key )  #The prefixing star makes it get transliterated to ascii.
        prepare_bible.TARGETS.insert( 0, key )


    prepare_bible.PREP = 'bible.prep.abc_lang'
    prepare_bible.TMP = prepare_bible.PREP + '/tmp'
    prepare_bible.BPE_CODE = prepare_bible.PREP + '/code'
    prepare_bible.main()

    
    return loader_splicer

if __name__ == '__main__':
    main()