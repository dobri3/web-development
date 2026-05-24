from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from services.subscription_service import (
    create_subscription,
    get_user_subscription
)


class SubscriptionServiceTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="test"
        )

    def test_create_subscription(self):

        subscription = create_subscription(
            self.user,
            timezone.now() + timedelta(days=30)
        )

        self.assertTrue(subscription.is_active)

    def test_get_subscription(self):

        create_subscription(
            self.user,
            timezone.now() + timedelta(days=30)
        )

        subscription = get_user_subscription(
            self.user
        )

        self.assertIsNotNone(subscription)