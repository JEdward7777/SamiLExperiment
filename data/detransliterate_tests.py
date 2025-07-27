
from unidecode import unidecode
import prepare_bible__in_SILNLP_format

def main():
    #Load the raw data:
    vref = "/home/lansford/bible_token_models/scripture_from_David/vref.txt"
    source_filepath = "/home/lansford/bible_token_models/scripture_from_David/blx-AMIU.txt"
    loaded_module = prepare_bible__in_SILNLP_format.load_silnlp(vref,source_filepath)

    output_train_file = "/home/lansford/bible_token_models/scripture_from_David/detransliterate_test.csv"

    with open( output_train_file, "wt" ) as fout:
        fout.write( "ref,non_roman,roman\n" )

        for ref,verse in loaded_module.items():
            verse_roman = unidecode(verse)

            verse = verse.replace( '"', '""' )
            verse_roman = verse_roman.replace( '"', '""' )
            

            fout.write( f'"{ref}","{verse}","{verse_roman}"\n')

if __name__ == '__main__': main()