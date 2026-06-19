# 📖 SGSS Bible — Simplified God's Sacred Scriptures

**SGSS** (Simplified God's Sacred Scriptures) is an open-source adaptation of the King James Version (KJV) Bible into **simple, easy-to-understand English**.

## 🌐 Website & Download

- **Read online:** [walusimbi-leon1.github.io/sgss-bible](https://walusimbi-leon1.github.io/sgss-bible/) — browse all 66 books by chapter
- **Download PDF:** [sgss-bible.pdf](https://walusimbi-leon1.github.io/sgss-bible/sgss-bible.pdf) (~4.4 MB, full Bible for offline reading)

## About This Project

The King James Version is a beautiful but **archaic** translation — full of "thee," "thou," "hast," and complex sentence structures that can be difficult for modern readers. **SGSS** takes the KJV as its source text and **rewrites each verse into clear, straightforward English** while preserving the original meaning, structure, and intent.

## Structure

```
sgss-bible/
├── README.md           ← You are here
├── LICENSE             ← CC0 — public domain
├── CONTRIBUTING.md     ← How to help
├── index.html          ← Website homepage
├── styles.css          ← Website styling
├── books/              ← Individual book pages (all 66 books)
├── sgss-bible.pdf      ← Full Bible PDF for download (~4.4 MB)
├── scripts/
│   └── parse_kjv.py    ← KJV source parser
├── kjv/                ← KJV source text (raw material)
│   ├── 01-Genesis.txt
│   ├── 02-Exodus.txt
│   └── ... (66 books)
└── sgss/               ← SGSS adapted version (the output)
    ├── 01-Genesis.txt
    ├── 02-Exodus.txt
    └── ... (66 books — initially populated from KJV)
```

### Book Numbering

Books are numbered 01–66 following the standard Protestant canon:
- **OT:** 01 Genesis → 39 Malachi
- **NT:** 40 Matthew → 66 Revelation

## How the Translation Works

Each verse in the KJV is adapted following these principles:

1. **Replace archaic language** — "thee/thou/thy" → "you/your"
2. **Simplify complex sentences** — break long verses into shorter, clearer ones
3. **Update outdated words** — "privily" → "secretly," "wot" → "know"
4. **Add clarifying context** — explain pronouns when the referent is unclear
5. **Preserve meaning** — the message stays faithful to the original
6. **Maintain verse numbering** — so it's always cross-referencable with KJV

## Contributing

This is an open-source project! Whether you want to translate a book, review existing work, suggest improvements, or help with tooling, **you're welcome**.

Check out [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

## License

The King James Version is **public domain**.

The SGSS adaptation is dedicated to the **public domain** under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). You are free to copy, modify, distribute, and use this work for any purpose — no permission needed.

## Why SGSS?

- **📖 Readable** — Clear English anyone can understand
- **🔓 Free** — No copyright, no restrictions, no paywalls
- **🤝 Community-driven** — Built by people who care about making Scripture accessible
- **📜 Faithful to the KJV** — Based on the most influential English translation ever made

---

*"The grass withers, the flower fades, but the word of our God stands forever."* — Isaiah 40:8 (SGSS)
