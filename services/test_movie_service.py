from django.test import TestCase
from domain.models import Movie, Genre

from services.movie_service import (
    get_movie,
    get_movies
)


class MovieServiceTests(TestCase):

    def setUp(self):

        genre = Genre.objects.create(
            name="Sci-Fi"
        )

        self.movie = Movie.objects.create(
            title="Interstellar",
            description="Space movie",
            release_year=2014
)
    def test_get_movie(self):

        movie = get_movie(
            self.movie.id
        )

        self.assertEqual(
            movie.title,
            "Interstellar"
        )

    def test_get_movies(self):

        queryset = get_movies()

        self.assertEqual(
            queryset.count(),
            1
        )