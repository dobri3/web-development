from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from domain.models import Movie, Watchlist


@transaction.atomic
def add_to_watchlist(user, movie_id: int) -> Watchlist:
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist as exc:
        raise NotFound(detail="Movie not found.") from exc

    if Watchlist.objects.filter(user=user, movie=movie).exists():
        raise ValidationError({"detail": "Movie is already in watchlist."})

    return Watchlist.objects.create(user=user, movie=movie)


@transaction.atomic
def remove_from_watchlist(user, movie_id: int) -> None:
    deleted_count, _ = Watchlist.objects.filter(
        user=user,
        movie_id=movie_id,
    ).delete()

    if deleted_count == 0:
        raise NotFound(detail="Movie is not in watchlist.")