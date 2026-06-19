#!/usr/bin/env python3
"""
Build the Songs of the SGSS Bible — a lyrics file for Suno AI / music generation.
Reads the SGSS text files (sgss/*.txt), removes verse numbers, splits long chapters,
and outputs a single formatted lyrics file.
"""

import os, re, math

SGSS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sgss')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'sgss-bible-songs.txt')

# Traditional authorship mapping
AUTHORS = {
    'Genesis': 'Moses',
    'Exodus': 'Moses',
    'Leviticus': 'Moses',
    'Numbers': 'Moses',
    'Deuteronomy': 'Moses',
    'Joshua': 'Joshua',
    'Judges': 'Samuel',
    'Ruth': 'Samuel',
    '1Samuel': 'Samuel',
    '2Samuel': 'Samuel',
    '1Kings': 'Jeremiah',
    '2Kings': 'Jeremiah',
    '1Chronicles': 'Ezra',
    '2Chronicles': 'Ezra',
    'Ezra': 'Ezra',
    'Nehemiah': 'Nehemiah',
    'Esther': 'Mordecai',
    'Job': 'Moses',
    'Psalms': 'David',
    'Proverbs': 'Solomon',
    'Ecclesiastes': 'Solomon',
    'SongOfSolomon': 'Solomon',
    'Isaiah': 'Isaiah',
    'Jeremiah': 'Jeremiah',
    'Lamentations': 'Jeremiah',
    'Ezekiel': 'Ezekiel',
    'Daniel': 'Daniel',
    'Hosea': 'Hosea',
    'Joel': 'Joel',
    'Amos': 'Amos',
    'Obadiah': 'Obadiah',
    'Jonah': 'Jonah',
    'Micah': 'Micah',
    'Nahum': 'Nahum',
    'Habakkuk': 'Habakkuk',
    'Zephaniah': 'Zephaniah',
    'Haggai': 'Haggai',
    'Zechariah': 'Zechariah',
    'Malachi': 'Malachi',
    'Matthew': 'Matthew',
    'Mark': 'Mark',
    'Luke': 'Luke',
    'John': 'John',
    'Acts': 'Luke',
    'Romans': 'Paul',
    '1Corinthians': 'Paul',
    '2Corinthians': 'Paul',
    'Galatians': 'Paul',
    'Ephesians': 'Paul',
    'Philippians': 'Paul',
    'Colossians': 'Paul',
    '1Thessalonians': 'Paul',
    '2Thessalonians': 'Paul',
    '1Timothy': 'Paul',
    '2Timothy': 'Paul',
    'Titus': 'Paul',
    'Philemon': 'Paul',
    'Hebrews': 'Paul',
    'James': 'James',
    '1Peter': 'Peter',
    '2Peter': 'Peter',
    '1John': 'John',
    '2John': 'John',
    '3John': 'John',
    'Jude': 'Jude',
    'Revelation': 'John',
}

# Short book names for use in song titles
BOOK_SHORT = {
    '01-Genesis.txt': 'Genesis',
    '02-Exodus.txt': 'Exodus',
    '03-Leviticus.txt': 'Leviticus',
    '04-Numbers.txt': 'Numbers',
    '05-Deuteronomy.txt': 'Deuteronomy',
    '06-Joshua.txt': 'Joshua',
    '07-Judges.txt': 'Judges',
    '08-Ruth.txt': 'Ruth',
    '09-1Samuel.txt': '1 Samuel',
    '10-2Samuel.txt': '2 Samuel',
    '11-1Kings.txt': '1 Kings',
    '12-2Kings.txt': '2 Kings',
    '13-1Chronicles.txt': '1 Chronicles',
    '14-2Chronicles.txt': '2 Chronicles',
    '15-Ezra.txt': 'Ezra',
    '16-Nehemiah.txt': 'Nehemiah',
    '17-Esther.txt': 'Esther',
    '18-Job.txt': 'Job',
    '19-Psalms.txt': 'Psalms',
    '20-Proverbs.txt': 'Proverbs',
    '21-Ecclesiastes.txt': 'Ecclesiastes',
    '22-SongOfSolomon.txt': 'Song of Solomon',
    '23-Isaiah.txt': 'Isaiah',
    '24-Jeremiah.txt': 'Jeremiah',
    '25-Lamentations.txt': 'Lamentations',
    '26-Ezekiel.txt': 'Ezekiel',
    '27-Daniel.txt': 'Daniel',
    '28-Hosea.txt': 'Hosea',
    '29-Joel.txt': 'Joel',
    '30-Amos.txt': 'Amos',
    '31-Obadiah.txt': 'Obadiah',
    '32-Jonah.txt': 'Jonah',
    '33-Micah.txt': 'Micah',
    '34-Nahum.txt': 'Nahum',
    '35-Habakkuk.txt': 'Habakkuk',
    '36-Zephaniah.txt': 'Zephaniah',
    '37-Haggai.txt': 'Haggai',
    '38-Zechariah.txt': 'Zechariah',
    '39-Malachi.txt': 'Malachi',
    '40-Matthew.txt': 'Matthew',
    '41-Mark.txt': 'Mark',
    '42-Luke.txt': 'Luke',
    '43-John.txt': 'John',
    '44-Acts.txt': 'Acts',
    '45-Romans.txt': 'Romans',
    '46-1Corinthians.txt': '1 Corinthians',
    '47-2Corinthians.txt': '2 Corinthians',
    '48-Galatians.txt': 'Galatians',
    '49-Ephesians.txt': 'Ephesians',
    '50-Philippians.txt': 'Philippians',
    '51-Colossians.txt': 'Colossians',
    '52-1Thessalonians.txt': '1 Thessalonians',
    '53-2Thessalonians.txt': '2 Thessalonians',
    '54-1Timothy.txt': '1 Timothy',
    '55-2Timothy.txt': '2 Timothy',
    '56-Titus.txt': 'Titus',
    '57-Philemon.txt': 'Philemon',
    '58-Hebrews.txt': 'Hebrews',
    '59-James.txt': 'James',
    '60-1Peter.txt': '1 Peter',
    '61-2Peter.txt': '2 Peter',
    '62-1John.txt': '1 John',
    '63-2John.txt': '2 John',
    '64-3John.txt': '3 John',
    '65-Jude.txt': 'Jude',
    '66-Revelation.txt': 'Revelation',
}

# For author lookup, map short book name (no number prefix) to author key
def get_author(book_short):
    # Map short names to author keys
    author_key = book_short.replace(' ', '')
    author_key = author_key.replace('1', '1').replace('2', '2')
    if author_key in AUTHORS:
        return AUTHORS[author_key]
    return 'The LORD'


def parse_book(filepath):
    """Parse a SGSS book file and return structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Clean lines
    lines = [l.rstrip('\n').rstrip('\r') for l in lines]
    
    book_title = lines[0].strip() if lines else ''
    
    chapters = []
    current_verses = []
    current_chapter_num = 0
    seen_first_chapter = False
    
    verse_pattern = re.compile(r'^(\d+)\s+(.*)')
    
    for line in lines[1:]:
        stripped = line.rstrip()
        
        # Check for chapter header
        chapter_match = re.match(r'^Chapter\s+(\d+)$', stripped)
        if chapter_match:
            # Save previous chapter
            if seen_first_chapter:
                chapters.append({
                    'num': current_chapter_num,
                    'verses': current_verses
                })
            seen_first_chapter = True
            current_chapter_num = int(chapter_match.group(1))
            current_verses = []
            continue
        
        # Check for verse start
        verse_match = verse_pattern.match(stripped)
        if verse_match:
            verse_num = int(verse_match.group(1))
            verse_text = verse_match.group(2).strip()
            current_verses.append(verse_text)
        else:
            # Continuation of previous verse - append to last verse
            if current_verses:
                current_verses[-1] += ' ' + stripped.strip()
    
    # Save last chapter
    if seen_first_chapter and current_verses:
        chapters.append({
            'num': current_chapter_num,
            'verses': current_verses
        })
    
    return book_title, chapters


def split_chapter(chapter, max_verses=30):
    """Split a chapter into parts if it has more than max_verses verses."""
    verses = chapter['verses']
    total = len(verses)
    
    if total <= max_verses:
        return [(chapter['num'], 1, total, verses)]
    
    # Calculate how many parts - aim for 25-30 verses per part
    num_parts = math.ceil(total / 27)  # try for ~27 verses per part
    verses_per_part = math.ceil(total / num_parts)
    
    parts = []
    for i in range(num_parts):
        start = i * verses_per_part
        end = min(start + verses_per_part, total)
        if start >= total:
            break
        part_verses = verses[start:end]
        parts.append((chapter['num'], start + 1, end, part_verses))
    
    return parts


def format_verse_text(verse_texts):
    """Join verse texts into a flowing paragraph, removing verse numbers."""
    # Clean up: replace double spaces, trim
    text = ' '.join(v.strip() for v in verse_texts if v.strip())
    # Clean up excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Clean quotes to smart quotes for readability
    return text


def format_song_entry(song_num, book_short, chapter_num, verse_start, verse_end, verses_text, author, total_verses=None):
    """Format one song entry."""
    if total_verses is None:
        total_verses = len(verses_text)
    
    # Build the reference string
    if verse_start == 1 and verse_end == total_verses:
        ref = f"{book_short} {chapter_num}"
    else:
        ref = f"{book_short} {chapter_num}:{verse_start}-{verse_end}"
    
    lyrics = format_verse_text(verses_text)
    
    entry = f"""Song {song_num}
Version 1.0
Date: 6/19/2026
Description: {ref}
Composed by: {author}
Written by: Walusimbi Leon
Created by: Not Yet

{ref}
{lyrics}
"""
    return entry


def slug_for_author(book_short_name):
    """Get author for a book."""
    key = book_short_name.replace(' ', '')
    if key in AUTHORS:
        return AUTHORS[key]
    return 'The LORD'


def main():
    song_counter = 0
    all_entries = []
    
    # Process files in order
    for i in range(1, 67):
        filename = f"{i:02d}-*.txt"
        import glob
        files = glob.glob(os.path.join(SGSS_DIR, f"{i:02d}-*.txt"))
        if not files:
            print(f"WARNING: No file for index {i}")
            continue
        
        filepath = files[0]
        basename = os.path.basename(filepath)
        book_short = BOOK_SHORT.get(basename, basename.replace('.txt', ''))
        author = get_author(book_short)
        
        print(f"Processing {book_short}...")
        book_title, chapters = parse_book(filepath)
        
        for chapter in chapters:
            parts = split_chapter(chapter)
            for ch_num, v_start, v_end, verses in parts:
                if not verses:
                    continue
                total_in_chapter = len(chapter['verses'])
                song_counter += 1
                entry = format_song_entry(
                    song_counter, book_short, ch_num, v_start, v_end, verses, author, total_in_chapter
                )
                all_entries.append(entry)
    
    # Write output
    header = """Songs of the SGSS Bible
Based on the Simplified God's Sacred Scriptures (SGSS) Translation
Generated: June 19, 2026

========================================
"""
    
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write('\n'.join(all_entries))
    
    print(f"\n{'='*60}")
    print(f"Done! {song_counter} songs written to {OUTPUT}")
    
    # Stats
    total_chars = sum(len(e) for e in all_entries) + len(header)
    print(f"Total size: {total_chars:,} characters")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
