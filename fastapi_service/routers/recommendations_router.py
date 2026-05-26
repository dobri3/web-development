import logging

from fastapi import APIRouter, Depends, Path, Query

from auth import get_current_user
from clients.django_client import fetch_movies_from_django
from schemas import RecommendationResponse
from services.recommendation_service import build_recommendations

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
logger = logging.getLogger(__name__)


@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int = Path(gt=0),
    limit: int = Query(default=5, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
) -> RecommendationResponse:
    movies = await fetch_movies_from_django()

    recommendations = build_recommendations(
        movies=movies,
        user_id=user_id,
        limit=limit,
    )

    logger.info(
        "Recommendations requested: user_id=%s auth_user=%s count=%s",
        user_id,
        current_user["email"],
        len(recommendations),
    )

    return RecommendationResponse(movies=recommendations)