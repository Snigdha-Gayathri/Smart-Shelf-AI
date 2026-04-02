"""Book repository helpers for the local SmartShelf dataset.

The dataset is file-backed, but this module keeps the access pattern
repository-like so controllers and services do not know where the data
comes from.
"""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


@lru_cache(maxsize=1)
def load_books() -> List[Dict]:
    """Load the book dataset from disk once and cache it in memory."""
    books_path = Path(__file__).parent.parent / "data" / "books_data.json"
    if not books_path.exists():
        logger.warning(f"Books dataset not found at {books_path}")
        return []

    with open(books_path, "r", encoding="utf-8") as handle:
        books = json.load(handle)

    if not isinstance(books, list):
        raise ValueError("books_data.json must contain a list of books")

    return [book for book in books if isinstance(book, dict)]


def normalize_book_record(book: Dict) -> Dict:
    """Return a copy of a book record with a stable id field."""
    normalized = dict(book)
    normalized["id"] = book.get("id") or _slugify(book.get("title", ""))
    tags = []
    for value in book.get("embedding_tags", []) or []:
        tag = str(value).strip().lower()
        if tag and tag not in tags:
            tags.append(tag)
    genre = str(book.get("genre") or "").strip().lower()
    if genre and genre not in tags:
        tags.append(genre)
    for word in str(book.get("mood") or "").split():
        word = word.strip().lower()
        if word and word not in tags:
            tags.append(word)
    normalized["tags"] = tags
    normalized["emotionProfile"] = list(dict.fromkeys([
        str(value).strip().lower()
        for value in (book.get("emotion_tags") or [])
        if str(value).strip()
    ]))
    return normalized


def get_all_books() -> List[Dict]:
    """Return all books with derived ids."""
    return [normalize_book_record(book) for book in load_books()]


def get_book_by_id(book_id: str) -> Optional[Dict]:
    """Find a book by derived id, title, or explicit id field."""
    lookup = (book_id or "").strip().lower()
    if not lookup:
        return None

    for book in load_books():
        candidate_id = (book.get("id") or _slugify(book.get("title", ""))).strip().lower()
        title = (book.get("title") or "").strip().lower()
        if lookup in {candidate_id, title}:
            return normalize_book_record(book)

    return None