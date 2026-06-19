#!/usr/bin/env python3
"""Build SGSS Bible website + PDF for GitHub Pages."""

import os, re, json

SGSS_DIR = "sgss"
BOOKS_DIR = "books"
PDF_DIR = "."
INDEX_FILE = "index.html"
STYLE_FILE = "styles.css"

BOOK_ORDER = [
    # Old Testament
    "01-Genesis", "02-Exodus", "03-Leviticus", "04-Numbers", "05-Deuteronomy",
    "06-Joshua", "07-Judges", "08-Ruth", "09-1Samuel", "10-2Samuel",
    "11-1Kings", "12-2Kings", "13-1Chronicles", "14-2Chronicles", "15-Ezra",
    "16-Nehemiah", "17-Esther", "18-Job", "19-Psalms", "20-Proverbs",
    "21-Ecclesiastes", "22-SongOfSolomon", "23-Isaiah", "24-Jeremiah",
    "25-Lamentations", "26-Ezekiel", "27-Daniel", "28-Hosea", "29-Joel",
    "30-Amos", "31-Obadiah", "32-Jonah", "33-Micah", "34-Nahum",
    "35-Habakkuk", "36-Zephaniah", "37-Haggai", "38-Zechariah", "39-Malachi",
    # New Testament
    "40-Matthew", "41-Mark", "42-Luke", "43-John", "44-Acts",
    "45-Romans", "46-1Corinthians", "47-2Corinthians", "48-Galatians",
    "49-Ephesians", "50-Philippians", "51-Colossians", "52-1Thessalonians",
    "53-2Thessalonians", "54-1Timothy", "55-2Timothy", "56-Titus",
    "57-Philemon", "58-Hebrews", "59-James", "60-1Peter", "61-2Peter",
    "62-1John", "63-2John", "64-3John", "65-Jude", "66-Revelation"
]

def parse_book(filepath):
    """Parse an SGSS book file into structured data."""
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    
    title = lines[0].strip()
    chapters = {}
    current_chap = None
    chapter_verses = {}
    
    for line in lines[1:]:
        raw = line.rstrip('\n')
        line_stripped = raw.strip()
        if not line_stripped:
            continue
        if line_stripped.startswith('Chapter '):
            if current_chap is not None:
                chapters[current_chap] = chapter_verses
            current_chap = int(line_stripped.split()[1])
            chapter_verses = {}
        elif current_chap is not None:
            parts = line_stripped.split(' ', 1)
            if parts[0].isdigit():
                chapter_verses[int(parts[0])] = parts[1] if len(parts) > 1 else ''
            else:
                # continuation - append to last verse
                if chapter_verses:
                    last_v = max(chapter_verses.keys())
                    chapter_verses[last_v] += ' ' + line_stripped
    
    if current_chap is not None:
        chapters[current_chap] = chapter_verses
    
    return title, chapters


def get_short_name(name):
    """Extract short book name from filename."""
    return name[3:]  # Remove "01-", "40-", etc.


def render_chapter_html(chapter_num, verses):
    """Render a chapter as HTML."""
    html = f'<div class="chapter">\n<h2>Chapter {chapter_num}</h2>\n'
    for v in sorted(verses.keys()):
        text = verses[v]
        html += f'<p class="verse"><span class="vnum">{v}</span> {text}</p>\n'
    html += '</div>\n'
    return html


def render_nav(current_idx, all_books):
    """Render prev/next/home navigation."""
    prev_link = ''
    next_link = ''
    if current_idx > 0:
        prev_book = all_books[current_idx - 1]
        prev_link = f'<a href="{prev_book}.html" class="nav-btn">← {get_short_name(prev_book)}</a>'
    if current_idx < len(all_books) - 1:
        next_book = all_books[current_idx + 1]
        next_link = f'<a href="{next_book}.html" class="nav-btn">{get_short_name(next_book)} →</a>'
    
    return f'''
    <nav class="book-nav">
        {prev_link}
        <a href="index.html" class="nav-btn home-btn">📖 Home</a>
        {next_link}
    </nav>'''


STYLES_CSS = '''/* SGSS Bible - Global Styles */
:root {
    --primary: #2c3e50;
    --accent: #c0392b;
    --gold: #d4a017;
    --bg: #faf8f5;
    --card-bg: #ffffff;
    --text: #1a1a1a;
    --text-light: #555;
    --border: #e0d8cc;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
}

/* Header */
.site-header {
    background: linear-gradient(135deg, var(--primary), #34495e);
    color: #fff;
    text-align: center;
    padding: 2.5rem 1rem;
    border-bottom: 4px solid var(--gold);
}
.site-header h1 { font-size: 2rem; margin-bottom: 0.3rem; }
.site-header h1 a { color: #fff; text-decoration: none; }
.site-header .subtitle { font-size: 1rem; opacity: 0.85; font-style: italic; }

/* Main container */
.container {
    max-width: 960px;
    margin: 0 auto;
    padding: 1.5rem;
}

/* Book list */
.testament-section { margin: 2rem 0; }
.testament-section h2 {
    font-size: 1.4rem;
    color: var(--primary);
    border-bottom: 2px solid var(--gold);
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}
.book-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 0.6rem;
}
.book-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.7rem 1rem;
    text-decoration: none;
    color: var(--text);
    transition: all 0.2s;
    display: block;
    font-size: 0.95rem;
}
.book-card:hover {
    border-color: var(--gold);
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}
.book-card .bnum {
    color: var(--accent);
    font-weight: bold;
    font-size: 0.8rem;
    margin-right: 0.3rem;
}

/* Download section */
.download-section {
    background: var(--card-bg);
    border: 2px solid var(--gold);
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    margin: 1.5rem 0;
}
.download-section h2 { margin-bottom: 0.5rem; color: var(--primary); }
.download-btn {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    padding: 0.8rem 2rem;
    border-radius: 6px;
    text-decoration: none;
    font-size: 1.1rem;
    transition: background 0.2s;
}
.download-btn:hover { background: #a93226; }
.download-info { margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-light); }

/* Book page */
.book-header {
    text-align: center;
    padding: 1.5rem 1rem;
    border-bottom: 2px solid var(--gold);
    margin-bottom: 1.5rem;
}
.book-header h1 { font-size: 1.7rem; color: var(--primary); }
.book-header .badge {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    padding: 0.2rem 0.7rem;
    border-radius: 4px;
    font-size: 0.8rem;
    margin-top: 0.3rem;
}

.chapter { margin-bottom: 1.8rem; }
.chapter h2 {
    font-size: 1.2rem;
    color: var(--primary);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.3rem;
    margin-bottom: 0.6rem;
}
.verse {
    margin-bottom: 0.5rem;
    padding-left: 2rem;
    text-indent: -2rem;
}
.vnum {
    font-weight: bold;
    color: var(--accent);
    font-size: 0.8rem;
    vertical-align: super;
    margin-right: 0.3rem;
}

/* Book nav */
.book-nav {
    display: flex;
    justify-content: space-between;
    padding: 1rem 0;
    margin-bottom: 1rem;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.nav-btn {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.5rem 1rem;
    text-decoration: none;
    color: var(--text);
    font-size: 0.9rem;
    transition: all 0.2s;
}
.nav-btn:hover { border-color: var(--gold); }
.home-btn { margin: 0 auto; }

/* Footer */
.site-footer {
    text-align: center;
    padding: 1.5rem;
    font-size: 0.85rem;
    color: var(--text-light);
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}

/* PDF-specific styles */
@media print {
    .book-nav, .site-header, .site-footer, .download-section { display: none; }
    body { background: #fff; font-size: 11pt; }
    .container { max-width: 100%; padding: 0.5in; }
    .book-header { border-bottom: 1pt solid #000; }
    .chapter h2 { font-size: 14pt; }
    .vnum { font-size: 7pt; }
}
'''


def build_index(all_books, all_data):
    """Build the main index.html."""
    ot_books = [(n, d) for n, d in zip(all_books, all_data) if int(n[:2]) <= 39]
    nt_books = [(n, d) for n, d in zip(all_books, all_data) if int(n[:2]) >= 40]
    
    def render_book_list(books):
        html = '<div class="book-grid">\n'
        for name, (title, _) in books:
            num = name[:2]
            short = get_short_name(name)
            html += f'<a href="books/{name}.html" class="book-card"><span class="bnum">{num}.</span> {short}</a>\n'
        html += '</div>\n'
        return html
    
    # Estimate PDF size
    total_bytes = sum(os.path.getsize(f'{SGSS_DIR}/{b}.txt') for b in all_books)
    pdf_est_mb = total_bytes * 3 / (1024 * 1024)  # rough estimate
    
    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGSS Bible — Simplified God's Sacred Scriptures</title>
    <link rel="stylesheet" href="styles.css">
    <meta name="description" content="Read the SGSS Bible online — a simplified, easy-to-understand adaptation of the King James Version.">
</head>
<body>

<header class="site-header">
    <h1><a href="index.html">📖 SGSS Bible</a></h1>
    <p class="subtitle">Simplified God's Sacred Scriptures</p>
</header>

<div class="container">

    <div class="download-section">
        <h2>📥 Download the Complete Bible</h2>
        <p>Get the full SGSS Bible as a PDF — read offline on your phone, tablet, or computer.</p>
        <p style="margin-top:0.8rem;">
            <a href="sgss-bible.pdf" class="download-btn" download>📄 Download PDF (~{"%.0f" % pdf_est_mb} MB)</a>
        </p>
        <p class="download-info">Based on the King James Version — adapted into simple, clear English.</p>
    </div>

    <div class="testament-section">
        <h2>📜 Old Testament</h2>
        {render_book_list(ot_books)}
    </div>

    <div class="testament-section">
        <h2>✝️ New Testament</h2>
        {render_book_list(nt_books)}
    </div>

</div>

<footer class="site-footer">
    <p>SGSS Bible — Simplified God's Sacred Scriptures. Public Domain (CC0).</p>
    <p>Based on the King James Version. Freely available for reading, copying, and sharing.</p>
</footer>

</body>
</html>'''
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"✓ {INDEX_FILE}")


def build_book_pages(all_books, all_data):
    """Build individual HTML pages for each book."""
    os.makedirs(BOOKS_DIR, exist_ok=True)
    
    total_chapters = sum(len(chapters) for _, chapters in all_data)
    total_verses = sum(sum(len(vv) for vv in chapters.values()) for _, chapters in all_data)
    print(f"Total: {len(all_books)} books, {total_chapters} chapters, {total_verses} verses")
    
    for idx, (name, (title, chapters)) in enumerate(zip(all_books, all_data)):
        short = get_short_name(name)
        num = name[:2]
        
        chapters_html = ''
        for ch_num in sorted(chapters.keys()):
            chapters_html += render_chapter_html(ch_num, chapters[ch_num])
        
        nav = render_nav(idx, all_books)
        testament = "Old Testament" if int(num) <= 39 else "New Testament"
        
        book_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — SGSS Bible</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>

<header class="site-header">
    <h1><a href="../index.html">📖 SGSS Bible</a></h1>
</header>

<div class="container">

    {nav}

    <div class="book-header">
        <h1>{title}</h1>
        <span class="badge">{testament} · {len(chapters)} chapters</span>
    </div>

    {chapters_html}

    {nav}

</div>

<footer class="site-footer">
    <p>SGSS Bible — Simplified God's Sacred Scriptures. Public Domain (CC0).</p>
</footer>

</body>
</html>'''
        
        filepath = f'{BOOKS_DIR}/{name}.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(book_html)
    
    print(f"✓ {len(all_books)} book pages created in {BOOKS_DIR}/")


def build_pdf(all_books, all_data):
    """Generate full Bible PDF using WeasyPrint."""
    print("\nGenerating PDF...")
    
    pdf_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SGSS Bible — Complete</title>
    <style>
''' + STYLES_CSS + '''
body { background: #fff; }
.container { max-width: 700px; margin: 0 auto; padding: 0.5in; }
.chapter { page-break-inside: avoid; }
h1.book-title { font-size: 1.8rem; text-align: center; color: #2c3e50; margin: 1.5rem 0; }
.test-break { page-break-before: always; }
    </style>
</head>
<body>
<div class="container">
    <h1 style="text-align:center;font-size:2.2rem;margin-top:2in;">SGSS Bible</h1>
    <p style="text-align:center;font-style:italic;font-size:1.1rem;color:#555;">Simplified God's Sacred Scriptures</p>
    <p style="text-align:center;margin-top:1in;font-size:0.9rem;">Based on the King James Version<br>Adapted into simple, clear English</p>
    <div style="page-break-after:always;"></div>
'''
    
    for idx, (name, (title, chapters)) in enumerate(zip(all_books, all_data)):
        if int(name[:2]) == 40:
            pdf_html += '<div class="test-break"></div>\n'
        
        pdf_html += f'<h1 class="book-title">{title}</h1>\n'
        
        for ch_num in sorted(chapters.keys()):
            pdf_html += render_chapter_html(ch_num, chapters[ch_num])
    
    pdf_html += '''
</div>
</body>
</html>'''
    
    # Write temp HTML
    tmp_html = '/tmp/sgss-bible-full.html'
    with open(tmp_html, 'w', encoding='utf-8') as f:
        f.write(pdf_html)
    
    # Generate PDF with WeasyPrint
    import weasyprint
    pdf_path = 'sgss-bible.pdf'
    weasyprint.HTML(filename=tmp_html).write_pdf(pdf_path)
    
    pdf_size = os.path.getsize(pdf_path)
    print(f"✓ {pdf_path} ({pdf_size / (1024*1024):.1f} MB)")
    
    # Clean up temp
    os.remove(tmp_html)


def main():
    print("=" * 50)
    print("SGSS Bible Website + PDF Builder")
    print("=" * 50)
    
    # Parse all books
    all_books = []
    all_data = []
    
    for name in BOOK_ORDER:
        filepath = f'{SGSS_DIR}/{name}.txt'
        if not os.path.exists(filepath):
            print(f"⚠ Missing: {filepath}")
            continue
        title, chapters = parse_book(filepath)
        all_books.append(name)
        all_data.append((title, chapters))
        print(f"  📖 {title} ({len(chapters)} chapters)")
    
    print(f"\nParsed {len(all_books)} books.")
    
    # Write CSS
    with open(STYLE_FILE, 'w', encoding='utf-8') as f:
        f.write(STYLES_CSS)
    print(f"✓ {STYLE_FILE}")
    
    # Build pages
    build_index(all_books, all_data)
    build_book_pages(all_books, all_data)
    build_pdf(all_books, all_data)
    
    # Create .gitkeep for books dir if needed
    with open(f'{BOOKS_DIR}/.gitkeep', 'w') as f:
        f.write('')
    
    print("\n✅ ALL DONE!")
    print(f"   Website: index.html + {len(all_books)} book pages")
    print(f"   PDF: sgss-bible.pdf")
    print(f"\n   Push to GitHub and enable Pages from root (main branch).")


if __name__ == '__main__':
    main()
