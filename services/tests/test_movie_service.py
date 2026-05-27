from django.test import TestCase

from domain.exceptions import MovieNotFound
from domain.models import Genre, Movie
from services.movie_service import get_movie, get_movies


class MovieServiceTests(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(
            name="Action"
        )

        self.movie = Movie.objects.create(
            title="Matrix",
            release_year=1999
        )

        self.movie.genres.add(self.genre)

    def test_get_movie_success(self):
        movie = get_movie(self.movie.id)

        self.assertEqual(
            movie.title,
            "Matrix"
        )

    def test_get_movie_not_found(self):

        with self.assertRaises(MovieNotFound):
            get_movie(9999)


    def test_get_movies_by_genre(self):

        movies = get_movies(
            {"genre": "Action"}
        )
        self.assertIn(self.movie, movies)

    def test_get_movies_by_release_year(self):
        old_movie = Movie.objects.create(
            title="Alien",
            release_year=1979,
        )

        movies = get_movies({
            "release_year": 1999
        })

        self.assertIn(self.movie, movies)
        self.assertNotIn(old_movie, movies)


    def test_get_movies_without_filters(self):
            second_movie = Movie.objects.create(
                title="Alien",
                release_year=1979,
            )

            movies = get_movies({})

            self.assertEqual(
                movies.count(),
                2
            )

            self.assertIn(self.movie, movies)
            self.assertIn(second_movie, movies)