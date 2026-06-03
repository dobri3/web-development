from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from domain.models import Genre, Movie, Subscription, Watchlist


class MovieAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.action = Genre.objects.create(name="Action")
        self.drama = Genre.objects.create(name="Drama")

        for index in range(12):
            movie = Movie.objects.create(
                title=f"Action Movie {index}",
                description="Action description",
                release_year=2020 + index,
            )
            movie.genres.add(self.action)

        self.drama_movie = Movie.objects.create(
            title="Interstellar",
            description="Space drama",
            release_year=2014,
        )
        self.drama_movie.genres.add(self.drama)

    def _results(self, response):
        return response.data.get("results", response.data)

    def test_movies_list_is_paginated(self):
        response = self.client.get("/api/movies/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)

    def test_movies_can_be_filtered_by_genre(self):
        response = self.client.get("/api/movies/", {"genre": "Drama"})

        self.assertEqual(response.status_code, 200)
        titles = [movie["title"] for movie in self._results(response)]
        self.assertEqual(titles, ["Interstellar"])

    def test_movies_can_be_filtered_by_release_year(self):
        response = self.client.get("/api/movies/", {"release_year": 2014})

        self.assertEqual(response.status_code, 200)
        titles = [movie["title"] for movie in self._results(response)]
        self.assertEqual(titles, ["Interstellar"])

    def test_movies_can_be_searched(self):
        response = self.client.get("/api/movies/", {"search": "Inter"})

        self.assertEqual(response.status_code, 200)
        titles = [movie["title"] for movie in self._results(response)]
        self.assertEqual(titles, ["Interstellar"])

    def test_movie_detail(self):
        response = self.client.get(f"/api/movies/{self.drama_movie.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Interstellar")

    def test_movie_detail_not_found_returns_domain_error(self):
        response = self.client.get("/api/movies/999999/")

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "MOVIE_NOT_FOUND")

    def test_invalid_release_year_returns_400(self):
        response = self.client.get("/api/movies/", {"release_year": "bad"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

    def test_too_old_release_year_returns_400(self):
        response = self.client.get("/api/movies/", {"release_year": 1000})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])


class WatchlistAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            password="password",
        )
        self.movie = Movie.objects.create(
            title="Movie",
            description="Description",
            release_year=2024,
        )
        self.client.force_authenticate(user=self.user)

    def _results(self, response):
        return response.data.get("results", response.data)

    @patch("services.watchlist_service.httpx.post")
    def test_add_movie_to_watchlist(self, mock_post):
        mock_post.return_value.status_code = 200

        response = self.client.post(
            "/api/watchlist/",
            {"movie": self.movie.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["movie"], self.movie.id)
        self.assertEqual(Watchlist.objects.count(), 1)

    @patch("services.watchlist_service.httpx.post")
    def test_duplicate_watchlist_item_returns_error(self, mock_post):
        mock_post.return_value.status_code = 200
        self.client.post(
            "/api/watchlist/",
            {"movie": self.movie.id},
            format="json",
        )

        response = self.client.post(
            "/api/watchlist/",
            {"movie": self.movie.id},
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["error"]["code"], "ALREADY_IN_WATCHLIST")

    def test_list_watchlist(self):
        watchlist_item = Watchlist.objects.create(
            user=self.user,
            movie=self.movie,
        )

        response = self.client.get("/api/watchlist/")

        self.assertEqual(response.status_code, 200)
        results = self._results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], watchlist_item.id)

    def test_delete_watchlist_item(self):
        watchlist_item = Watchlist.objects.create(
            user=self.user,
            movie=self.movie,
        )

        response = self.client.delete(f"/api/watchlist/{watchlist_item.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Watchlist.objects.filter(id=watchlist_item.id).exists())


class SubscriptionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="subscriber",
            password="password",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_subscription_returns_404_when_missing(self):
        response = self.client.get("/api/subscription/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"]["code"], "SUBSCRIPTION_NOT_FOUND")

    def test_create_subscription(self):
        response = self.client.post("/api/subscription/", {}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("expires_at", response.data)
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)

    def test_create_subscription_extends_existing_subscription(self):
        subscription = Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )
        old_expires_at = subscription.expires_at

        response = self.client.post("/api/subscription/", {}, format="json")

        subscription.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)
        self.assertGreater(subscription.expires_at, old_expires_at)

    def test_get_active_subscription(self):
        Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )

        response = self.client.get("/api/subscription/active/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("expires_at", response.data)

    def test_get_active_subscription_returns_404_when_expired(self):
        Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() - timedelta(days=1),
        )

        response = self.client.get("/api/subscription/active/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"]["code"], "ACTIVE_SUBSCRIPTION_NOT_FOUND")

    def test_cancel_subscription(self):
        subscription = Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )

        response = self.client.post("/api/subscription/cancel/", {}, format="json")

        subscription.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(subscription.expires_at, timezone.now())