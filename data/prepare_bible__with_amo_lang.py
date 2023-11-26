#This module will download a test bible which we do not have the old testament to give real world motion of translating into a Bible without an OT.
#data is downloaded from https://raw.githubusercontent.com/sil-ai/sil-microsoft-hackathon-2023/main/data/amo.json



import requests
import os
import json

import prepare_bible

def download_json(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(response.content)

def load_json_file(filename):
    with open(filename) as file:
        data = json.load(file)
    return data

def main():
    #download amo json from https://raw.githubusercontent.com/sil-ai/sil-microsoft-hackathon-2023/main/data/amo.json
    url = "https://raw.githubusercontent.com/sil-ai/sil-microsoft-hackathon-2023/main/data/amo.json"
    filename = "amo.json"
    download_json(url, filename)

    # Load the JSON file
    json_data = load_json_file(filename)

    amo_module = {}

    for verse in json_data:
        ref = verse['vref']
        target = verse['target']["content"]

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
           .replace( "REV", "Revelation" ) )
        
        #make sure we didn't miss one.
        assert( ref[3] != ' ' or ref[:3] == "Job" or ref[:3] == "III" )
        if target:
            amo_module[ref] = target
        
    
    default_loader = prepare_bible.BIBLE_LOADER
    def amo_loader_splicer( name, toascii ):
        if name=="AMO":
            return amo_module
        return default_loader( name, toascii=toascii )
    prepare_bible.BIBLE_LOADER = amo_loader_splicer
    prepare_bible.MODULES.append( "AMO" )
    prepare_bible.TARGETS.append( "AMO" )
    prepare_bible.main()

    
    return amo_loader_splicer

if __name__ == '__main__':
    main()