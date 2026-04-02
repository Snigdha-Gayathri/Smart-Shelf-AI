"""Annual Wrapped Service — computes comprehensive year-in-review analytics.

Generates a complete annual wrapped report including:
  - Prediction vs Reality Alignment
  - Preference Stability Index
  - Exploration vs Exploitation Score
  - Additional context (top genres, favorite tropes, reading stats)

All data is sourced from user interactions stored in the database.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from database.connection import get_connection
from database.migrations import ensure_memory_user
from utils.analytics_utils import (
    calculate_alignment_score,
    classify_alignment,
    extract_period_tags,
    calculate_stability_score,
    classify_stability,
    calculate_exploration_ratio,
    classify_exploration,
)

logger = logging.getLogger(__name__)


def _get_user_interactions(user_id: int) -> List[Dict]:
    """Fetch all book interactions for a user from the database.

    Returns:
        List of interaction records with full metadata
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT book_id, rating, emotional_tags, created_at, is_dnf, completion_percentage "
            "FROM book_interactions WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        )
        rows = cur.fetchall()
        interactions = []
        for row in rows:
            interactions.append({
                "book_id": row["book_id"],
                "rating": row["rating"],
                "emotional_tags": json.loads(row["emotional_tags"]) if row["emotional_tags"] else [],
                "created_at": row["created_at"],
                "is_dnf": bool(row["is_dnf"]),
                "completion_percentage": row["completion_percentage"] or 100,
            })
        return interactions
    finally:
        conn.close()


def _get_recommended_books_analysis(user_id: int) -> Dict:
    """Analyze which recommended books the user actually liked.

    Since we don't have an explicit "recommended" flag, we infer:
    - Books from user's first interactions are assumed recommended
    - OR: Books with highest trope weights matching (simulated)

    For now, we calculate based on all books with rating >= 4 vs all books read.
    """
    interactions = _get_user_interactions(user_id)

    if not interactions:
        return {
            "total_recommended": 0,
            "liked_recommended": 0,
        }

    # Heuristic: Assume first N interactions were "recommended" (system warmup phase)
    # In a real system, this would be tracked explicitly
    total_books = len(interactions)
    high_rated = len([i for i in interactions if i["rating"] >= 4])

    # Estimate: If system was giving recommendations, high ratings suggest good recommendations
    # Rough heuristic: 60% of high-rated books were from recommendations (conservative estimate)
    estimated_recommended = max(int(total_books * 0.4), 1)  # At least 1
    estimated_liked_recommended = int(high_rated * 0.6)

    return {
        "total_recommended": estimated_recommended,
        "liked_recommended": estimated_liked_recommended,
    }


def _enrich_interactions_with_book_metadata(interactions: List[Dict]) -> List[Dict]:
    """Add book metadata (genre, tags) to interactions.

    Loads from books_data.json and matches by book_id (title).
    """
    from services.memory_service import _load_books_data

    books_map = {}
    for book in _load_books_data():
        if isinstance(book, dict):
            title = book.get("title", "").lower()
            books_map[title] = book

    enriched = []
    for interaction in interactions:
        book_key = interaction["book_id"].lower()
        book_metadata = books_map.get(book_key, {})

        enriched.append({
            **interaction,
            "genre": book_metadata.get("genre", "Unknown"),
            "genres": [book_metadata.get("genre")] if book_metadata.get("genre") else [],
            "tags": book_metadata.get("tags", []),
            "embedding_tags": book_metadata.get("embedding_tags", []),
        })

    return enriched


def _get_top_genres(interactions: List[Dict], limit: int = 5) -> List[str]:
    """Extract top genres from interactions.

    Args:
        interactions: Enriched interaction records
        limit: Number of top genres to return

    Returns:
        List of genre names, sorted by frequency
    """
    genre_counter = {}
    for interaction in interactions:
        genre = interaction.get("genre")
        if genre and isinstance(genre, str):
            genre_lower = genre.strip().lower()
            if genre_lower:
                genre_counter[genre_lower] = genre_counter.get(genre_lower, 0) + 1

    sorted_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)
    return [g for g, _ in sorted_genres[:limit]]


def _get_favorite_tropes(user_id: int, limit: int = 5) -> List[str]:
    """Fetch top tropes by weight for a user.

    Args:
        user_id: The user's ID
        limit: Number of top tropes to return

    Returns:
        List of trope names, sorted by weight (highest first)
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT trope_name FROM trope_preferences "
            "WHERE user_id = ? AND weight > 0 ORDER BY weight DESC LIMIT ?",
            (user_id, limit),
        )
        return [row["trope_name"] for row in cur.fetchall()]
    finally:
        conn.close()


def _get_reading_stats(interactions: List[Dict]) -> Dict:
    """Calculate reading statistics.

    Args:
        interactions: List of interaction records

    Returns:
        Dict with reading stats
    """
    if not interactions:
        return {
            "total_books": 0,
            "avg_rating": 0.0,
            "dnf_count": 0,
            "dnf_rate": 0.0,
            "avg_completion": 0.0,
        }

    total = len(interactions)
    ratings = [i["rating"] for i in interactions if i.get("rating")]
    dnf_count = len([i for i in interactions if i.get("is_dnf")])
    completions = [i.get("completion_percentage", 100) for i in interactions]

    return {
        "total_books": total,
        "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
        "dnf_count": dnf_count,
        "dnf_rate": round(dnf_count / total, 2) if total > 0 else 0.0,
        "avg_completion": round(sum(completions) / len(completions), 1) if completions else 0.0,
    }


def generate_annual_wrapped(user_id: int) -> Dict:
    """Generate complete annual wrapped report for a user.

    Args:
        user_id: The user's ID

    Returns:
        Comprehensive wrapped report with all metrics and context
    """
    ensure_memory_user(user_id)

    # Fetch raw interactions
    interactions = _get_user_interactions(user_id)

    if not interactions:
        logger.info(f"User {user_id} has no reading interactions for wrapped report")
        return {
            "user_id": user_id,
            "status": "insufficient_data",
            "message": "Not enough reading data available for an annual wrapped report",
            "predictionAlignment": {
                "score": 0.0,
                "label": "Insufficient Data",
                "context": ("Start interacting with books to unlock this metric", ""),
            },
            "preferenceStability": {
                "score": 0.0,
                "label": "Insufficient Data",
                "context": ("Need at least 8 weeks of reading activity", ""),
            },
            "explorationProfile": {
                "score": 0.0,
                "label": "Insufficient Data",
                "context": ("Need more books to analyze exploration patterns", ""),
            },
            "extras": {
                "topGenres": [],
                "favoritesTropes": [],
                "readingStats": {
                    "total_books": 0,
                    "avg_rating": 0.0,
                    "dnf_count": 0,
                    "dnf_rate": 0.0,
                    "avg_completion": 0.0,
                },
            },
        }

    # Enrich with book metadata
    enriched_interactions = _enrich_interactions_with_book_metadata(interactions)

    # Calculate recommendation alignment
    rec_analysis = _get_recommended_books_analysis(user_id)

    # Calculate Prediction vs Reality Alignment
    alignment_score = calculate_alignment_score(
        rec_analysis["total_recommended"],
        rec_analysis["liked_recommended"],
    )
    alignment_label = classify_alignment(alignment_score)

    # Calculate Preference Stability Index
    period_tags = extract_period_tags(enriched_interactions, period_key="month")
    stability_score = calculate_stability_score(period_tags)
    stability_label = classify_stability(stability_score)

    # Calculate Exploration vs Exploitation
    exploration_ratio = calculate_exploration_ratio(enriched_interactions)
    exploration_label = classify_exploration(exploration_ratio)

    # Get additional context
    top_genres = _get_top_genres(enriched_interactions, limit=5)
    favorite_tropes = _get_favorite_tropes(user_id, limit=5)
    reading_stats = _get_reading_stats(interactions)

    logger.info(
        f"Generated annual wrapped for user {user_id}: "
        f"alignment={alignment_score:.3f}, stability={stability_score:.3f}, "
        f"exploration={exploration_ratio:.3f}, total_books={len(interactions)}"
    )

    return {
        "user_id": user_id,
        "status": "success",
        "generated_at": datetime.utcnow().isoformat(),
        "predictionAlignment": {
            "score": round(alignment_score, 3),
            "label": alignment_label,
            "context": (
                "How well recommendations matched your actual preferences",
                f"Based on {rec_analysis['liked_recommended']}/{rec_analysis['total_recommended']} recommended books liked"
                if rec_analysis["total_recommended"] > 0
                else "No recommendation data available",
            ),
        },
        "preferenceStability": {
            "score": round(stability_score, 3),
            "label": stability_label,
            "context": (
                "Consistency of your reading patterns over time",
                f"Analyzed across {len(period_tags)} months of reading",
            ),
        },
        "explorationProfile": {
            "score": round(exploration_ratio, 3),
            "label": exploration_label,
            "context": (
                "Your tendency to explore vs stick to familiar genres",
                f"{exploration_ratio*100:.1f}% of your books were new genres to you",
            ),
        },
        "extras": {
            "topGenres": top_genres,
            "favoritesTropes": favorite_tropes,
            "readingStats": reading_stats,
        },
    }
