import logging

from fastapi import APIRouter, Depends, Path

from auth import get_current_user
from clients.django_client import fetch_movie_from_django
from schemas import MovieDetailOut

router = APIRouter(prefix="/movies", tags=["Movies"])
logger = logging.getLogger(__name__)


@router.get("/{movie_id}", response_model=MovieDetailOut)
async def get_movie_detail(
    movie_id: int = Path(gt=0),
    current_user: dict = Depends(get_current_user),
) -> MovieDetailOut:
    movie = await fetch_movie_from_django(movie_id)

    logger.info(
        "Movie detail requested: movie_id=%s auth_user=%s",
        movie_id,
        current_user["email"],
    )

    return MovieDetailOut(**movie)