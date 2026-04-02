"""Analytics utilities for Annual Wrapped metrics.

Provides pure calculation functions for:
  - Prediction vs Reality Alignment
  - Preference Stability Index
  - Exploration vs Exploitation Score

All functions are stateless and operate on input data.
"""

from __future__ import annotations

from typing import List, Dict, Set, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ──────────────────── Prediction vs Reality Alignment ────────────────────

def calculate_alignment_score(
    total_recommended: int,
    liked_recommended: int,
) -> float:
    """Calculate alignment score between recommendations and user preferences.

    Args:
        total_recommended: Total books that were recommended to the user
        liked_recommended: Of those recommendations, how many did the user like (rating >= 4)

    Returns:
        Alignment score: 0.0-1.0 (0 if no recommendations)
    """
    if total_recommended <= 0:
        return 0.0
    return min(1.0, liked_recommended / total_recommended)


def classify_alignment(score: float) -> str:
    """Classify alignment score into user-friendly label.

    Args:
        score: Alignment score (0.0-1.0)

    Returns:
        Classification string
    """
    if score < 0.4:
        return "Low Alignment"
    elif score < 0.7:
        return "Moderate Alignment"
    else:
        return "High Alignment"


# ──────────────────── Preference Stability Index ────────────────────

def extract_period_tags(
    books: List[Dict],
    period_key: str = "month",
) -> List[Set[str]]:
    """Extract top tags for each time period (monthly or quarterly).

    Args:
        books: List of book interaction records with created_at timestamps
        period_key: "month" or "quarter"

    Returns:
        List of sets, where each set contains tags for that period
    """
    if not books:
        return []

    # Group books by period
    periods: Dict[str, List[Dict]] = {}

    for book in books:
        if not isinstance(book, dict):
            continue

        try:
            created_at = book.get("created_at")
            if not created_at:
                continue

            # Parse ISO timestamp
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            # Generate period key
            if period_key == "quarter":
                quarter = (dt.month - 1) // 3 + 1
                period = f"{dt.year}-Q{quarter}"
            else:  # month
                period = f"{dt.year}-{dt.month:02d}"

            if period not in periods:
                periods[period] = []
            periods[period].append(book)

        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse timestamp for book: {book}, error: {e}")
            continue

    # Extract top tags for each period
    period_tags: List[Set[str]] = []

    for period in sorted(periods.keys()):
        books_in_period = periods[period]
        tag_counter: Dict[str, int] = {}

        for book in books_in_period:
            # Collect tag sources
            tags = []
            if isinstance(book.get("tags"), list):
                tags.extend(book.get("tags", []))
            if isinstance(book.get("embedding_tags"), list):
                tags.extend(book.get("embedding_tags", []))
            if isinstance(book.get("genre"), str):
                tags.extend(book.get("genre", "").split())

            # Count tags
            for tag in tags:
                if tag and isinstance(tag, str):
                    tag_lower = tag.strip().lower()
                    if tag_lower:
                        tag_counter[tag_lower] = tag_counter.get(tag_lower, 0) + 1

        # Take top 5 tags for this period
        top_tags = set()
        if tag_counter:
            sorted_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)
            top_tags = {tag for tag, _ in sorted_tags[:5]}

        period_tags.append(top_tags)

    return period_tags


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets.

    Jaccard = |A ∩ B| / |A ∪ B|

    Args:
        set_a: First set
        set_b: Second set

    Returns:
        Similarity score: 0.0-1.0
    """
    if not set_a and not set_b:
        return 1.0  # Both empty = similar
    if not set_a or not set_b:
        return 0.0  # One empty = not similar

    intersection = len(set_a & set_b)
    union = len(set_a | set_b)

    if union == 0:
        return 0.0

    return intersection / union


def calculate_stability_score(period_tags: List[Set[str]]) -> float:
    """Calculate preference stability by comparing consecutive periods.

    Args:
        period_tags: List of tag sets, one per time period (sorted chronologically)

    Returns:
        Stability score: 0.0-1.0 (1.0 = perfectly stable, 0.0 = highly dynamic)
    """
    if len(period_tags) < 2:
        return 0.0  # Not enough data for comparison

    similarities = []
    for i in range(1, len(period_tags)):
        similarity = jaccard_similarity(period_tags[i - 1], period_tags[i])
        similarities.append(similarity)

    if not similarities:
        return 0.0

    return sum(similarities) / len(similarities)


def classify_stability(score: float) -> str:
    """Classify stability score into user-friendly label.

    Args:
        score: Stability score (0.0-1.0)

    Returns:
        Classification string
    """
    if score > 0.7:
        return "Highly Stable"
    elif score > 0.4:
        return "Moderately Evolving"
    else:
        return "Highly Dynamic"


# ──────────────────── Exploration vs Exploitation Score ────────────────────

def calculate_exploration_ratio(books: List[Dict]) -> float:
    """Calculate the ratio of books with new vs. repeated genres.

    Tracks genres chronologically:
      - First encounter with a genre = exploration
      - Repeated genres = exploitation
      - Ratio = exploration / total_books

    Args:
        books: List of book interaction records (in chronological order)

    Returns:
        Exploration ratio: 0.0-1.0
    """
    if not books:
        return 0.0

    seen_genres: Set[str] = set()
    exploration_count = 0
    total_count = 0

    for book in books:
        if not isinstance(book, dict):
            continue

        # Prefer genre field, fallback to first genre from genres list
        genre = book.get("genre")
        if not genre and isinstance(book.get("genres"), list):
            genres_list = book.get("genres", [])
            genre = genres_list[0] if genres_list else None

        if not genre or not isinstance(genre, str):
            continue

        genre_lower = genre.strip().lower()
        if not genre_lower:
            continue

        total_count += 1

        if genre_lower not in seen_genres:
            exploration_count += 1
            seen_genres.add(genre_lower)

    if total_count == 0:
        return 0.0

    return exploration_count / total_count


def classify_exploration(ratio: float) -> str:
    """Classify exploration ratio into user-friendly label.

    Args:
        ratio: Exploration ratio (0.0-1.0)

    Returns:
        Classification string
    """
    if ratio > 0.6:
        return "Explorer"
    elif ratio > 0.3:
        return "Balanced Reader"
    else:
        return "Preference-Focused Reader"


# ──────────────────── Combined Handler ────────────────────

def calculate_all_metrics(
    total_recommended: int,
    liked_recommended: int,
    books_with_metadata: List[Dict],
) -> Dict:
    """Calculate all three metrics in one call.

    Args:
        total_recommended: Total books recommended to user
        liked_recommended: Recommended books the user liked
        books_with_metadata: User's book interactions with full metadata

    Returns:
        Dict with all three metrics and classifications
    """
    # Prediction vs Reality Alignment
    alignment_score = calculate_alignment_score(total_recommended, liked_recommended)
    alignment_label = classify_alignment(alignment_score)

    # Preference Stability Index
    period_tags = extract_period_tags(books_with_metadata, period_key="month")
    stability_score = calculate_stability_score(period_tags)
    stability_label = classify_stability(stability_score)

    # Exploration vs Exploitation
    exploration_ratio = calculate_exploration_ratio(books_with_metadata)
    exploration_label = classify_exploration(exploration_ratio)

    return {
        "predictionAlignment": {
            "score": round(alignment_score, 3),
            "label": alignment_label,
            "context": ("How well recommendations matched your actual preferences",
                       f"Based on {liked_recommended}/{total_recommended} recommended books liked"),
        },
        "preferenceStability": {
            "score": round(stability_score, 3),
            "label": stability_label,
            "context": ("Consistency of your reading patterns over time",
                       f"Analyzed across {len(period_tags)} months"),
        },
        "explorationProfile": {
            "score": round(exploration_ratio, 3),
            "label": exploration_label,
            "context": ("Your tendency to explore vs stick to familiar genres",
                       f"{exploration_ratio*100:.1f}% of your reads were new genres"),
        },
    }
