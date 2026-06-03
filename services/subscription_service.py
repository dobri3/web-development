from datetime import timedelta

from django.utils import timezone

from domain.exceptions import InvalidSubscriptionDuration, SubscriptionNotFound, ActiveSubscriptionNotFound
from domain.models import Subscription


def get_user_subscription(user):
    try:
        return Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        raise SubscriptionNotFound(user.username)


def get_user_active_subscription(user):
    try:
        subscription = get_user_subscription(user)
    except SubscriptionNotFound:
        raise ActiveSubscriptionNotFound(user.username)

    if subscription.is_active and subscription.expires_at > timezone.now():
        return subscription

    raise ActiveSubscriptionNotFound(user.username)


def create_or_extend_subscription(user, duration_days=30):
    now = timezone.now()
    if duration_days <= 0:
        raise InvalidSubscriptionDuration()
    subscription = Subscription.objects.filter(user=user).first()

    if subscription is None:
        return Subscription.objects.create(
            user=user,
            expires_at=now + timedelta(days=duration_days),
            is_active=True,
        )

    if subscription.is_active and subscription.expires_at > now:
        subscription.expires_at += timedelta(days=duration_days)
    else:
        subscription.expires_at = now + timedelta(days=duration_days)

    subscription.is_active = True
    subscription.save(update_fields=["expires_at", "is_active"])

    return subscription


def cancel_subscription(user):
    subscription = get_user_subscription(user)

    subscription.expires_at = timezone.now()
    subscription.is_active = False
    subscription.save(update_fields=["expires_at", "is_active"])

    return subscription
