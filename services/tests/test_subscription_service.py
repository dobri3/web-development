from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from domain.exceptions import (
    SubscriptionNotFound,
    ActiveSubscriptionNotFound,
)

from services.subscription_service import (
    create_or_extend_subscription,
    cancel_subscription,
    get_user_active_subscription,
    get_user_subscription,
)


class SubscriptionServiceTests(
    TestCase
):

    def setUp(self):

        self.user = (
            User.objects.create_user(
                username="testuser",
                password="pass123"
            )
        )

    def test_create_subscription(
        self
    ):

        subscription = (
            create_or_extend_subscription(
                self.user
            )
        )

        self.assertIsNotNone(
            subscription
        )

        self.assertEqual(
            subscription.user,
            self.user
        )

    def test_get_subscription(
        self
    ):

        created = (
            create_or_extend_subscription(
                self.user
            )
        )

        subscription = (
            get_user_subscription(
                self.user
            )
        )

        self.assertEqual(
            subscription.id,
            created.id
        )

    def test_subscription_not_found(
        self
    ):

        with self.assertRaises(
            SubscriptionNotFound
        ):

            get_user_subscription(
                self.user
            )

    def test_get_active_subscription(
        self
    ):

        create_or_extend_subscription(
            self.user
        )

        subscription = (
            get_user_active_subscription(
                self.user
            )
        )

        self.assertEqual(
            subscription.user,
            self.user
        )

    def test_active_subscription_not_found(
        self
    ):

        with self.assertRaises(
            ActiveSubscriptionNotFound
        ):

            get_user_active_subscription(
                self.user
            )

    def test_cancel_subscription(
        self
    ):

        create_or_extend_subscription(
            self.user
        )

        cancelled = (
            cancel_subscription(
                self.user
            )
        )

        self.assertEqual(
            cancelled.user,
            self.user
        )

    def test_cancelled_subscription_is_not_active(
        self
    ):

        create_or_extend_subscription(
            self.user
        )

        cancel_subscription(
            self.user
        )

        with self.assertRaises(
            ActiveSubscriptionNotFound
        ):

            get_user_active_subscription(
                self.user
            )

    def test_extend_subscription(
        self
    ):

        subscription = (
            create_or_extend_subscription(
                self.user
            )
        )

        first_expire = (
            subscription.expires_at
        )

        extended = (
            create_or_extend_subscription(
                self.user
            )
        )

        self.assertGreater(
            extended.expires_at,
            first_expire
        )