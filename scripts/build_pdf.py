#!/usr/bin/env python3
"""Generate SGSS Bible Full PDF."""

import os, sys
import weasyprint

# Combine all book pages into one big HTML
all_books = sorted([f for f in os.listdir('sgss') if f.endswith('.txt')])

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SGSS Bible — Complete</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Georgia', 'Times New Roman', serif; background: #fff; color: #000; line-height: 1.6; font-size: 11pt; }
.container { max-width: 700px; margin: 0 auto; padding: 0.5in; }
.chapter { margin-bottom: 1.2em; page-break-inside: avoid; }
.chapter h2 { font-size: 14pt; color: #2c3e50; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; margin-bottom: 0.4em; }
.verse { margin-bottom: 0.3em; padding-left: 1.8em; text-indent: -1.8em; }
.vnum { font-weight: bold; color: #c0392b; font-size: 7pt; vertical-align: super; margin-right: 0.2em; }
h1.book-title { font-size: 18pt; text-align: center; color: #2c3e50; margin: 1.5em 0 0.8em 0; }
.title-page { text-align: center; padding-top: 3in; }
.title-page h1 { font-size: 28pt; margin-bottom: 0.3em; }
.title-page p { font-size: 14pt; font-style: italic; color: #555; }
.page-break { page-break-before: always; }
</style>
</head>
<body>
<div class="container">
<div class="title-page">
<h1>SGSS Bible</h1>
<p>Simplified God's Sacred Scriptures</p>
<p style="margin-top:1in;font-size:10pt;font-style:normal;">Based on the King James Version<br>Adapted into simple, clear English</p>
</div>
<div class="page-break"></div>
''')

for fname in all_books:
    with open(f'sgss/{fname}') as f:
        lines = f.readlines()
    
    title = lines[0].strip()
    html_parts.append(f'<h1 class="book-title">{title}</h1>\n')
    
    chap = None
    verses = {}
    
    for line in lines[1:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith('Chapter '):
            if chap is not None and verses:
                html_parts.append(f'<div class="chapter">\n<h2>Chapter {chap}</h2>\n')
                for v in sorted(verses.keys()):
                    html_parts.append(f'<p class="verse"><span class="vnum">{v}</span> {verses[v]}</p>\n')
                html_parts.append('</div>\n')
            chap = int(s.split()[1])
            verses = {}
        elif chap is not None:
            parts = s.split(' ', 1)
            if parts[0].isdigit():
                verses[int(parts[0])] = parts[1] if len(parts) > 1 else ''
            else:
                if verses:
                    last_v = max(verses.keys())
                    verses[last_v] += ' ' + s
    
    if chap is not None and verses:
        html_parts.append(f'<div class="chapter">\n<h2>Chapter {chap}</h2>\n')
        for v in sorted(verses.keys()):
            html_parts.append(f'<p class="verse"><span class="vnum">{v}</span> {verses[v]}</p>\n')
        html_parts.append('</div>\n')

html_parts.append('</div>\n</body>\n</html>')

full_html = '\n'.join(html_parts)

print(f"HTML size: {len(full_html) / 1024 / 1024:.1f} MB")

# Write temp HTML
tmp = '/tmp/sgss-bible-full.html'
with open(tmp, 'w', encoding='utf-8') as f:
    f.write(full_html)

# Generate PDF
print("Generating PDF with WeasyPrint...")
sys.stdout.flush()
weasyprint.HTML(filename=tmp).write_pdf('sgss-bible.pdf')
size = os.path.getsize('sgss-bible.pdf')
print(f"✓ sgss-bible.pdf ({size / 1024 / 1024:.1f} MB)")
os.remove(tmp)
print("Done!")
