from django.db import transaction
from domain.models import Movie, Watchlist
from domain.exceptions import MovieNotFound, AlreadyInWatchlist, WatchlistItemNotFound

@transaction.atomic
def add_to_watchlist(user, movie_id: int) -> Watchlist:
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        raise MovieNotFound(movie_id)

    if Watchlist.objects.filter(user=user, movie=movie).exists():
        raise AlreadyInWatchlist(movie_id, user.username)

    return Watchlist.objects.create(user=user, movie=movie)

@transaction.atomic
def remove_from_watchlist(user, movie_id: int) -> None:
    deleted_count, _ = Watchlist.objects.filter(
        user=user,
        movie_id=movie_id,
    ).delete()

    if deleted_count == 0:
        raise WatchlistItemNotFound(movie_id, user.username)