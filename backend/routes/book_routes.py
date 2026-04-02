"""Book Routes — API endpoints for book interactions.

POST /books/interact → Orchestrator.handleBookInteraction()

Phase 4: Routes now call the Agent Orchestrator instead of individual services.
The orchestrator coordinates: Memory → Tropes → ReadingHabit → Growth.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.schemas import BookInteractionRequest
from controllers.orchestrator_controller import handle_orchestrated_book_interaction
from controllers.book_controller import handle_get_all_books, handle_get_book_by_id

router = APIRouter(prefix="/books", tags=["books"])
catalog_router = APIRouter(prefix="/api/books", tags=["books"])


@router.post("/interact")
def interact_with_book(payload: BookInteractionRequest):
    """Store a book interaction and trigger the full agent pipeline.

    Phase 4: Now routed through the Agent Orchestrator which coordinates:
      1. Memory update (Phase 1) — stores interaction, updates weights
      2. Trope engine (Phase 2) — fatigue detection, suppression
      3. Reading Habit Agent — recalculates habit analytics
      4. Growth Agent — checks if diversification suggestion needed

    All data persists in the database.
    """
    try:
        result = handle_orchestrated_book_interaction(payload)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@catalog_router.get("")
def get_all_books():
    """Return the full book catalog as an array."""
    try:
        return handle_get_all_books()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@catalog_router.get("/{book_id}")
def get_book_by_id(book_id: str):
    """Return a single book by id or title."""
    if not book_id or not book_id.strip():
        return JSONResponse(status_code=404, content={"error": "Book not found"})

    try:
        return handle_get_book_by_id(book_id)
    except LookupError:
        return JSONResponse(status_code=404, content={"error": "Book not found"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
