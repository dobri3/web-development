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
    subscription = get_user_subscription(user)

    if subscription.expires_at > timezone.now():
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
        )

    if subscription.expires_at > now:
        subscription.expires_at += timedelta(days=duration_days)
    else:
        subscription.expires_at = now + timedelta(days=duration_days)

    subscription.save(update_fields=["expires_at"])

    return subscription


def cancel_subscription(user):
    subscription = get_user_subscription(user)

    subscription.expires_at = timezone.now()
    subscription.save(update_fields=["expires_at"])

    return subscription