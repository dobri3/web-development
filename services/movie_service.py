from domain.models import Movie
from django.shortcuts import get_object_or_404


def get_movies(filters=None):

    queryset = Movie.objects.all()

    if filters:

        title = filters.get("title")

        if title:
            queryset = queryset.filter(
                title__icontains=title
            )

    return queryset


def get_movie(movie_id):

    return get_object_or_404(
        Movie,
        pk=movie_id
    )