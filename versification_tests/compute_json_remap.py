import json
import datetime

verse_diff_file = "kjv_versification.diff"
output_remap_file = "eng_to_org_verses.json"
remap_identification = {
    "from": "ENG",
    "to": "ORG",
    "date": datetime.datetime.now().strftime( "%Y/%m/%d" )
}

ref_removed = None
ref_added = None

remap = {}
added_verses = []
removed_verses = []

with open( verse_diff_file, "r", encoding="utf-8" ) as data_in:

    for line in data_in:
        if "-ref:" in line:
            if ref_removed is None:
                ref_removed = line.replace( "-ref:", "" ).strip()

                if ref_added is not None:
                    remap[ref_removed] = ref_added
                    ref_removed = None
                    ref_added = None
            else:
                removed_verses.append( ref_removed )

                ref_removed = line.replace( "-ref:", "" ).strip()

        elif "+ref:" in line:
            if ref_added is None:
                ref_added = line.replace( "+ref:", "" ).strip()

                if ref_removed is not None:
                    remap[ref_removed] = ref_added
                    ref_removed = None
                    ref_added = None
            else:
                added_verses.append( ref_added )

                ref_added = line.replace( "+ref:", "" ).strip()
        else:
            if ref_added is not None:
                added_verses.append( ref_added )
                ref_added = None
            if ref_removed is not None:
                removed_verses.append( ref_removed )
                ref_removed = None

def shorten_verse_reference( ref ):
    verse_shorteners = {
        "Genesis": "GEN",
        "Exodus": "EXO",
        "Leviticus": "LEV",
        "Numbers": "NUM",
        "Deuteronomy": "DEU",
        "Joshua": "JOS",
        "Judges": "JDG",
        "Ruth": "RUT",
        "I Samuel": "1SA",
        "II Samuel": "2SA",
        "I Kings": "1KI",
        "II Kings": "2KI",
        "I Chronicles": "1CH",
        "II Chronicles": "2CH",
        "Ezra": "EZR",
        "Nehemiah": "NEH",
        "Esther": "EST",
        "Job": "JOB",
        "Psalms": "PSA",
        "Proverbs": "PRO",
        "Ecclesiastes": "ECC",
        "Song of Solomon": "SNG",
        "Isaiah": "ISA",
        "Jeremiah": "JER",
        "Lamentations": "LAM",
        "Ezekiel": "EZK",
        "Daniel": "DAN",
        "Hosea": "HOS",
        "Joel": "JOL",
        "Amos": "AMO",
        "Obadiah": "OBA",
        "Jonah": "JON",
        "Micah": "MIC",
        "Nahum": "NAM",
        "Habakkuk": "HAB",
        "Zephaniah": "ZEP",
        "Haggai": "HAG",
        "Zechariah": "ZEC",
        "Malachi": "MAL",
        "Matthew": "MAT",
        "Mark": "MRK",
        "Luke": "LUK",
        "John": "JHN",
        "Acts": "ACT",
        "Romans": "ROM",
        "I Corinthians": "1CO",
        "II Corinthians": "2CO",
        "Galatians": "GAL",
        "Ephesians": "EPH",
        "Philippians": "PHP",
        "Colossians": "COL",
        "I Thessalonians": "1TH",
        "II Thessalonians": "2TH",
        "I Timothy": "1TI",
        "II Timothy": "2TI",
        "Titus": "TIT",
        "Philemon": "PHM",
        "Hebrews": "HEB",
        "James": "JAM",
        "I Peter": "1PE",
        "II Peter": "2PE",
        "I John": "1JN",
        "II John": "2JN",
        "III John": "3JN",
        "Jude": "JUD",
        "Revelation": "REV"
    }

    num_replacements = 0
    shorter_ref = ""
    for longer, shorter in verse_shorteners.items():
        if ref.startswith( longer ):
            shorter_ref = ref.replace( longer, shorter )
            num_replacements += 1
    
    if num_replacements != 1:
        raise Exception( "Unexpected number of replacements: " + str( num_replacements ) )

    return shorter_ref
        

remap_shorter = {shorten_verse_reference(k): shorten_verse_reference(v) for k, v in remap.items()}
added_verses_shorter = [shorten_verse_reference(v) for v in added_verses]
removed_verses_shorter = [shorten_verse_reference(v) for v in removed_verses]

with open( output_remap_file, "w", encoding="utf-8" ) as f:
    json.dump( {
        "identification": remap_identification,
        "added": added_verses_shorter,
        "removed": removed_verses_shorter,
        "remap": remap_shorter,
    }, f, indent=4 )