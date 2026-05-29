"""
Bible RAG Pipeline
------------------
Downloads a public-domain KJV Bible JSON, embeds verses using
sentence-transformers, stores them in ChromaDB, and provides:
  - Semantic verse retrieval
  - Verse existence verification (hallucination guard)
  - Citation formatting
"""

import os
import json
import re
import requests
import chromadb
from chromadb.utils import embedding_functions
from typing import Optional


# ── Constants ────────────────────────────────────────────────────────────────

KJV_URL = r"D:\personal_projects\RAG_MODEL\eval_dataset.json"

BIBLE_CACHE = "kjv_bible.json"
CHROMA_DIR  = "./chroma_db"
COLLECTION  = "bible_verses"

BOOK_ABBREVS = {
    # Old Testament
    "gen": "Genesis",      "exo": "Exodus",       "lev": "Leviticus",
    "num": "Numbers",      "deu": "Deuteronomy",  "jos": "Joshua",
    "jdg": "Judges",       "rut": "Ruth",         "1sa": "1 Samuel",
    "2sa": "2 Samuel",     "1ki": "1 Kings",      "2ki": "2 Kings",
    "1ch": "1 Chronicles", "2ch": "2 Chronicles", "ezr": "Ezra",
    "neh": "Nehemiah",     "est": "Esther",       "job": "Job",
    "psa": "Psalms",       "pro": "Proverbs",     "ecc": "Ecclesiastes",
    "son": "Song of Solomon","isa": "Isaiah",     "jer": "Jeremiah",
    "lam": "Lamentations", "eze": "Ezekiel",      "dan": "Daniel",
    "hos": "Hosea",        "joe": "Joel",         "amo": "Amos",
    "oba": "Obadiah",      "jon": "Jonah",        "mic": "Micah",
    "nah": "Nahum",        "hab": "Habakkuk",     "zep": "Zephaniah",
    "hag": "Haggai",       "zec": "Zechariah",    "mal": "Malachi",
    # New Testament
    "mat": "Matthew",      "mar": "Mark",         "luk": "Luke",
    "joh": "John",         "act": "Acts",         "rom": "Romans",
    "1co": "1 Corinthians","2co": "2 Corinthians","gal": "Galatians",
    "eph": "Ephesians",    "phi": "Philippians",  "col": "Colossians",
    "1th": "1 Thessalonians","2th": "2 Thessalonians",
    "1ti": "1 Timothy",    "2ti": "2 Timothy",    "tit": "Titus",
    "phm": "Philemon",     "heb": "Hebrews",      "jam": "James",
    "1pe": "1 Peter",      "2pe": "2 Peter",      "1jo": "1 John",
    "2jo": "2 John",       "3jo": "3 John",       "jud": "Jude",
    "rev": "Revelation",
}

# ── Bible loader ─────────────────────────────────────────────────────────────

def _download_bible() -> dict:
    """Download and cache the KJV Bible JSON."""
    if os.path.exists(BIBLE_CACHE):
        with open(BIBLE_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Check if KJV_URL is a local file path or a real URL
    if os.path.exists(KJV_URL):
        # Local file — read directly
        print("📖 Loading KJV Bible from local file…")
        with open(KJV_URL, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Remote URL — use requests
        print("📖 Downloading KJV Bible (first run only)…")
        resp = requests.get(KJV_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()

    with open(BIBLE_CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data

def _build_verse_index(bible: dict) -> dict:
    """
    Returns a flat lookup: { "John 3:16": "For God so loved…" }
    Works with the aruljohn/Bible-kjv JSON schema.
    """
    index = {}
    books = bible if isinstance(bible, list) else bible.get("books", [])
    for book_obj in books:
        book_name = book_obj.get("name", "")
        for chap_obj in book_obj.get("chapters", []):
            chap_num = chap_obj.get("chapter", "")
            for verse_obj in chap_obj.get("verses", []):
                v_num = verse_obj.get("verse", "")
                text  = verse_obj.get("text", "").strip()
                key   = f"{book_name} {chap_num}:{v_num}"
                index[key] = text
    return index


# ── ChromaDB setup ───────────────────────────────────────────────────────────

_client: Optional[chromadb.Client]     = None
_collection                            = None
_verse_index: dict                     = {}


def _get_collection():
    global _client, _collection, _verse_index

    if _collection is not None:
        return _collection

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    _client = chromadb.PersistentClient(path=CHROMA_DIR)

    existing = [c.name for c in _client.list_collections()]
    if COLLECTION in existing:
        _collection = _client.get_collection(COLLECTION, embedding_function=ef)
        # Also rebuild verse_index for hallucination checks
        bible       = _download_bible()
        _verse_index = _build_verse_index(bible)
        return _collection

    # First-time: build & ingest
    bible        = _download_bible()
    _verse_index = _build_verse_index(bible)

    _collection = _client.create_collection(COLLECTION, embedding_function=ef)

    docs, ids, metas = [], [], []
    for ref, text in _verse_index.items():
        docs.append(f"{ref}: {text}")
        ids.append(ref.replace(" ", "_").replace(":", "_"))
        metas.append({"reference": ref, "text": text})

    # Batch insert
    batch = 500
    for i in range(0, len(docs), batch):
        _collection.add(
            documents=docs[i:i+batch],
            ids=ids[i:i+batch],
            metadatas=metas[i:i+batch],
        )
    print(f"✅ Indexed {len(docs)} verses into ChromaDB.")
    return _collection


# ── Public API ───────────────────────────────────────────────────────────────

def retrieve_verses(query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search: returns top_k verses relevant to the query.
    Each result: { "reference": "John 3:16", "text": "…" }
    """
    col     = _get_collection()
    results = col.query(query_texts=[query], n_results=top_k)
    verses  = []
    for meta in results["metadatas"][0]:
        verses.append({"reference": meta["reference"], "text": meta["text"]})
    return verses


def verse_exists(reference: str) -> Optional[str]:
    """
    Check if a verse reference exists in the Bible.
    Returns the verse text if found, None otherwise.
    Handles formats like 'John 3:16', 'john 3:16', 'Jn 3:16'.
    """
    _get_collection()   # ensure index is loaded

    # Direct lookup
    if reference in _verse_index:
        return _verse_index[reference]

    # Normalise case
    norm = reference.strip()
    for key in _verse_index:
        if key.lower() == norm.lower():
            return _verse_index[key]

    return None


def verify_cited_verses(text: str) -> list[dict]:
    """
    Scan a model response for Bible reference patterns and verify each one.
    Returns list of { "reference": str, "valid": bool, "text": str|None }
    """
    _get_collection()

    # Pattern: optional number prefix + book name + chapter:verse
    pattern = re.compile(
        r'\b(\d\s)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s(\d+):(\d+)\b'
    )
    found = pattern.findall(text)
    results = []
    seen    = set()

    for num_prefix, book, chap, verse in found:
        ref = f"{num_prefix.strip()+' ' if num_prefix.strip() else ''}{book} {chap}:{verse}"
        if ref in seen:
            continue
        seen.add(ref)
        actual = verse_exists(ref)
        results.append({
            "reference": ref,
            "valid":     actual is not None,
            "text":      actual,
        })

    return results


def format_citation_context(verses: list[dict]) -> str:
    """Format retrieved verses as a context block for the LLM prompt."""
    if not verses:
        return ""
    lines = ["RELEVANT SCRIPTURE (KJV):"]
    for v in verses:
        lines.append(f'  • {v["reference"]}: "{v["text"]}"')
    return "\n".join(lines)
