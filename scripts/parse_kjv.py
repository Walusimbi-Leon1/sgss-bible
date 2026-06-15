#!/usr/bin/env python3
"""
Parse the KJV Bible from Project Gutenberg into individual book files.

Usage:
    curl -sL https://www.gutenberg.org/cache/epub/10/pg10.txt -o kjv-full.txt
    python3 scripts/parse_kjv.py

Output: kjv/ directory with one file per book.
"""

import re
import os
import sys

def main():
    input_file = "kjv-full.txt"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        print("Download it first:")
        print("  curl -sL https://www.gutenberg.org/cache/epub/10/pg10.txt -o kjv-full.txt")
        sys.exit(1)

    output_dir = "kjv"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find Bible text boundaries
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "The First Book of Moses: Called Genesis" and i > 50:
            start_idx = i
        if "*** END OF THE PROJECT GUTENBERG" in stripped:
            end_idx = i
            break

    if not start_idx or not end_idx:
        print("Error: Could not find Bible text boundaries.")
        sys.exit(1)

    print(f"Bible text: lines {start_idx+1} to {end_idx}")

    ALL_BOOKS = [
        # Old Testament
        "The First Book of Moses: Called Genesis",
        "The Second Book of Moses: Called Exodus",
        "The Third Book of Moses: Called Leviticus",
        "The Fourth Book of Moses: Called Numbers",
        "The Fifth Book of Moses: Called Deuteronomy",
        "The Book of Joshua",
        "The Book of Judges",
        "The Book of Ruth",
        "The First Book of Samuel",
        "The Second Book of Samuel",
        "The First Book of the Kings",
        "The Second Book of the Kings",
        "The First Book of the Chronicles",
        "The Second Book of the Chronicles",
        "Ezra",
        "The Book of Nehemiah",
        "The Book of Esther",
        "The Book of Job",
        "The Book of Psalms",
        "The Proverbs",
        "Ecclesiastes",
        "The Song of Solomon",
        "The Book of the Prophet Isaiah",
        "The Book of the Prophet Jeremiah",
        "The Lamentations of Jeremiah",
        "The Book of the Prophet Ezekiel",
        "The Book of Daniel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
        "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
        # New Testament
        "The Gospel According to Saint Matthew",
        "The Gospel According to Saint Mark",
        "The Gospel According to Saint Luke",
        "The Gospel According to Saint John",
        "The Acts of the Apostles",
        "The Epistle of Paul the Apostle to the Romans",
        "The First Epistle of Paul the Apostle to the Corinthians",
        "The Second Epistle of Paul the Apostle to the Corinthians",
        "The Epistle of Paul the Apostle to the Galatians",
        "The Epistle of Paul the Apostle to the Ephesians",
        "The Epistle of Paul the Apostle to the Philippians",
        "The Epistle of Paul the Apostle to the Colossians",
        "The First Epistle of Paul the Apostle to the Thessalonians",
        "The Second Epistle of Paul the Apostle to the Thessalonians",
        "The First Epistle of Paul the Apostle to Timothy",
        "The Second Epistle of Paul the Apostle to Timothy",
        "The Epistle of Paul the Apostle to Titus",
        "The Epistle of Paul the Apostle to Philemon",
        "The Epistle of Paul the Apostle to the Hebrews",
        "The General Epistle of James",
        "The First Epistle General of Peter",
        "The Second General Epistle of Peter",
        "The First Epistle General of John",
        "The Second Epistle General of John",
        "The Third Epistle General of John",
        "The General Epistle of Jude",
        "The Revelation of Saint John the Divine",
    ]

    NAME_MAP = {
        "The First Book of Moses: Called Genesis": "01-Genesis",
        "The Second Book of Moses: Called Exodus": "02-Exodus",
        "The Third Book of Moses: Called Leviticus": "03-Leviticus",
        "The Fourth Book of Moses: Called Numbers": "04-Numbers",
        "The Fifth Book of Moses: Called Deuteronomy": "05-Deuteronomy",
        "The Book of Joshua": "06-Joshua",
        "The Book of Judges": "07-Judges",
        "The Book of Ruth": "08-Ruth",
        "The First Book of Samuel": "09-1Samuel",
        "The Second Book of Samuel": "10-2Samuel",
        "The First Book of the Kings": "11-1Kings",
        "The Second Book of the Kings": "12-2Kings",
        "The First Book of the Chronicles": "13-1Chronicles",
        "The Second Book of the Chronicles": "14-2Chronicles",
        "Ezra": "15-Ezra",
        "The Book of Nehemiah": "16-Nehemiah",
        "The Book of Esther": "17-Esther",
        "The Book of Job": "18-Job",
        "The Book of Psalms": "19-Psalms",
        "The Proverbs": "20-Proverbs",
        "Ecclesiastes": "21-Ecclesiastes",
        "The Song of Solomon": "22-SongOfSolomon",
        "The Book of the Prophet Isaiah": "23-Isaiah",
        "The Book of the Prophet Jeremiah": "24-Jeremiah",
        "The Lamentations of Jeremiah": "25-Lamentations",
        "The Book of the Prophet Ezekiel": "26-Ezekiel",
        "The Book of Daniel": "27-Daniel",
        "Hosea": "28-Hosea", "Joel": "29-Joel", "Amos": "30-Amos",
        "Obadiah": "31-Obadiah", "Jonah": "32-Jonah", "Micah": "33-Micah",
        "Nahum": "34-Nahum", "Habakkuk": "35-Habakkuk",
        "Zephaniah": "36-Zephaniah", "Haggai": "37-Haggai",
        "Zechariah": "38-Zechariah", "Malachi": "39-Malachi",
        "The Gospel According to Saint Matthew": "40-Matthew",
        "The Gospel According to Saint Mark": "41-Mark",
        "The Gospel According to Saint Luke": "42-Luke",
        "The Gospel According to Saint John": "43-John",
        "The Acts of the Apostles": "44-Acts",
        "The Epistle of Paul the Apostle to the Romans": "45-Romans",
        "The First Epistle of Paul the Apostle to the Corinthians": "46-1Corinthians",
        "The Second Epistle of Paul the Apostle to the Corinthians": "47-2Corinthians",
        "The Epistle of Paul the Apostle to the Galatians": "48-Galatians",
        "The Epistle of Paul the Apostle to the Ephesians": "49-Ephesians",
        "The Epistle of Paul the Apostle to the Philippians": "50-Philippians",
        "The Epistle of Paul the Apostle to the Colossians": "51-Colossians",
        "The First Epistle of Paul the Apostle to the Thessalonians": "52-1Thessalonians",
        "The Second Epistle of Paul the Apostle to the Thessalonians": "53-2Thessalonians",
        "The First Epistle of Paul the Apostle to Timothy": "54-1Timothy",
        "The Second Epistle of Paul the Apostle to Timothy": "55-2Timothy",
        "The Epistle of Paul the Apostle to Titus": "56-Titus",
        "The Epistle of Paul the Apostle to Philemon": "57-Philemon",
        "The Epistle of Paul the Apostle to the Hebrews": "58-Hebrews",
        "The General Epistle of James": "59-James",
        "The First Epistle General of Peter": "60-1Peter",
        "The Second General Epistle of Peter": "61-2Peter",
        "The First Epistle General of John": "62-1John",
        "The Second Epistle General of John": "63-2John",
        "The Third Epistle General of John": "64-3John",
        "The General Epistle of Jude": "65-Jude",
        "The Revelation of Saint John the Divine": "66-Revelation",
    }

    # Find book start lines (skip "Otherwise Called:" subtitles)
    book_starts = []
    prev_line = ""
    for i, line in enumerate(lines[start_idx:end_idx], start=start_idx):
        stripped = line.strip()
        if prev_line.strip() == "Otherwise Called:":
            prev_line = stripped
            continue
        if stripped in ALL_BOOKS:
            book_starts.append((i, stripped))
        prev_line = line

    print(f"Found {len(book_starts)} books")

    for bi, (start_line, title) in enumerate(book_starts):
        end_line = book_starts[bi + 1][0] if bi + 1 < len(book_starts) else end_idx
        book_lines = lines[start_line:end_line]
        filename = NAME_MAP.get(title, f"{bi+1:02d}-{title}")

        outpath = os.path.join(output_dir, f"{filename}.txt")
        with open(outpath, "w", encoding="utf-8") as out:
            out.write(title + "\n\n")
            for line in book_lines:
                stripped = line.strip()
                if stripped == title or stripped.startswith("The Old Testament") \
                   or stripped.startswith("The New Testament") or stripped == "***" \
                   or stripped == "Otherwise Called:" or stripped.isdigit():
                    continue
                if stripped:
                    out.write(stripped + "\n")

        print(f"  ✓ {filename}.txt")

    print(f"\nDone! {len(book_starts)} books extracted to '{output_dir}/'.")

if __name__ == "__main__":
    main()
