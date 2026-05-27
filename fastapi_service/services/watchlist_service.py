from domain.models import Watchlist, Movie
from domain.exceptions import (
    MovieNotFound,
    AlreadyInWatchlist,
    WatchlistItemNotFound,
)

def add_to_watchlist(user, movie_id):

    try:
        movie = Movie.objects.get(id=movie_id)

    except Movie.DoesNotExist:
        raise MovieNotFound(movie_id)

    if Watchlist.objects.filter(
        user=user,
        movie=movie
    ).exists():

        raise AlreadyInWatchlist(movie_id)

    return Watchlist.objects.create(
        user=user,
        movie=movie
    )