import argparse
import os
import re
from pathlib import Path

name_to_id = {
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
    "Revelation of John": "REV",
}

def parse_bible_file(input_file):
    sfm_files = {}
    with open(input_file, "r", encoding="utf-8") as file:
        current_book = None
        current_chapter = None
        for line in file:
            match = re.match(r"(.+?) (\d+):(\d+) (.+)", line)
            if match:
                book = name_to_id[match.group(1).strip()]
                chapter = int(match.group(2).strip())
                verse = int(match.group(3).strip())
                text = match.group(4).strip()

                if book != current_book:
                    current_book = book
                    current_chapter = None
                    if current_book not in sfm_files:
                        sfm_files[current_book] = []

                if chapter != current_chapter:
                    current_chapter = chapter
                    sfm_files[current_book].append([])

                sfm_files[current_book][-1].append((verse, text))

    return sfm_files


def write_sfm_files(sfm_files, output_dir):
    for book_num, (book, chapters) in enumerate(sfm_files.items(),1):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for idx, chapter in enumerate(chapters):
            output_file = os.path.join(output_dir, f"{book_num:02}{book}.sfm")
            with open(output_file, "a", encoding="utf-8") as file:
                if idx == 0:
                    file.write(f"\\id {book}\n")
                file.write(f"\\c {idx + 1}\n")
                for verse, text in chapter:
                    file.write(f"\\v {verse} {text}\n")
                file.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Convert text files to project format."
    )
    parser.add_argument("file", type=Path, help="File to convert")
    parser.add_argument("output", type=Path, help="Folder for the output project.")

    args = parser.parse_args()
    file = Path(args.file)

    output_folder = Path(args.output)
    print(file, output_folder)
    sfm_files = parse_bible_file(file)
    write_sfm_files(sfm_files, output_dir=output_folder)


if __name__ == "__main__":
    main()
