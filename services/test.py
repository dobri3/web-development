from django.test import TestCase
from django.contrib.auth.models import User
from domain.models import Movie, Genre, Watchlist
from domain.exceptions import AlreadyInWatchlist, MovieNotFound
from services.watchlist_service import add_to_watchlist, remove_from_watchlist
from unittest.mock import patch


class WatchlistServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass'
        )

        self.genre = Genre.objects.create(
            name='Action'
        )

        self.movie = Movie.objects.create(
            title='Test Movie',
            description='A test movie',
            release_year=2024,
        )

        self.movie.genres.add(self.genre)

    @patch("services.watchlist_service.httpx.post")
    def test_add_to_watchlist_success(self, mock_post):
        """Фильм успешно добавляется в watchlist"""

        mock_post.return_value.status_code = 200

        item = add_to_watchlist(
            self.user,
            self.movie.id
        )

        self.assertEqual(item.movie, self.movie)
        self.assertEqual(item.user, self.user)

    @patch("services.watchlist_service.httpx.post")
    def test_add_duplicate_raises_error(self, mock_post):
        """Нельзя добавить один фильм дважды"""

        mock_post.return_value.status_code = 200

        add_to_watchlist(
            self.user,
            self.movie.id
        )

        with self.assertRaises(AlreadyInWatchlist):
            add_to_watchlist(
                self.user,
                self.movie.id
            )

    @patch("services.watchlist_service.httpx.post")
    def test_add_nonexistent_movie_raises_error(self, mock_post):
        """Добавление несуществующего фильма бросает MovieNotFound"""

        mock_post.return_value.status_code = 200

        with self.assertRaises(MovieNotFound):
            add_to_watchlist(
                self.user,
                99999
            )

    @patch("services.watchlist_service.httpx.post")
    def test_remove_from_watchlist_success(self, mock_post):
        """Фильм успешно удаляется из watchlist"""

        mock_post.return_value.status_code = 200

        add_to_watchlist(
            self.user,
            self.movie.id
        )

        remove_from_watchlist(
            self.user,
            self.movie.id
        )

        self.assertFalse(
            Watchlist.objects.filter(
                user=self.user,
                movie=self.movie
            ).exists()
        )