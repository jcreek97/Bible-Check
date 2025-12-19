import json
import re
from pathlib import Path

# =========================
# FILE LOCATIONS (repo root)
# =========================
INPUT = Path("verses-1769.json")
OUTPUT = Path("kjv_word_counts.json")

# =========================
# CANONICAL KJV BOOK ORDER
# =========================
BOOK_ORDER = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy",
    "Joshua","Judges","Ruth","1 Samuel","2 Samuel",
    "1 Kings","2 Kings","1 Chronicles","2 Chronicles",
    "Ezra","Nehemiah","Esther","Job","Psalms",
    "Proverbs","Ecclesiastes","Song of Solomon","Isaiah",
    "Jeremiah","Lamentations","Ezekiel","Daniel",
    "Hosea","Joel","Amos","Obadiah","Jonah","Micah",
    "Nahum","Habakkuk","Zephaniah","Haggai","Zechariah",
    "Malachi",
    "Matthew","Mark","Luke","John","Acts",
    "Romans","1 Corinthians","2 Corinthians","Galatians",
    "Ephesians","Philippians","Colossians","1 Thessalonians",
    "2 Thessalonians","1 Timothy","2 Timothy","Titus",
    "Philemon","Hebrews","James","1 Peter","2 Peter",
    "1 John","2 John","3 John","Jude","Revelation"
]

# =========================
# BOOK NAME NORMALISATION
# =========================
ALIASES = {
    "Song of Songs": "Song of Solomon",
    "Canticles": "Song of Solomon",
    "Solomon's Song": "Song of Solomon",
    "Song of Solomon": "Song of Solomon"
}

# =========================
# WORD TOKEN RULE
# =========================
# Counts:
# - letters A–Z
# - allows internal apostrophes or hyphens
#   (God's, can't, well-being)
WORD_RE = re.compile(r"[A-Za-z]+(?:[\'’-][A-Za-z]+)*")

def normalise_book(book: str) -> str:
    return ALIASES.get(book, book)

def count_words(text: str) -> int:
    # Remove paragraph markers and brackets,
    # but KEEP the words inside brackets
    text = (
        text.replace("#", " ")
            .replace("[", "")
            .replace("]", "")
    )
    text = re.sub(r"\s+", " ", text).strip()
    return len(WORD_RE.findall(text))

def parse_ref(ref: str):
    """
    Parses references like:
      'Genesis 1:1'
      '1 John 5:7'
      'Solomon's Song 2:3'
    """
    book, chv = ref.rsplit(" ", 1)
    book = normalise_book(book)
    chapter, verse = chv.split(":")
    return book, int(chapter), int(verse)

def main():
    verses = json.loads(INPUT.read_text(encoding="utf-8"))

    out = {
        "_meta": {
            "translation": "KJV",
            "source": "verses-1769.json (public-domain KJV)",
            "countingRules": (
                "Words are A–Z tokens with internal apostrophes or hyphens; "
                "brackets removed but words counted; '#' removed; "
                "selected verse counts as completed."
            ),
            "totalWords": 0
        },
        "_order": BOOK_ORDER
    }

    total_words = 0

    for ref, verse_text in verses.items():
        book, chapter, verse = parse_ref(ref)
        wc = count_words(verse_text)

        out.setdefault(book, {}) \
           .setdefault(str(chapter), {})[str(verse)] = wc

        total_words += wc

    out["_meta"]["totalWords"] = total_words

    # Final integrity check
    missing_books = [b for b in BOOK_ORDER if b not in out]
    if missing_books:
        raise RuntimeError(f"Missing books in output: {missing_books}")

    OUTPUT.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )

    print("✅ Created:", OUTPUT)
    print("📖 Total KJV words:", total_words)

if __name__ == "__main__":
    main()

