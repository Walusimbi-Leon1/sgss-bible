# Contributing to SGSS Bible

Thank you for your interest in making Scripture more accessible!

## Ways to Contribute

### 🖊️ Translate a Book
Pick a book from the `kjv/` directory, read the KJV text, and write the SGSS version into the corresponding file in `sgss/`. Follow the style guide below.

### 📝 Review & Edit
Read through existing SGSS chapters and submit improvements — clearer wording, better flow, fixing mistakes.

### 🛠️ Build Tools
Help with tooling: validation scripts, diff checkers, web viewer, or automated aid for translation.

### 🐛 Report Issues
Spotted an error or confusing verse? Open a GitHub issue.

## Style Guide

1. **Use modern English** — you/your instead of thee/thou/thy
2. **Keep it simple** — short sentences, common words
3. **Preserve meaning** — don't add interpretation, just clarify
4. **Keep verse numbering** — always match the KJV chapter:verse structure
5. **Maintain paragraph flow** — verses can run together where natural
6. **Faithful, not fancy** — the goal is understanding, not poetry

### Example

**KJV (Genesis 1:1-3):**
> 1:1 In the beginning God created the heaven and the earth.
> 1:2 And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.
> 1:3 And God said, Let there be light: and there was light.

**SGSS:**
> 1:1 In the beginning, God created the heavens and the earth.
> 1:2 The earth was empty and had no shape. Darkness covered the deep waters, and the Spirit of God was moving over the surface of the water.
> 1:3 Then God said, "Let there be light," and there was light.

## Getting Started

1. Fork this repository
2. Create a branch: `git checkout -b translate/book-name`
3. Translate a full book into `sgss/`
4. Commit and push
5. Open a Pull Request

## Code of Conduct

Be respectful. This is a volunteer project aimed at making Scripture accessible to everyone.
