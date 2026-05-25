from domain.exceptions import MovieNotFound
from domain.models import Movie


def get_movies(query_params=None):
    query_params = query_params or {}

    queryset = Movie.objects.all()

    genre = query_params.get("genre")
    release_year = query_params.get("release_year")

    if genre:
        queryset = queryset.filter(genres__name__icontains=genre)

    if release_year:
        queryset = queryset.filter(release_year=release_year)

    return queryset.distinct()


def get_movie(movie_id):
    try:
        return Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        raise MovieNotFound(movie_id)