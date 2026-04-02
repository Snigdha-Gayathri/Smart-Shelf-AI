"""Book service layer for catalog read operations."""

from __future__ import annotations

from typing import Dict, List

from services.book_repository import get_all_books as repo_get_all_books
from services.book_repository import get_book_by_id as repo_get_book_by_id


def list_books() -> List[Dict]:
    """Return all catalog books."""
    return repo_get_all_books()


def fetch_book_by_id(book_id: str) -> Dict:
    """Return a single catalog book or raise LookupError."""
    book = repo_get_book_by_id(book_id)
    if book is None:
        raise LookupError("Book not found")
    return book