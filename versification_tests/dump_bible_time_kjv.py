import os,re
os.sys.path.append("../data")
import osis_tran

def split_by_punctuation(text):
    # Regular expression to match any punctuation character
    pattern = r'([\.\!\?\-\;\,\\\:\(\)])'
    # Split the text by the pattern, keeping the punctuation in the result
    result = re.split(pattern, text)
    # Filter out any empty strings from the result
    result = [elem.strip() for elem in result if elem.strip()]
    return result


def produce_list():
    bible_time_kjv = osis_tran.load_osis_module("KJV", lower=False)

    output_lines = []

    for ref,verse in bible_time_kjv.items():
        output_lines.append({"type": "ref", "value":ref})
        for piece in split_by_punctuation(verse):
            output_lines.append({"type": "verse", "value": piece.lower()})

    return output_lines


def main():
    output_lines = produce_list()

    with open( "kjv_bible_time.txt", "w", encoding="utf-8") as f:
        f.write( "\n".join( output_line["type"] + ": " + output_line["value"] for output_line in output_lines ) )

if __name__ == "__main__":
    main()
