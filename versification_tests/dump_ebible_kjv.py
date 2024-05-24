import os
import dump_bible_time_kjv

#https://github.com/BibleNLP/ebible/
ebible_repo = "/home/lansford/temp/ebible"

vref_file = os.path.join( ebible_repo, "./metadata/vref.txt" )
kjv_file = os.path.join( ebible_repo, "./corpus/eng-eng-kjv.txt" )

def normalize_ref( ref ):
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
            

    return ref

def process_verse( verse ):
    characters_to_remove = "¶"
    characters_to_replace = {
        "’": "'",
        "æ": "e",
        'Æ': 'E',
        "Judaea": "Judea",
        "Alphaeus": "Alpheus",
        "Thaddaeus": "Thaddeus",
        "Caesarea": "Cesarea",
        "Caesar": "Cesar",
        "Idumaea": "Idumea",
        "Galilaean": "Galilean",
        "Arimathaea": "Arimathea",
        "Ituraea": "Iturea",
        "Epaenetus": "Epenetus",
        "Endor": "En-Dor",
    }

    for character in characters_to_remove:
        verse = verse.replace( character, " " )

    for character, replacement in characters_to_replace.items():
        verse = verse.replace( character, replacement )

    return verse

def load_kjv_file():
    result = {}
    with open( kjv_file, "r", encoding="utf-8" ) as data_in:
        with open( vref_file, "r", encoding="utf-8" ) as vref_in:
            for line, vref_line in zip( data_in, vref_in ):
                result[ normalize_ref(vref_line.strip()) ] = process_verse(line.strip()).strip()

    return result

def produce_list():
    ebible_kjv = load_kjv_file()

    output_lines = []

    for ref,verse in ebible_kjv.items():
        if verse.strip():
            output_lines.append({"type": "ref", "value": ref})
            for piece in dump_bible_time_kjv.split_by_punctuation(verse):
                output_lines.append({"type": "verse", "value": piece.lower()})
        else:
            print( "dropping empty verse: " + ref )

    return output_lines


def main():
    output_lines = produce_list()

    with open( "kjv_ebible.txt", "w", encoding="utf-8") as f:
        f.write( "\n".join( output_line["type"] + ": " + output_line["value"] for output_line in output_lines ) )



if __name__ == "__main__":
    main()

