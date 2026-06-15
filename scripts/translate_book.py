#!/usr/bin/env python3
"""
Translate any KJV book to SGSS (Simplified God's Sacred Scriptures) style.
Usage: python3 translate_book.py <book_number>
Example: python3 translate_book.py 02 (for Exodus)
"""

import re
import os
import sys
import json

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_kjv(path):
    """Load KJV text and parse into chapters with proper verse splitting."""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    title = lines[0].strip()
    
    content_lines = []
    in_header = True
    for line in lines[1:]:
        if in_header and line.strip() == '':
            continue
        in_header = False
        content_lines.append(line)
    
    raw = '\n'.join(content_lines)
    
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
    
    chapters = {}
    for line in normalized_lines:
        parts = re.split(r'(\d+):(\d+)\s*', line)
        if len(parts) < 3:
            continue
        i = 0
        while i < len(parts):
            if not re.match(r'^\d+$', parts[i]):
                i += 1
                continue
            if i + 2 >= len(parts):
                break
            ch = int(parts[i])
            vs = int(parts[i+1])
            text_part = parts[i+2].strip() if i+2 < len(parts) else ''
            chapters.setdefault(ch, {})[vs] = text_part
            i += 3
    
    return title, chapters


# ─── ARCHAIC WORD MAPS ───────────────────────────────────────────────────

# Known irregular forms (these override all rules)
_IRREGULAR_VERBS = {
    # -eth / -s irregulars
    'hath': 'has', 'doth': 'does', 'saith': 'says',
    # -est / modern irregulars  
    'didst': 'did', 'hadst': 'had', 'saidst': 'said', 'madest': 'made',
    'camest': 'came', 'gavest': 'gave', 'wast': 'were', 'wert': 'were',
    'wentest': 'went', 'spakest': 'spoke', 'knewest': 'knew',
    'sawest': 'saw', 'stoodest': 'stood', 'sleptest': 'slept',
    'foundest': 'found', 'brakest': 'broke', 'barest': 'bore',
    'tookest': 'took', 'spakest': 'spoke',
    'broughtest': 'brought', 'thoughtest': 'thought',
    'swarest': 'swore', 'leddest': 'led', 'leftest': 'left',
    'forgavest': 'forgave', 'rentest': 'rent', 'forsookest': 'forsook',
    'smotest': 'smote', 'sentest': 'sent', 'drewest': 'drew',
    'threwest': 'threw', 'wroughtest': 'wrought', 'withheldest': 'withheld',
    'heardest': 'heard', 'slewest': 'slew',
    # -st / -ll irregulars
    'wilt': 'will', 'shalt': 'shall', 'canst': 'can', 'wilt': 'will',
    'art': 'are', 'dost': 'do', 'doest': 'do', 'hast': 'have',
    'mightest': 'might', 'couldest': 'could', 'wouldest': 'would',
    'shouldest': 'should', 'mayest': 'may', 'durst': 'dared',
    'oughtest': 'ought', 'hadst': 'had',
    # -eth full irregulars
    'begetteth': 'becomes the father of', 'begettest': 'becomes the father of',
}

# Words that end in -eth or -est but are NOT archaic verb forms
_EXCLUDED_WORDS = {
    # People/places
    'japheth', 'mephibosheth', 'ishbosheth', 'elizabeth', 'azmaveth', 
    'bethazmaveth', 'benzoheth', 'hazarmaveth', 'hamoleketh', 'shallecheth',
    'tanhumeth', 'meshullemeth', 'zereth', 'zoheleth', 'zoheth', 'sibeth',
    'sibboeth', 'shibboleth', 'pibeseth', 'pochereth', 'topheth',
    'ashtoreth', 'kirharaseth', 'kirhareseth', 'harosheth', 'sophereth',
    'dabbasheth', 'chinnereth', 'remeth', 'sheth', 'peleth', 'tebeth',
    'alameth', 'aleneth', 'mispereth', 'jetheth', 'heth', 'seth', 'azeth',
    # Common nouns/adjectives
    'priest', 'behest', 'request', 'forest', 'harvest', 'protest',
    'tempest', 'interest', 'attest', 'digest', 'conquest', 'contest',
    'modest', 'honest', 'invest', 'infest', 'suggest', 'congest', 'ingest',
    'detest', 'molest', 'incest', 'bequest', 'manifest',
    # Superlatives
    'greatest', 'sweetest', 'earnest', 'fullest', 'latest', 'wisest',
    'boldest', 'mildest', 'kindest', 'tallest', 'oldest', 'youngest',
    'strongest', 'weakest', 'hardest', 'softest', 'fastest', 'slowest',
    'deepest', 'highest', 'lowest', 'nearest', 'fairest', 'holiest',
    'smallest', 'vilest', 'straitest', 'poorest', 'fattest', 'finest',
    'hottest', 'mightiest', 'choicest', 'goodliest', 'chiefest',
    'forthrightest', 'valiantest',
    # Other common words
    'best', 'nest', 'rest', 'test', 'guest', 'chest', 'crest', 'zest',
    'lest', 'pest', 'vest', 'west',
    'twelfth', 'twentieth', 'thirtieth', 'fortieth', 'fiftieth', 'sixtieth',
    'seventieth', 'eightieth', 'ninetieth', 'hundredth', 'thousandth',
    'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh',
}

def _add_s_to_stem(stem):
    """Apply modern English -s/-es rules to a verb stem."""
    if not stem:
        return stem
    if stem.lower().endswith(('s', 'z', 'sh', 'ch', 'x')):
        return stem + 'es'
    if stem.lower().endswith('o'):
        return stem + 'es'
    if stem.lower().endswith('y') and len(stem) > 1 and stem[-2].lower() not in 'aeiou':
        return stem[:-1] + 'ies'
    return stem + 's'

# Load valid English verb stems from word_base.json
_VERB_STEMS = set()
_wb_path = os.path.join(_SCRIPT_DIR, 'word_base.json')
if os.path.exists(_wb_path):
    try:
        with open(_wb_path, 'r') as f:
            _VERB_STEMS = set(json.load(f))
    except:
        pass

def _fix_eth_verb(word):
    """Convert -eth archaic to modern -s form."""
    lower = word.lower()
    
    # Check irregulars
    if lower in _IRREGULAR_VERBS:
        r = _IRREGULAR_VERBS[lower]
        return r[0].upper() + r[1:] if word[0].isupper() else r
    
    # Check exclusions
    if lower in _EXCLUDED_WORDS:
        return word
    
    # Must end in 'eth' 
    if not lower.endswith('eth') or len(word) <= 3:
        return word
    
    stem = word[:-3]  # Remove 'eth'
    stem_lower = stem.lower()
    
    # Try stem directly (for verbs like leadeth -> lead + s -> leads)
    if stem_lower in _VERB_STEMS:
        result = _add_s_to_stem(stem)
    else:
        # Try stem + 'e' (for verbs like loveth -> love + s -> loves)
        stem_with_e = stem + 'e'
        if stem_with_e.lower() in _VERB_STEMS:
            result = _add_s_to_stem(stem_with_e)
        else:
            # Try y -> i pattern (envieth -> envi -> envy -> envies)
            if stem_lower.endswith('i') and len(stem) > 1:
                stem_with_y = stem[:-1] + 'y'
                if stem_with_y.lower() in _VERB_STEMS:
                    result = _add_s_to_stem(stem_with_y)
                    if word[0].isupper():
                        return result[0].upper() + result[1:]
                    return result
            # Last resort: just add s
            result = _add_s_to_stem(stem)
    
    if word[0].isupper():
        return result[0].upper() + result[1:]
    return result

def _fix_est_verb(word):
    """Convert -est archaic to modern form."""
    lower = word.lower()
    
    if lower in _IRREGULAR_VERBS:
        r = _IRREGULAR_VERBS[lower]
        return r[0].upper() + r[1:] if word[0].isupper() else r
    
    if lower in _EXCLUDED_WORDS:
        return word
    
    if not lower.endswith('est') or len(word) <= 4:
        return word
    
    stem = word[:-3]  # Remove 'est'
    stem_lower = stem.lower()
    
    # Try stem directly
    if stem_lower in _VERB_STEMS:
        result = stem
    else:
        # Try stem + 'e'
        stem_with_e = stem + 'e'
        if stem_with_e.lower() in _VERB_STEMS:
            result = stem_with_e
        else:
            # Handle -st forms: thous didst -> thou did
            if lower.endswith('st') and not lower.endswith('est'):
                result = word[:-2] if len(word) > 3 else word
            else:
                result = stem
    
    if word[0].isupper():
        return result[0].upper() + result[1:]
    return result

_ARCHAIC_PATTERN = re.compile(r'\b[a-zA-Z]+(?:eth|est)\b')


# ─── TRANSLATION RULES ───────────────────────────────────────────────────

PRONOUN_RULES = [
    (r'\bthou art\b', 'you are'), (r'\bthou hast\b', 'you have'),
    (r'\bthou shalt\b', 'you shall'), (r'\bthou didst\b', 'you did'),
    (r'\bthou wilt\b', 'you will'), (r'\bthou mayest\b', 'you may'),
    (r'\bthou canst\b', 'you can'), (r'\bthou couldest\b', 'you could'),
    (r'\bthou shouldest\b', 'you should'),
    (r'\bthou\b', 'you'), (r'\bthee\b', 'you'),
    (r'\bthy\b', 'your'), (r'\bthine\b', 'your'), (r'\bye\b', 'you'),
]

ARCHAIC_VERB_MAP = {
    'didst': 'did', 'hadst': 'had', 'madest': 'made',
    'camest': 'came', 'wentest': 'went', 'gavest': 'gave',
    'calledst': 'called', 'takest': 'take', 'atest': 'ate',
    'spakest': 'spoke', 'barest': 'bore', 'knewest': 'knew',
    'sleptest': 'slept', 'stoodest': 'stood', 'foundest': 'found',
    'saidst': 'said', 'sawest': 'saw', 'eatest': 'eat',
    'wast': 'were', 'shalt': 'shall', 'wilt': 'will',
    'durst': 'dared', 'canst': 'can', 'couldst': 'could',
    'wouldst': 'would', 'shouldst': 'should', 'mightst': 'might',
    'dost': 'do', 'doest': 'do', 'hast': 'have', 'art': 'are',
    'doth': 'does', 'hath': 'has', 'saith': 'says',
    'knoweth': 'knows', 'moveth': 'moves', 'giveth': 'gives',
    'liveth': 'lives', 'creepeth': 'creeps', 'yieldeth': 'yields',
    'bringeth': 'brings', 'doeth': 'does', 'sheddeth': 'sheds',
    'goeth': 'goes', 'cometh': 'comes', 'seeth': 'sees',
    'heareth': 'hears', 'taketh': 'takes', 'maketh': 'makes',
    'sheweth': 'shows', 'shew': 'show', 'remaineth': 'remains',
    'fleeth': 'flees', 'crieth': 'cries', 'laugheth': 'laughs',
    'dealeth': 'deals', 'weepeth': 'weeps', 'weareth': 'wears',
    'raiseth': 'raises', 'worketh': 'works', 'drinketh': 'drinks',
    'eateth': 'eats', 'getteth': 'gets', 'findeth': 'finds',
    'appointeth': 'appoints', 'compasseth': 'goes around',
    'blesseth': 'blesses', 'killeth': 'kills', 'loveth': 'loves',
    'hateth': 'hates', 'lovest': 'love', 'goest': 'go',
    'comest': 'come', 'knowest': 'know', 'seest': 'see',
    'findest': 'find', 'meanest': 'mean',
    'fearest': 'fear', 'seekest': 'seek', 'liest': 'lie',
    'badest': 'commanded', 'fleddest': 'fled', 'defiledst': 'defiled',
    'vowedst': 'vowed', 'begettest': 'becomes the father of',
    'layeth': 'lays', 'runneth': 'runs', 'speaketh': 'speaks',
    'aileth': 'troubles', 'asketh': 'asks', 'biteth': 'bites',
    'breaketh': 'breaks', 'divineth': 'divines', 'faileth': 'fails',
    'lieth': 'lies', 'longeth': 'longs', 'meeteth': 'meets',
    'needeth': 'needs', 'pleaseth': 'pleases', 'proceedeth': 'proceeds',
    'repenteth': 'repents', 'toucheth': 'touches', 'walketh': 'walks',
    'shouldest': 'should', 'standeth': 'stands', 'sitteth': 'sits',
    'holdeth': 'holds', 'curseth': 'curses',
    'shewed': 'showed', 'shewedst': 'showed',
    'whoso': 'whoever', 'anointedst': 'anointed', 'thyself': 'yourself',
    'leadeth': 'leads', 'suffereth': 'suffers', 'profiteth': 'profits',
    'restoreth': 'restores', 'prepareth': 'prepares',
    'doeth': 'does', 'cometh': 'comes',
    'prayeth': 'prays', 'layeth': 'lays',
}

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
    (r'\btarry\b', 'stay'), (r'\btarried\b', 'stayed'),
    (r'\bdwelled?\b', 'lived'), (r'\bdwelt\b', 'lived'),
    (r'\bdwell\b', 'live'), (r'\bdwelling\b', 'living'),
    (r'\bwot\b', 'know'), (r'\bwotteth\b', 'knows'), (r'\bwist\b', 'knew'),
    (r'\blift\b', 'lifted'), (r'\bclave\b', 'held fast'),
    (r'\bcleave\b', 'hold fast'),
    (r'\bbuilded\b', 'built'), (r'\bsware\b', 'swore'),
    (r'\bsod\b', 'cooked'), (r'\bgat\b', 'went'),
    (r'\bstraitly\b', 'strictly'), (r'\bholpen\b', 'helped'),
    (r'\bchode\b', 'argued'), (r'\bchiding\b', 'arguing'),
    (r'\bminished\b', 'diminished'), (r'\bseethed?\b', 'cooked'),
    (r'\bsprent\b', 'sprinkled'),
    (r'\bburyingplace\b', 'burial place'), (r'\bmess\b', 'portion'),
    (r'\bbegun\b', 'began'), (r'\bcoasts\b', 'regions'),
    (r'\bvisage\b', 'face'), (r'\braiment\b', 'clothing'),
    (r'\bharlot\b', 'prostitute'), (r'\ban prostitute\b', 'a prostitute'),
    (r'\bwhoredom\b', 'prostitution'), (r'\bwhelp\b', 'cub'),
    (r'\bnoisome\b', 'harmful'), (r'\bconcupiscence\b', 'lust'),
    (r'\bconey\b', 'rabbit'), (r'\bchapmen\b', 'traders'),
    (r'\bresorted\b', 'went'), (r'\bstuff\b', 'goods'),
    (r'\bswaddling\b', 'wrapping'), (r'\bbeguiled?\b', 'deceived'),
    (r'\bslayeth\b', 'kills'), (r'\bslain\b', 'killed'),
    (r'\bslew\b', 'killed'), (r'\bslay\b', 'kill'),
    (r'\bforgat\b', 'forgot'),
    (r'\bwhereof\b', 'of which'), (r'\bwherewith\b', 'with which'),
    (r'\bstandest\b', 'stand'), (r'\bwouldest\b', 'would'),
    (r'\blongedst\b', 'longed'),
    (r'\bwhither\b', 'where'), (r'\bthence\b', 'there'),
    (r'\bhindermost\b', 'hindmost'), (r'\bwhence\b', 'where'),
    (r'\bhither\b', 'here'), (r'\bthither\b', 'there'),
    (r'\bhenceforth\b', 'from now on'), (r'\bhitherto\b', 'until now'),
    (r'\btillest\b', 'till'),
    (r'\ban harlot\b', 'a prostitute'), (r'\ban handmaid\b', 'a servant girl'),
    (r'\ban husbandman\b', 'a farmer'),
    (r'\bfourscore\b', 'eighty'), (r'\bthreescore\b', 'sixty'),
    (r'\bthe which\b', 'which'), (r'\bin the which\b', 'in which'),
    (r'\bto the which\b', 'to which'), (r'\bof the which\b', 'of which'),
    (r'\bhowbeit\b', 'however'), (r'\bholden\b', 'held'),
    (r'\bmought\b', 'might'), (r'\bought\b', 'owed'),
    (r'\bputrifying\b', 'decaying'),
    (r'\bhiding\b', 'covering'), (r'\bmenstruous\b', 'unclean'),
]

PHRASE_RULES = [
    (r'I pray thee', 'please'), (r'I pray you', 'please'),
    (r'I beseech thee', 'please'), (r'I beseech you', 'please'),
]

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
    
    # Apply archaic verb map
    for old_word, new_word in ARCHAIC_VERB_MAP.items():
        result = re.sub(r'\b' + re.escape(old_word) + r'\b', new_word, result, flags=re.IGNORECASE)
    
    # Apply old word rules
    for pattern, replacement in OLD_WORD_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Apply pronoun rules
    for pattern, replacement in PRONOUN_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Catch-all: convert remaining archaic -eth -> -s, -est -> modern
    result = _ARCHAIC_PATTERN.sub(lambda m: _fix_eth_verb(m.group(0)) 
                                  if m.group(0).lower().endswith('eth') 
                                  else _fix_est_verb(m.group(0)), result)
    
    # Process editorial brackets from KJV
    result = re.sub(r'\{([a-zA-Z]+)\}', r'\1', result)
    result = re.sub(r'\{[^}]*\}', '', result)
    
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
    result = re.sub(r'\bgave birth to to\b', 'gave birth to', result, flags=re.IGNORECASE)
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
        best_break = -1
        for punct in ['. ', '? ', '! ']:
            idx = remaining.rfind(punct, max(0, cutoff - 30), cutoff + 10)
            if idx > best_break:
                best_break = idx + 2
        if best_break <= 0:
            idx = remaining.rfind('; ', max(0, cutoff - 30), cutoff + 10)
            if idx > 0: best_break = idx + 2
        if best_break <= 0:
            idx = remaining.rfind(', ', max(0, cutoff - 30), cutoff + 10)
            if idx > 0: best_break = idx + 2
        if best_break <= 0:
            idx = remaining.rfind(' ', max(0, cutoff - 20), cutoff + 10)
            if idx > 0: best_break = idx + 1
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
    if len(sys.argv) < 2:
        print("Usage: python3 translate_book.py <book_number>")
        print("Example: python3 translate_book.py 02 (for Exodus)")
        sys.exit(1)
    
    book_num = sys.argv[1]
    kjv_dir = '/tmp/sgss-bible/kjv'
    sgss_dir = '/tmp/sgss-bible/sgss'
    
    import glob
    files = sorted(glob.glob(os.path.join(kjv_dir, f'{book_num}-*.txt')))
    if not files:
        files = sorted(glob.glob(os.path.join(kjv_dir, f'{book_num}*.txt')))
    if not files:
        print(f"Error: No KJV file found for book number {book_num}")
        sys.exit(1)
    
    input_path = files[0]
    basename = os.path.basename(input_path)
    output_path = os.path.join(sgss_dir, basename)
    
    print(f"Loading: {input_path}")
    title, chapters = load_kjv(input_path)
    print(f"Title: {title}")
    print(f"Loaded {len(chapters)} chapters, {sum(len(v) for v in chapters.values())} verses")
    
    os.makedirs(sgss_dir, exist_ok=True)
    output_lines = [title, '']
    
    for chapter_num in sorted(chapters.keys()):
        print(f"  Translating Chapter {chapter_num}...")
        chapter_text = translate_chapter(chapter_num, chapters[chapter_num])
        output_lines.append(chapter_text)
        output_lines.append('')
    
    while output_lines and output_lines[-1] == '':
        output_lines.pop()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    print(f"✓ Translation saved to {output_path}")

if __name__ == '__main__':
    main()
