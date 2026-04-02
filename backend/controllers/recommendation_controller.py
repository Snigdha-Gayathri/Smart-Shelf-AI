"""Controller for natural-language mood recommendations."""

from __future__ import annotations

import logging
from typing import Dict

from services.mood_recommendation_service import generate_mood_recommendations

logger = logging.getLogger(__name__)


def handle_mood_recommendation(query: str, limit: int = 10) -> Dict:
    """Return mood-aware recommendations for a free-text query."""
    try:
        return generate_mood_recommendations(query, limit=limit)
    except ValueError:
        raise
    except Exception as exc:
        logger.error(f"Error generating mood recommendations: {exc}", exc_info=True)
        raise
