#!/usr/bin/env python3
"""
Translate KJV Genesis to SGSS (Simplified God's Sacred Scriptures) style.
"""

import re
import os

def load_kjv(path):
    """Load KJV text and parse into chapters with proper verse splitting."""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Remove the title line and its following blank line
    lines = text.split('\n')
    if lines[0].startswith('The First Book'):
        lines = lines[2:]
    
    raw = '\n'.join(lines)
    
    # Step 1: Join continuation lines (lines without verse markers)
    normalized_lines = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+:\d+\s', line) or re.match(r'^\d+:\d+$', line):
            normalized_lines.append(line)
        else:
            if normalized_lines:
                normalized_lines[-1] = normalized_lines[-1] + ' ' + line
            else:
                normalized_lines.append(line)
    
    # Step 2: Split each line by verse markers
    chapters = {}
    
    for line in normalized_lines:
        # Split on verse markers like "1:14" or " 1:15 "
        # re.split captures the delimiter parts
        parts = re.split(r'(\d+):(\d+)\s*', line)
        
        if len(parts) < 3:
            continue
        
        i = 0
        while i < len(parts):
            # Skip text before any verse marker
            if not re.match(r'^\d+$', parts[i]):
                i += 1
                continue
            
            if i + 2 >= len(parts):
                break
            
            ch = int(parts[i])
            vs = int(parts[i+1])
            text = parts[i+2].strip() if i+2 < len(parts) else ''
            
            chapters.setdefault(ch, {})[vs] = text
            i += 3
    
    return chapters


# === TRANSLATION RULES ===

# Archaic pronoun replacements (longer patterns first)
PRONOUN_RULES = [
    (r'\bthou art\b', 'you are'),
    (r'\bthou hast\b', 'you have'),
    (r'\bthou shalt\b', 'you shall'),
    (r'\bthou didst\b', 'you did'),
    (r'\bthou wilt\b', 'you will'),
    (r'\bthou mayest\b', 'you may'),
    (r'\bthou canst\b', 'you can'),
    (r'\bthou couldest\b', 'you could'),
    (r'\bthou shouldest\b', 'you should'),
    (r'\bthou\b', 'you'),
    (r'\bthee\b', 'you'),
    (r'\bthy\b', 'your'),
    (r'\bthine\b', 'your'),
    (r'\bye\b', 'you'),
]

# Archaic verb forms (whitelist only - no broad pattern matching)
ARCHAIC_VERB_MAP = {
    # -est verbs
    'didst': 'did', 'hadst': 'had', 'madest': 'made',
    'camest': 'came', 'wentest': 'went', 'gavest': 'gave',
    'calledst': 'called', 'takest': 'take', 'atest': 'ate',
    'spakest': 'spoke', 'barest': 'bore', 'knewest': 'knew',
    'sleptest': 'slept', 'stoodest': 'stood', 'foundest': 'found',
    'saidst': 'said', 'sawest': 'saw', 'eatest': 'eat',
    # -st verbs
    'wast': 'were', 'shalt': 'shall', 'wilt': 'will',
    'durst': 'dared', 'canst': 'can', 'couldst': 'could',
    'wouldst': 'would', 'shouldst': 'should', 'mightst': 'might',
    'dost': 'do',
    'doest': 'do',
    'hast': 'have',
    'art': 'are',
    # -eth verbs
    'doth': 'does', 'hath': 'has', 'saith': 'says',
    'knoweth': 'knows', 'moveth': 'moves', 'giveth': 'gives',
    'liveth': 'lives', 'creepeth': 'creeps', 'yieldeth': 'yields',
    'bringeth': 'brings', 'doeth': 'does', 'sheddeth': 'sheds',
    'goeth': 'goes', 'cometh': 'comes', 'seeth': 'sees',
    'heareth': 'hears', 'taketh': 'takes', 'maketh': 'makes',
    'sheweth': 'shows', 'shew': 'show', 'remaineth': 'remains', 'fleeth': 'flees',
    'crieth': 'cries', 'laugheth': 'laughs', 'dealeth': 'deals',
    'weepeth': 'weeps', 'weareth': 'wears', 'raiseth': 'raises',
    'worketh': 'works', 'drinketh': 'drinks', 'eateth': 'eats',
    'getteth': 'gets', 'findeth': 'finds', 'appointeth': 'appoints',
    'compasseth': 'goes around', 'blesseth': 'blesses',
    'killeth': 'kills', 'loveth': 'loves', 'hateth': 'hates',
    'lovest': 'love', 'goest': 'go', 'comest': 'come', 'knowest': 'know',
    'seest': 'see', 'findest': 'find', 'meanest': 'mean',
    'fearest': 'fear', 'seekest': 'seek', 'liest': 'lie',
    'badest': 'commanded', 'fleddest': 'fled', 'defiledst': 'defiled',
    'vowedst': 'vowed', 'begettest': 'becomes the father of',
    'layeth': 'lays', 'runneth': 'runs', 'speaketh': 'speaks',
    'aileth': 'troubles', 'asketh': 'asks', 'biteth': 'bites',
    'breaketh': 'breaks', 'divineth': 'divines', 'faileth': 'fails',
    'lieth': 'lies', 'longeth': 'longs for', 'meeteth': 'meets',
    'needeth': 'needs', 'pleaseth': 'pleases', 'proceedeth': 'proceeds',
    'repenteth': 'repents', 'toucheth': 'touches', 'walketh': 'walks',
    'shouldest': 'should',
    'standeth': 'stands', 'sitteth': 'sits', 'holdeth': 'holds',
    'curseth': 'curses',
    'shewed': 'showed', 'shalt': 'shall',
    'shewedst': 'showed',
    # whoso
    'whoso': 'whoever',
    'anointedst': 'anointed',
    'thyself': 'yourself',
}

# Old word replacements
OLD_WORD_RULES = [
    (r'\bspake\b', 'spoke'),
    (r'\bbegat\b', 'became the father of'),
    (r'\bbare\b', 'gave birth to'),
    (r'\bwroth\b', 'angry'),
    (r'\bsubtil\b', 'cunning'),
    (r'\bsubtilty\b', 'cunning'),
    (r'\basswaged?\b', 'went down'),
    (r'\bslime\b', 'bitumen'),
    (r'\bbewrayeth\b', 'reveals'),
    (r'\bprivily\b', 'secretly'),
    (r'\bperadventure\b', 'perhaps'),
    (r'\btarry\b', 'stay'),
    (r'\btarried\b', 'stayed'),
    (r'\bdwelled?\b', 'lived'),
    (r'\bdwelt\b', 'lived'),
    (r'\bdwell\b', 'live'),
    (r'\bdwelling\b', 'living'),
    (r'\bwot\b', 'know'),
    (r'\bwotteth\b', 'knows'),
    (r'\bwist\b', 'knew'),
    (r'\blift\b', 'lifted'),
    (r'\bclave\b', 'held fast'),
    (r'\bcleave\b', 'hold fast'),
    (r'\bbuilded\b', 'built'),
    (r'\bsware\b', 'swore'),
    (r'\bsod\b', 'cooked'),
    (r'\bgat\b', 'went'),
    (r'\bstraitly\b', 'strictly'),
    (r'\bholpen\b', 'helped'),
    (r'\bchode\b', 'argued'),
    (r'\bchiding\b', 'arguing'),
    (r'\bminished\b', 'diminished'),
    (r'\bseethed?\b', 'cooked'),
    (r'\bsprent\b', 'sprinkled'),
    (r'\bshewed\b', 'showed'),
    (r'\bburyingplace\b', 'burial place'),
    (r'\bmess\b', 'portion'),
    (r'\bbegun\b', 'began'),
    (r'\bcoasts\b', 'regions'),
    (r'\bvisage\b', 'face'),
    (r'\braiment\b', 'clothing'),
    (r'\bharlot\b', 'prostitute'),
    (r'\ban prostitute\b', 'a prostitute'),
    (r'\bwhoredom\b', 'prostitution'),
    (r'\bwhelp\b', 'cub'),
    (r'\bnoisome\b', 'harmful'),
    (r'\bconcupiscence\b', 'lust'),
    (r'\bconey\b', 'rabbit'),
    (r'\bchapmen\b', 'traders'),
    (r'\bresorted\b', 'went'),
    (r'\bstuff\b', 'goods'),
    (r'\bswaddling\b', 'wrapping'),
    (r'\bbeguiled?\b', 'deceived'),
    (r'\bslayeth\b', 'kills'),
    (r'\bslain\b', 'killed'),
    (r'\bslew\b', 'killed'),
    (r'\bslay\b', 'kill'),
    (r'\bforgat\b', 'forgot'),
    (r'\bwhereof\b', 'of which'),
    (r'\bwherewith\b', 'with which'),
    (r'\bstandest\b', 'stand'),
    (r'\bwouldest\b', 'would'),
    (r'\blongedst\b', 'longed'),
    (r'\bwhither\b', 'where'),
    (r'\bthence\b', 'there'),
    (r'\bhindermost\b', 'hindmost'),
    (r'\bwhence\b', 'where'),
    (r'\bhither\b', 'here'),
    (r'\bthither\b', 'there'),
    (r'\bhenceforth\b', 'from now on'),
    (r'\bhitherto\b', 'until now'),
    (r'\btillest\b', 'till'),
    (r'\ban harlot\b', 'a prostitute'),
    (r'\ban handmaid\b', 'a servant girl'),
    (r'\ban husbandman\b', 'a farmer'),
    # Numbers
    (r'\bfourscore\b', 'eighty'),
    (r'\bthreescore\b', 'sixty'),
]

# Phrase-level replacements (applied before individual words)
PHRASE_RULES = [
    (r'I pray thee', 'please'),
    (r'I pray you', 'please'),
    (r'I beseech thee', 'please'),
]

# "It came to pass" removal patterns
CTP_PATTERNS = [
    (r'And it came to pass after these things,?\s*(that\s+)?', 'After these things, '),
    (r'And it came to pass at that time,?\s*', 'At that time, '),
    (r'And it came to pass that,?\s*', ''),
    (r'And it came to pass,?\s+when\s+', 'When '),
    (r'And it came to pass,?\s+in\s+', 'In '),
    (r'And it came to pass,?\s+after\s+', 'After '),
    (r'And it came to pass,?\s+as\s+', 'As '),
    (r'And it came to pass,?\s+on\s+', 'On '),
    (r'And it came to pass,?\s+about\s+', 'About '),
    (r'And it came to pass,?\s+before\s+', 'Before '),
    (r'And it came to pass,?\s*', ''),
    (r'it came to pass that,?\s*', ''),
    (r'it came to pass,?\s*', ''),
    (r',\s*and it came to pass,?\s*', ', '),
]


def translate_text(text):
    """Apply SGSS translations to verse text."""
    result = text
    
    # Handle "it came to pass" first
    for pattern, replacement in CTP_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Apply phrase replacements
    for pattern, replacement in PHRASE_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Apply archaic verb map (word-by-word, boundary-safe)
    for old_word, new_word in ARCHAIC_VERB_MAP.items():
        result = re.sub(r'\b' + re.escape(old_word) + r'\b', new_word, result, flags=re.IGNORECASE)
    
    # Apply old word rules
    for pattern, replacement in OLD_WORD_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Apply pronoun rules (after other replacements so "thou" etc. are caught)
    for pattern, replacement in PRONOUN_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Clean up artifacts
    result = re.sub(r' +', ' ', result)
    result = re.sub(r'\s+,', ',', result)
    result = re.sub(r'\s+\.', '.', result)
    result = re.sub(r',\s*,', ',', result)
    result = re.sub(r'\.\s*\.', '.', result)
    result = re.sub(r'\s+;', ';', result)
    result = re.sub(r';\s*;', ';', result)
    result = re.sub(r'\s+:', ':', result)
    result = re.sub(r'\s+\?', '?', result)
    result = re.sub(r'"\s+', '"', result)
    result = re.sub(r'\s+"', '"', result)
    # Fix double words from replacements
    result = re.sub(r'\bgave birth to to\b', 'gave birth to', result, flags=re.IGNORECASE)
    result = re.sub(r'\bto the\b to\b', 'to the', result)
    result = result.strip()
    
    return result


def handle_sentence_start(text):
    """Remove leading 'And ' to vary sentence openings."""
    if not text:
        return text
    while text.startswith('And ') or text.startswith('and '):
        text = text[4:].strip()
    return text


def capitalize_first(text):
    """Ensure first letter is capitalized."""
    if not text:
        return text
    return text[0].upper() + text[1:]


def wrap_verse(verse_line, max_width=85):
    """Wrap a long verse line for readability."""
    if len(verse_line) <= max_width:
        return verse_line
    
    wrapped = []
    remaining = verse_line
    
    while remaining:
        if len(remaining) <= max_width:
            wrapped.append(remaining)
            break
        
        cutoff = max_width - 5
        
        # Try to break at sentence end
        best_break = -1
        for punct in ['. ', '? ', '! ']:
            idx = remaining.rfind(punct, max(0, cutoff - 30), cutoff + 10)
            if idx > best_break:
                best_break = idx + 2
        
        if best_break <= 0:
            idx = remaining.rfind('; ', max(0, cutoff - 30), cutoff + 10)
            if idx > 0:
                best_break = idx + 2
        
        if best_break <= 0:
            idx = remaining.rfind(', ', max(0, cutoff - 30), cutoff + 10)
            if idx > 0:
                best_break = idx + 2
        
        if best_break <= 0:
            idx = remaining.rfind(' ', max(0, cutoff - 20), cutoff + 10)
            if idx > 0:
                best_break = idx + 1
        
        if best_break <= 0:
            best_break = min(cutoff, len(remaining))
        
        wrapped.append(remaining[:best_break].rstrip())
        remaining = remaining[best_break:].strip()
    
    return '\n'.join(wrapped)


def translate_chapter(chapter_num, verses):
    """Translate a single chapter."""
    output_parts = []
    
    output_parts.append(f'Chapter {chapter_num}')
    output_parts.append('')
    
    for verse_num in sorted(verses.keys()):
        text = verses[verse_num].strip()
        if not text:
            output_parts.append(f'{verse_num}')
            continue
        
        translated = translate_text(text)
        translated = handle_sentence_start(translated)
        translated = capitalize_first(translated)
        
        verse_line = f'{verse_num} {translated}'
        output_parts.append(wrap_verse(verse_line))
    
    return '\n'.join(output_parts)


def main():
    input_path = '/tmp/sgss-bible/kjv/01-Genesis.txt'
    output_dir = '/tmp/sgss-bible/sgss'
    output_path = os.path.join(output_dir, '01-Genesis.txt')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading KJV text...")
    chapters = load_kjv(input_path)
    print(f"Loaded {len(chapters)} chapters.")
    for ch in sorted(chapters.keys()):
        print(f"  Chapter {ch}: {len(chapters[ch])} verses")
    
    output_lines = ['The First Book of Moses: Called Genesis', '']
    
    for chapter_num in sorted(chapters.keys()):
        print(f"Translating Chapter {chapter_num}...")
        chapter_text = translate_chapter(chapter_num, chapters[chapter_num])
        output_lines.append(chapter_text)
        output_lines.append('')
    
    # Remove trailing blank lines
    while output_lines and output_lines[-1] == '':
        output_lines.pop()
    
    final_text = '\n'.join(output_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"Translation complete. Output written to {output_path}")
    
    total_verses = sum(len(v) for v in chapters.values())
    print(f"Total chapters: {len(chapters)}, Total verses: ~{total_verses}")


if __name__ == '__main__':
    main()
