from django.db import transaction
from django.conf import settings
from domain.models import Movie, Watchlist
from domain.exceptions import MovieNotFound, AlreadyInWatchlist, WatchlistItemNotFound
import httpx
import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def add_to_watchlist(user, movie_id: int) -> Watchlist:
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        raise MovieNotFound(movie_id)

    if Watchlist.objects.filter(user=user, movie=movie).exists():
        raise AlreadyInWatchlist(movie_id, user.username)

    watchlist_item = Watchlist.objects.create(user=user, movie=movie)

    try:
        response = httpx.post(
            f"{settings.FASTAPI_SERVICE_URL}/watchlist/notify",
            json={"user_id": user.id, "movie_id": movie_id},
            timeout=2.0
        )
        logger.info(f"FastAPI уведомлён: user={user.id}, movie={movie_id}, status={response.status_code}")
    except httpx.RequestError as e:
        logger.warning(f"FastAPI недоступен, продолжаем без уведомления: {e}")

    return watchlist_item


@transaction.atomic
def remove_from_watchlist(user, movie_id: int) -> None:
    deleted_count, _ = Watchlist.objects.filter(
        user=user,
        movie_id=movie_id,
    ).delete()

    if deleted_count == 0:
        raise WatchlistItemNotFound(movie_id, user.username)