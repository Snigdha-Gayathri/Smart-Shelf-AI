"""Helpers for mapping free-form mood text to known emotion anchors."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

FALLBACK_MOOD_MAP = {
    "hungry": "curiosity",
    "bored": "neutral",
    "lonely": "sadness",
    "overthinking": "anxiety",
}


def normalize_query_text(text: Optional[str]) -> str:
    """Validate and normalize recommendation text."""
    normalized = (text or "").strip()
    if not normalized:
        raise ValueError("Query text cannot be empty")
    return normalized


def resolve_fallback_mood(text: str) -> Optional[str]:
    """Map an out-of-vocabulary mood to a known emotion label."""
    normalized = (text or "").strip().lower()
    if not normalized:
        return None

    if normalized in FALLBACK_MOOD_MAP:
        return FALLBACK_MOOD_MAP[normalized]

    tokens = re.findall(r"[a-z]+", normalized)
    for token in tokens:
        if token in FALLBACK_MOOD_MAP:
            return FALLBACK_MOOD_MAP[token]

    return None


def resolve_reference_emotions(text: str, compound_emotions: Optional[Dict[str, float]] = None) -> List[str]:
    """Return the reference emotion list for the ML pipeline."""
    fallback_mood = resolve_fallback_mood(text)
    if fallback_mood:
        return [fallback_mood]

    if compound_emotions:
        return list(compound_emotions.keys())[:5]

    return []


def should_skip_query_filtering(text: str, compound_emotions: Optional[Dict[str, float]] = None) -> bool:
    """Return True when the query should not be narrowed before ranking."""
    return resolve_fallback_mood(text) is not None and not compound_emotions