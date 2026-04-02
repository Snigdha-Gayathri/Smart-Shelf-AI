"""Routes for natural-language mood recommendations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from controllers.recommendation_controller import handle_mood_recommendation
from models.schemas import MoodRecommendationRequest

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend")
def recommend(payload: MoodRecommendationRequest, limit: int = Query(default=10, ge=1, le=50)):
    """Return recommendations for a free-text mood query."""
    query = payload.query if payload.query is not None else payload.text
    try:
        return handle_mood_recommendation(query or "", limit=limit)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
