from fastapi import APIRouter, Depends, HTTPException, status, Header
from auth import get_current_user
from models.user import User
import logging

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_watchlist(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} accessed watchlist")
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "watchlist": []
    }


@router.post("/add/{movie_id}")
async def add_to_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Movie {movie_id} added to watchlist for user {current_user.email}")
    return {"message": "Movie added to watchlist", "movie_id": movie_id}


@router.delete("/remove/{movie_id}")
async def remove_from_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Movie {movie_id} removed from watchlist for user {current_user.email}")
    return {"message": "Movie removed from watchlist", "movie_id": movie_id}