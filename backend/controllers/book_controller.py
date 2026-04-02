"""Book Controller — handles book interaction requests.

Validates input, delegates business logic to services, and
returns structured responses. Contains NO business logic itself.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from models.schemas import BookInteractionRequest
from services.memory_service import update_user_memory
from services.book_service import list_books, fetch_book_by_id

logger = logging.getLogger(__name__)


def handle_book_interaction(payload: BookInteractionRequest) -> Dict:
    """Process a new book interaction.

    Delegates to memory_service.update_user_memory which handles:
      - Storing the interaction
      - Updating trope weights
      - Recalculating personality profile

    Args:
        payload: Validated BookInteractionRequest.

    Returns:
        Dict with the stored interaction and status info.

    Raises:
        ValueError: If validation fails inside the service.
        Exception: For unexpected errors (logged and re-raised).
    """
    try:
        result = update_user_memory(
            user_id=payload.user_id,
            book_id=payload.book_id,
            emotional_tags=payload.emotional_tags,
            rating=payload.rating,
            liked_mmc_type=payload.liked_mmc_type,
            is_dnf=payload.is_dnf,
            completion_percentage=payload.completion_percentage,
            explicit_feedback=payload.explicit_feedback,
        )
        return {
            "status": "ok",
            "interaction": result,
            "message": "Book interaction stored and memory updated successfully",
        }
    except ValueError as ve:
        logger.warning(f"Validation error in book interaction: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error processing book interaction: {e}", exc_info=True)
        raise


def handle_get_all_books() -> List[Dict]:
    """Return all book catalog entries."""
    try:
        return list_books()
    except Exception as e:
        logger.error(f"Error fetching books catalog: {e}", exc_info=True)
        raise


def handle_get_book_by_id(book_id: str) -> Dict:
    """Return a single book record by id or title."""
    try:
        return fetch_book_by_id(book_id)
    except LookupError:
        raise
    except Exception as e:
        logger.error(f"Error fetching book '{book_id}': {e}", exc_info=True)
        raise
