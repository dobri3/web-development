from unittest.mock import patch

from django.test import TestCase

from django.contrib.auth.models import (
    User
)

from domain.models import (
    Movie,
    Watchlist,
)

from domain.exceptions import (
    AlreadyInWatchlist,
)

from services.watchlist_service import (
    add_to_watchlist,
)


class WatchlistServiceTests(
    TestCase
):

    def setUp(self):

        self.user = (
            User.objects.create_user(
                username="test"
            )
        )

        self.movie = (
            Movie.objects.create(
                title="Movie",
                release_year=2024,
            )
        )

    @patch(
        "services.integration_service.notify_fastapi_watchlist_added"
    )
    def test_add_success(
        self,
        mock_notify,
    ):

        item = add_to_watchlist(
            self.user,
            self.movie.id,
        )

        self.assertEqual(
            item.movie,
            self.movie,
        )

    def test_duplicate(
        self
    ):

        Watchlist.objects.create(
            user=self.user,
            movie=self.movie,
        )

        with self.assertRaises(
            AlreadyInWatchlist
        ):

            add_to_watchlist(
                self.user,
                self.movie.id,
            )