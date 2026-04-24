from django.test import TestCase
from django.contrib.auth.models import User
from domain.models import Movie, Genre, Watchlist
from domain.exceptions import AlreadyInWatchlist, MovieNotFound
from services.watchlist_service import add_to_watchlist, remove_from_watchlist


class WatchlistServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.genre = Genre.objects.create(name='Action')
        self.movie = Movie.objects.create(
            title='Test Movie',
            description='A test movie',
            release_year=2024,
        )
        self.movie.genres.add(self.genre)

    def test_add_to_watchlist_success(self):
        """Фильм успешно добавляется в watchlist"""
        item = add_to_watchlist(self.user, self.movie.id)
        self.assertEqual(item.movie, self.movie)
        self.assertEqual(item.user, self.user)

    def test_add_duplicate_raises_error(self):
        """Нельзя добавить один фильм дважды"""
        add_to_watchlist(self.user, self.movie.id)
        with self.assertRaises(AlreadyInWatchlist):
            add_to_watchlist(self.user, self.movie.id)

    def test_add_nonexistent_movie_raises_error(self):
        """Добавление несуществующего фильма бросает MovieNotFound"""
        with self.assertRaises(MovieNotFound):
            add_to_watchlist(self.user, 99999)

    def test_remove_from_watchlist_success(self):
        """Фильм успешно удаляется из watchlist"""
        add_to_watchlist(self.user, self.movie.id)
        remove_from_watchlist(self.user, self.movie.id)
        self.assertFalse(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())